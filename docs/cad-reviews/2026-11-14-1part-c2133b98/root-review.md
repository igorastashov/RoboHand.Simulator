---
tags: [robohand, eb300, cad, assembly, audit, kompas]
type: review
updated: 2026-11-14
status: read-only-reviewed-gaps-before-kinematics
source_sha256: c2133b98a331749d9bc693e12e561800be17ae545d0c379defbd53a1004f203d
---

# Первая переданная сборка EB300: 1part.a3d

[Индекс Simulator](../../index.md) · [Задание CAD-агенту](../../cad-agent-task.md) · [CAD handoff](../../cad-handoff.md).

Владелец передал сборку для внимательного изучения, проверок и плана последующей подготовки. Аудит выполняется через готовый `hymaxo/kompas3d-mcp@adef44fdc41401af3b239a5c9b1a4e108e1a237a`; новые exporter/framework/controller не создаются. Проверка ниже относится к сохранённой ревизии, не к несохранённым изменениям в CAD.

## Идентифицированные входы

| Параметр | Значение |
|---|---|
| Исходная сборка | [1part.a3d](<E:/RoboHand/data/cad/Robot Arm EB300 - 6283770 - part 1 of 3/files/1part.a3d>) |
| Размер / source mtime UTC | 62 508 bytes / `2026-11-14T14:41:22.9326681Z` |
| SHA256 | `c2133b98a331749d9bc693e12e561800be17ae545d0c379defbd53a1004f203d` |
| Копия для проверки | [snapshot 1part.a3d](<E:/RoboHand/data/cad-reviews/2026-11-14-1part-c2133b98/input/Robot Arm EB300 - 6283770 - part 1 of 3/files/1part.a3d>) |
| Комплект копии | 255 файлов / 164 119 291 bytes; сохранена взаимная структура пяти CAD-каталогов; исключены `.zip`/`.bak` |
| Побайтовая проверка | Для каждого файла SHA256 source-before = snapshot = source-after при копировании |
| Полный manifest | [source-manifest.json](<E:/RoboHand/data/cad-reviews/2026-11-14-1part-c2133b98/source-manifest.json>), SHA256 `cd18ea5cd5ae337c22812a4cd4f9c5285ed12e52ec8bab5e83aab10577992658` |
| CAD | KOMPAS v25 Study, текущий PID 28120; установленный pin MCP подтверждён git rev-parse |

Место при этом preflight: C 12.9 GiB, D 59.5 GiB, E 678 GiB свободно. E подходит как кандидат размещения больших данных; положение virtual disk Docker/WSL и работа GPU внутри него этим не проверены.

## Проверено независимо root

1. Исходник существует, его размер/mtime/digest зарегистрированы; копия и сохранность файлов при копировании проверены.
2. В snapshot есть отдельный захват `gripper20.a3d`, native `tube1.m3d`/`tube2.m3d`, все три части исходного комплекта и update-файлы.
3. Прочитан [stage1-open-inventory.json](stage1-open-inventory.json): точный snapshot открыт `read_only=True, visible=False`, `kind=assembly`, `Changed=False`. Верхний уровень содержит 10 occurrences. Все 10 `FileName` существуют и указывают внутрь snapshot; `1_update` зафиксирован.
4. Перед открытием список CAD-документов был пуст. Несмотря на `visible=False`, Open вернул `Active=True`: отсутствие видимого окна не означает отсутствие active-document эффекта. Изначально открытого пользовательского документа, к которому надо возвращать Active, не было. Не выполнялись Save/Rebuild/Solve/редактирование исходника.
5. Независимо разобраны 28 исходных STL из part1/files: 286 346 треугольников, конечные координаты, локальные bounds. [STL-инвентарь](<E:/RoboHand/data/cad-reviews/2026-11-14-1part-c2133b98/root-review/stl-local-inventory.json>). Единицы и assembly transforms из этого не выводились; topology/contact/physics этим не проверены.
6. PDF инструкции производителя имеют 58 и 27 страниц, без текстового слоя. Для сверки реально просмотрены полноразмерные растровые страницы assembly PDF 4, 50, 51, 56 и 58; комплектация PDF относится к reference, не автоматически к нашему физическому экземпляру.
7. После CAD-аудита повторно сверены **все 255 source и snapshot файлов**: несовпадений с manifest нет, исходная сборка сохранила тот же SHA256. Обе открытые копии закрыты штатным `close_document(discard_changes=False)` после `ReadOnly=True/Changed=False`; список документов снова пуст, как до проверки. [Независимая проверка root](root-verification.json).

