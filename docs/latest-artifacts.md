---
tags: [robohand, eb300, latest, release, recovery]
type: artifact-index
updated: 2026-11-17
status: accepted-r8
---

# Актуальная EB300: открывать R8

**Runtime17.11:** [полная7action EB300/EBG20 + LeRobot EnvHub](research/2026-11-17-eb300-envhub-execution.md) отдельно в `E:\RoboHand\LATEST\SIMULATION\EB300-ENVHUB`. Запись/replay/base-policy interface проверены, [GIF](<E:/RoboHand/LATEST/SIMULATION/EB300-ENVHUB/SHOWCASE/EB300-workcell.gif>) показывает заданное движение. Native CAD R8 ниже сохранена; grasp skill ещё не обучен. Новый runtime имеет7position targets,1wrist image и собственный standard JSON contract; прежняя inspection scene остаётся историческим6axis asset.

**Рабочий комплект теперь отдельно: `E:\RoboHand\LATEST\CAD\EB300.a3d`.** Один главный A3D и 23 зависимости в `components/`; штатные ссылки перепривязаны внутрь LATEST. Геометрия и сопряжения сохранены. [Проверка](cad-reviews/2026-11-15-latest-package/cad-agent-report.md), [независимый readback](cad-reviews/2026-11-15-latest-package/root-readback.json).

[С чего начать на этом ПК](start-here-r8.md) · [Проверки и ограничения](cad-reviews/2026-11-15-logical-r8/root-review.md) · [Индекс](index.md).

| Что | Актуальный файл |
|---|---|
| Постоянный machine-readable указатель | [E:/RoboHand/CURRENT.json](<E:/RoboHand/CURRENT.json>) · [D-копия](<D:/RoboHand-Backups/CURRENT.json>) |
| КОМПАС assembly — работать здесь | [LATEST/CAD/EB300.a3d](<E:/RoboHand/LATEST/CAD/EB300.a3d>) |
| Native tree/dependencies LATEST | [24 файла и hashes](cad-reviews/2026-11-15-latest-package/native-closure.json) |
| MuJoCo одним кликом | [ПОСМОТРЕТЬ-В-MuJoCo.lnk](<E:/RoboHand/LATEST/ПОСМОТРЕТЬ-В-MuJoCo.lnk>) |
| Backup рабочего CAD-комплекта LATEST | [ZIP на E](<E:/RoboHand/releases/EB300-LATEST-R8-2026-11-15/EB300-LATEST-R8-2026-11-15.zip>) · [зеркало D](<D:/RoboHand-Backups/EB300-LATEST-R8-2026-11-15.zip>) |
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

В рабочем LATEST все 23 зависимости перепривязаны. Сохранять весь `LATEST\CAD`, включая `components`. ZIP `EB300-LATEST-R8-2026-11-15.zip` содержит этот комплект, памятку и ярлык. [Проверка архива](cad-reviews/2026-11-15-latest-package/archive-verification.json). Восстанавливать дерево `LATEST` на `E:\RoboHand\LATEST`; перенос на произвольный другой путь/ПК не проверялся. Ярлык использует установленный Python на E: и scene/meshes репозитория на D:; симуляционные данные не входят в этот native-only ZIP.

Прежний `EB300-R8-jaw-2026-11-15.zip` — исторический recovery package с полным robot description/meshes/licenses и прежним CAD layout. Его native-ссылки требуют восстановления дерева `cad-work/2026-11-14-eb300-c2133b98` по исходному пути `E:\RoboHand\data\cad-work\2026-11-14-eb300-c2133b98` с `input/outputs`. Не заменять новые рабочие правки при восстановлении: сначала извлекать отдельно.

Архивы наE/D проверены побайтно и поSHA256, установлены read-only flags. Рабочая CAD-версия остаётся редактируемой; для следующей геометрической ревизии использовать новую копию и заново зафиксировать зависимости. Backup не подменяет versioned inputs и не удаляет старую принятую версию.

Позднее старый root был пересохранён с другим byte hash; [read-only сравнение](cad-reviews/2026-11-15-latest-package/source-resave-review.json) подтвердило прежние позы/геометрию/сопряжения. Рабочий указатель остаётся LATEST.

## Рабочее место от16.11 — отдельно от принятой CAD

[Рабочий стол EB300 R1](desktop-workcell-r1.md) открывается ярлыком `E:\RoboHand\LATEST\РАБОЧИЙ-СТОЛ-EB300.lnk`. Исходная CAD и старый ярлык осмотра не заменены.

