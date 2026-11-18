---
tags: [eb300, envhub, simulation, interface, reuse-first]
updated: 2026-11-18
---

# EB300 EnvHub

**Последняя итерация18.11:** [dataset/официальный LoRA pilot/evaluation](../../docs/research/2026-11-18-pilot-and-lora.md) выполнены:11train/4validation episodes,1000updates, exact80tensor reload. Base и LoRA обе0/4validation и0/3valid stress; trained grasp не принят. Успешные fixed-input движения ниже — экспертные показы. Контроллер/геометрия не менялись; добавлены только read-only physics quality peaks и13-я contract test.

**18.11:** отдельно разрешён и проверен [Mink teleop binding](../../docs/research/2026-11-18-mink-execution.md). Он лежит в `teleop_mink.py`; исходный EnvHub ниже по-прежнему не содержит IK внутри environment. Полный990frame pickup/hold/place/release повторён с0rad ошибки. Это fixed operator inputs, не learned policy.

## Mink: готовое окно и запись

Дополнительные [requirements](requirements-teleop.txt) фиксируют Mink5f800f0/DAQP/qpsolvers. Baseline `assets/eb300_envhub_scene.xml` сохранена; `assets/eb300_mink_teleop.xml` включает её и добавляет только viewer target group5. Восстановить локальные meshes необходимо, как описано ниже.

На этом ПК native viewer уже проверен. PowerShell:

```powershell
$eb300Session = Get-Date -Format 'yyyyMMdd-HHmmss'
& 'E:\RoboHand\tools\mink-1.4.0-2026-11-18\.venv\Scripts\python.exe' `
  'E:\RoboHand\LATEST\SIMULATION\EB300-ENVHUB\envhub\teleop_mink.py' `
  --continue-after-success --no-shadows --steps 10000 `
  --output "E:\RoboHand\runs\manual-eb300-$eb300Session"
```

`9` включает готовый Mink keyboard teleop; стрелки — localX/Y цели, `6/7` — localZ, `.` переключает rotation, `-/+` меняют шаг. Upstream manual step по умолчанию10мм/10°: для точного подвода уменьшать шаг; `n` переключает continuous mode. `[` закрывает, `]` открывает MG995. Native viewer camera/target — помощь оператору; model input только полный wrist frame. Физические body perturbations/редактирование gravity и states запрещены guard; неудачный run не принимается в обучение. Закрытие окна завершает сеанс и report. Это не autonomous visual grasp.

Исходный `mink-1.4.0` native venv не содержит LeRobot writer. В новой итерации18.11 отдельно установлен `E:\RoboHand\tools\lerobot-record-win-2026-11-18\.venv` с официальным `lerobot[dataset]`: native Windows headless запись всего11train/4validation pilot проверена. Совместный ручной GUI+writer сеанс в этом новом Windows venv ещё не оценён. Ранее проверенная комбинация viewer+writer использует Linux окружение/WSLg на том же ПК (не remote server), из runtime directory:

```bash
MUJOCO_GL=glfw /var/tmp/robohand-pi05-7910c20-2026-11-17/.venv/bin/python \
  teleop_mink.py --record --continue-after-success --no-shadows --steps 10000 \
  --instruction "Pick up the pencil, hold it above the table, then put it back down and release it." \
  --output /mnt/e/RoboHand/runs/manual-eb300-UNIQUE-NAME
```

Выбрать новый output path: существующие папки не перезаписываются. Writer не загружает данные в Hub. Проверены viewer+writer5frame smoke,50frame diagnostic и полный990frame headless record/API replay; ручная операторская демонстрация сложного хвата ещё не оценена. `--instruction` должна соответствовать всему записанному действию. Reports имеют `learned_policy=false`; при `--continue-after-success` `task_success` означает, что evaluator достигал цели раньше, а последнее `info.is_success` после releaseFalse.

Воспроизводимый physics diagnostic, **не сбор varied training demonstrations**:

```bash
python teleop_mink.py --headless --continue-after-success --no-shadows --steps 1200 \
  --targets assets/mink-pencil-diagnostic-targets.json \
  --instruction "Pick up the pencil, hold it above the table, then put it back down and release it." \
  --output /path/to/a/NEW-run