## Состав и сопряжения: вывод root по реальным данным

- Дерево содержит **10 компонентов верхнего уровня** и **8 occurrences внутри захвата** (19 записей с корнем). Все прочитанные native component paths существуют внутри snapshot.
- В основном документе прочитаны **18 сопряжений**, все с `Valid=True`: 9 соосностей, 7 расстояний, 2 совпадения. Этот флаг подтверждает чтение состояния объектов, но не доказывает правильность кинематической схемы и механических limits.
- Захват проверен **отдельно в собственном документном контексте**: [stage3-gripper-own-context.json](stage3-gripper-own-context.json). **25 сопряжений, все Valid=True**, Hidden=False, ошибок вызовов нет. Закрыт только собственный unchanged/read-only snapshot.
- В [stage2-tree-mates-geometry.json](stage2-tree-mates-geometry.json) есть placements/матрицы/bounds и корректное чтение root mates. Однако **его вложенные gripper mate rows неавторитетны**: имена захвата сочетались с endpoints и типами сопряжений руки. Первоначальные 12 `Valid=False` из этого чтения отозваны: отдельный stage3 их не подтвердил. Не восстанавливать захват по этим ложным flags.
- Root численно проверил 19 возвращённых rotation blocks: max orthogonality error `4.37e-14`, max `|det−1|=4.86e-14`. [root-matrix-check.json](root-matrix-check.json). Это проверка корректности матриц вращения, не FK, joint frames, масштаба и DOF.
- Root реально просмотрел [snapshot-saved-view.png](snapshot-saved-view.png): рука, трубы и захват видимы. Вспомогательные поверхности/линии остались в сохранённом виде; их видимость не равна дополнительным physics bodies и не является измерением взаимопроникновений.

## Что требует следующего CAD-прохода

### 1. Полная цепочка запястья

На [странице 50 инструкции](<E:/RoboHand/data/cad-reviews/2026-11-14-1part-c2133b98/root-review/assembly-page-50.png>) показаны Wrist1/27 и Wrist2/31. [Страница 51](<E:/RoboHand/data/cad-reviews/2026-11-14-1part-c2133b98/root-review/assembly-page-51.png>) обозначает Wrist3 как actuator/output flange; [страница 56](<E:/RoboHand/data/cad-reviews/2026-11-14-1part-c2133b98/root-review/assembly-page-56.png>) показывает, что деталь32 — крышка, не отдельное звено Wrist3.

В переданной сборке gripper непосредственно сопряжён с `27_update`; корпуса `31_update` в прочитанном дереве нет. Нужно привести цепочку к **Wrist1/27 → Wrist2/31 → Wrist3/output flange → tool/gripper**, затем зарегистрировать физические оси и крепления. Нельзя объявить произвольное вращение gripper относительно27 подтверждённой полной схемой EB300.

Геометрия уже есть: [31_update.stl](<E:/RoboHand/data/cad/Robot Arm EB300 - 6283770 - part 3 of 3/files/31_update.stl>) и [32_update.stl](<E:/RoboHand/data/cad/Robot Arm EB300 - 6283770 - part 3 of 3/files/32_update.stl>). Крышка32 влияет на внешнюю геометрию, но сама не добавляет сустав. Первоначальная гипотеза root по thumbnail о двух недостающих корпусах31/32 отозвана после полного просмотра листов.

### 2. Жёсткие длинные звенья и лишние вращения

| Пара | Что прочитано в CAD | Что подготовить для описания робота |
|---|---|---|
| `7_update` ↔ `14_update` | Соосность + расстояние −220 | Корпуса и `tube1` относятся к одному физическому длинному звену; зафиксировать их взаимный поворот, сохранить конструктивную ориентацию |
| `18_update` ↔ `23_update` | Соосность + расстояние −220 | Аналогично: один rigid link с `tube2`, без произвольного скручивания концов |
| `tube1` ↔ `7_update`, `tube2` ↔ `18_update` | Соосность + совпадение | Включить трубы в соответствующие rigid links. Цилиндрическая форма трубы не требует отдельной динамической вращательной DOF |
| `1_update` ↔ `3_update`, `3_update` ↔ `7_update`, `14_update` ↔ `18_update`, `23_update` ↔ `27_update` | Соосность + расстояние, endpoints читаются | Кандидаты физических вращательных стыков; уточнить ось, ноль, знак, limits и связь с J1–J6 после восстановления запястья |

