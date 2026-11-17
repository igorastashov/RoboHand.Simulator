---
tags: [eb300, ebg20, cad, mujoco, contact, review]
type: independent-review
updated: 2026-11-17
status: standalone-contact-candidate-reviewed-full-arm-integration-pending
---

# EBG20: подвижный контактный кандидат и независимое ревью

Подготовлен **отдельный стандартный MJCF-кандидат EBG20**, в котором губки закрываются, удерживают свободный карандаш, поднимают его и отпускают. Это диагностический захват заранее поставленного вертикально предмета. Поиск лежащего карандаша, подвод EB300, motor policy и клавиатурный эпизод ещё не выполнены. Кандидат не заменяет принятую `E:\RoboHand\LATEST\CAD\EB300.a3d`.

## Что выяснено по имеющейся механике

В исходном комплекте есть15STL и описание одного MG995 или более мощного servo. В отдельно собранной native CAD —8occurrences/25сопряжений: корпус/направляющая и две группы губок. Свежий native read-only audit и независимая сверка геометрии подтверждают их положения. Шестерня015 и рейки005/010 присутствуют среди исходных STL, но не были включены в native сборку.

Реальная принципиальная схема — **один сервопривод → шестерня → две рейки**, а не две независимо управляемые губки. В MJCF — один servo hinge и две внутренние slide joints со штатными joint equalities. Детали013/014 в этом варианте объединены с соответствующей губкой; пассивная адаптивность/шарниры, не подтверждённые сборкой, не изобретались.

Из18зубьев pinion и измеренного шага rack≈2,3876mm получен ideal pitch radius≈6,83999mm. Это геометрическая оценка, **не измеренная передаточная характеристика MG995**. Неизвестные backlash, реальные stiffness/inertia/torque/friction остаются calibration gap. Точное крепление missing racks к carriage в native CAD также ещё не восстановлено; произвольные placements реек не выдаются за проверенную сборку.

## Что проверил root независимо

Проверен [R2 MJCF](ebg20_axial_prepositioned_candidate_r2.xml), SHA256 `8a4d26badc72796e247059d9182d59970261e9d0f62688f78e5b9ae6ba45f698`, MuJoCo4.0.1. Профиль изменён относительно agent-run: μ0,35, closure−0,60rad, smoothstep lift30mm за1,2s, удержание2s, отпускание0,6s. Maxima накапливались **на каждом physics step**. [Числовая evidence](root-independent-r2-review.json).

| Проверка | timestep2ms | timestep0,5ms |
|---|---:|---:|
| Подъём свободного предмета |29,996mm |29,996mm |
| Падение после отпускания |29,996mm |29,996mm |
| Контакт обеих рабочих губок при удержании |есть |есть |
| Максимальное отклонение rack equality |83,24µm |76,27µm |
| Максимальное проникновение предмета в губки |39,70µm |73,40µm |
| Максимальное проникновение при ударе о пол после release |1,194mm |0,940mm |
| Internal contact penetration |0 |0 |
| Warning / time reset / nonfinite |нет |нет |

Предмет имеет free joint; у него нет weld/mocap/actuator. Единственные equality constraints связывают внутренние joints привода. Подъём выполняет отдельная диагностическая position-controlled вертикальная fixture, **не обученная EB300**. В full-arm scene fixture joint/actuator должны быть удалены: останутся шесть arm actions плюс один MG995.

Скриншот `E:\RoboHand\runs\2026-11-17-ebg20-motion\R2-diagnostic-hold.png` просмотрен root: предмет удерживается вдоль губок. Предыдущий horizontal case был поперечным хватом и осевой ориентацией не называется. Поворот запястья не исправляет взаимную ориентацию уже зажатых губок и карандаша.

## Численная устойчивость и границы приёмки

R1 работал при50µs, но root обнаружил QACC/reset при0,5ms. R1 файлы сохранены неизменными. **Именно R2**, с positive solref0,004/1, filtered position timeconst0,05s и effective servo armature0,001kg·m², проверен при2ms общей desktop scene. Armature выбран как минимальный из протестированных для bounded solver stability, это не оценка реальной инерции MG995. Torque limit±0,25N·m, массы и исходная геометрия при этом не увеличивались для удержания предмета.

Широкий strict gate «любое проникновение<250µm» **не пройден** из-за release floor impact. В собственном nominal профиле агента every-step gear peak≈101,57/112,10µm также немного превысил первоначальный gate100µm; прежние sampled maxima этот пик пропускали. У root изменённый профиль ниже100µm, но это не отменяет nominal failure. Эти ограничения сохранены в evidence; успешный bounded grip/lift/hold/release их не отменяет. Нельзя объявлять всей физике production-ready или скрывать floor event в усреднённой метрике.

Верхняя полная CAD и старые R1 XML не менялись. Принятая CAD SHA256 остаётся `3b919e9642686f2194ca007484ad860229b4fccadf0ea7517d40e6c2383254db`. Новые model data пока кандидат, без fake trained policy и без hardware motion.

## Где лежат файлы и что дальше

- В этом каталоге — числовые contract/review, source-derived standard MJCF и [отчёт агента](agent-report.md). Raw CAD, STL/meshes, картинки и SDK calls хранятся локально вне публичного Git: `E:\RoboHand\runs\2026-11-17-ebg20-motion`. У исходного EBG20 есть NC/ND ограничения; отдельные meshes не публикуются заново.
- Для просмотра создан отдельный локальный каталог `E:\RoboHand\LATEST\SIMULATION\MOVING-GRIPPER-CANDIDATE`: `EBG20-standalone-r2.xml`, необходимые meshes, README и manifest. В этой portable copy изменён только compiler.meshdir; accepted CAD не заменена. Viewer открывает сцену, а последовательность диагностического теста автоматически не проигрывает.
- Сначала объединить кандидат с отдельной EB300 scene, проверить frame transform, self/table clearances, nominal inertia и один полный wrist-view выбранного крепления. Это отдельный gate, текущий standalone result его не подменяет.
- Для записей и rollout используем готовый LeRobot SimRobot/EnvHub. [Upstream smoke и конкретный proposal](../../research/2026-11-17-eb300-envhub-adaptation.md) отделены от разрешённых standard model data. Нового executable bridge до решения владельца нет.
- После совместимого data/action contract — demonstrations EB300 и [штатный π0.5 LoRA](../../research/2026-11-17-pi05-tokenizer-lora.md), далее независимая оценка свободного хвата. Keyboard/слово и Codex coordinator идут после работающей операции.

[Индекс](../../index.md) · [целевая задача](../../research/2026-11-16-typing-tool-acquisition-plan.md).
