---
tags: [robohand, eb300, latest, release, recovery]
type: artifact-index
updated: 2026-11-15
status: accepted-r8
---

# Актуальная EB300: открывать R8

[С чего начать на этом ПК](start-here-r8.md) · [Проверки и ограничения](cad-reviews/2026-11-15-logical-r8/root-review.md) · [Индекс](index.md).

| Что | Актуальный файл |
|---|---|
| Постоянный machine-readable указатель | [E:/RoboHand/CURRENT.json](<E:/RoboHand/CURRENT.json>) · [D-копия](<D:/RoboHand-Backups/CURRENT.json>) |
| КОМПАС assembly | [EB300-R8-jaw-typing.a3d](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R8-jaw-typing.a3d>) |
| Native tree/dependencies | [24файла и hashes](cad-reviews/2026-11-15-logical-r8/r8-dependency-closure.json) |
| URDF | [eb300_jaw_typing_r8.urdf](../robohand_ws/src/robohand_description/urdf/eb300_jaw_typing_r8.urdf) |
| Номинальные параметры/frames | [Численный контракт R8](../robohand_ws/src/robohand_description/config/eb300_jaw_typing_r8_contract.json) |
| Готовая inspection scene | [eb300_jaw_typing_r8.validation.xml](../robohand_ws/src/robohand_description/urdf/eb300_jaw_typing_r8.validation.xml) |
| Сохранённый release | [ZIP наE](<E:/RoboHand/releases/EB300-R8-jaw-2026-11-15/EB300-R8-jaw-2026-11-15.zip>) · [копия наD](<D:/RoboHand-Backups/EB300-R8-jaw-2026-11-15.zip>) |
| Проверка архива | [SHA256 и manifest readback](cad-reviews/2026-11-15-logical-r8/r8-release-verification.json) |
| Предыдущая recovery version | [R7S наE](<E:/RoboHand/releases/EB300-R7S-2026-11-15/EB300-R7S-2026-11-15.zip>) · [наD](<D:/RoboHand-Backups/EB300-R7S-2026-11-15.zip>) |

R8 — одна корневая сборка с7логическими физическими узлами. Стержень и его держатель исключены; контакт — кромкой обычной губки. Старые `eb300_cad2.*` — исторический profileR7 со стержнем, ROS launch по умолчанию выбираетR8.

## Посмотреть на текущем Windows ПК

```powershell
& 'E:\RoboHand\tools\cad-validation-2026-11-14\.venv\Scripts\python.exe' -m mujoco.viewer --mjcf 'D:\ПРОЕКТЫ\_ЛИЧНОЕ_\ВОПЛОЩЕННЫЙ_ЭЙАЙ\РОБОРУКА\RoboHand\RoboHand.Simulator\robohand_ws\src\robohand_description\urdf\eb300_jaw_typing_r8.validation.xml'
```

Это штатный viewerMuJoCo4.0.1. Scene gravity0 и безactuator/controller предназначена для просмотра геометрии; камера `redmi8a_nominal`, collision shapes вgroup3. Сама клавиатура, управляемое нажатие и обучение остаются следующим этапом. [Изображение](cad-reviews/2026-11-15-logical-r8/r8-full-jaw-profile.png).

## Как не потерять native assembly

ОдногоA3D недостаточно: он ссылается на24native files. ZIP сохраняет полный dependency tree, description package, mesh licenses и evidence, с manifest всех файлов. Native path references не перепривязывались: это **recovery package**, не проверенный переносимый Pack-and-Go. Для восстановления CAD вернуть дерево `cad-work/2026-11-14-eb300-c2133b98` по исходному пути `E:\RoboHand\data\cad-work\2026-11-14-eb300-c2133b98`, сохранив `input/outputs`; сначала извлечь в отдельную папку, если по этому пути уже есть более новые правки. Простое открытие A3D из произвольной папки может продолжать использовать старые absolute references.

Архивы наE/D проверены побайтно и поSHA256, установлены read-only flags. Рабочая CAD-версия остаётся редактируемой; для следующей геометрической ревизии использовать новую копию и заново зафиксировать зависимости. Backup не подменяет versioned inputs и не удаляет старую принятую версию.