```

Семь абсолютных углов вrad, прежние torque caps,25Hz simulation clock/2ms. Fixed targets рассчитаны для исходной pencil pose и одного nominal actuator profile, включая фиксированное уточнение по hover. Это не universal grasp planner или real calibration. Collision limit учитывает robot↔obstacles; глобальная self-collision-free траектория не гарантируется. Deep runtime contacts прекращают запись, а всеquality metrics проверяются отдельно. Для benchmark success/rate нужны новые starts/test set.

Разрешённая владельцем минимальная адаптация готового EnvHub к EB300. Штатные LeRobot SimRobot, dataset writer, replay, model factory и transport используются без fork. Сам environment не содержит IK/teleoperator/motor policy; отдельно разрешённый Mink binding описан выше. Собственный UI/training framework не создавался.

Source pins: `huggingface/lerobot@7910c20a75834ad3fa6a9792df4d44a614d1bba6` и [исходный EnvHub](https://huggingface.co/lerobot/so101-tabletop-mujoco/tree/e68145d8bd793c27fa2c13e31369a616895c5acb) `e68145d8bd793c27fa2c13e31369a616895c5acb`. Сохранён Apache-2.0 header/[LICENSE](LICENSE). Simulator requirements находятся в [requirements.txt](requirements.txt); LeRobot policy/data dependencies устанавливаются отдельно. Механика взята из CAD нашей EB300/EBG20.

## Модель и интерфейс

- [Scene](assets/eb300_envhub_scene.xml), [численный contract](assets/robot-contract.json): стол, монитор, клавиатура, PC справа, рука слева, свободный карандаш.
- State/action: `J1.pos`…`J6.pos`, `MG995.pos` — **семь абсолютных углов в rad**. Пределы — nominal simulation limits, не real calibration. Две rack slides — внутренняя механика, не дополнительные действия.
- Policy input: `agent_pos[7]`, `pixels.wrist[360,640,3]` uint8. SimRobot преобразует их в `observation.state` и `observation.images.wrist`. Только основная wrist Redmi8A, полный16:9кадр; нет zoom/ROI/кропов/внешней policy camera. Размер для тестов можно уменьшать, сохраняя16:9. PI05 использует свой штатный full-frame resize/padding.
- `fps=25`, timestep0.002s,20physics steps/action. `reset(seed=...)` восстанавливает согласованный `envhub_ready`; randomization пока не реализована. Нулевой вектор не является удержанием: использовать `home_action` из contract.
- Формат LeRobot semantics `eb300-joint-radians-v1`, `robot_type=eb300`. Фактические углы под gravity не обязаны совпадать с position targets.
- Evaluator видит привилегированную pose только для проверки двух рабочих pad contacts, подъёма≥20mm и удержания≥0.5s без поддержки столом. Она не входит в observation. Subject — free joint, запрещены weld/mocap; `info.metrics` сохраняет penetration/equality peaks на каждом шаге. Окончание — success или episode limit.

Неверные shapes/NaN/Inf отклоняются до движения. Конечные targets ограничиваются штатными actuator ranges; `info.action_clipped` сообщает ограничение. MuJoCo warning, nonfinite state или time reset прекращают rollout с ошибкой. Работа с физической MCU этим не разрешается/не проверяется.

## Локальные assets

**Чистый Git clone без private geometry не запустит scene.** В репозитории нет34STL с лицензионными ограничениями. Восстановить `assets/meshes` из локального bundle `E:\RoboHand\runs\2026-11-17-eb300-envhub\assets` либо пакета `EB300-ENVHUB-2026-11-17`; сверить mesh manifest. Подробности [публикации](../../docs/publication-scope.md). Точная принятая CAD `E:\RoboHand\LATEST\CAD\EB300.a3d` сохранена.

Для текущего ПК создан отдельный runtime copy `E:\RoboHand\LATEST\SIMULATION\EB300-ENVHUB\envhub`, рядом — настоящий server config/команды и GIF. Это copy версионированного adapter/data плюс локальные meshes, не ещё один framework. Основные файлы/резервные копии наE/D; ограниченный native Linux cache `/var/tmp/robohand-pi05-7910c20-2026-11-17` находится в существующем Ubuntu VHD наC.

## Штатный запуск

В Python≥3.12 с указанным pinned LeRobot и `requirements.txt`, из каталога, содержащего `env.py`:

```bash
python -m unittest discover -s tests -v
```

Локальный API, по штатному LeRobot tutorial:

```python
from lerobot.envs.configs import HubEnvConfig
from lerobot.robots.sim_robot import SimRobot, SimRobotConfig

robot = SimRobot(SimRobotConfig(env=HubEnvConfig(
    hub_path="./envhub", trust_remote_code=True,
)))
robot.connect()
try:
    observation = robot.get_observation()
    # Передавать только осмысленные seven-joint position targets из contract/data.
finally:
    robot.disconnect()
