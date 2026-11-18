---
tags: [eb300, mink, lerobot, teleoperation, pencil, execution]
type: verified-execution
updated: 2026-11-18
status: physical-sim-cycle-record-replay-verified-not-learned
---

# EB300: первый полный контактный цикл и готовая связка Mink

**В симуляции полная EB300 подошла к свободно лежащему карандашу, зажала его рабочими pads, подняла на69,306мм, удержала, опустила и разжала губки.** Пройдено990управляющих кадров/39,6s и19 800physics steps. Это заранее заданные operator targets через готовую Mink IK, **не learned policy, зрительный поиск или перенос на реальное железо**.

[Числовая evidence](evidence/2026-11-18-mink-execution.json) · [Разрешённый владельцем18.11 scope](2026-11-18-eb300-teleop-adaptation.md) · [Геометрический анализ](../cad-reviews/2026-11-18-pencil-clearance/agent-report.md) · [Команды](../../integrations/lerobot_envhub/README.md) · [Индекс](../index.md).

## Что реализовано и переиспользовано

Владелец отдельно разрешил binding после source audit четырёх готовых решений. Реализация — [teleop_mink.py](../../integrations/lerobot_envhub/teleop_mink.py), standard [config](../../integrations/lerobot_envhub/mink-config.json), [viewer-only target scene](../../integrations/lerobot_envhub/assets/eb300_mink_teleop.xml), optional requirements и contract tests. Готовые `Mink FrameTask/solve_ik/DAQP/ConfigurationLimit/VelocityLimit/CollisionAvoidanceLimit/DofFreezingTask`, `TeleopMocap`, `mujoco.viewer.launch_passive` и `LeRobotDataset` используются без fork. Нового IK solver, motor law, UI, agent framework или формата датасета нет.

