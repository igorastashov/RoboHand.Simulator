---
tags: [robohand, eb300, cad, logical-tree, jaw-contact]
type: cad-execution-report
updated: 2026-11-15
status: native-checks-passed
---

# R8: подсборки и контакт обычной губкой

В новой [EB300-R8-jaw-typing.a3d](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R8-jaw-typing.a3d>) создано семь узлов верхнего уровня. Держатель и стержень удалены вместе только с двумя их dependent-position сопряжениями. Настоящий захват и три компонента телефона сохранены. Исходная R7S и все её 23 native-файла побайтно неизменны. [Задание](task.md), [финальные native-проверки](r8-six-axis-native-final.json), [PNG](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R8-jaw-typing.png>).

SHA256 корневой R8: `c6b0003ee6e4a8774d6d51577289e323eeb2001b7d75c71a586b48703deba774`.

## Готовый штатный путь

Использованы установленный `hymaxo/kompas3d-mcp@adef44fdc41401af3b239a5c9b1a4e108e1a237a`, штатный MCP SDK-клиент и интерфейсы SDK КОМПАС v25 Study. Установленный SDK: `C:\Program Files\ASCON\KOMPAS-3D v25 Study\SDK\Help\KOMPAS_SDK_ru-RU.zip`. Новый exporter, server, controller или framework не создавался.

`IPart7.UserFolders → IUserFolders.Add → IUserFolder.SetObjects → Update` проверен на изолированной R8. Ни direct IPart7 array, ни single/array IModelObject не приняты: `SetObjects=False`, количество папок осталось нулевым. Empty-folder `Update=False`. Поэтому папки компонентов через этот API не объявлены работающими. [Последний bounded folder probe](userfolder-dispatch-types-smoke.json).

Подтверждён официальный [IParts7.CreateSubAssembly](https://help.ascon.ru/KOMPAS_SDK/25/ru-RU/iparts7_createsubassembly.html): массив выбранных компонентов и новое имя A3D. Он переносит внутренние связи и сохраняет внешние ссылки сопряжений. Дополнительно создаётся совпадение ЛСК с корнем; только это новое автоматическое сопряжение удалялось в каждом случае, чтобы не закреплять подвижное звено относительно world. Первый upper smoke проверен через J1/J2 и save/close/reopen до дальнейшего применения. [Smoke](subassembly-upper-roundtrip-smoke.json), [группировка](r8-remove-and-group.json).

## Сохранённая структура

| Узел верхнего уровня | Native-состав | Внутренние связи новой подсборки |
|---|---|---|
| Основание `1_update` | исходная деталь | — |
| Плечевой узел `3_update` | исходная деталь | — |
| «Верхнее звено — труба и локти» | `7_update + tube1 + 14_update` | 2 dependent-position |
| «Предплечье — труба и локти» | `18_update + tube2 + 23_update` | 2 dependent-position |
| Wrist1 `27_update` | исходная деталь | — |
| Wrist2 `31_update` | подготовленная деталь | — |
| «Захват и телефон» | flange, gripper20, Redmi8A, low-arm, backing-post | 4 dependent-position |

Человекочитаемые имена заданы и сохранены только трём новым подсборкам. Верхняя подсборка находится в `EB300-R8-upper-rigid-smoke.a3d`: несмотря на исторический суффикс имени файла, это действительная финальная зависимость, её нужно включать в релиз. Остальные новые файлы: `EB300-R8-forearm.a3d`, `EB300-R8-end-effector.a3d` рядом с корневой R8. Внутренние 25 сопряжений gripper20 сохранены.

После сохранения и повторного открытия: 18/18 root mates Valid — шесть coaxial, шесть axial-distance, шесть driving-angle. В собственном документном контексте новых подсборок подтверждены 2/2, 2/2, 4/4 Valid; gripper20 — 25/25 Valid. Чтение nested mates из root-контекста не использовалось как доказательство их состояния.

## Проверки и handoff

- Шесть осей по отдельности: native angle `90→92.5→95→92.5→90→87.5→85→87.5→90°`, всего 48 обновлений. Проверены движение всех downstream компонентов одним преобразованием, неподвижность предков и совпадение оси вращения с native coax. Все шаги пройдены. Максимальные ошибки: group translation `0.000367873 мм`, rotation `3.015e-7`, axis-point `0.000010890 мм`; пороги `0.001 мм / 1e-5`. Это демонстрационный диапазон, не механические пределы.
- После save/close/reopen позы сохранённых компонентов относительно R7S отличаются максимум на `0.000144073 мм / 1.618e-7` rotation. Разница восьми mesh→output трансформов захвата не более `8.701e-12` по элементам матриц. Физическая кинематическая цепь и CAD-angle→q convention прежние; driving-angle mates не становятся fixed joints в URDF.
- Реальный контакт: `013.m3d`, occurrence index 3 внутри gripper, source vertex `(101.5, 92.5, 40) мм`. Штатный `IPart7.TransformPoint` дал output `(-7.703917786872, -15.929691036835, 136.000000000007) мм`, отклонение от source datum `7.873e-12 мм`. В CAD-world эта точка `(91.819825344167, 810.296075466258, 234.098058317782) мм`. Семантический TCP следует губке; новой физической детали или датчика нет. [Datum](jaw-contact-datum.json).
- Fresh camera basis в CAD-world/output, все 26 записей дерева с native `GetSummMatrix`, значения/оси шести сопряжений и результаты всех шагов находятся в [финальном JSON](r8-six-axis-native-final.json). CAD-world остаётся Y-up, линейные данные — мм; преобразование в robot Z-up выполняется существующим стандартным description-контрактом.
- [Dependency closure](r8-dependency-closure.json): 24 уникальных native-файла, 2 943 520 байт; четыре новых R8 и 20 frozen shared dependencies. Все существуют внутри разрешённого work-root. Typing parts отсутствуют в активной closure; исторические файлы сохранены. Все 23 R7S SHA256 до/после CAD-операций совпали. `SaveAll` не вызывался. Финальный root открыт, `Changed=False`; чужие документы не закрывались.
- Native PNG просмотрен: стержня и держателя нет, телефон и захват видны; полигональные рёбра исходных visual meshes остаются видимыми. Дополнительный [read-only visibility inventory](r8-visibility-readonly.json) подтвердил в R8 root 68/68 hidden open BRep, 16/16 visible polygon meshes и 6/6 visible solid bodies. В собственных контекстах новых подсборок hidden/open counts: upper 10/10, fore 9/9, end 37/37. Все документы остались `Changed=False`, root hash и 23 R7S hash прежние. Отдельные datum-линии и стиль отображения полигональных рёбер не входят в эти 68 open BRep; полностью гладкий viewport не обещается. Cosmetic-мутаций после финального SHA не выполнялось.

## Границы результата

Контактная точка находится в nominal FOV, но camera ray до кромки перекрывается собственной геометрией губки примерно за 4.6 мм до контакта. Монтаж телефона сохранён; прямая видимость точки не обещается. [Проверка root](jaw-corner-visibility-candidates.json). При другом раскрытии захвата TCP надо пересчитывать по реальной кинематике пальца.

Моторные пределы, калибровка камеры/TCP, точная масса/inertia, полная collision-free рабочая область и real-hardware readiness этим проходом не подтверждались. Унаследованные nominal flange/phone/mount допущения R7 остаются. Frozen leaves не перепривязывались: архив должен сохранять штатные native references и их восстановление по manifest. URDF/MJCF, сцена нажатия и обучение проверяются отдельными gates под ревью root.
