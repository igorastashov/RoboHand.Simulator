---
tags: [eb300, isaaclab, newton, ppo, vision, verification]
type: validation
updated: 2026-11-16
status: native-six-axis-teacher-vision-evaluation-replay-validated
---

# EB300: адаптация готового NVIDIA teacher → vision

Владелец 16.11 явно разрешил [точечную адаптацию](2026-11-16-eb300-training-adaptation.md). Использован прежний `NVIDIA/so101-typing-task@7aec2ed26dce8c88ae007a2714680cce572e1466`, исходная обучающая клавиатура и готовые Isaac Lab/Newton/RSL-RL/OVRTX компоненты. Платформа — наша EB300 R8, шесть действий J1–J6, обычная губка, номинальная камера Redmi на запястье. ACT, новый контроллер, renderer class или framework не добавлены.

## Что изменено

[Patch, профиль, Dockerfile и воспроизведение](../../integrations/nvidia_typing/README.md). Патч добавляет выбор EB300 в существующей factory, конфигурацию articulation/приводов/камеры/TCP, список шести controlled joints и размер teacher по `env.num_actions`. Все четыре существующих loader call sites согласованы. Исходные пять действий остаются default для reference.

SO-specific reset отсутствующего gripper joint для нашей жёсткой оснастки отключён; scrape reward/termination используют нашу губку. Камере `RedmiCamera` задан обычный USD pinhole, исходная Workshop camera сохраняет проверку своей OpenCV calibration. Replay восстанавливает правильный robot profile и записывает фактическое имя/разрешение камеры. Изменения поведения видны в diff, они не выдаются за один JSON.

## Почему понадобился отдельный native asset

Первый teacher/vision запуск r4 действительно выполнил два PPO updates и сохранил модели. Однако evaluation показала `abnormal_robot` и `excessive_contact` сразу после сброса. Это не было рабочей обучающей сценой. Исходные результаты/веса сохранены отдельно как не принятый физический вариант.

Диагностика обнаружила две причины:

- Body-level `<exclude>` из штатного converter превращается в USD body `physics:filteredPairs`, а закреплённый Newton importer читает эти отношения на collider prims. Телефон, его рычаг и опорная пластина/стойка одной жёсткой оснастки давали ложные силы до5,44кН. В стандартном USD layer перечислены пять конкретных collider pairs; внешние контакты и self-collisions подвижной руки сохраняются.
- Импортированный viewer USD дал12 arm actuators вместо6. Отдельно проверено, что полное удаление actuator data оставляет руку без приводов. Поэтому native MJCF не содержит MjcActuator definitions, а USD layer задаёт ровно шесть обычных angular `PhysicsDriveAPI`. Их gains/limits соответствуют номинальному Isaac Lab config. В итоговом solver model **114 actuators =108 клавиш +6 руки**, а actions руки —6.

Это стандартные данные MJCF/USD нашей механики. Converter, Newton и Isaac Lab SDK не исправлялись. Принятые CAD/URDF и локальная [desktop R1 с10/10 нажатий](../desktop-workcell-r1.md) сохранены. Между двумя physics runtimes не заявлена динамическая эквивалентность.

## Проверенная устойчивость

Итоговый native asset прошёл100 последовательных control steps, 4секунды под гравитацией. Нулевые rate actions означают удержание nominal rest targets встроенными PD drives; координаты не переставляются на каждом шаге. Все termination flags во всех100срезах false, внешних контактов в этой позе нет. Максимальная скорость0,2696085рад/с при прежнем nominal limit0,3; финальные скорости около5,6×10⁻⁶рад/с. Лимит для прохождения теста не повышен.

Удержание имеет номинальную просадку под гравитацией: J2 устанавливается около0,9294 при target0,9рад. Это не измеренная точность реальной руки и не доказательство нажатия всех клавиш.

## Обучение и оценка

Финальные r6 camera/teacher/vision/evaluation/replay проверки завершились с `SubState=exited`, `Result=success`, `ExecMainStatus=0`. Состояние running с нулевым текущим кодом не считалось успехом. Сборка Docker image отдельно не является GPU smoke.

