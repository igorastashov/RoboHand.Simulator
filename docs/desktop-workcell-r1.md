---
tags: [robohand, eb300, desktop, mujoco, nominal-dynamics]
type: guide
updated: 2026-11-16
status: nominal-six-axis-contact-scene-validated
---

# Рабочий стол EB300: первая действующая сцена

Наша EB300 R8 закреплена на левом ближнем к человеку углу стола. Системный блок — справа у дальнего угла; монитор сзади по центру, клавиатура перед ним, мышь справа. Владелец просмотрел принятую CAD-сборку 16.11. Native CAD, URDF и прежняя inspection scene не изменены.

## Что теперь работает

- Шесть встроенных position actuators MuJoCo управляют J1–J6. Это отдельный номинальный профиль с гравитацией −9,81 м/с² и встроенным фильтром targets `timeconst=0.15`.
- Обычная губка без стержня нажимает тестовую клавишу A и отпускает её: **10/10 повторов** в фиксированной сцене. Проверены контакты на каждом шаге нажатия, а не только последняя поза; контактов с соседними неподвижными клавишами нет.
- Смещение клавиши при нажатии около 1,882 мм, в покое около 0,218 мм от её собственного веса. Порог проверки 1,5 мм, полный номинальный ход 3 мм. В каждом повторе одно пересечение порога вниз и возврат после отпускания.
- Все шесть приводов отдельно проверены малым положительным изменением цели. Численные состояния конечны, warnings MuJoCo отсутствуют.
- Получены общий вид и изображение существующей номинальной камеры Redmi на запястье. Геометрия кронштейна и оптика не подменены камерой, следящей за целью.

Это заданные targets штатных приводов, **не обученная policy**. Работает одна подвижная тестовая клавиша; остальные keycaps в этой сокращённой сцене неподвижны. Обучающая задача NVIDIA с её клавиатурой подключается отдельно.

## Файлы

| Файл | Назначение |
|---|---|
| [Сцена рабочего места](../robohand_ws/src/robohand_description/scenes/eb300_desktop_r1.xml) | Стол 1600×900 мм, поверхность на высоте 780 мм, крепление, периферия, клавиша и два presets |
| [Номинальная динамика EB300](../robohand_ws/src/robohand_description/urdf/eb300_jaw_typing_r8.nominal-dynamics.xml) | Принятая геометрия R8 и шесть встроенных сервоприводов; отдельный файл от inspection scene |
| [Численные проверки](research/2026-11-16-desktop-validation.json) | 10 contact trials, шесть направлений, параметры рендера и отдельно native Newton import/FK |
| [Аппаратные источники](../robohand_ws/src/robohand_description/config/eb300_hardware_reference_2026-11-16.json) | Факты OneMotor/Firmware/Control, SHA официальных PDF, паспортные классы моторов и незаполненная калибровка |

Полные изображения, анимация, USD, меши и журналы находятся вне публичного Git: `E:\RoboHand\runs\2026-11-16-hardware-workcell`. Там есть `desktop-final.png`, `wrist-final.png` и шестисекундный `EB300-key-A.gif`. Непубличная геометрия берётся из существующего комплекта владельца, как описано в [границах публикации](publication-scope.md).

SHA в проверке/архиве фиксируют исходные Windows bytes; дополнительные поля `*_lf` описывают Git-текст с LF вместо CRLF. Численные результаты и геометрия от переноса строк не меняются.

## Как открыть и управлять

В `E:\RoboHand\LATEST` создан отдельный ярлык рабочего стола. Прежний ярлык inspection scene и `CAD\EB300.a3d` сохраняются. Прямой запуск штатного viewer с начальным preset:

```powershell
& 'E:\RoboHand\tools\cad-validation-2026-11-14\.venv\Scripts\python.exe' -c "import mujoco,mujoco.viewer; m=mujoco.MjModel.from_xml_path(r'D:\ПРОЕКТЫ\_ЛИЧНОЕ_\ВОПЛОЩЕННЫЙ_ЭЙАЙ\РОБОРУКА\RoboHand\RoboHand.Simulator\robohand_ws\src\robohand_description\scenes\eb300_desktop_r1.xml'); d=mujoco.MjData(m); mujoco.mj_resetDataKeyframe(m,d,0); mujoco.viewer.launch(m,d)"
```

