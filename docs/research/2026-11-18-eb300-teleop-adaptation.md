---
tags: [eb300, teleoperation, mink, lerobot, reuse-first, scope]
type: implementation-proposal
updated: 2026-11-18
status: approved-implemented-and-verified
---

# Минимальная связка готовой IK и записи демонстраций EB300

**Реализовано18.11:** [полный отчёт,12tests, контактный цикл и990frames record/replay](2026-11-18-mink-execution.md). Границы разрешения ниже сохранены; physical sim успех не является trained skill.

[Индекс](../index.md) · [Принятый EnvHub](2026-11-17-eb300-envhub-execution.md) · [Политика](../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/reuse-first-policy.md)

Цель — управлять виртуальным захватом EB300 через готовый MuJoCo viewer/keyboard target, получать семь обычных joint targets и записывать успешные демонстрации штатными средствами LeRobot. Новый solver, UI, motor law, planner framework и training stack не требуются. Но соединяющего исполняемого кода в проверенных upstream нет, поэтому ниже предложен **новый узкий adapter scope**, а не выдаваемая за конфигурацию готовая интеграция.

Общее поручение продолжать работу позволяло исследование, штатные smokes и данные механики. Предыдущее разрешение на EnvHub явно исключало IK/teleoperator. **Владелец18.11 отдельно разрешил описанный scope**, ответив: «Да, реализовать описанный узкий binding». Реализация ведётся в пределах этого документа; новый controller law/framework и real hardware в него не входят.

## Что уже проверено по исходному коду и запуску

