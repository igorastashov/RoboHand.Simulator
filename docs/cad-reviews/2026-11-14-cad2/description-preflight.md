---
tags: [robohand, eb300, cad, urdf, frames, validation]
type: verification-preflight
updated: 2026-11-15
status: preflight-completed-full-asset-verified
---

# Штатный путь описания и проверки после CAD-2

[Задание](task.md) · [Индекс](../../index.md).

**Результат15.11:** штатный путь применён к полной EB300, [проверки и принятые файлы](root-review.md), [команда просмотра](viewing-and-next-step.md). Ниже сохранён preflight до CAD-2; фраза о ещё не созданном URDF относится к началу прохода.

Root проверил read-only: WSL `Ubuntu-22.04` видит рабочий E-каталог через `/mnt/e/RoboHand/data/cad-work/2026-11-14-eb300-c2133b98`. В окружении `/opt/ros/humble` уже доступны:

| Инструмент | Фактический пакет/версия |
|---|---|
| `/opt/ros/humble/bin/xacro` | `ros-humble-xacro 2.1.1-1jammy.20260304.195513` |
| `/opt/ros/humble/bin/check_urdf` | `ros-humble-urdfdom 3.0.2-2jammy.20260304.202852` |

`dpkg-query -S /opt/ros/humble/bin/check_urdf` подтвердил owning package. Запрос `liburdfdom-tools` ничего не нашёл, но нужный бинарник установлен из ROS-пакета; это не отсутствие validator. Новых ROS-пакетов не устанавливалось. Сам CAD-2 URDF ещё не создан/проверен, старый approximate description не выдаётся за него.

## Применяемый стандартный образец

- ROS [REP103](https://raw.githubusercontent.com/ros-infrastructure/rep/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0103.rst), inspected HEAD `11ca24a41f31480dfb9562ba99f2a5b93d3ebda5`: SI, right-handed body frame, optical frame +Z forward/+X right/+Y down. Primary ros.org page заблокировала автоматическое чтение; прочитан официальный GitHub mirror.
- ROS [urdf_tutorial/07-physics.urdf](https://github.com/ros/urdf_tutorial/blob/050f1e47cfdb2c5f3eb0746bc15c57e6a870faef/urdf/07-physics.urdf), inspected ros2 branch `050f1e47cfdb2c5f3eb0746bc15c57e6a870faef`: стандартные link/joint/visual/collision/inertial поля, mesh URI и limits. Это образец формата, его примерные массы/размеры не относятся к EB300.
- В нашем existing `robohand_description` сохраняется пакет и стандартный Xacro/URDF workflow. Новый exporter/runtime не нужен для заполнения данных конкретной руки.
- [MuJoCo Python/модель editing](https://mujoco.readthedocs.io/en/stable/python.html), [XML camera reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera), [Trimesh quick start](https://trimesh.org/quick_start.html): штатные URDF loader, MjSpec serializer, viewer/renderer и mesh normal repair/convex hull. Установлены `mujoco-core[rendering]==4.0.1`, `trimesh==5.2.1`; [полный requirements lock с hashes](validation-requirements.lock), [минимальные smokes](validator-smoke.json).

## Данные, ожидаемые от CAD-итераций

Согласованная reference pose; семь rigid arm links, шесть arm joints; для каждого joint — parent/child, point/axis и rotation в объявленном frame, zero/sign/nominal demo range; отдельные tool/TCP/camera frames; part-local mesh transforms и units. Исходные STL можно использовать без изменения вершин, задавая `<visual><origin>` и явный scale. CAD component origin автоматически не равен joint origin.

Штатный SDK `IMateConstraint3D.GetMateParams` возвращает параметры геометрии сопряжения в СК сборки: Pc(3), V(3), radii(2). Использовать actual identity/контекст и обе стороны, затем согласованно переводить frames. `Fixed` у mate — enum выбора фиксируемого компонента, не lock rotation.

Сначала генерируется и проверяется **один фактический joint/link** выбранной CAD-ревизии, затем вся цепь. Структурный `check_urdf` дополняется проверкой разрешения meshes, численной согласованностью поз с CAD и корректными positive mass/inertia estimates. Он сам не доказывает collisions, динамику привода или sim-to-real readiness.