Полный локальный комплект сцены/meshes/USD/evidence сохранён в `E:\RoboHand\releases\EB300-DESKTOP-R1-2026-11-16\EB300-DESKTOP-R1-2026-11-16.zip`, зеркало — `D:\RoboHand-Backups\EB300-DESKTOP-R1-2026-11-16.zip`. SHA256 `ba26cff2160c2e0ed573279fa41fee777f0062bbc6b03c1a4b8449902e3eebe9`, 9 365 720 байт, 63 файла; CRC/все file SHA и зеркало проверены. Восстанавливать отдельно с сохранением относительных `urdf/scenes/meshes`; не заменять более новые рабочие файлы. USD содержит задокументированные потери camera/sensor/keyframe данных конвертера.

## Native PPO smoke от16.11

[Результаты EB300 teacher/vision/eval/replay](research/2026-11-16-eb300-native-training.md), [численные данные](research/2026-11-16-eb300-native-validation.json), [patch и стандартный USD drive/filter layer](../integrations/nvidia_typing/README.md). Это минимальные nominal checkpoints, не выученный навык и не физический deployment.

Рабочие результаты: `E:\RoboHand\runs\2026-11-16-hardware-workcell\training-r6` и `evaluation-r6`. В `E:\RoboHand\LATEST\SIMULATION` находятся6-секундный `ЗАДАННОЕ-НАЖАТИЕ-A.gif` из локальной сцены и `EB300-PPO-smoke-episode-1.mp4` из отдельного native rollout. Последний26кадров/1,04с и0набранных символов; эти два вида движения не смешиваются.

Frozen комплект native assets/config/patch/checkpoints/evidence сохранён в `E:\RoboHand\releases\EB300-NATIVE-PPO-R1-2026-11-16\EB300-NATIVE-PPO-R1-2026-11-16.zip`; зеркало — `D:\RoboHand-Backups\EB300-NATIVE-PPO-R1-2026-11-16.zip`. SHA256 `b39936015da4308f8d7a4f1b78460d22b55beb7ec204a27375dd77ddee142aab`, 63 537 051 байт,108payload files плюс manifest/README. CRC, каждый file SHA и зеркало проверены, ZIP read-only. Геометрия/веса/полные SDK logs остаются локальными. Base Docker runtime не входит в этот архив: восстановление использует pinned upstream setup и отдельные лицензированные assets; сначала извлекать в отдельную папку.

`CURRENT.json` дополнен путями desktop/native smoke; CAD path/hash и прежние recovery archives сохранены. Свои GPU jobs завершены, ресурсы освобождены; переключение соседнего стенда — по существующему частному операционному плану.


## Исследование камеры16.11 — отдельный кандидат

[Результаты и параметры](research/2026-11-16-redmi-wrist-mount-study.md), [датчики телефона](research/2026-11-16-redmi-phone-sensors.md). Материалы на E: `E:\RoboHand\runs\2026-11-16-redmi-wrist-camera-study`; сравнение для просмотра — `E:\RoboHand\LATEST\SIMULATION\CAMERA-STUDY\camera-mount-comparison.png`. Кандидат не заменяет `LATEST\CAD\EB300.a3d`, default URDF/MJCF или старую training camera.

Архив исследования: `E:\RoboHand\releases\EB300-CAMERA-STUDY-2026-11-16\EB300-CAMERA-STUDY-2026-11-16.zip`; зеркало `D:\RoboHand-Backups\EB300-CAMERA-STUDY-2026-11-16.zip`.35 268 853байт,575payload файлов + manifest; CRC/SHA256 каждого payload и зеркала проверены. SHA256: `18cbf37e687bb8d4d838432650c9592f221d0c100e3d5afeef9cfaadb61159cc`. Внутри — снимок отчётов, результаты/полные кадры и сохранённые исходные metadata SensorServer; это архив исследования, не release робота.


## Заранее зажатая палочка и практика креплений

[Обзор готовых конструкций](research/2026-11-16-wrist-camera-practice.md), [результат preview](research/2026-11-16-pregrasped-tool-preview.md). Отдельная рабочая папка: `E:\RoboHand\LATEST\SIMULATION\HELD-TOOL-CANDIDATE`; есть XML+meshes, полные PNG и GIF. Это кандидат с fixed pregrasp, а не новая активная CAD/обученный захват. Основная EB300.a3d сохранена.

Архив практики креплений и held-tool candidate: `E:\RoboHand\releases\EB300-WRIST-TOOL-RESEARCH-2026-11-16\EB300-WRIST-TOOL-RESEARCH-2026-11-16.zip`, зеркало `D:\RoboHand-Backups\EB300-WRIST-TOOL-RESEARCH-2026-11-16.zip`.19 204 253байт,64payload файла + manifest; CRC, каждый payload SHA256 и зеркало проверены. SHA256: `dd99b7ca65a18742b67586fbb827b1227601b02c9ebd17622a198ae946bdbcc9`.