Source pins: [Mink5f800f0](https://github.com/kevinzakka/mink/tree/5f800f0a369d05bab88b5e5582cf95122d3b82a5),1.4.0; [LeRobot7910c20](https://github.com/huggingface/lerobot/tree/7910c20a75834ad3fa6a9792df4d44a614d1bba6). Исходные quickstart/tasks-and-limits Mink выполнены без изменений. Альтернатива [RoboSimStudioba3650c](https://github.com/robosimstudio/robosimstudio/tree/ba3650c4669fffabb7bd52802f4fdf6cdc66cb19) реально установлена отдельно:4unregistered-robot tests прошли наRTX3090. Миграции EB300 туда не было: physics/import и native-record→LeRobot gaps описаны в scope, а не объявлены готовой интеграцией.

Binding держит nominal commanded configuration, как upstream actuator example. На старте сохраняются существующие ctrl, а не подставляется просевший measured qpos в новый target каждый кадр. Физический мир двигается только штатными7actuators,2ms/25Hz. IK работает на отдельном MjData; все non-arm DOFs заморожены. MG995 регулируется отдельно с ограничением изменения команды. Недостижимая цель отвергается без изменения мира; доступность конечной позы не объявляется глобальным планированием пути.

Для интерактивной работы используются штатные окно/клавиши Mink. Marker не имеет collision/weld/joint и находится в скрытой для sensor renderer group5. Проверка ставит его прямо перед объективом и сравнивает кадры: совпадают побайтно. Отдельный guard отвергает native viewer edits физического состояния/gravity и внешние perturbation forces; такие записи не принимаются как демонстрации. Проверены открытие/автоматическое закрытие viewer на Windows и Linux, а на Linux — одновременно viewer+LeRobot writer. Человеческая ручная запись сложного хвата ещё не предъявлена.

EnvHub получил только явный optional `terminate_on_success=False`, чтобы после успешного подъёма можно было записать опускание/release. Default `True` и прежняя семантика завершения сохранены. В continue-mode `info.is_success` — текущее событие evaluator, поэтому после release оноFalse; report отдельно фиксирует, что success был достигнут раньше. Это не подмена результата финальным положением предмета на столе.

## Физический результат и границы

Принятая CAD `E:\RoboHand\LATEST\CAD\EB300.a3d` и baseline scene SHA501e… не менялись. Сцена по-прежнему содержит Redmi8A на запястье, стол/клавиатуру/монитор/PC и свободный карандашØ7×110мм в исходной точке. Никакого weld, переноса object qpos во время эпизода, внешней силы или дополнительной policy camera нет.

Строго осевой pickup лежащего карандаша исключён текущей геометрией housing: даже расширенная optimistic contact область требует высоты оси≥18,996мм вместо3,5мм. Для поперечного хвата найдены две точные симметричные позы; зазор actual013↔стол1,5мм. Статическая Mink проверила10poses двух ветвей с максимальной position residual0,000145мм и без contacts глубже0,1мм. Это отдельно от последующих физических запусков.

Первый прямой ввод геометрических целей дал только12,23мм подъёма: nominal position actuators проседают под gravity. Следующая попытка подняла50,51мм, но дала transient pencil↔other penetration0,639мм. После **одного фиксированного уточнения operator targets** по измеренной hover pose полный цикл ниже прошёл без этого продавливания. Offset≈(+5,707,−1,063,+19,394)мм и counter-rotation2,672° относятся к одной nominal simulation setup; это не новый online gravity controller и не калибровка реальной EB300.

| Проверка полного native цикла04 | Результат |
|---|---:|
| Управляющие кадры / время | 990 /39,600s |
| Максимальный подъём относительно reset | 69,306мм |
| Максимальный непрерывный evaluator hold при lift≥20мм | 10,304s |
| Пиковое проникновение карандаша в pads | 0,029959мм |
| Пиковое проникновение в любую геометрию, на каждом2ms шаге | 0,054825мм |
| Проникновение в contacts без карандаша | 0 |
| Пиковое использование actuator force caps | 87,291% |
| Максимальный residual rack equalities | 0,026701мм |
| Финал | Губки открыты; карандаш поддерживается только столом; lift≈−0,004918мм |
| Physics warnings/time reset | Нет; EnvHub guards не сработали |

Силы/трение/массы nominal. Limits и equalities не отключались и не увеличивались ради результата. Самостоятельная смена стартового XY карандаша, распознавание, выбор grasp и клавиатурная задача этим опытом не проверены. Transverse grasp ещё не обеспечивает удобный рабочий конец для typing.

## Запись и повтор

На Linux штатный LeRobot writer сохранил **1episode/990frames**, state/action7rad, один raw wrist640×360RGB,25Hz simulation clock. Read→SimRobot API replay дал max error **0rad** и до, и после действия. Событие успешного подъёма повторилось; финальное событиеFalse соответствует законченному release. Timestamp max error1,831µs укладывается в округление float32 за40s: half-ULP bound1,917µs. Первая диагностическая проверка ошибочно требовала<1µs независимо от длительности; после исправления критерия по формату состояния/действия менять не потребовалось.

Отдельный50frame writer smoke также повторился с0rad; **штатный `lerobot-replay` CLI прошёл** на этом формате. Полный990frame native physics replay дал0rad и0m pencil error, проверил все19 800substeps и стал источником GIF. Renderer реально выполнен; кадры не синтезированы image generator.

**Это diagnostic dataset, не пилотный обучающий набор.** У ранней990frame записи task annotation сохранила исходное «Pick up the pencil and hold it above the table», хотя trace дополнительно включает place/release. На ней LoRA не запускается. Для новых записей добавлен `--instruction`; annotation должна описывать весь эпизод. Понадобятся разнообразные качественные demonstrations и независимый test set. Никакой success rate по вариациям из одного trace не оценивается.

Final contract suite: **12tests Windows4,658s и Linux17,391s**, включая marker invisibility/dynamics equivalence, no-input hold при PD sag, unreachable target без изменений мира, limits/units/non-arm freeze, continue-mode и rejection внешнего viewer assistance. Earlier11test smokes сохранены как промежуточные; final count12. Optional instruction CLI — обычные task metadata, не изменение solver.

В текущем WSL EGL сообщает `/dev/dri` permission warning и software fallback; TorchCodec не загрузил FFmpeg, библиотека использует PyAV fallback. PNG-backed dataset/read/replay и GLFW viewer работают, GPU-ускорение renderer и25Hz wall-time этим запуском не заявляются. В Linux accepted LeRobot environment добавлены только Mink/DAQP/qpsolvers, прежние package versions сохранены. Native Windows venv соответствует MuJoCo4.0.1/NumPy2.2.6/Gymnasium1.4.0; LeRobot writer в нём не установлен, запись проверялась в существующем Linux environment.

## Где лежит результат и что дальше

- Рабочая копия и GIF: `E:\RoboHand\LATEST\SIMULATION\EB300-ENVHUB`; [EB300-pencil-cycle.gif](<E:/RoboHand/LATEST/SIMULATION/EB300-ENVHUB/SHOWCASE/EB300-pencil-cycle.gif>),1280×720,127frames.
- Полный run, dataset, counters, source freezes и traces: `E:\RoboHand\runs\2026-11-18-teleop-grasp`.
- Источники/пины готовых решений: `E:\RoboHand\research\2026-11-18-teleop`.
- Recovery packet: `E:\RoboHand\releases\EB300-MINK-2026-11-18\EB300-MINK-2026-11-18.zip`, зеркало `D:\RoboHand-Backups`; SHA/manifest — в evidence/receipt. Исходные CAD/release17.11 сохраняются.

Дальше — принять удобство готового teleop на реальном ручном сеансе, собрать начальные10–20качественных demonstrations с корректными instructions и отдельные новые test poses. Затем officialπ0.5 LoRA и closed-loop evaluation.10–20 — старт пилота, не обещание достаточности данных. Если для varied starts нужен дополнительный sampling/IK/model adapter, сначала найти готовый hook и отдельно описать непокрытый gap. Одну fixed sequence не размножаем и не объявляем навыком.

Владелец18.11 уточнил: мнения из чатов не основания решений; ориентир — проверяемый международный фронтир. Переписки сохранены отдельно в private research как вопросы, а не новые technical decisions. Данная итерация основана на pinned source, выполненных smokes и собственной физической/данной проверке. Remote GPU host и физическая MCU не использовались.
