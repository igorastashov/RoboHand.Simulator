---
tags: [robohand, eb300, cad, viewing, handoff]
type: runbook
updated: 2026-11-15
status: accepted-nominal-simulation-asset
---

# Открыть подготовленную EB300 и продолжить работу

**Эта страница — историческаяR7 со стержнем.** После решения владельца15.11 активна [R8 без стержня, контакт обычной губкой](../../latest-artifacts.md). Для текущего запуска использовать новый URDF/MJCF из latest index, не командуR7 ниже.

[Ревью и результаты](root-review.md) · [Индекс](../../index.md).

## Что открывать

- Итоговый CAD: [EB300-R7-prepared.a3d](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R7-prepared.a3d>), [native preview](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R7-clean-native.png>), [outputs](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs>). Сборка ссылается на детали внутри этого work root; перенос одного A3D без зависимостей недостаточен. Исходный `1part.a3d` в `data/cad` не заменён.
- [URDF](../../../robohand_ws/src/robohand_description/urdf/eb300_cad2.urdf): шесть вращательных суставов, действительная геометрия исходных STL, nominal выход/оснастка и Redmi8A. Захват закреплён в текущей позе для typing profile. Его native механизм сохранён, но ложная однокоординатная URDF-конверсия не добавлена.
- [Контракт с числами](../../../robohand_ws/src/robohand_description/config/eb300_cad2_contract.json): frames/transforms, направления, связь угла CAD с q, массы/COM/inertias и происхождение оценок.
- [Готовая сцена MuJoCo](../../../robohand_ws/src/robohand_description/urdf/eb300_cad2.validation.xml): штатный импорт URDF и сериализация MuJoCo4.0.1, относительные пути meshes, виртуальная камера и визуальная плоскость. Это сцена проверки геометрии; gravity0, actuator/controller отсутствуют. Collision shapes скрыты в штатной group3, но включены в физическую модель.
- [Общий вид](full-eb300-reference.png) и [изображение wrist camera](redmi8a-nominal-view.png). FOV60° и позиция lens — проектные значения до калибровки телефона.

## Просмотр на текущем Windows ПК

MuJoCo установлен в отдельном E-окружении; устанавливать Isaac для открытия этой модели сейчас не требуется. Из PowerShell:

```powershell
& 'E:\RoboHand\tools\cad-validation-2026-11-14\.venv\Scripts\python.exe' -m mujoco.viewer --mjcf 'D:\ПРОЕКТЫ\_ЛИЧНОЕ_\ВОПЛОЩЕННЫЙ_ЭЙАЙ\РОБОРУКА\RoboHand\RoboHand.Simulator\robohand_ws\src\robohand_description\urdf\eb300_cad2.validation.xml'
```

Используется готовый `mujoco.viewer`; собственного приложения/GUI нет. Файл повторно загружен штатным `MjModel.from_xml_path` без VFS/внешнего resolver; renderer и кадры проверены. Отдельное интерактивное окно root не открывал. Для wrist view выбрать камеру `redmi8a_nominal` в штатном viewer.

ROS2 description package собран в WSL Humble; `check_urdf` и `display.launch.py --show-args` прошли. Launch по умолчанию выбирает CAD-2. Старый approximate Xacro сохранён и может быть выбран через аргумент `model:=...`; GUI RViz в этом проходе не запускался. Запуск ROS GUI требует WSLg/display, а не только успешной сборки пакета.

## Что подтверждено и что ещё измерить

Шесть суставов проверены в CAD в пределах±5°, геометрия23 mesh occurrences сверена в25 поосевых позах. Это не паспортные пределы руки и не проверка всех комбинаций суставов. `q=0` означает reference pose с CAD angles90°, а не физический homing zero. Знаки приводов/энкодеров ещё не калиброваны. Для keyboard task потребуется расширить виртуальные диапазоны с проверкой CAD/mesh clearances; ждать железа для такой simulation-only проверки не обязательно. Аппаратные limits и homing затем принимаются отдельно.

Сумма nominal масс9.468кг — параметр текущей виртуальной модели, не результат взвешивания EB300. Только масса телефона188г взята из официальной спецификации; COM/inertia телефона также оценочные. Остальные массы заданы диапазонами, а inertia рассчитаны как physically valid uniform box-envelope surrogates. README производителя указывает ABS-трубы; default steel density CAD не используется. Перед содержательным подбором привода/обучением динамики эти оценки заменить измерениями либо обоснованным BOM.

Реальные lens position/intrinsics/distortion, USB/Wi-Fi capture latency, крепёж/прочность/кабели, масса двигателя с редуктором, friction/backlash/compliance и mechanical limits остаются отдельными входами. Наличие URDF не заменяет actuator/camera/task config typing recipe.

## Следующий технический шаг

Применить уже выбранный pinned `NVIDIA/so101-typing-task` как reference: сначала его минимальный runtime/GPU smoke на текущем ПК, затем штатный URDF/asset import EB300 и проверка доступного пути6-axis action/actuator/task configuration. CAD-2 снимает отсутствие геометрии/frames; он не доказывает, что5-axis reference принимает EB300 одними параметрами. Если нужен новый исполняемый adapter, зафиксировать конкретный gap и решение владельца до его реализации. PPO state teacher и vision student сохраняют метод reference; ACT не подставляется вместо PPO.

После runtime/adaptation gate — стол, клавиатура с физическими клавишами, реалистичная wrist camera, повторяемый reset и первое контролируемое нажатие. Hermes/голос подключаются к проверенному навыку позднее. Физическое железо и прошивка пока остаются следующим самостоятельным этапом.
