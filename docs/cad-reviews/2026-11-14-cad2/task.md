---
tags: [robohand, eb300, cad, preparation, iterative-work]
type: execution-brief
updated: 2026-11-15
status: completed-nominal-cad-asset-preparation
---

# CAD-2: подготовить EB300 к robot description и физической среде

[Индекс](../../index.md) · [Предыдущий аудит](../2026-11-14-1part-c2133b98/root-review.md) · [Общий CAD brief](../../cad-agent-task.md).

**Выполнено15.11:** принят [R7 и независимый root review](root-review.md), [готовые файлы/просмотр/следующий gate](viewing-and-next-step.md). Полная native цепь/оснастка, six-axis sweeps, URDF/meshes, nominal физические данные,25поз независимой проверки и штатная открываемая MuJoCo сцена подготовлены. [23native dependencies с hashes](root-dependency-closure.json), [исходник/snapshot сохранны](source-preservation-final.json). Неизвестные аппаратные параметры отмечены; изготовление/калибровка/обучение не входили в приёмку этой CAD-задачи.

**Прямое поручение владельца после первого аудита:** «делай все что нужно со сборкой что бы она физически была готова к следующим этапам. действуй сколько нужно и в цикле». Разрешены необходимые изменения отдельной рабочей копии, проверки и исправления до результата. Повторное разрешение на каждую обычную CAD-операцию не требуется. Платформа только EB300; используются готовый pinned MCP/SDK и стандартные CAD/URDF/config данные. Новый exporter/framework/controller/UI не создавать.

## Входы и сохранность

- Исходная ревизия `c2133b98a331749d9bc693e12e561800be17ae545d0c379defbd53a1004f203d` и immutable audit snapshot остаются неизменными.
- Рабочий корень: `E:\RoboHand\data\cad-work\2026-11-14-eb300-c2133b98`.
- Рабочая сборка: [1part.a3d](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/input/Robot Arm EB300 - 6283770 - part 1 of 3/files/1part.a3d>).
- Перенесены все255 файлов из проверенного snapshot, каждый SHA256 подтверждён. [Provenance](<E:/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98/workcopy-provenance.json>).
- Новые native части и ревизии assembly сохранять внутри work root; exports — `outputs`. Перед изменением/сохранением проверять документ и реальные component paths: ни один не должен указывать на исходник или immutable snapshot.
- CAD-специалист выполняет изменения, root ревьюит данные/картинки/проверки и готовит robot description. Одновременно одному CAD-документу пишет только один агент.

## Итерации и ожидаемые выходы

| Итерация | Работа | Проверка и артефакт |
|---|---|---|
| R1 | Writable workcopy, rigid links `7+tube1+14` и `18+tube2+23`, конструктивная ориентация | Native checkpoint, фактические mate properties, unchanged reference pose либо явные изменения. Не фиксировать все звенья относительно world |
| R2 | Полная цепочка `Wrist1/27 → Wrist2/31 → Wrist3/output flange → tool/gripper` | Штатный STL import31, native part/assembly, корректные interfaces, preview.32 — крышка, не отдельный сустав |
| R3 | Семь rigid arm links и шесть физических arm joints, отдельный gripper, frames/reference pose/zero/sign | Таблица parent/child/origin/axis/units, источники/assumptions; число CAD-компонентов не заменяет число DOF |
| R4 | TCP, typing tip, Redmi8A/mount и camera optical frame | Native оснастка, transforms, массы/инерции с provenance. Достаточная внешняя геометрия; внутренние зубья/каждый винт не обязательны |
| R5 | Проверка движения, несколько поз/поосевые sweeps и доступные clearance checks, исправление найденного | Pose/config/видео или реальные кадры, точная методика и результат. Limits до измерений могут быть ограниченными nominal demo ranges, не паспортными mechanical limits |
| R6 | Стандартный CAD/robot-description handoff и сохранность результата | Reopen final native assembly, dependency closure, per-part/per-link meshes или сохранённые исходные STL, joint/rigid-link tables, clean preview и отчёт. Root готовит URDF/Xacro и стандартную проверку |

Порядок итераций можно уточнять по найденному штатному workflow; checkpoint сохраняется до рискованной операции. Ошибки/неудачные попытки не перезаписываются. Изменение → проверка → ревью → исправление повторяются, пока не закрыты применимые пункты.

## Геометрия и неизвестные параметры

`31_update.stl` доступен в workcopy `Robot Arm EB300 - 6283770 - part 3 of 3/files`. По исходной инструкции31 — корпус Wrist2; Wrist3 — актуатор/выходной фланец. Для пока отсутствующего actuator/tool envelope допустимы стандартные primitives как CAD/config данные, с маркировкой nominal, не точная реконструкция неизвестного узла.

Для Redmi8A [официальная спецификация Xiaomi](https://www.mi.com/in/redmi-8a/specs/) подтверждает **156.48×75.41×9.4 мм,188 г**, rear12MP f/1.8, video1080p30. Положение lens center, intrinsics/distortion, capture latency и физический кронштейн этим не калиброваны. Создать проверяемую nominal wrist компоновку по задаче, lens position/угол и clearance записать как design assumption, допускающий правку; не копировать reference camera calibration.

Массы printed parts/motors/cables не выводить из default density7.856. Первые mass/inertia допустимы как явно маркированные physically valid estimates с диапазоном/источником; неизвестная точная hardware calibration не повод выдавать такие оценки за измерение. Настоящие калибровки и sim-to-real validation — последующий этап.

## Готовые инструменты и границы

- `hymaxo/kompas3d-mcp@adef44fdc41401af3b239a5c9b1a4e108e1a237a`, установленный SDK v25 Study. Допустим standard MCP Python SDK client к нему, как в пройденных экспериментах, без нового сервера/обёртки/runtime.
- Перед native mutation читать выбранный SDK метод/готовый example и пройти самый маленький сценарий. В частности, [штатный LoadFromAdditionFormat](https://help.ascon.ru/KOMPAS_SDK/25/ru-RU/ksdocument3d_loadfromadditionformat.html) поддерживает STL; не писать собственный STL→CAD converter.
- `IMateConstraint3D.Fixed` не считать запретом вращения без чтения его точной семантики. Выбрать штатный orientation/rigid mate, preserving relative pose, по фактическому SDK.
- Вложенные gripper mates читать в собственном документном контексте: прошлый audit обнаружил context contamination при чтении их полей из root. Сам gripper standalone25/25Valid; не чинить его по отозванным flags.
- Geometry/frames/URDF/config — данные нашей руки. Controller/model/action adaptation и training runtime — отдельный future gate, не прятать новый executable code в CAD-работе.

## Критерий окончания CAD-2

Критерий закрыт итоговой R7; доказательства и ограничения приведены в актуальном review выше. Текст ниже сохраняет исходное определение приёмки.

Есть конкретная native ревизия и её замкнутые зависимости, правильные rigid groups и полная arm joint chain, оснастка/камера и данные frames, проверенное движение в перечисленных позах, пригодная для стандартного импорта геометрия, записанные estimates/неизвестные и воспроизводимые результаты проверок. Наличие valid mates или красивой картинки отдельно недостаточно.

Если какой-то физический параметр нельзя определить без железа, результат явно nominal для симуляции; это не блокирует завершение CAD/asset подготовки. Если технический gap требует нового исполняемого exporter/controller/framework, описать точный gap и продолжить независимую работу; не создавать его без отдельного решения.
