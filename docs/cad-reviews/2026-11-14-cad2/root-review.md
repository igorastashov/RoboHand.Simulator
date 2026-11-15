---
tags: [robohand, eb300, cad, review, simulation]
type: verification-report
updated: 2026-11-15
status: accepted-nominal-cad-and-simulation-asset
---

# CAD-2: независимое ревью результата

[Задание и приёмка](task.md) · [Индекс](../../index.md) · [Штатные инструменты](description-preflight.md).

**Принят R7 от15.11.2026:** [редактируемая сборка EB300-R7-prepared.a3d](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R7-prepared.a3d>), [native preview](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R7-clean-native.png>), [независимая финальная приёмка](root-final-acceptance.json). Сборка и стандартный asset готовы к следующему simulation этапу с явно nominal физическими параметрами. Это не приёмка изготовленной руки или обученного typing controller.

Native component-file tree замкнут: [23unique files, paths и SHA256](root-dependency-closure.json), все внутри work root, никаких component paths в original/audit. Native assembly SHA256 `b168ef3cf87969168d0f20ec70986f0ecae15319d609c6688986fcdb089e7254`. Одного A3D недостаточно для переноса: сохранять корень с зависимостями. Установленный ROS package также проверен на наличие URDF/MJCF/meshes/contract и обоих upstream notices.

Работа разрешена владельцем до завершения необходимых CAD-итераций. Исходная сборка и immutable snapshot сохраняются; изменения выполняются в `E:\RoboHand\data\cad-work\2026-11-14-eb300-c2133b98`.

## Принятые результаты

- R3B: конструктивная ориентация трубных звеньев исправлена по исходной инструкции EB300. После сохранения, закрытия и повторного открытия все12 поз компонентов совпали с целевыми; наибольшая разница элементов матриц `5.301e-12`. Все17 root mates действительны. [Журнал](r3b-full-root-mate-rebuild.json).
- R4: добавлены31/Wrist2, nominal выход Wrist3, Redmi8A, раздельные элементы крепления и typing tool. Семь rigid arm links образуют шесть физических вращательных интерфейсов; только основание закреплено относительно мира. Все17 top-level компонентов и28 mates прочитаны заново после reopen: разница матриц0, все mates действительны. Состав:6 coaxial,6 axial-distance,10 dependent-position,6 angular-pose. [Журнал](r4-final-passed.json).
- Шесть angular-pose mates задают устойчивую reference pose CAD. Это управляемые размеры позы, а не шесть неподвижных соединений экспортируемого робота. Их reference parameter90° не означает hardware zero. Автоматические имена КОМПАС не удалось переименовать; соответствие определяется парами деталей/опорными плоскостями и отдельной таблицей.
- Пять аксессуаров проверены относительно фактического выходного фланца. Наибольшая ошибка solver fit `0.000231882 мм`, rotation matrix `3.318e-7`; принята точность `0.001 мм`/`1e-5`. Два последовательных Rebuild не изменили матрицы. TCP в СК выхода примерно `(0,-55,170) мм`. Nominal camera lens `(95,-60,33.4) мм`; optical +Z совпадает с нормалью физически наклонённой задней плоскости телефона и направлен на TCP.
- Из13 исходных STL подготовлены visual meshes с исправленной ориентацией нормалей и отдельные convex collision meshes штатным Trimesh. Геометрия источников не перерисовывалась, отверстия не заполнялись. Все13 collision hulls замкнуты. Это приближение столкновений, не точная геометрия отверстий. [Provenance](prepared-source-meshes.json).
- Минимальный фактический фрагмент EB300 — основание и J1 — прошёл `check_urdf`, штатный URDF loader MuJoCo4.0.1 и1000 шагов с конечными состояниями. Положение compiled mesh совпало с независимым преобразованием CAD с ошибкой менее `4.91e-9 м`. [Проверка](j1-geometry-frame-check.json), [кадр](j1-import-smoke.png). Это проверка фрагмента, не всей руки и не Isaac runtime.
- Финальный R7: после отдельного сохранения12 unique native part files и повторного открытия root все68/68 открытых helper bodies скрыты,16 source mesh occurrences видимы; solid geometry и faces для mates сохранены. Все28 root и25 standalone gripper mates действительны;17component matrices совпадают с уже проверенным URDF source **точно**, gripper relative transforms — до2.274e-13. Native camera/TCP совпали с contract до3e-17м; шесть axis lines — до4.172e-6мм, directions — до4.354e-6°. [Fresh readback](r7-final-native-readback.json), [root acceptance](root-final-acceptance.json).

## Отозванные промежуточные результаты

Ранние R3/R4 placement attempts не являются принятыми ревизиями. API7 `Part.Placement` возвращал изменяемый snapshot: положительные ответы отдельных setter/getter не доказывали сохранение позы. После reopen обнаружена прежняя ориентация. Применён существующий API5 bound `ksPart.GetPlacement()` по официальному примеру `SDK/Samples/CSharp.zip/Automation/Step3d2/Step3d2.cs`; перестановка свободных деталей с последующим восстановлением root mates прошла обязательный persistence gate. Внутренние25 сопряжений захвата не заменялись.

`robot-description-handoff-r3.json` относится к R2 и не используется как финальное описание. Картинка R3 также не доказывает выполненную коррекцию.32 в исходной инструкции — крышка; отсутствовавший корпус запястья —31.

## Полная проверка asset

Проверки завершены; [открыть модель и следующий шаг](viewing-and-next-step.md).

