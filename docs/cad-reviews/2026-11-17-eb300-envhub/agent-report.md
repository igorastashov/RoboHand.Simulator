---
tags: [eb300, ebg20, envhub, mujoco, scene, camera]
type: model-data-integration-report
updated: 2026-11-17
status: full-scene-data-and-bounded-hold-passed
---

# Полная сцена EB300 с подвижным EBG20

Подготовлены отдельные standard model data для EnvHub: шесть управляемых осей руки, один MG995, две внутренние связанные каретки и свободный карандаш. Стол, клавиатура, монитор, PC, мышь, выбранное крепление телефона и gravity сохранены. Fixed preview rod удалён. Принятая CAD/LATEST, исходный held-tool preview и standalone R2 не изменялись.

Рабочий переносимый по структуре комплект: `E:\RoboHand\runs\2026-11-17-eb300-envhub\assets\`. Там XML, `robot-contract.json`, `mesh-manifest.json` и34 private mesh assets с относительными путями. В Git сохраняются только [scene XML](../../../integrations/lerobot_envhub/assets/eb300_envhub_scene.xml) и [численный contract](../../../integrations/lerobot_envhub/assets/robot-contract.json). Их копии в E-bundle побайтно совпадают. Для WSL нужно переносить весь bundle, включая `meshes/`; Windows absolute paths в XML отсутствуют. Без private meshes публичный XML сам по себе не загружается.

Scene SHA256: `501e0cbeffc54c161131eedce9a37d5845c7cb8dd7ab80153955eeb80fad735c`. Contract SHA256: `30f7114ebaf141e530cb34062abde82cf47dcaa44c7efcbd32f713e2ec15356b`. [Evidence](evidence.json).

## Что перенесено и проверено

Источник layout — `LATEST\SIMULATION\HELD-TOOL-CANDIDATE\EB300-pregrasped-rod.xml`; кинематика захвата — [R2, SHA8a4d26…](../2026-11-17-ebg20-motion/agent-report.md). Использованы штатные MJCF bodies, position actuators, equality joints, keyframe и MuJoCo4.0.1. Одноразовые XML/data orchestration и диагностики находятся вне Git; новый runtime/controller/IK/exporter не создавался. EnvHub adapter реализует root.

Canonical frame C — source003 local `(100,100,0) мм`, +X вдоль направляющей, +Z вдоль захвата. Матрица `T_wrist3_C` получена из точного принятого R8/URDF mesh003 transform, а не из повёрнутого world AABB. Конвенция — column vectors, `p_wrist3=T_wrist3_C·p_C`, трансляция в метрах. [Матрица и audit](scene-audit.json).

При theta=0 восемь перенесённых source mesh AABB совпадают с compiled preview до `0.366 мкм`; остаток соответствует округлению прежнего MJCF. Camera FK в той же arm pose совпадает точно, fovy сохранён. Старый jaw-contact semantic frame прикреплён к действительной движущейся Jaw A, чтобы site следовал губке.

Из прежнего wrist3 budget0.52кг выделены0.208кг захвата: base0.15, jaw0.025+0.025, pinion0.008. Carrier получает0.312кг. В reference pose сохранены масса, COM и полный spatial inertia исходного budget; остаточный тензор положителен и выполняет triangle condition. Телефон и mount0.328кг остаются отдельными source bodies. Все moving bodies имеют положительные массы/inertia; три нулевые массы относятся к допустимым fixed semantic frames. Номинальная масса robot data9.348кг не является измерением реальной руки. Удалённые0.008кг fixed rod перенесены в свободный pencil, поэтому общая масса scene не выросла.

## Контракт reset/step/render

| Поле | Значение |
|---|---|
| Controlled joints0…5 | `eb300/J1` … `eb300/J6` |
| Controlled joint6 | `ebg20/servo_angle` |
| Actuators0…5 | `eb300/J1_position` … `eb300/J6_position` |
| Actuator6 | `ebg20/MG995_position` |
| State/action names | `J1.pos` … `J6.pos`, `MG995.pos`; все7в rad |
| Reset | `envhub_ready`, полные qpos17/ctrl7/act7 в contract |
| Reset ctrl/act | `[-0.785398,0.9,0.85,0,-0.7,1,1]` |
| Internal joints | `ebg20/jaw_A_slide`, `ebg20/jaw_B_slide`, qpos7/8 в m |
| Passive keyboard | `key_A_travel`, qpos9 в m |
| Free object | body=`pencil`, geom=`pencil_contact`, joint=`pencil_free`, qpos10…16: XYZ(m)+quaternion(wxyz) |
| Actual pads | `ebg20/jawA_014_7`, `ebg20/jawB_014_4` |
| Policy camera | только `eb300/redmi8a_nominal`, selected `h120_b0_s-160_a20` |
| Render | полный RGB uint8 HWC360×640,16:9; без crop/zoom |
| Spectator | `overview`; не policy input |
| Clock | fps25,20physics steps/action, timestep0.002с |

Итого nq17/nv16/nu7/na7, две внутренние equality. Diagnostic fixture axis/actuator отсутствуют. Пределы actual actuator ctrlrange: первые6±2.96706rad, MG995−0.75…2rad; это nominal simulation limits. Семь qpos feedback и семь control targets не обязаны совпадать под gravity/PD load. «No action» здесь означает удерживать reset controls, а не подавать семь нулей.

## Физическая проверка и GIF

После согласованного keyframe reset выполнено10с удержания под gravity−9.81м/с² с peak accumulation на каждом physics step:

- warnings/time resets отсутствуют; max controlled drift≈`6.077e−5 rad`;
- max rack equality error≈`0.461 мкм`;
- max pencil–desktop penetration≈`54.825 мкм`; иных контактов нет;
- max J2 effort≈26.625Нм при limit35Нм; остальные приводные нагрузки также внутри limits;
- при static theta−0.75/0/1/2 с отключённым parent filter контактов новых губок с parent/phone/arm не обнаружено.

Карандаш свободно лежит на столе в `[-0.08,-0.30,0.7835] м`; pose выбран для видимости в полном wrist frame и не является демонстрацией grasp. Его состояние остаётся только у physics/evaluator.

[GIF](<E:/RoboHand/runs/2026-11-17-eb300-envhub/EB300-EnvHub-joint-gripper-demo.gif>) содержит57полных wrist frames: раскрытие/закрытие и небольшое изменение J1/J6 targets. Поле зрения и камера не меняются. Карандаш остаётся на столе; поиск, физический pickup и learned policy этим GIF не заявляются. Joint-target diagnostic также завершился без warnings/неожиданных контактов.

Сохраняются ограничения R2: nominal servo/inertia/friction, идеальная зубчатая связь, неподтверждённые omitted rack attachment transforms и открытый strict floor-impact gate при выпуске предмета. No-action/contact-free ready pose не означает collision-free workspace для произвольных действий. Полный arm grasp/lift, данные демонстраций и policy acceptance — следующие отдельные проверки.

Raw source/build audit, hold trace, renderer PNG и одноразовые команды находятся в `E:\RoboHand\runs\2026-11-17-eb300-envhub`. Ни `env.py`, ни README/индексы/CURRENT, ни accepted assets CAD-агентом не редактировались.