В штатной панели **Control** находятся `eb300/J1_position` … `eb300/J6_position`; значения в радианах. Начальный preset `ready_nominal` уже выставлен. Для проверенного нажатия меняется только цель J2: **0.94 → 0.971 → 0.94**; остальные цели остаются как в preset. `press_A_nominal` сохраняет эти же targets в модели. Joint panel меняет позу напрямую и не равнозначна управлению приводами. Поле камеры позволяет выбрать `eb300/redmi8a_nominal`; `Space` ставит симуляцию на паузу.

## Что означает физическая достоверность

Стол, монитор, мышь, PC и клавиатура сейчас имеют условные габариты из стандартных MJCF primitives. Конкретная CAD-модель мебели не выдаётся за измеренное рабочее место. Проверенный upstream NVIDIA keyboard остаётся выбранной основой обучающей задачи; внешний Keychron assembly example просмотрен, но его controllers с прямой перестановкой тел не используются как наш роботный контроллер.

Паспорт EB300 подтверждает три NEMA17 60 мм, один NEMA23 76 мм и два NEMA23 82 мм, шаг 1,8°. Но удерживающий момент мотора не задаёт непрерывный момент на выходе редуктора. Указанный `gear_ratio=1` в example OneMotor — не калибровка. Поэтому ±170°, gains, armature и effort limits в новом MJCF — **открыто обозначенные номинальные simulation assumptions**. Реальные диапазоны, люфты, массы и динамику ещё предстоит измерить. Раскрытие захвата фиксировано.

## Готовый путь в USD и Newton

Использован официальный [newton-physics/mujoco-usd-converter](https://github.com/newton-physics/mujoco-usd-converter/tree/64e3695dddc30b4ef9658d6609ff4cbef86927c4), v0.9.0 / commit `64e3695dddc30b4ef9658d6609ff4cbef86927c4`. Он установлен отдельно на E:, без изменения MuJoCo 4.0.1 текущего viewer. [Точный набор пакетов](research/2026-11-16-converter-requirements.lock). Готовая команда:

```text
mujoco_usd_converter --no-openpbr INPUT.xml OUTPUT_DIRECTORY
```

CLI завершился с exit 0 для робота и всей сцены. С MuJoCo 3.17 в окружении конвертера путь на кириллице не открылся; проверенная побайтная копия входов в ASCII-папку на E: сработала. Свой exporter не создавался.

Конвертер предупреждает: камеры, lights, keyframes и sensors не переносятся; checker texture и ellipsoid мыши также не сохранены полностью. Поэтому USD не объявляется полной копией сцены. Камера/сенсоры/стартовая поза для NVIDIA задаются отдельно стандартными configs; пропущенную геометрию потребуется заменить поддерживаемой перед приёмкой всей сцены там.

В native Linux runtime NVIDIA `7aec2ed`, Newton 1.4.0.dev0, выполнены стандартные `ModelBuilder.add_mjcf` / `add_usd`, `finalize(device='cuda:0')` и GPU FK: у руки **6 DOF / 13 bodies / 46 shapes**, у desktop USD **7 DOF / 25 bodies / 124 shapes**. Все три импорта прошли, unit exit 0. Это проверка импорта и кинематики, **не проверка эквивалентности solver dynamics или RTX-камеры EB300 в Isaac Lab**.

## Другие места крепления и следующий шаг

`arm_mount` хранит положение основания отдельно от геометрии руки. После перестановки нужны известная поза базы, проверка доступности клавиш/коллизий и отдельная оценка. Фиксированная пара targets одной сцены не переносится на произвольное место стола автоматически.

Владелец16.11 разрешил [точечную адаптацию обучения для шести осей](research/2026-11-16-eb300-training-adaptation.md). [Минимальная native цепочка](research/2026-11-16-eb300-native-training.md) уже пройдена на EB300: camera, teacher → vision PPO, evaluation и replay. Для неё есть отдельный native-contact MJCF и стандартный USD drive/filter layer; viewer profile выше не заменён. Следующий этап — свести мировую desktop layout с training scaffold и проверить native нажатие до длинного обучения. Новые framework, UI, MCP-server и собственный контроллер не создавались.

Источники механизма: [MJCF attachment и actuator/position](https://mujoco.readthedocs.io/en/stable/XMLreference.html), [штатный Python viewer](https://mujoco.readthedocs.io/en/stable/python.html#interactive-viewer), [Newton ModelBuilder](https://newton-physics.github.io/newton/latest/api/_generated/newton.ModelBuilder.html), [официальные руководства EB300](https://toolboxrobotics.com/robotic-arm-eb300).

[Индекс](index.md) · [Исходная сборка R8](latest-artifacts.md) · [Начать здесь](start-here-r8.md).
