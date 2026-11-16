---
tags: [eb300, reuse-first, isaaclab, ppo, adaptation]
type: decision-proposal
updated: 2026-11-16
status: explicitly-approved-minimum-adaptation-validated
---

# Граница следующего этапа: обучение EB300 в готовом NVIDIA recipe

Платформа — EB300. Исходный NVIDIA/so101-typing-task закреплён на `7aec2ed26dce8c88ae007a2714680cce572e1466`. До этого решения были отдельно выполнены reference smoke, импорт нашей модели в Newton и локальное заданное нажатие MuJoCo; EB300 ещё не была подключена к learning task. Ниже сохранён исходный gap и явно разрешённый объём. [Результат реализации16.11](2026-11-16-eb300-native-training.md): минимальная цепочка camera → teacher → vision → evaluation/replay пройдена; навык печати не обучен.

## Исходные ограничения закреплённого upstream

| Прочитанный исходник | Конкретное ограничение |
|---|---|
| `scripts/reinforcement_learning/rsl_rl/public_task.py:load_config` | Разрешены только schema_version, keyboard и domain_randomization. Robot asset, суставы и выбор environment factory в этот JSON не входят |
| `scripts/vision/runtime.py:make_config` | Создаёт SO-101-specific environment; общего параметра для нашей robot/environment configuration нет |
| `scripts/vision/agent.py:load_teacher` | Создаёт teacher MLP с литералом 5 actions. Существующий шестисуставной checkpoint этим loader не становится совместимым |
| `source/so101_typing/tasks/so101_env_cfg.py` | Robot asset, имена пяти суставов, gripper body/TCP и начальная IK-поза принадлежат SO-101 |
| `source/so101_typing/tasks/vision_typing_env_cfg.py` | CameraCfg указывает камеру Workshop SO-101. Для EB300 нужен отдельный camera config с нашей позой и номинальной оптикой Redmi |
| `scripts/vision/export_actor.py` | 5 outputs, action_dim=5 и proprio dimensions 45/57. Для виртуального smoke export на физическое устройство пока не нужен; этот файл не исправляется заранее ради необязательного deployment |

Generic joint-rate action уже вычисляет размер действия по списку суставов. Готовые Isaac Lab articulation, actuator, camera, contact, IK и PPO компоненты сохраняем. Метод PPO teacher → vision не заменяем ACT. Нового контроллера, модели обучения или фреймворка для этого не требуется.

**16.11 владелец явно разрешил описанную ниже адаптацию.** Это решение относится к этому ограниченному объёму, не отменяет reuse-first и не разрешает отдельный framework/controller.

## Разрешённый объём адаптации

1. Стандартная конфигурация EB300 для имеющихся articulation/action/observation/reset/camera hooks: J1–J6, обычная губка, Redmi, исходная клавиатура NVIDIA. Это данные механики и сцены.
2. Узкое подключение этой configuration к существующему factory/entrypoint. Прежде использовать штатную регистрацию environment и существующие CLI Isaac Lab; новый runner, task framework, UI или MCP не создавать.
3. В используемом teacher loader получать число actions из проверенного environment/checkpoint contract вместо константы 5; согласовать вызывающие места и проверку размеров. Это исполняемая model adaptation, поэтому она требует отдельного решения по AGENTS.md.
4. Проверить прочие SO-101-specific assumptions выбранного пути. При дополнительном изменении поведения показать его в diff и отчёте, не выдавать за замену чисел в JSON.

Принятые CAD/URDF/inspection files и физическая прошивка этим разрешением не заменяются. SO-101 reference сохраняется для regression check. Firmware, serial-adapter и физический deployment в этот объём не входят.

## Приёмка

- Запускается именно EB300 с шестью arm actions; пассивные клавиши и фиксированное раскрытие захвата не считаются дополнительными действиями руки.
- Контакты, reset, рабочая точка губки и image observations принадлежат EB300. Camera/task configs заданы явно; ошибки или потери конвертера не скрыты.
- Штатный минимальный PPO teacher → vision: checkpoints/sidecars, evaluation и replay имеют согласованные размеры. Два updates не объявляются выученным навыком.
- Отдельно проверяется прежний SO-101 reference после изменений, затрагивающих его loader/factory.
- Долгое обучение начинается после проверки остановки/возврата ресурсов стенду и supported resume. Само разрешение на адаптацию не означает запуск неограниченного training.

## Перестановка руки на столе

Основной mount — левый ближний к человеку угол; PC tower — правый дальний. Требование владельца — работать после перестановки базы. Это означает известный transform основания, проверку досягаемости и коллизий, затем обучение/оценку на разных **относительных** позах базы и клавиатуры. Простое перемещение всей сцены вместе не проверяет это требование. Текущие фиксированные targets для одной клавиши не являются универсальным решением для всех mount poses.

[Рабочая сцена](../desktop-workcell-r1.md) · [Исходный аудит hooks](2026-11-15-manual-control-and-typing-hooks.md) · [Правила проекта](../../AGENTS.md).
