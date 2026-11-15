---
tags: [robohand, eb300, teleop, reuse-first, typing, source-audit]
type: research
updated: 2026-11-15
status: source-audited-runtime-not-run
---

# Ручное управление и перенос typing recipe: проверка до Docker

**Позднейшее уточнение15.11:** Docker уже перенесён наE:, локальные CUDA/Newton/reference teacher проверки выполнены; RTX-камера вWSL2 не прошла. Актуальные runtime-факты — в [отчёте запуска](2026-11-15-runtime-gpu-smoke.md), очерёдность — в [рабочем плане15.11](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-15-execution-plan.md>). Исходная проверка ниже сохраняется как source audit, не текущее ожидание переноса Docker.

Поручение владельца: понять пользу джойстика и продолжать независимые работы, пока он сам переносит Docker на E:. Docker settings, containers и WSL storage этим проходом не изменялись.

## Принятая очерёдность

1. Осмотр и изменение позы в готовом MuJoCo viewer — на текущем Windows, без новых покупок и Docker.
2. GPU/reference smoke после проверки переноса Docker владельцем.
3. Настройка именно EB300, её виртуальных приводов и рабочего места; ручная проверка направлений/рабочей точки, затем одна клавиша.
4. Штатное обучение PPO teacher→vision, отдельная оценка. Геймпад — необязательный интерфейс ручного этапа, не новый обязательный проект.

## Готовые средства

