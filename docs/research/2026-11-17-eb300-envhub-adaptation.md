---
tags: [eb300, lerobot, envhub, simrobot, reuse-first, decision]
type: bounded-adaptation-proposal
updated: 2026-11-17
status: stock-reference-smoke-passed-eb300-adapter-awaits-owner-decision
---

# EB300: готовый LeRobot runtime и точный integration gap

После [проверенного π0.5 LoRA update/reload](2026-11-17-pi05-tokenizer-lora.md) нужен путь от нашей физической scene к штатным record/replay/rollout. Готовые транспорт, recorder и policy runner есть в LeRobot. Готовая конфигурация EB300 для этого пути не найдена; новый исполняемый adapter пока не написан.

## Проверенный готовый путь

Прочитаны actual source и requirements:

- `huggingface/lerobot@7910c20a75834ad3fa6a9792df4d44a614d1bba6`: `docs/source/simulation.mdx`, `envhub.mdx`, `src/lerobot/robots/sim_robot`, EnvHub implementation. [Simulation](https://huggingface.co/docs/lerobot/simulation), [EnvHub](https://huggingface.co/docs/lerobot/envhub).
- `lerobot/so101-tabletop-mujoco@e68145d8bd793c27fa2c13e31369a616895c5acb`: прочитаны `env.py`, README, requirements; скачаны все30source/asset files. [Pinned reference](https://huggingface.co/lerobot/so101-tabletop-mujoco/tree/e68145d8bd793c27fa2c13e31369a616895c5acb). Apache-2.0 header и вложенные attribution/license сохраняются.
- Reference requirements: `mujoco==3.3.7`, Gymnasium, NumPy, Hugging Face Hub. Отдельное Windows-окружение `E:\RoboHand\tools\envhub-mujoco-3.3.7\.venv`: Python3.12.10, MuJoCo3.3.7, Gymnasium1.4.0, NumPy2.2.6, Hub2.4.0. CAD/physics environment MuJoCo4.0.1 не изменялось.

**Штатный минимальный smoke выполнен:** неизменённый `SO101Env`, reset(seed=0),16шагов с HOME, rendering одного полного wrist image480×640×3; state/action6, все значения finite, warnings отсутствуют. Reward0, успех задачи false. Проверены load/step/render reference, **не EB300, не policy и не env-server transport**. Сырые source/hash/requirements, команды и `stock-smoke.json` лежат в `E:\RoboHand\research\2026-11-17-lerobot-sim-path`.

[Числовая сводка source/smoke](../../evidence/2026-11-17-lerobot-sim-path.json) сохраняет первоначальный source-only audit отдельно от последующего выполнения.

У LeRobot уже есть `--robot.type=sim` (SimRobot), `lerobot-record`, `lerobot-replay`, `lerobot-rollout`, `lerobot-eval`, `lerobot-env-server`. Environment можно обслуживать отдельно от policy, сохраняя разные dependencies. Собственный recorder/transport/UI/framework не требуется. Старые LeIsaac/Arena tutorials в inspected source помечены Deprecated; их не устанавливаем как будто это подтверждённый современный EB300 путь.

## Почему недостаточно заменить XML

Reference `env.py` жёстко задаёт пять arm joints плюс gripper, degree/0–100 semantics, загрузку Menagerie SO101 и success evaluator четырёх кубиков. Constructor позволяет менять scene/cameras/home/FOV, но не делает joint list, units и robot loader универсальными. У EB300 шесть arm axes плюс MG995, то есть семь независимых position targets. Две рейки EBG20 связаны с одним сервоприводом и не являются двумя дополнительными policy actions.

Одинаковая длина7у LIBERO action и будущей EB300 action не означает одинаковые единицы/семантику. Reference LoRA smoke не переносит навык и не определяет этот mapping.

## Конкретный предлагаемый объём

Отдельное решение запрашивается **только на минимальный EnvHub adapter EB300**, производный от указанного `env.py`, в `integrations/lerobot_envhub/`:

1. Один environment implementation с обычными `reset/step/render/close` и metadata hooks штатного EnvHub; README, requirements и стандартные scene/config data рядом. LeRobot core, recorder, transport, trainer и PI05 architecture не менять.
2. Загружать отдельную EB300 scene с принятым контактным кандидатом EBG20. Исключить диагностическую вертикальную fixture axis: policy управляет только J1–J6 и MG995. Существующую LATEST CAD не менять. Для EB300 сохранить проверяемую MuJoCo4.0.1 physics configuration в изолированном окружении; совместимость с EnvHub проверять отдельно, не выдавать smoke3.3.7 за неё.
3. Явный ordered contract: шесть joint position targets в rad, затем nominal MG995 shaft target в rad; state в тех же единицах. Реальные servo limits/zero пока не откалиброваны. Использовать штатные MuJoCo position actuators и их ограничители; новый motor controller/IK/trajectory planner не писать.
4. Только одна wrist RGB camera Redmi8A, полный кадр, HWC uint8. Сохранить выбранное крепление `h120_b0_s-160_a20`; разрешён model resize/padding полного кадра. Без crop/zoom/дубликатов камер. Для policy — image, proprioception и текст; свободный предмет/poses доступны только физике и evaluator.
5. Заменить cube evaluator на ограниченную проверку контакта двух губок со свободным инструментом, подъёма и удержания. Привилегированную object pose не отдавать policy. Это evaluator, а не scripted grasp policy. Подбор предмета, fine-tuning campaign и keyboard task входят в следующие этапы после проверки interface.

## Приёмка разрешённой адаптации

- Семь действий и states имеют одинаковые имена/порядок/единицы; перепутанные shapes и нечисловые значения отклоняются. Две rack joints являются внутренней механикой.
- Reset воспроизводим по seed, timestep/frame timestamps согласованы; один полный wrist frame рендерится. No-action hold конечен, без QACC warning/time reset и начальных самопересечений.
- Reference remains separately labelled. На EB300 штатные SimRobot/EnvHub создаются без собственных fork framework/runner; выполняется короткий record/replay smoke. Если для teleop нужен новый controller, предъявить отдельный gap, не прятать его в adapter.
- Physical evaluator не засчитывает предмет, который fixed/welded/teleported или касается только стола. Измерения solver residual, pad/floor penetration и номинальные параметры остаются видимыми.
- Только после этого возможен короткий bounded base-policy rollout и сбор demonstrаtions. Случайные finite действия не объявляются навыком, один reference optimizer step не объявляется EB300 training.

Альтернатива — пока сохранить только standard scene и отложить data/rollout bridge; или дождаться upstream generic joint/asset configuration. Замена EB300 на SO101 не рассматривается. Isaac migration не устраняет action/robot-definition gap сама по себе.

## Основание отдельного решения

В [reuse-first-policy.md, §7](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/reuse-first-policy.md>) прямо сказано: «Не начинать собственный exporter, MCP-server, orchestration framework, UI или robot adapter без отдельного решения владельца». Root AGENTS.md§3 также запрещает новый исполняемый код при таком gap без отдельного решения. Ранее разрешённая шестимерная NVIDIA/PPO adaptation относится к другому scoped изменению и этот adapter не разрешает.

До решения разрешённые CAD/MJCF data, диагностика, LoRA reference, documentation и backup продолжаются. Этот документ не является согласием и не утверждает, что adapter уже реализован.

[Индекс](../index.md), [план](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-17-foundation-lora.md>).
