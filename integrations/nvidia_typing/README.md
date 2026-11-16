# EB300 в существующем NVIDIA typing recipe

Владелец 16.11.2026 явно разрешил [этот ограниченный объём адаптации](../../docs/research/2026-11-16-eb300-training-adaptation.md). Основа — `NVIDIA/so101-typing-task@7aec2ed26dce8c88ae007a2714680cce572e1466`. `eb300.patch` применяется к отдельному checkout; принятый исходный reference не изменяется.

Патч добавляет стандартную конфигурацию EB300, явный `robot: eb300` в task JSON, размер действия environment в teacher loader и configurable controlled joints в существующий typing command. Штатный camera smoke также использует размер environment. Фиксированное раскрытие R8 не превращается в вымышленный gripper actuator: SO-101-specific gripper reset для EB300 отключён.

Renderer остаётся существующим NVIDIA compatibility adapter для OVRTX 0.5. Для явно названной `RedmiCamera` используется авторская standard USD pinhole projection без Workshop OpenCV calibration. Наличие Workshop intrinsics продолжает строго проверяться для исходной камеры SO-101. Реальная калибровка Redmi этим не выполнена.

`eb300_profile.py` и `Dockerfile` рядом показаны отдельно для ревью; такие же версии включены в patch. Физическая прошивка, serial transport, новый RL-алгоритм, renderer class, UI и framework не добавляются. Акторы и critic создаются существующим RSL-RL; метод остаётся PPO teacher → vision.

## Воспроизведение