Пары через трубы не превращать в motor joints ради количества шести осей. Данная интерпретация следует из инструкции сборки и структуры деталей; формальный solver DOF и sweeps ещё не выполнялись. Жёсткость дочерних деталей должна задаваться относительно своего звена, не общей фиксацией всей руки в CAD-world.

### 3. Оснастка, frames и физические параметры

- Дать физическим суставам имена J1–J6; записать parent/child, origins/axes, reference pose, zero/sign/limits. `Placement` компонента не является автоматически joint origin; старый приблизительный Xacro не источник этих значений.
- Определить tool/TCP, нажимной наконечник и fixed mount Redmi 8A с optical frame. В прочитанном дереве нет отдельных phone/bracket/tip компонентов; наличие позиции камеры не выводить из вида gripper.
- Подготовить mass/COM/inertia с источниками. Aggregate CAD вернул `mass_kg≈3.88223` и raw density `7.856`; это не измеренная масса руки с приводами и не достаточная модель 3D-печати. Цифры/units записаны в evidence, не переносятся в physics без проверки.
- Solid `body_count=0` aggregate inspection не означает отсутствие модели: исходные геометрии полигональные. Контакты и collision geometry готовить штатными средствами среды; внутренние зубья/каждый винт не нужны отдельными телами.
- [Stage4](stage4-polygon-counts-close.json) подтвердил по одному полигональному объекту в семи главных printed components, включая `27_update`; прочитанные feature flags не показывают exclusion/rollback/object error. Это не проверка watertight mesh или физического контакта.

## Порядок дальнейшей работы и приёмка

| Проход | Работа | Ожидаемый выход |
|---|---|---|
| **CAD-2** | Рабочая копия, полное запястье, rigid tube links, reference pose и физические J1–J6; согласованные camera/tool mounts | Сохранённая ревизия, карта rigid links/joints и исправленных сопряжений. Затем контроль нескольких поз и пересечений на этой копии |
| **Robot description** | Исходные per-part STL + штатный экспорт недостающих meshes; заполнить существующий Xacro/URDF как данные, задать simple collisions и маркированные estimates dynamics | Standard URDF/meshes и таблица происхождения параметров; сравнение масштаба/frames/поз с CAD. Прямой exporter КОМПАС → URDF не предполагается |
| **Среда, параллельно** | Размещение больших данных на E, штатный setup/debug принятого pinned typing runtime, минимальный GPU/physics/render smoke | Воспроизводимая команда/log/кадр и ресурсный профиль либо конкретный platform/runtime blocker. Full Isaac Sim desktop не обязательный первый шаг |
| **Физическая EB300 в sim** | Импорт через проверенный готовый путь, стол/клавиатура, joints/drives/collisions, wrist camera | Поосевая проверка, стабильная физика, 10 resets и контролируемое press/release. Потом проверка готовых hooks адаптации task к шести arm actions |
| **Обучение** | После предыдущих gates — штатный PPO state teacher → wrist vision student и independent eval | Checkpoint/config/log, точность последовательности/лишние нажатия/время/отказы. ACT/Hermes не подменяют принятый метод |

Ближайший полезный результат — CAD-2 и согласованный стандартный robot description. Голосовой supervisor и реальное железо идут после работающего виртуального навыка с отдельной приёмкой. Точная длительность CAD-2 пока не измерена; прогноз пересчитывается по реально закрытым пунктам, без обещания обучения из текущего файла одним импортом.

## Границы текущей проверки

Не выполнялись редактирование CAD, Rebuild/Solve, перемещения/sweeps, восстановление joint limits, collision/clearance test, camera calibration, physics/import/training и real hardware trials. В stage2 зафиксирован 81 отказ необязательного `UniqueNum` getter; это ошибка выбора API-чтения, не 81 дефект модели. Повторные попытки прекращены, identity устанавливалась по occurrence path/file/матрицам.

**Итог:** сохранённая ревизия и её component dependencies приняты как вход CAD-2; полная кинематика шести осей и готовность к physics ещё не приняты. Исходник сохранён без изменений. Новые модели/прошивка/обучение этим аудитом не создавались.
