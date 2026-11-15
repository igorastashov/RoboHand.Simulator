---
tags: [robohand, simulator, workcell, redmi8a, scene, jaw-typing]
type: design
updated: 2026-11-15
status: cad-asset-ready-keyboard-scene-pending
---

# Сцена рабочего стола EB300

**Курс15.11:** [R8](cad-reviews/2026-11-15-logical-r8/task.md) использует универсальный EBG20 и реальную кромку губки; стержень/держатель удаляются из активного CAD/URDF/MJCF profile. CAD/inspection asset уже есть, но keyboard task scene/actuators/training ещё не приняты. Сначала штатный runtime/GPU smoke pinned NVIDIA typing recipe, затем EB300 robot/contact/6-action configuration.

[Индекс](index.md) · [Первый sim backend](simulation-first.md) · [Полный pipeline](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/virtual-workcell-pipeline.md>).

## Состав asset

Для первого навыка: стол/опоры, EB300/J1–J6, штатный захват с выбранным jaw contact frame, Redmi8A/mount, физические клавиши клавиатуры, lighting и optical frame. Источник robot geometry — CAD/STL владельца; keyboard/task assets — выбранный upstream recipe. Геометрия/units/limits и physical parameters versioned; mass/inertia estimates не выдаются за измерение.

Концевики физически есть со слов владельца; симулируемые limits/homing/reset не доказывают готовность соответствующей прошивки.

## Сенсоры

Подтверждён Redmi 8A на запястье: virtual RGB камера жёстко связана с wrist frame через mount transform. FOV/resolution/distortion до калибровки отмечены estimated, а не «точная копия камеры».

Масса телефона (номинально 188 г по Xiaomi) плюс mount/COM входят в динамику руки; фактический комплект взвесить. Положение камеры следует FK. Добавить обзорную позу/сканирование, проверку видимости при захвате и routing кабеля.

Virtual accelerometer можно добавить как отдельный канал, если он используется; не включать gyro в deployable observations без подтверждения: в спецификации Redmi 8A он не указан. Датчики телефона не заменяют joints. [Профиль Redmi 8A](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/camera-profile.md>).

## Выход к Control

RGB + camera metadata/time, q/dq/gripper, sim time/reset seed и статусы. Ground-truth object poses/depth/segmentation отдельно, для teacher/evaluator; не подмешивать в learned policy, предназначенную для real RGB.

## Приёмка

Нужны: стол/клавиатура, CAD-correct EB300, управляемое нажатие и отпускание выбранной клавиши кромкой губки, отсутствие лишних нажатий и10воспроизводимых resets. Отдельно operator view и wrist view. Обычный захват пока в captured opening; изменение его раскрытия требует реальной кинематики/actuator configuration, а не фиктивной URDFmimic модели.

Официальный workflow выбранного reference: PPO state teacher → wrist vision student → eval; ACT не подставляется вместо него. Контактную геометрию/normal/friction и доступную ориентацию губки проверить вместе с расширением nominal simulation limits. Current±5°demo ranges недостаточны как готовая keyboard workspace. Нажатие/force изphysics иRGBvisuals — отдельные наблюдаемые величины; success не назначается только по достижениюTCP.

В R8 inspection camera выбранный угол губки находится в nominalFOV, но точная front corner частично закрыта боковиной самой губки. [Camera/frustum/ray evidence](cad-reviews/2026-11-15-logical-r8/r8-import-camera-check.json). Это известная окклюзия; необходимость переноса камеры или использования других видимых признаков оценивается на keyboard scene, а не замалчивается перед vision training. Полное открытие клавиши/губки во всех позах не подтверждено.
