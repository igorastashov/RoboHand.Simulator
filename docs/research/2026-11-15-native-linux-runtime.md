---
tags: [robohand, eb300, runtime, native-linux, newton, ovrtx]
type: validation
updated: 2026-11-15
status: native-reference-camera-ppo-evaluation-and-video-validated
---

# Дополнительный Linux-сервер: проверка камеры и обучения

Разработка, CAD, репозитории и управление экспериментами остаются на основном Windows-ПК. Дополнительный native Linux host используется по необходимости для GPU-вычислений. Это продолжение [локального запуска](2026-11-15-runtime-gpu-smoke.md): Newton/teacher в WSL2 прошли, RTX-камера получила Vulkan error.

Платформа проекта — **EB300**. Во время инфраструктурной проверки выполняется исходный **SO-101 reference**, его результат не считается EB300 policy.

## Подтверждённая среда

Read-only аудит и разрешённое владельцем обслуживание подтвердили Ubuntu 24.04.3 x86_64, i7-9800X (8 ядер / 16 потоков), около 125,5 GiB RAM и две RTX 3090 по 24576 MiB. Уже установленные kernel 6.8.0-149 и NVIDIA 580.178.04 загружены одной плановой reboot; kernel module и NVML теперь совпадают. Пакеты/драйвер не переустанавливались. Наличие NVML само по себе не доказывает исполнение нашего runtime.

Существующий стенд сохранён штатными maintenance/drain/backup средствами; его данные, образы и контейнеры не заменялись ради руки. Его приём закрыт, GPU workers временно остановлены; API/frontend оставлены для maintenance/status. Подробный аудит и доступы находятся в частном операционном плане, не в публичном Git.

## Источники и доставка

