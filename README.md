# RoboHand.Simulator

**17.11: [целевой план с GR00T и Codex](<../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-17-groot-first.md>)** — gripper/свободный инструмент/данные EB300, затем проверенный релиз и адаптация общей модели. [Что обучает текущий PPO](docs/research/2026-11-17-policy-models.md); прежние результаты сохраняются как reference, отдельная PPO campaign не обязательна.

**16.11: [рабочий стол EB300 R1](docs/desktop-workcell-r1.md)** — рука слева спереди, PC справа сзади, шесть штатных приводов и10/10 заданных нажатий тестовой A обычной губкой. [Native NVIDIA recipe для шести осей](docs/research/2026-11-16-eb300-native-training.md): проверены исправленный drive/contact profile, камера и минимальные teacher/vision PPO updates; полноценный навык печати ещё не обучен. [Единственная wrist camera: крепление и полный кадр](docs/research/2026-11-16-camera-coverage.md). [Готовая практика креплений](docs/research/2026-11-16-wrist-camera-practice.md), [пробное нажатие зажатой палочкой](docs/research/2026-11-16-pregrasped-tool-preview.md).

**Рабочая CAD отдельно:** `E:\RoboHand\LATEST\CAD\EB300.a3d`; [файлы/проверка/ярлыки MuJoCo](docs/latest-artifacts.md). [URDF, суставы и сцена — понятное объяснение](docs/urdf-mujoco-explained.md). CAD владельцем просмотрена; Docker на E: и дополнительный native GPU runtime проверены.

**[Начать здесь: что готово, как открыть R8 и что делаем на этом ПК](docs/start-here-r8.md).** Для просмотра установлен MuJoCo, рабочий стол открывается отдельным ярлыком в LATEST. [Состав публичного Git и локальные assets](docs/publication-scope.md).

**Актуальная версия15.11 — [R8:7логических узлов и контакт обычной губкой](docs/cad-reviews/2026-11-15-logical-r8/root-review.md).** Стержень и его держатель удалены. Три штатные native подсборки, шесть подвижных интерфейсов,49состояний независимой сверки. [Открывать R8 / файлы / backup наE иD](docs/latest-artifacts.md). R7 ниже — предыдущая принятая версия со стержнем, сохранённая для истории.

**15.11: [подготовлен полный CAD-2 asset EB300](docs/cad-reviews/2026-11-14-cad2/root-review.md).** Исправлены rigid tube links и запястье, добавлены оснастка/Redmi8A и шесть управляемых CAD-углов. Native sweeps±5° прошли; полное URDF прошло ROS build/check_urdf, штатный MuJoCo import и независимое сравнение геометрии в25 позах. [Файлы и команда просмотра](docs/cad-reviews/2026-11-14-cad2/viewing-and-next-step.md). Массы/приводы/камера пока nominal; typing runtime/training и real hardware этим не проверены.

Предыдущие записи ниже — история этапов.

**14.11: [завершён read-only аудит первой сборки EB300](docs/cad-reviews/2026-11-14-1part-c2133b98/root-review.md).** Зафиксирован snapshot на E; прочитаны компоненты, placements и сопряжения: 18/18 root и 25/25 отдельно проверенного gripper имеют Valid=True. До robot description нужны полное запястье, rigid tube links и joint/tool/camera данные. Исходные255 файлов неизменны, собственные копии закрыты без сохранения; sweeps/physics/training ещё не выполнены.

**09.11: [задание отдельному CAD-агенту](docs/cad-agent-task.md).** Владелец собирает EB300 из STL в КОМПАС через вспомогательную геометрию; агент затем проверяет сохранённую копию и готовит robot description/meshes по [handoff](docs/cad-handoff.md). [Готовый MCP установлен и app-level connect проверен](docs/research/2026-11-09-kompas-mcp-setup.md); CAD review/импорт не выполнены. DH-таблица со скриншота включена как reference с непроверенной конвенцией/единицами.

**08.11: [виртуальная EB300 стала первым рабочим треком](docs/simulation-first.md).** CAD доступен по подтверждению владельца; physics/камеры/обучение ещё предстоит реализовать. Существующий RViz description не выдаём за физический симулятор.

> **Audit 2026-11-07:** the implemented package is `robohand_description`; a fresh Humble build and URDF generation passed. Gazebo/bringup/controllers are planned. The YAML configuration is not loaded by the current xacro. See the [documentation index](docs/index.md) and [audit](docs/research/2026-11-07-state.md).

ROS2 description, reviewed CAD-based EB300 asset, a nominal MuJoCo desktop/contact scene, and an owner-approved six-axis adaptation of the pinned NVIDIA typing recipe. Learning checks are documented separately from learned task success and real hardware execution.

## Workspace layout

```
robohand_ws/src/
  robohand_description/
    urdf/                 # CAD-2 URDF, derived MuJoCo inspection XML, historical Xacro
    meshes/eb300_cad2/     # source-based visual meshes, collision proxies, attribution
    config/               # CAD-2 numeric contract and historical approximate YAML
    launch/               # standard ROS description/RViz launch
```

## Prerequisites (WSL2 Ubuntu 22.04)

See [docs/wsl-ros2-setup.md](docs/wsl-ros2-setup.md).

## Quick start (after ROS 2 Humble is installed)

```bash
cd '/mnt/d/ПРОЕКТЫ/_ЛИЧНОЕ_/ВОПЛОЩЕННЫЙ_ЭЙАЙ/РОБОРУКА/RoboHand/RoboHand.Simulator/robohand_ws'
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select robohand_description --symlink-install
source install/setup.bash
ros2 launch robohand_description display.launch.py
```

## Model data

The display launch defaults to `urdf/eb300_jaw_typing_r8.urdf`; frame/mass provenance is in `config/eb300_jaw_typing_r8_contract.json`. See [current artifacts and recovery](docs/latest-artifacts.md). `urdf/eb300_jaw_typing_r8.validation.xml` opens in the stock MuJoCo viewer. R8 uses an existing jaw corner, with no stylus/holder. The `eb300_cad2.*` files retain the historical R7 profile.

The older `robohand.urdf.xacro` is an approximate historical model. Its `config_file` argument does not load the YAML; editing `kine_eb300_approx.yaml` alone does not change that Xacro. It is not the reviewed CAD-2 asset.

## Phases

1. **Verified:** CAD-based six-joint asset, frame checks, ROS description and nominal MuJoCo import/inspection.
2. **Next:** Pinned NVIDIA typing runtime/GPU smoke and supported EB300 action/actuator/task configuration path.
3. **Then:** Physical keyboard scene, PPO teacher and wrist vision student; hardware calibration/transfer remains a separate stage.