| Готовое решение / pin | Результат | Ограничение для нас |
|---|---|---|
| [Mink](https://github.com/kevinzakka/mink/tree/5f800f0a369d05bab88b5e5582cf95122d3b82a5),1.4.0 | На Windows установлен именно pinned source. Без изменений выполнены `examples/docs/quickstart.py` и `tasks_and_limits.py`; оба exit0. Есть FrameTask, DOF freezing, limits, DAQP и готовый TeleopMocap | `arm_ur5e_actuators.py` зашивает robot names/path/home и делает `data.ctrl = configuration.q`. У EB300 nq17,nu7: полный qpos отправлять в actuator vector нельзя. Это не готовый configurable CLI |
| [RoboSimStudio](https://github.com/robosimstudio/robosimstudio/tree/ba3650c4669fffabb7bd52802f4fdf6cdc66cb19) | Linux/RTX3090: четыре неизменённых `tests.test_unregistered_robot` PASS;232.365s с первым JIT. Custom robot декларативно поддержан, готовые gizmo/IK/record есть | Импорт перестраивает physics через Newton; locked MuJoCo3.15.0 против нашей4.0.1. Store — NPZ/JSONL/MP4. Обещанный комментарием LeRobot/RLDS converter в полном tree этого pin не найден. Сохранение нашего contact/camera/action contract не доказано |
| [Teleop_Gamepad_Mujoco](https://github.com/sento2310/Teleop_Gamepad_Mujoco/tree/fee0b7ddd220357bbc054cbe5c72c1b7772cda93) | Actual config/simulation/IK/requirements прочитаны; install не выполнялся | Registry известных robots и предположения qpos/ctrl зашиты в код. Требует gamepad, старый MuJoCo3.2.7. Одной заменой config наша сцена не подключается |
| [XRoboToolkit](https://github.com/XR-Robotics/XRoboToolkit-Teleop-Sample-Python/tree/79e5cb8a56e3455515ce1b476e993c764ec58739) | Actual config/controller/requirements прочитаны; runtime не устанавливался | Требует XR client/device, Placo и согласованный URDF/MJCF. Готовая связка с нашим EnvHub recorder не найдена |
| [LeRobot](https://github.com/huggingface/lerobot/tree/7910c20a75834ad3fa6a9792df4d44a614d1bba6) | Существующие SimRobot/record/replay уже проверены17.11. Actual keyboard_ee/kinematic processors/record entry прочитаны18.11 | KeyboardEE даёт XYZ+gripper без полного wrist orientation. Готовый RobotKinematics принимает degrees, а наша action semantics — rad; gripper step узнаёт имя `gripper`, а не MG995. Нельзя послать его вывод напрямую и назвать настройкой |

RoboSimStudio установлен отдельно, со своим lock и без необязательной RTX group. Это рабочий reference, не принятая миграция EB300. Для продолжения сохраняем существующие EnvHub/MuJoCo4.0.1/LeRobot и рассматриваем Mink как готовый solver. Версии и resolved dependency lists сохранены в `E:\RoboHand\research\2026-11-18-teleop` и `E:\RoboHand\runs\2026-11-18-teleop-grasp`.

## Предлагаемый разрешаемый объём

1. Небольшой EB300 binding поверх неизменённых `mink.FrameTask`, `DofFreezingTask`, limits и `solve_ik`. Читаем действительные углы руки, считаем конфигурацию на отдельной копии и передаём только J1…J6 плюс отдельно MG995. Free-pencil, passive key и rack coordinates не становятся IK variables/actions.
2. Переиспользовать готовые `mujoco.viewer.launch_passive` и `mink.contrib.TeleopMocap` для клавиатурного/мышиного target. Никакого нового GUI или сервера. Target — только указатель цели, без weld/силовой связи с рукой либо предметом. Model input по-прежнему один полный wrist frame.
3. Узкое соединение с уже принятым EnvHub и штатной записью LeRobot: использовать существующий recorder/API/processor hooks вместо нового формата. Если stock CLI требует отдельного registration/processor, локализовать его в этом binding; не fork всего LeRobot. Выбор Windows/WSL разделения проверяется smoke, не обещается заранее.
4. Standard config для joint/body names, units/ranges, IK/velocity/collision limits, nominal open/close MG995 и начальных поз. Номинальные servo parameters и tracking error остаются явными; скрытого gravity compensation/controller rewrite не добавлять.
5. Контрактные проверки и bounded headless smoke; затем реальный viewer/teleop и демонстрация свободного карандаша. Отсутствие достижимой позы/контакта возвращает явную ошибку/удержание, не teleport предмета.

Ожидаемые файлы при реализации: отдельный модуль `integrations/lerobot_envhub/teleop_mink.py`, optional pinned requirements/config и соответствующие contract tests/README. Только если stock recorder registration требует пакетной точки входа — минимальный packaging metadata рядом; это не разрешение нового framework. Если обнаружится потребность в другом контроллере или миграции physics, сначала отдельное описание gap.

## Приёмка

- Upstream Mink pin и LeRobot pin не меняются незаметно; отдельная среда, smoke/recovery commands и resolved versions сохранены.
- Action всегда7finite absolute radians с корректными именами/порядком/лимитами; measured qpos и commanded ctrl не смешиваются.
- IK не двигает free-pencil/keyboard/racks и не пишет qpos физического мира. Все дальнейшие движения проходят существующие actuator dynamics и torque caps при2ms/25Hz.
- Проверены orientation, недостижимая цель, no-input hold и независимое open/close; лимиты и solver failures не маскируются успешной записью.
- Один full640×360 wrist input; spectator target/view не попадают в observations. Native CAD/LATEST сохраняются.
- Пилотная запись читается штатным LeRobotDataset и воспроизводится штатным replay; события/units/frame timing сверены. Неуспешные diagnostic records не помечаются successful grasp.
- Для физического успеха нужны оба pad contacts, отсутствие поддержки столом/другой геометрией, подъём≥20мм и hold≥0.5s; дополнительно проверяются penetration/equality/warnings и безопасный release. Ни один объект не приклеен и не переносится присваиванием pose.

## Альтернативы решения владельца

**Рекомендация:** разрешить описанный узкий Mink/LeRobot binding. Он сохраняет проверенную сцену и данные, добавляя недостающую связь готовых компонентов.

Без нового binding можно продолжить ручные проверки штатными actuator sliders MuJoCo и статическими конфигурациями. Это пригодно для диагностики, но пока не даёт проверенного удобного SE3 teleop+recorder. Миграция на RoboSimStudio потребует отдельной проверки импорта механики/камеры и решения converter gap; сейчас не предлагается как автоматически готовая замена.

Это предложение не разрешает real hardware control, другой захват, внешние камеры, собственный trajectory planner, neural policy architecture или LoRA training на диагностических50frames. Успешный хват полной EB300 на момент предложения ещё не выполнен.