- Upstream: [NVIDIA/so101-typing-task @7aec2ed26dce8c88ae007a2714680cce572e1466](https://github.com/NVIDIA/so101-typing-task/tree/7aec2ed26dce8c88ae007a2714680cce572e1466). Повторный `git ls-remote HEAD` 15.11 показал тот же commit.
- [Штатный setup](https://github.com/NVIDIA/so101-typing-task/blob/7aec2ed26dce8c88ae007a2714680cce572e1466/docs/setup.md) и [tutorial](https://github.com/NVIDIA/so101-typing-task/blob/7aec2ed26dce8c88ae007a2714680cce572e1466/docs/tutorial.md). Новый installer/runner не создавался.
- Перенесён уже собранный локальный runtime стандартными `docker image save`, OpenSSH SFTP и `docker image load`; используется отдельный tag `robohand/so101-tutorial:7aec2ed-20261115`, без подмены чужих image tags.
- Archive runtime: **17 785 642 496 байт**, SHA256 `ce66ff2286f09a4130793ffcd8703905794e61b5e918c262c11da44cdab95ffb`.
- Source archive: **19 568 640 байт**, SHA256 `03c59934226b6ea8f89d9e6da1e29aa3c15397ca620f959655cca93e35392a62`. Оба SHA проверены после SFTP.
- Штатный Linux `tar -xpf` сохранил оба symlinks; `so101.source_fingerprint()` совпал с label образа: `7b20cbb929b2161b0e713364773bca0eb79da7bac9fb3161a55861809f9a1f1f`.

SHA архива, исходников и совпадение label доказывают доставку и происхождение, но не GPU/render smoke. Платформенный image ID после load фиксируется отдельно от исходного Desktop image ID.

Native image ID: `sha256:653ebeac7606b05068d06f88472144b2c3ccb8ca2da0e90ade2f2d056224e981`; исходный Desktop ID — `sha256:57e449f1f1d5b54a82f9f12527f78343fe1f92a730cb251d46ec80aef3d7347a`. Первое SSH-соединение с `docker image load` закрылось через 600 с, удалённый процесс продолжил распаковку. Повторный import не запускался: дождались завершения удалённого процесса, проверили tag/label и успешно выполнили stock debug. Нулевой exit исходного transport не заявляется.

Для длительных заданий использован готовый `systemd-run --user --remain-after-exit`, который сохраняет process result до явного stop. На установленном systemd 255 для пользователя включён стандартный linger, чтобы user manager продолжал работу после SSH logout; собственный supervisor не создавался. Upstream `scripts/vision/launch.sh` также использует `systemd-run --user`. [systemd-run](https://www.freedesktop.org/software/systemd/man/latest/systemd-run.html), [loginctl linger](https://www.freedesktop.org/software/systemd/man/latest/loginctl.html).

## Последовательность проверки

1. Stock `./so101 debug --image TAG --gpu 0`: Docker/GPU/runtime/assets. Import не считается полученным изображением.
2. Готовый `scripts/vision/smoke.py` через существующий tutorial Docker launcher: две reference-среды, два шага, PNG wrist-camera. Сам upstream проверяет `pixel_std > 2` и full-domain reset.
3. Stock tutorial: teacher, его короткая evaluation, затем vision warmup/PPO и evaluation; preset `configs/tutorial/smoke.json` с двумя updates.
4. Готовый `scripts/vision/evaluate_policy.py` экспортирует USD replay; готовый `scripts/tutorial/render_video.py` отдельно строит overview MP4. Оба вызываются через существующий tutorial Docker launcher. Это отдельная обзорная камера, не замена wrist PNG из шага 2. Полный `./so101 replay --video` не заявляется пройденным: его shell wrapper требует base tag даже при указанном собственном final image; повторная сборка base ради проверки не запускалась.

Все generated outputs — в отдельных новых каталогах, входы монтируются штатно. Один прогон выбирает одну GPU; автоматического объединения памяти двух карт не предполагается. Checkpoint/sidecars/метрики сохраняются штатными средствами.

## Результаты

| Проверка | Состояние |
|---|---|
| Native host, совпадающие module/NVML, две GPU | Подтверждено |
| Доставка runtime/source, SHA, symlinks, fingerprint | Подтверждено; образ зарегистрирован и исполняется |
| Debug нашего образа на сервере | Пройден: Docker 29, обе GPU, свободное место, CUDA/OVRTX/USD imports, Workshop asset; unit exit 0 |
| Wrist-camera PNG и pixel variance | Пройден на GPU 0, unit exit 0. Два PNG 160×120 получены/просмотрены; pixel_std 73,4258/74,3397; FULL_DOMAIN_RESET_OK |
| Teacher updates на сервере | Пройден на GPU 1: две среды, два updates, model_0.pt/model_1.pt и sidecars; unit exit 0 |
| Teacher evaluation | Exit 0: 2 эпизода, лимит 2 шага, success 0%, оба step_limit |
| Vision warmup и updates | Exit 0 на GPU 0: warmup + два PPO updates; image_gradient_norm = 0,02670967765527621 |
| Vision evaluation | Exit 0: 2 эпизода, лимит 2 шага, success 0%, оба step_limit |
| USD replay vision checkpoint | Exit 0: 1 эпизод / 2 шага, 3 кадра при 25 fps, 116 Newton bodies; success=false/step_limit |
| Headless replay MP4 | Повторный render exit 0; H.264 1920×1080, 25 fps, 3 кадра / 0,12 с; FFmpeg декодировал весь файл, первый кадр просмотрен |
| EB300 task/policy | Не подключена этим infrastructure test |

Текущие raw логи/receipts: `E:\RoboHand\runs\2026-11-15-remote-typing-runtime` и `E:\RoboHand\transfer\2026-11-15-typing-runtime`. Большие файлы/логи остаются вне публичного Git; в отчёте фиксируются только обезличенные факты. Все восемь принятых этапов завершились `SubState=exited`, `Result=success`, `ExecMainStatus=0`. Failed attempts сохранены отдельно и в этот счёт не включены.

Camera запущена через существующую функцию `scripts/tutorial/cli.py:docker` и исходный `scripts/vision/smoke.py`; её лимиты 8 CPU / 48 GiB задавались при создании. После измерения 13,26 GiB RAM начат независимый минимальный teacher run на второй GPU. Teacher/vision/evaluation используют штатный CLI, две среды и OMP 8; активные GPU containers больше не перенастраиваются. Compute-стенд на время выделен руке, приём соседнего приложения закрыт. Source/controller/model code не исправлялся.

Первый teacher attempt завершился CUDA error 100 после изменения CPU/RAM limits через `docker update`. Это соответствует документированному NVIDIA Container Toolkit сбою legacy hook при container updates; отдельного controlled reproduction не выполнялось. Свежий запуск без изменения работающего контейнера прошёл на той же GPU 1. Host driver/cgroup configuration не менялась; первый failed output сохранён отдельно. Для следующих прогонов квоты задавать при создании, не через live update. [NVIDIA troubleshooting](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/troubleshooting.html).

Checkpoint SHA256 нового native teacher: `model_0.pt` — `75c8dc2097cb5c60bef0e934083e11d905c6d92620d71a3d972c1cbb336e4195`, `model_1.pt` — `a7b0c614f474ed6ebcfae0f134deea0af20c409becb8180eb0318fddab2c5dd5`. Они совпали с локальным pinned smoke; это наблюдение для этих двух updates, не обещание детерминизма произвольного обучения.

## Отдельный headless render

Исходный обзорный renderer запросил `/usr/share/nvidia/nvoptix.bin`, отсутствовавший внутри контейнера; на хосте файл существует (60 858 204 байт). Первый собственный render остановлен, его log сохранён; первая попытка не считается успешной. Для повторного запуска подключён только этот файл штатным read-only bind mount при создании контейнера. Повторный render завершился с exit 0; MP4 декодирован FFmpeg, первый кадр просмотрен. Холодная RTX-компиляция заняла около 306 с; это не скорость inference или постоянная стоимость кадра. Драйвер, Container Toolkit и приложение соседнего стенда не менялись. Это готовый механизм Docker, а не изменение renderer/model code. [NVIDIA: missing nvoptix.bin](https://github.com/NVIDIA/nvidia-container-toolkit/discussions/1872), [Docker: read-only bind mount](https://docs.docker.com/engine/storage/bind-mounts/#use-a-read-only-bind-mount).

В готовом `scripts/vision/evaluate_policy.sh` проверка base image `so101-typing-public:dev` выполняется до выбора `SO101_EVAL_IMAGE`. Поэтому экспорт/рендер здесь вызваны непосредственно существующими Python entrypoints и существующим `scripts/tutorial/cli.py:docker()`, с лимитами 8 CPU / 48 GiB при создании. Wrapper не изменён, отсутствующий base tag не подменён final image.

## Сохранение и конечное состояние

Checkpoints, sidecars, evaluation JSON, USD replay, MP4 и полные логи скопированы на рабочий ПК в `E:\RoboHand\runs\2026-11-15-remote-typing-runtime\artifacts`. Обе переданные TAR-копии совпали с серверными SHA256; исходные серверные копии сохранены.

- Teacher `model_1.pt`: SHA256 `a7b0c614f474ed6ebcfae0f134deea0af20c409becb8180eb0318fddab2c5dd5`.
- Vision `model_1.pt`: 25 862 915 байт, SHA256 `cb017d517c8edcccefcced0ad109b863bb1c5f15d66e984587629bbb5469536d`.
- MP4: 53 660 байт, SHA256 `aa4cbdc417d352a74a4f082e776d8880a9deb39b29a73e5a06650aab22f25b31`. Это только 3 кадра короткого infrastructure smoke, не демонстрация выученной печати.

[Обезличенный машиночитаемый результат](2026-11-15-native-runtime-evidence.json) содержит exit status, размеры наблюдений, метрики, hashes и точные ограничения. Весов/изображений/raw SDK logs в публичном Git нет.

После сохранения результатов остановлены только наши завершённые transient units. Наших running containers и CUDA compute-processes нет, обе GPU показывают 0 MiB. Соседнее приложение остаётся в согласованном maintenance-режиме до команды владельца вернуть стенд; его API/frontend доступны. Это не фоновый долгий training: в конце проверки GPU-задач руки не оставлено.

Даже успешные два updates не означают выученную печать. Для EB300 остаются собственные actuator/camera/task configs и [найденный 5-output loader gap](2026-11-15-manual-control-and-typing-hooks.md#дополнительная-проверка-vision-teacher-loader-1511). Новая исполняемая adaptation без отдельного решения владельца не создаётся.

[Индекс](../index.md) · [Рабочий план15.11](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-15-execution-plan.md>) · [R8 на этом ПК](../start-here-r8.md).