| Проверка | Фактический результат |
|---|---|
| Camera smoke | State[2,25], proprio[2,60], RGB history[2,6,120,160]; pixel std57,423/57,904; два PNG просмотрены, FULL_DOMAIN_RESET_OK |
| Teacher |2PPOupdates,2envs; сохранены model_0/model_1, environment/agent/run и asset identity |
| Teacher evaluation |2эпизода random13, seed900001, max_steps2; оба только step_limit,0символов/0%успеха |
| Vision |1warmup +2PPOupdates,2envs; image gradient0,0031596065, MSE0,0001281440; checkpoints/sidecars сохранены |
| Vision evaluation + USD replay | Seeds14001/14002; по25control steps, оба только step_limit,0символов/0%успеха; по26кадров USD, actual wrist160×120 |
| MP4 |2clips штатным upstream script; каждый26кадров,1920×1080,25fps. Полностью декодированы FFmpeg, первый overview кадр просмотрен; видео относится к тем же ограниченным evaluations |

Шесть image channels — два кадра одной камеры. Ненулевой gradient подтверждает обучение image branch, но не смысловое распознавание клавиш и не выученную печать. Модели после двух updates — технические checkpoints, не готовый навык.

[Численные доказательства и provenance](2026-11-16-eb300-native-validation.json). Итоговый source fingerprint `46b58089de60fa4f6b81f5046a4584a479e602c931370935ad346b99193b0e52`, patch SHA256 `7c5ff843755c26398c77cf759631271beeb9ce6f90026093d86ced84e22af42c`. Image `robohand/typing-eb300:7aec2ed-r6` / ID `sha256:0ca0132cb929c666c43708c89e7f770ac89e94404e2404c7e02144502884dc5c`. Standard USD data layer и весь локальный asset отдельно имеют свои hashes: fingerprint кода не выдаётся за identity геометрии.

Исходные SHA файлов относятся к проверенным Windows bytes в frozen archives. Для XML с CRLF численные JSON дополнительно содержат `*_lf` SHA нормализованного Git-текста. Это различие переносов строк, не различие геометрии; patch/USD configuration layer закреплены как LF в Git attributes.

## Regression и требования

- 10 штатных tutorial unit tests пройдены в итоговом r6 Linux image. Windows CLI attempt не считается модельной регрессией: upstream CLI использует Linux-only host API.
- У проверенного command-contract набора22pass/4fail. На неизменённом base image и исходном source получены те же22/4 и те же failing test IDs: два baseline contract strings и два USD-drive effort defaults расходятся с ожиданиями старых tests. Чужие tests/контракты не изменяли, полный зелёный suite не заявляется.
- Исходный пятиосевой SO-101 checkpoint после общих loader/command изменений загружен и оценён стандартным GPU entrypoint:2ограниченных эпизода, штатное завершение по step_limit. Это regression загрузки/исполнения, не успешная печать.
- Native runtime: isaaclab6.1.11, Newton1.4.0.dev0, MuJoCo3.8.1, Warp1.15.0.dev20260626, OVRTX0.5. Базовый image ID `sha256:653ebeac7606b05068d06f88472144b2c3ccb8ca2da0e90ade2f2d056224e981` сохранён. Исходный setup и его requirements не заменялись; точный converter closure — [отдельно](2026-11-16-converter-requirements.lock).

## Что ещё требуется

Свести native training scaffold в координатах основания с мировой desktop layout, проверить доступность целей и реальные контакты губки с отдельной клавишей. Затем проверить остановку/штатный resume, подобрать размер parallel batch и проводить полноценное teacher → vision обучение с отдельными seed/позами оценки. Несколько updates и эпизоды с `max_steps=2` этого не заменяют.

Крепление/оптика единственной Redmi исследованы [отдельно](2026-11-16-camera-coverage.md). Последующее решение владельца исключило zoom/crop и внешние камеры; новый ракурс пока не заменяет оптику этих smoke checkpoints. Массы, ±170°, gains, effort/rate limits и pinhole остаются номинальными. Реальная калибровка и firmware шести осей относятся к последующему этапу.

Полные SDK logs, PNG/MP4, USD/meshes, checkpoints и source/asset receipts — локально в `E:\RoboHand\runs\2026-11-16-hardware-workcell`. В публичный Git идут patch, стандартные configs и численные доказательства; [геометрия/веса остаются локальными](../publication-scope.md).

[Индекс](../index.md) · [Текущий вход](../start-here-r8.md) · [Desktop R1](../desktop-workcell-r1.md).