```

Локальный policy runtime проверен в WSL2: один полный кадр EB300+текст+state → PI05 actions → три ограниченных sim steps. Это проверка interface, не zero-shot grasp: нормализация взята из диагностического50-frame dataset, несколько axes там постоянны. Для реального навыка нужны качественные task demonstrations и новые statistics; не обучать policy на interface smoke.

## Симулятор Windows и клиент WSL

По [официальному simulation workflow](https://huggingface.co/docs/lerobot/simulation) environment можно обслуживать отдельно от policy. Использован тот же pinned `lerobot-env-server`; torch-free набор взят **из его `docker/sim/requirements.txt`**, затем LeRobot установлен `--no-deps` в отдельное Windows-окружение. Это штатный server вне Docker, не новый transport. На текущем ПК: `E:\RoboHand\tools\envhub-server-win-2026-11-17\.venv`; версия/Python/source/полный freeze — в evidence packet. Само отсутствие Torch проверяется в этом окружении.

Windows server, из runtime copy root:

```powershell
& 'E:\RoboHand\tools\envhub-server-win-2026-11-17\.venv\Scripts\lerobot-env-server.exe' --config_path=server-win.yaml
```

`server-win.yaml` в локальном пакете использует `envhub: ./envhub`, `trust_remote_code: true`, `max_envs: 1`, `max_sessions: 1`, `sim.kwargs.make_env_kwargs: {episode_length: 80, render_shadows: false}`. Listener привязан только к IPv4 виртуального Windows/WSL adapter. Он может измениться после перезапуска: текущий gateway показывает `wsl -d Ubuntu-22.04 -- ip route show default`. Не открывать listener на всех сетевых интерфейсах. Firewall/drivers не менялись. После сессии server останавливается Ctrl+C; persistent service не устанавливается.

Клиентский штатный CLI (подставить gateway и путь к dataset):

```bash
lerobot-replay \
  --robot.type=sim --robot.env.type=envhub --robot.env.hub_path=./envhub \
  --robot.env.server.endpoint=tcp/<WSL_GATEWAY>:7448 \
  --robot.env.make_env_kwargs='{"episode_length":80,"render_shadows":false}' \
  --dataset.repo_id=local/eb300-interface-smoke --dataset.root=<DATASET_ROOT> \
  --dataset.episode=0 --dataset.fps=25 --play_sounds=false
```

Client и server должны указывать одинаковые hub_path и make_env_kwargs. Полный RGB передаётся в stock `raw` encoding; JPEG не использовался. `render_shadows=false` выключает только стандартный raster shadow flag, не contact physics, FOV, mount или кадр. Default adapter оставляет тени включёнными; GIF снят с тенями. Эта визуальная настройка должна оставаться частью dataset/runtime provenance.

На этом ПК WSL с тенями дал5.40Hz, native Windows server без теней —24.86Hz в50-tick CLI run при целевых25Hz;1/49judged ticks превысил40ms. Это короткая измеренная cadence, **не hard-real-time гарантия**. Native Windows OpenGL в этом запуске выбрал Intel UHD750; RTX3090 использовалась для PI05. WSL-render также отдельно проверен на RTX3090 через штатный Mesa adapter setting, но оказался медленнее.

## Запись и границы следующего этапа

**Обновление18.11:** нижеследующий50frame smoke — история интерфейса. После отдельно разрешённого [Mink binding](../../docs/research/2026-11-18-eb300-teleop-adaptation.md) выполнен [полный fixed-target цикл](../../docs/research/2026-11-18-mink-execution.md), затем собран [новый пилот11train/4validation episodes и запущен официальный LoRA workflow](../../docs/research/2026-11-18-pilot-and-lora.md). В train используются только новые качественные pickup/hold записи;50/990diagnostics исключены. Новые read-only substep peaks `max_non_tool_penetration_m` и `max_force_cap_fraction` нужны для контроля качества; reward/termination/controller не меняют.

Штатными `LeRobotDataset.create/add_frame/save_episode/finalize` и `build_dataset_frame` записан1episode/50frames, затем он прочитан и повторён через SimRobot: max joint replay error0, timestamp error≈5.72e−8s. Изображения сохранялись как image-backed dataset; streaming video не проверялось. Повторён и штатный `lerobot-replay` CLI. Это diagnostic joint motion, не human/grasp demonstrations и не training campaign.

`lerobot-record` требует совместимый teleoperator. Готового seven-joint EB300 teleoperator в проверенном source не найдено; generic keyboard/другая leader arm не объявляются совместимыми автоматически. Следующий reuse-first шаг — выбрать готовый способ показа grasp demonstrations, проверить именно успешные free-object contact/lift/hold эпизоды, затем сделать официальный PI05 LoRA pilot. Новый teleop controller/IK/UI данным scope не создавался.

Изображения/GIF, dataset, полные traces и локальные scripts сохраняются вне публичного Git. [Разрешённый scope](../../docs/research/2026-11-17-eb300-envhub-adaptation.md), [данные CAD-агента](../../docs/cad-reviews/2026-11-17-eb300-envhub/agent-report.md), [индекс](../../docs/index.md).