| Задача | Проверенный первоисточник / pin | Что покрывает / что не проверено |
|---|---|---|
| Изменить позу и осмотреть геометрию | MuJoCo **4.0.1**, установленная модель R8; [официальный viewer](https://mujoco.readthedocs.io/en/stable/programming/samples.html#simulate) | Панель Joint и пауза; текущие пределы ±5°, без приводов. Это не динамическое управление пультом |
| Геймпад и клавиатура в Isaac Lab | [IsaacLab v3.0.0](https://github.com/isaac-sim/IsaacLab/tree/e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4), `scripts/environments/teleoperation/teleop_se3_agent.py` и `source/isaaclab/isaaclab/devices/` | Готовые устройства ввода и SE(3) команды. Прочитанный legacy `Se3Gamepad` использует `carb.input`/app window; его нельзя автоматически считать независимым от Kit/Newton drop-in. Teleop factory/совместимость выбранного backend проверять штатным example |
| Геймпад/клавиатура через ROS 2 | [MoveIt tutorials humble@b8f954c](https://github.com/moveit/moveit2_tutorials/tree/b8f954ce045b00f29de4da24146eb7732e7b2a9e), [штатный Servo tutorial](https://moveit.picknik.ai/humble/doc/examples/realtime_servo/realtime_servo_tutorial.html) | Документированный Xbox 1 / `joy`, joint jog и Cartesian velocity. Demo использует Panda; keyboard example содержит имена `panda_joint1..7`/frames. EB300 пока не имеет MoveIt/SRDF/controller-конфига. Не объявляется готовым EB300 adapter |

Для upstream MoveIt demo готовые команды — `ros2 run joy joy_node`, `ros2 launch moveit_servo servo_example.launch.py`, запуск Servo service и `ros2 run moveit2_tutorials servo_keyboard_input`. Это команды reference demo; на EB300 здесь не запускались. Установка отдельного ROS/MoveIt стека только ради пульта пока не выбрана.

Первый критерий ручной проверки: каждая из J1–J6 движется в ожидаемом направлении, движение прекращается после отпускания команды, reset воспроизводит позу; рабочая кромка и нужные клавиши имеют достаточный обзор. Ручное управление рабочей точкой требует проверенного IK и ограничений. Физический робот в этот этап не включён.

## Actual source NVIDIA recipe

Pin: [NVIDIA/so101-typing-task@7aec2ed26dce8c88ae007a2714680cce572e1466](https://github.com/NVIDIA/so101-typing-task/tree/7aec2ed26dce8c88ae007a2714680cce572e1466). Прочитаны README, `docs/tutorial.md`, `configs/tutorial/smoke.json`, robot/action/reset configs и vision contract через `git show REV:path` из локального audit repo. Никаких training/runtime imports для этой проверки не выполнялось.

| Область | Что есть в source | Значение для EB300 |
|---|---|---|
| Minimal run | `configs/tutorial/smoke.json`: `num_envs=2`; setup/debug/train/evaluate штатным CLI | Следующий GPU gate после переноса хранилища. Большой run на 4096 сред не является первым запуском |
| Robot asset | `tasks/SO101/so101_cfg.py`: USD/поза/профили привода SO-101 | Наш URDF сам по себе не заменяет spawn/actuator profile |
| Суставы и reset | `tasks/so101_env_cfg.py`: список пяти суставов, `body_name="gripper"`, SO-101 offset и IK pose | Для EB300 нужны J1–J6, собственный frame губки, начальная поза и диапазоны; простое переименование URDF не завершает перенос |
| Generic action hook | `tasks/mdp/joint_rate_actions.py`: `action_dim = len(self._joint_ids)`, вектор limits сверяется с числом суставов | Есть готовая размерно-зависимая реализация: сначала пробовать её конфигурирование, не писать новый action controller |
| Контакты | `robot_contact`/illegal contact termination, spawn contact reporting; teacher/task рассчитаны на keyboard geometry | Должны работать на наших collision bodies и нашей губке, а не на прежнем SO-101 offset |
| Vision | Свой task/checkpoint contract; tutorial отдельно отмечает пять actions teacher/vision | Совместимость observation/action/checkpoint dimensions нужно проверить по всему выбранному маршруту; готовые SO-101 веса не считать EB300 policy |

**Статус:** найдены подходящие готовые блоки, но законченный шестисуставной EB300 recipe не подтверждён. Нужны штатная конфигурация и GPU smoke; если выявится необходимость нового исполняемого adapter/model adaptation, сначала отдельное решение владельца по [политике](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/reuse-first-policy.md>). Новый такой код этим исследованием не создавался.

## Дополнительная проверка vision teacher loader, 15.11

В actual [scripts/vision/agent.py:29 @7aec2ed](https://github.com/NVIDIA/so101-typing-task/blob/7aec2ed26dce8c88ae007a2714680cce572e1466/scripts/vision/agent.py#L29) `load_teacher` создаёт `MLPModel` с числом outputs **5**, переданным литералом. Это не размер, взятый из J1–J6 или конфигурации нашей руки. Такой loader вызывается выбранным teacher/vision маршрутом.

Повторная проверка официального upstream15.11 через GitHub metadata и `git ls-remote ... HEAD` показала тот же `7aec2ed26dce8c88ae007a2714680cce572e1466`: найденный gap присутствует и в текущем HEAD, не только в отложенном snapshot. В `scripts/vision/runtime.py:make_config` выбранный tutorial создаёт SO-101-specific `VisionIsaacLabPhraseEnvCfg`/`VisionTypingEnvCfg`; готового CLI-переключателя на наш robot asset в этом маршруте не найдено. Generic Isaac Lab configuration остаётся кандидатом для минимального переноса, но законченный EB300 путь этим чтением не доказан.

Поэтому generic `JointRateActions.action_dim = len(joints)` ещё не доказывает полный6-axis путь. Даже после стандартного подключения EB300/config остаётся конкретная несовместимость загрузчика с6-output teacher. Изменение loader/model behavior считается исполняемой adaptation и не выполнено под видом данных. Проверка остальных hardcoded SO-101 asset/body/reset/controller предположений остаётся необходимой; одна найденная строка не объявляется полным объёмом переноса.

Штатный reference smoke уже прошёл на native Linux: [камера, teacher/vision PPO и оценки](2026-11-15-native-linux-runtime.md), без изменения исходного recipe. До обучения EB300 подготовить минимальный список необходимой adaptation и готовых альтернатив, затем отдельное решение владельца по reuse-first. Отключать одну ось EB300 или выдавать5-action checkpoint за6-axis policy нельзя.

Дополнительно прочитан [готовый exporter actor](https://github.com/NVIDIA/so101-typing-task/blob/7aec2ed26dce8c88ae007a2714680cce572e1466/scripts/vision/export_actor.py): CNN создаётся с 5 выходами, metadata содержит `action_dim=5`, proprio order включает группы по 5 суставов; допустимые proprio dimensions ограничены 45/57. Это ещё одна точка проверки для EB300, а не разрешение править exporter. Legacy `scripts/vision/train.py` также использует найденный `load_teacher`, поэтому его наличие само по себе не обходит 5-output gap.

## Исторический checklist после переноса Docker владельцем

- Docker Desktop показывает новый путь data image на E:, а VHDX и свободное место соответствуют настройке; проверить сохранность нужных существующих images/containers.
- Docker daemon работает, GPU доступна **в контейнере**, драйвер/объём памяти соответствуют RTX 3090. Видимость `nvidia-smi` в WSL отдельно недостаточна.
- Выполнить минимальный pinned `./so101 debug --viewer`/smoke по setup и сохранить версии/логи. Совместимость RTX 3090 не выводить из результата на upstream Blackwell.

Полные прочитанные upstream snapshots находятся локально в `E:\RoboHand\research\2026-11-15-dogs-teleop`; в репозитории сохраняются выводы и точные pins. [Понятное объяснение URDF/MuJoCo](../urdf-mujoco-explained.md) · [Индекс](../index.md).