Нужны Linux runtime, собранный по [официальному setup этого pin](https://github.com/NVIDIA/so101-typing-task/blob/7aec2ed26dce8c88ae007a2714680cce572e1466/docs/setup.md), POSIX checkout с сохранёнными symlinks и локальный лицензированный USD-комплект EB300. Docker overlay использует существующий runtime, не устанавливает пакеты на хост и не заменяет исходный image tag.

```bash
git clone https://github.com/NVIDIA/so101-typing-task.git eb300-typing
cd eb300-typing
git checkout --detach 7aec2ed26dce8c88ae007a2714680cce572e1466
git apply --check /path/to/RoboHand.Simulator/integrations/nvidia_typing/eb300.patch
git apply /path/to/RoboHand.Simulator/integrations/nvidia_typing/eb300.patch
```

После вычисления `so101.source_fingerprint()` на этом POSIX tree — штатный Docker build:

```bash
docker build -f docker/eb300-overlay.Dockerfile \
  --build-arg BASE_IMAGE=so101-tutorial:dev \
  --build-arg SOURCE_SHA256=ACTUAL_POSIX_SOURCE_FINGERPRINT \
  --build-arg ADAPTATION_SHA256=ACTUAL_PATCH_SHA256 \
  -t robohand/typing-eb300:LOCAL_REVISION .
```

Для запуска используются существующие `scripts/tutorial/cli.py:docker()` и готовые scripts, с read-only bind лицензированных assets в `/eb300`. По умолчанию ожидается `/eb300/usd-robot-ascii/eb300_welded_contacts.usda`; путь можно указать `EB300_USD` внутри контейнера. CPU/RAM limits задаются **при создании** контейнера. `docker update` работающих GPU containers не применяется.

### Asset для обучения

Локальная viewer scene содержит position actuators и рассчитана на MuJoCo. Для native import используется отдельное стандартное описание [eb300_jaw_typing_r8.native-contact.xml](../../robohand_ws/src/robohand_description/urdf/eb300_jaw_typing_r8.native-contact.xml). Оно содержит ту же геометрию/инерции, явные исключения контактов жёстко соединённых деталей и **не содержит MuJoCo actuators**. Принятые CAD/URDF/локальная desktop R1 этим не заменяются.

1. Штатным `mujoco_usd_converter --no-openpbr INPUT.xml ASSET_ROOT/usd-robot-ascii` из закреплённой версии0.9.0 экспортировать native-contact XML вместе с локальными meshes. При кириллице использовать проверенную ASCII-копию, как описано в [desktop guide](../../docs/desktop-workcell-r1.md).
2. Скопировать [eb300_welded_contacts.usda](eb300_welded_contacts.usda) рядом с полученным `eb300_r8_native_contact_r2.usda`. Это стандартный USD composition layer: явный defaultPrim, пять collider filter pairs и шесть обычных angular `PhysicsDriveAPI` с номинальными stiffness/damping/force limits. Собственного exporter или SDK patch нет. Стартовые targetPosition записаны в градусах, параметры Isaac Lab — в его стандартных единицах.
3. Монтировать `ASSET_ROOT` read-only в `/eb300`. Не использовать прежний USD с локальными MjcActuator prims: в проверенном native runtime он давал два набора приводов, а не шесть. Полное удаление actuator data без корректного стандартного drive config также не является рабочим импортом.

Newton этого runtime читает `physics:filteredPairs` на collider prims. Исключений на body prims, полученных converter из MJCF `<exclude>`, недостаточно. В слое перечислены ровно пять пар collider между телефоном, его жёстким рычагом и опорной пластиной/стойкой. Самостолкновения подвижных звеньев и контакты с клавиатурой/столом этим не отключаются. Параметры штатных приводов остаются номинальными данными; реальная калибровка отсутствует.

### Вызов готового launcher

Пример вызова существующей функции upstream без нового runner. Сначала создать `output` от имени пользователя, чтобы Docker не создал её с владельцем root. Пути и image tag заменить на свои проверенные значения:

```python
from pathlib import Path
from scripts.tutorial.cli import ROOT, docker, execute

(ROOT / 'output').mkdir(exist_ok=True)
assets = Path('/absolute/path/to/owner-assets').resolve()
command = docker('0', 'robohand/typing-eb300:LOCAL_REVISION',
    'scripts/tutorial/runtime.py', [
        '--mode', 'train-teacher', '--headless',
        '--config', '/repo/configs/tutorial/eb300-smoke.json',
        '--task-config', '/repo/configs/tasks/eb300-r8.json',
        '--output', '/repo/output/eb300-teacher-smoke'])
command[2:2] = ['--cpus', '8', '--memory', '48g', '--memory-swap', '48g',
    '--mount', f'type=bind,source={assets},target=/eb300,readonly']
execute(command)
```

Для camera/replay следовать штатному host/runtime setup и доступности NVIDIA driver resources. В проверенных запусках использовались отдельные writable Warp caches и read-only bind уже установленного `nvoptix.bin`; пакеты/драйверы хоста этим overlay не менялись. Точные команды и полные журналы сохранены локально, без внутренних адресов в публичном Git.

Task data — `configs/tasks/eb300-r8.json`, smoke preset — `configs/tutorial/eb300-smoke.json`. Существующий teacher entrypoint: `scripts/tutorial/runtime.py --mode train-teacher`; camera smoke: `scripts/vision/smoke.py`; vision: `scripts/vision/train_simple.py`. Все штатные flags/config/checkpoint/evaluation сохраняются. Дополнительный asset mount не подменяется наличием описания в README: geometry/USD/weights не распространяются в публичном Git.

## Текущая граница проверки

Локальная MuJoCo сцена отдельно [проверена](../../docs/desktop-workcell-r1.md). [Итоговый native r6](../../docs/research/2026-11-16-eb300-native-training.md):6actions/6arm drives,100stable control steps, camera/reset,2teacher updates,1vision warmup +2PPOupdates, teacher evaluation и2vision episodes по25шагов с USD/MP4 replay. Unit exits и checkpoints проверены; clip26frames1920×1080 полностью декодирован. В evaluation0набранных символов/0%успеха: это работающая минимальная цепочка, не выученная печать.

`export_actor.py` и hardware/deployment routes upstream всё ещё содержат SO-101-specific размеры и не приняты для EB300. Минимальные checkpoints не подключаются к физическому экземпляру и не являются готовыми skill weights.

Первый training scaffold использует координаты основания и собственную начальную позу EB300. Это не обещание универсальной работы с любой точки стола. Перенос мирового mount transform, доступность клавиш, контакты, camera и generalization принимаются отдельно. Все actuator/rate/optics значения пока nominal simulation configuration.
