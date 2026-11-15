---
tags: [robohand, eb300, cad, release, jaw-typing, verification]
type: verification-report
updated: 2026-11-15
status: accepted-nominal-r8-jaw-profile
---

# R8 принята: одна сборка, логические узлы, обычная губка

[Актуальные файлы и восстановление](../../latest-artifacts.md) · [Задание](task.md) · [Отчёт CAD-агента](cad-agent-report.md) · [Индекс](../../index.md).

**Итоговый native файл:** [EB300-R8-jaw-typing.a3d](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R8-jaw-typing.a3d>), SHA256 `c6b0003ee6e4a8774d6d51577289e323eeb2001b7d75c71a586b48703deba774`. [Native preview](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/outputs/EB300-R8-jaw-typing.png>).

Раньше детали уже находились в одном rootA3D, но на плоском верхнем уровне. Теперь штатным `IParts7.CreateSubAssembly` созданы три настоящие подсборки. Иерархия отражает жёсткие физические звенья:

```text
EB300-R8
├─ Основание:1_update
├─ Плечевой узел:3_update
├─ Верхнее звено:7_update + tube1 +14_update
├─ Предплечье:18_update + tube2 +23_update
├─ Запястье1:27_update
├─ Запястье2:31_update
└─ Кисть:выходной фланец + EBG20 + Redmi8A и2части крепления
```

Шесть вращательных интерфейсов сохранены. Автоматические совпадения новых ЛСК с world, создаваемые stock operation, удалены и проверены движением. `IUserFolder.SetObjects` не принял components в smallest probes; неподтверждённые папки не выдавались за результат. Использован существующий pinned MCP и официальный SDK, без нового exporter/framework.

## Что изменилось для печати

По прямому требованию владельца удалены стержень, его держатель и только2их fixed-position mates. Их нет в активной native dependency closure, новом URDF и MJCF. Историческая R7S сохранена отдельно; старые mesh files не означают их присутствие в R8.

Контакт — существующий угол губки `013.m3d`, occurrence3 внутри EBG20, source vertex `(101.5,92.5,40)мм`. Его output coordinates примерно `(-7.70391778687,-15.92969103684,136)мм`. Это semantic frame `jaw_contact_frame`, не новый концевик/датчик/деталь. [Точный datum](jaw-contact-datum.json). Печать требует ориентации обычного захвата, чтобы выбранная кромка нажимала нужную клавишу без соседних нажатий. Это следующий task/actuator этап, а не уже обученное поведение.

Раскрытие захвата пока зафиксировано в captured reference;25native mates сохранены. Для изменения раскрытия требуется правильная кинематика его механизма. Не создана фиктивная one-DOF URDF-конверсия.

## Проверки root

| Проверка | Результат | Evidence |
|---|---|---|
| Native hierarchy | 7top nodes;24unique native files:4новых и20shared R7S. Включена обязательная upper dependency `EB300-R8-upper-rigid-smoke.a3d`, несмотря на исторический суффикс | [Closure](r8-dependency-closure.json) |
| Сопряжения | 18root =6coax+6axial-stop+6pose angles; внутри новых upper/fore/end:2/2/4, gripper25. ВсеValid в собственном контексте | [Native final](r8-six-axis-native-final.json) |
| Native motion/persistence | 48шагов шести осей±2.5°/±5° и возвраты; после save/close/reopen reference к R7S отличается ≤0.000144073мм | [Native sweeps](r8-six-axis-native-final.json) |
| Независимая сверка | 49сохранённых состояний,25различных заданных конфигураций,21mesh occurrence; MuJoCo compiled geometry против fresh nested CAD poses. MaxAABBerror3.769e-7м; jaw-contact error3.239e-7м, camera3.683e-7м, порог1e-6м | [Root acceptance](root-acceptance.json) |
| Направления | Native angle=90+sign×q_rad×180/π, signs `[-1,-1,-1,-1,-1,+1]`. Direct child rotation delta подтвердил ошибку менее0.000004697° | [Sign diagnostic](root-sweep-sign-diagnostic.json) |
| URDF/physics data | 13links/12joints,6revolute;22visual/23collision geometries,45MuJoCo geoms;10positive physical inertias, nominal mass9.348кг;1000passive steps отдельно0g/1g конечны | [URDF](../../../robohand_ws/src/robohand_description/urdf/eb300_jaw_typing_r8.urdf), [profile check](sim-profile-validation.json), [check_urdf](urdf-check.txt) |
| Visual state | 68/68open BRep скрыты,16/16source polygon meshes и6/6solids видимы. Read-only inventory не изменилroot/23R7Sfiles | [Visibility](r8-visibility-readonly.json) |
| Сохранность | Все23файла R7S до/после совпали. R7S имеет собственный проверенный recovery ZIP наE иD | [R7S backup verification](r7s-release-verification.json) |

После CreateSubAssembly raw coax endpoint J2 сменил направление. Его `measured_angle_deg` в CAD-журнале относится к этому raw axis и имеет противоположный знак canonical URDFJ2. Реальное соответствие native95°→URDFq−5° осталось прежним. Root использовал canonical parameter signs и независимо проверил child rotation delta; неподтверждённый raw знак в policy contract не перенесён. Движение CAD исправлять не требовалось.

## Камера и границы готовности

[Общий вид новой модели](r8-full-jaw-profile.png) · [выбранная существующая губка выделена цветом](r8-selected-jaw.png) · [wrist view](r8-redmi-view.png).

Точка контакта попадает в nominal60°FOV, примерно в normalizedpixel `(0.384,0.739)`. Однако её прямая линия от камеры перекрыта боковиной самой губки примерно за4.6мм до угла. [Frustum/ray/render check](r8-import-camera-check.json). Это частичная окклюзия, не доказательство прямой видимости. Телефон не перенесён; необходимость другого монтажа/видимых признаков оценивается на keyboard scene до vision training.

Native edge display может показывать треугольники реальных STL и datum lines; это не68скрытых вспомогательных BRep и не физические детали нового URDF.

Демонстрационные±5° не являются real limits или готовой keyboard workspace. Нужны дальнейшие virtual clearance checks/расширение диапазонов, штатный typing runtime/GPU smoke и6-axis actuator/task configuration. Приводов/controller в inspection model нет; simulation не подтверждает real-ready управление. Массы/COM/inertias/камера/фланец/крепления nominal, кроме официальной массы Redmi188г.

Все физические базовые компоненты подтверждены владельцем15.11; [докупаемые дополнения и vendor software](<../../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/hardware-and-vendor-software-2026-11-15.md>). Encoder измеряет угол, а не силу на губке. Приобретение фирменного software для simulation не нужно; пакет включает Mega firmware, егоAPI/лицензия/цена пока не проверены.
