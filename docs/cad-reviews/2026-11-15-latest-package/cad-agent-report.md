---
tags: [robohand, eb300, cad, latest, native-package]
type: cad-execution-report
updated: 2026-11-15
status: native-package-checks-passed
---

# LATEST: отдельная рабочая сборка

Открывать [E:\RoboHand\LATEST\CAD\EB300.a3d](<E:/RoboHand/LATEST/CAD/EB300.a3d>). В верхнем уровне CAD находится один A3D, остальные 23 native-зависимости расположены в `components/`. Все ссылки перепривязаны штатным КОМПАС SDK на файлы внутри этой папки; зависимостей от прежнего `outputs` в прочитанном native closure нет.

Root SHA256: `3b919e9642686f2194ca007484ad860229b4fccadf0ea7517d40e6c2383254db`. Полный комплект — 24 native-файла, 2 938 144 байт. [Пофайловый manifest/SHA256](native-closure.json).

## Применённый готовый путь

Использован установленный `hymaxo/kompas3d-mcp@adef44fdc41401af3b239a5c9b1a4e108e1a237a`, Python 3.12 и официальный SDK КОМПАС v25 Study. Просмотрены upstream commit/requirements и установленная справка `ipart7_filename.html`: для вставленного компонента допускается `IPart7.FileName SET`, изменение применяется через `IModelObject.Update`. В просмотренных готовых MCP tools и SDK отдельный полный pack-and-go не обнаружен; `SaveAsEx` сам по себе не закрывает перенос зависимостей.

Сначала 24 файла скопированы из проверенных дисковых байтов принятой R8, root SHA `c6b0003ee6e4a8774d6d51577289e323eeb2001b7d75c71a586b48703deba774`. Smallest smoke перепривязал только `7_update` в копии upper: Update=True, save/close/reopen сохранил новый путь, две связи Valid, pose delta=0. [Smoke](smallest-smoke.json).

Далее штатные FileName+Update применены к копиям снизу вверх: gripper, upper, forearm, end-effector, root. Каждый документ сохранён явно только по собственному новому пути и проверен повторным открытием. `SaveAll` не применялся, нового exporter/server/framework не создавалось.

## Фактическая проверка

| Документ | Сопряжения после повторного открытия |
|---|---:|
| EB300.a3d | 18/18 Valid |
| upper | 2/2 Valid |
| forearm | 2/2 Valid |
| end-effector | 4/4 Valid |
| gripper20 | 25/25 Valid |

- Все 26 записей дерева имеют native `GetSummMatrix`, совпадающий с принятой сохранённой R8: max element delta=0. Геометрия, captured jaw opening и кинематическая структура не изменялись.
- Штатный `IKompasDocument1.GetExternalFilesNamesEx(True)` вернул ровно 23 ссылки внутри `LATEST\CAD\components`; список совпал с рекурсивным native component tree. У всех 19 M3D метод `GetExternalFilesNamesEx(False)` вернул пустой список зависимостей. Все 24 файла существуют. [Сводка](complete-relink.json), [closure](native-closure.json).
- 27 защищённых исходных файлов — принятая R8, её closure и дополнительные frozen R7S-файлы — сохранили исходные SHA256.
- Исходная пользовательская R8 с `Changed=True` осталась открытой с тем же документным reference и теми же 26 матрицами (delta=0). Она не сохранялась, не закрывалась и не перестраивалась. Сборка LATEST оставлена открытой, `Changed=False`.

Полные одноразовые MCP traces и stderr находятся только в `E:\RoboHand\data\cad-reviews\2026-11-15-latest-package`; в Simulator сохранены краткие JSON и этот отчёт. Служебный скрытый lock-файл открытого КОМПАС не является native-зависимостью; его не удаляли.

Проверка выполнена на текущем ПК и при указанном пути. Открытие после переноса папки либо на другом ПК не проверялось. Унаследованные R8 nominal/camera/physics ограничения сохраняются; перепаковка не является новым hardware, collision или training gate. Папки индексов, `CURRENT.json` и указатели LATEST редактирует root после ревью.
