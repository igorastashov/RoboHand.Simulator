---
tags: [robohand, eb300, teleop, reuse-first, typing, source-audit]
type: research
updated: 2026-11-15
status: source-audited-runtime-not-run
---

# Ручное управление и перенос typing recipe: проверка до Docker

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

## Что проверять после переноса Docker владельцем

- Docker Desktop показывает новый путь data image на E:, а VHDX и свободное место соответствуют настройке; проверить сохранность нужных существующих images/containers.
- Docker daemon работает, GPU доступна **в контейнере**, драйвер/объём памяти соответствуют RTX 3090. Видимость `nvidia-smi` в WSL отдельно недостаточна.
- Выполнить минимальный pinned `./so101 debug --viewer`/smoke по setup и сохранить версии/логи. Совместимость RTX 3090 не выводить из результата на upstream Blackwell.

Полные прочитанные upstream snapshots находятся локально в `E:\RoboHand\research\2026-11-15-dogs-teleop`; в репозитории сохраняются выводы и точные pins. [Понятное объяснение URDF/MuJoCo](../urdf-mujoco-explained.md) · [Индекс](../index.md).