| Проверка | Фактический результат | Evidence |
|---|---|---|
| Native движение J1–J6 | stepped±5° по каждой оси, шаг2.5°; mates valid, reference восстановлена. Worst native FK translation error0.000253мм. Native angle degrees =90 + sign×q_rad×180/π, signs `[-1,-1,-1,-1,-1,+1]` | [Sweeps](r5-six-axis-native-sweeps.json) |
| Полное описание | 15links,14joints, из них6revolute;24visual и27collision geometries. Семь rigid arm links, fixed typing gripper/accessories и semantic optical/TCP frames | [URDF](../../../robohand_ws/src/robohand_description/urdf/eb300_cad2.urdf), [численный контракт](../../../robohand_ws/src/robohand_description/config/eb300_cad2_contract.json) |
| ROS2 | Xacro CLI принимает стандартный URDF, check_urdf проходит; colcon build description и launch --show-args проходят | [check_urdf](full-check-urdf.txt), [build](full-ros-build.txt) |
| Независимые frames/meshes | 25сохранённых native состояний×23mesh occurrences:13различных заданных конфигураций, включая reference и±5°; повторные reference restorations учитываются отдельно. Compiled canonical vertices MuJoCo → world AABB сверены с отдельным CAD-transform расчётом. Maxerror6.526e-8м | [Geometry check](full-geometry-sweeps-check.json) |
| Physical data | Для12physical links массы>0, inertia SPD и triangle inequalities выполнены; nominal total9.468кг. Это не измеренная масса EB300 | [Mass/inertia check](full-description-physical-data-check.json) |
| Численная интеграция | Stock MuJoCo URDF loader:6q/6v/51geoms;1000passive steps в0g и отдельно1g конечны, nu0. В1g суставы пассивно уходят к мягким limits (до0.10314rad), удержание не реализовано | [Dynamics](full-clearance-dynamics-check.json) |
| Fixed accessory clearance | Три constructive pieces holder отдельно отделены от gripper минимум1.00005/7.8183/5.8183мм по выбранным осям; shaft9.9188мм, phone20.0989мм, backing21.9072мм, lowarm1мм. Whole L-holder AABB сам по себе не доказывает пересечение | [Piece bounds](full-clearance-dynamics-check.json) |
| Сохранённая сцена/камера | Стандартный MJCF открывается с диска с relative meshes без VFS; есть общий/wrist/phone renders. Camera FOV60° nominal; axis→TCP ошибка≤0.000066° | [Scene check](full-mujoco-scene-check.json), [camera check](full-camera-render-check.json), [общий вид](full-eb300-reference.png), [оснастка](wrist-close-up.png), [camera](redmi8a-nominal-view.png) |
| Сохранность | Все255source и255immutable snapshot SHA256 совпали с исходным manifest | [Source preservation](source-preservation-final.json) |
| Isolated native solid exports | 8STL: обе трубы, nominal flange и5аксессуаров; всеwatertight/winding-consistent после stock processing, part-localмм подтверждены. Тесселяция даёт bbox undershoot до0.102672мм; это не ошибка native размеров | [Solid export checks](native-solid-export-checks-final.json) |

Нулевые MuJoCo contacts в25позах относятся к collision proxies и штатной фильтрации parent/welded bodies. Они не заменяют отдельную проверку fixed siblings, реальных поверхностей/всего workspace или всех комбинаций суставов. Демонстрационные±5° не являются mechanical limits. Для виртуальной keyboard task диапазон можно расширять после последующих simulation/CAD clearance checks, не дожидаясь физической руки.

## Вспомогательная геометрия CAD

У печатных деталей есть открытые BRep поверхности, созданные для сопряжений; они не входят в physical source STL. Экспорт native002 содержит всеvertices source002 с nearest error≤8.444e-6мм и дополнительно92vertices, удалённых отsource до18.009мм. [Независимое сравнение](gripper002-source-native-comparison.json). Поэтому whole-native STL и default CAD collision query нельзя без разбора использовать как физическую поверхность.

Native `ICollision` давал пересечения с открытыми helpers и контекстно недостоверные owner/body readbacks (`Valid=False`); это не доказательство physical tool/gripper interference. Физическая геометрия берётся из проверенных исходных STL, а collision proxies — из отдельно описанных hulls/primitives. Для статической оснастки выполнено независимое constructive-piece AABB разделение. Helpers не удаляются: на их геометрию ссылаются mates. Поддерживаемое display-only hide проверяется в собственном документном контексте с save/close/reopen; bulk hide из root не принято как доказательство persistence всех68 поверхностей.

В R7 display fix завершён надёжным own-document путём: backup каждой изменяемой work part, hide только `IsSolid=False` BRep bodies, `IBody.Update`, Save exact workfile, close/reopen собственной read-only копии. [Маленький smoke на1_update](helper-visibility-own-document-smoke.json), [остальные11 unique parts](helper-visibility-own-documents-final.json), [финальный root reopen](r7-final-native-readback.json). Bounds/meshes и poses остались прежними. Native save сохранил68/68 hide flags. Ни скрытие, ни их отсутствие не меняют источник физического mesh.

Номинальная компоновка кронштейнов, actuator envelope и typing tool пригодна для виртуальной сцены. Прочность, реальные крепёжные отверстия/проводка, массы приводов, момент/люфт/упругость, intrinsics и latency камеры требуют отдельных измерений перед физическим запуском. Их отсутствие не подменяется стандартной CAD density или симуляцией.

Первичный manufacturer README задаёт **black ABS pipes3-inch/2-inch**, а не сталь. Tube dimensions измерены из native геометрии; default density7.856 не используется. Единственная подтверждённая масса — Redmi188г, остальные aggregate masses и всеCOM/inertias являются design estimates. Инерции получены как uniform box-envelope surrogates, а не из signed volume незамкнутых STL. Лицензионные notices EB300/EBG20 сохранены раздельно в [mesh attribution](../../../robohand_ws/src/robohand_description/meshes/eb300_cad2/ATTRIBUTION.md).
