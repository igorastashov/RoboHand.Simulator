---
tags: [eb300, ppo, actor-critic, cnn, groot, training]
type: research
updated: 2026-11-17
status: pinned-source-and-existing-smoke-evidence-audit
---

# Какую модель обучает наш PPO

**PPO — алгоритм обновления параметров policy, а не имя модели.** В принятом NVIDIA typing recipe используются небольшие сети RSL-RL/PyTorch: state teacher — `MLPModel`, vision actor — `CNNModel` с полносвязной частью. GR00T/GPT/другой foundation backbone в этой архитектуре не загружается.

Источник: `NVIDIA/so101-typing-task@7aec2ed26dce8c88ae007a2714680cce572e1466`, [architecture](https://github.com/NVIDIA/so101-typing-task/blob/7aec2ed26dce8c88ae007a2714680cce572e1466/docs/policy_architecture.md), [state config](https://github.com/NVIDIA/so101-typing-task/blob/7aec2ed26dce8c88ae007a2714680cce572e1466/source/so101_typing/tasks/agents/rsl_rl_ppo_cfg.py), [vision config](https://github.com/NVIDIA/so101-typing-task/blob/7aec2ed26dce8c88ae007a2714680cce572e1466/scripts/vision/agent.py). Прочитаны файлы, а не только README; новая training installation в этом исследовании не выполнялась.

## Проверенная архитектура EB300

| Часть | Модель и вход | Роль |
|---|---|---|
| State teacher actor | MLP с hidden layers256/256/128, ELU;25значений состояния в нашем smoke | Выбирает6действий руки по состоянию/цели |
| Vision actor |3CNN layers: channels16/32/32, kernels5/3/3, strides2/2/2, ReLU; затем MLP256/256/128 | Выбирает6действий по RGB history и proprio/goal |
| Critic | Отдельная MLP256/256/128 по privileged state | Оценивает ожидаемый возврат при обучении; исполнитель actor обходится без неё |

Vision smoke EB300: RGB `[batch,6,120,160]` — два последовательных RGB-кадра **одной** камеры; proprio `[batch,60]`. CNN даёт7488features, вместе с60 получается7548inputs первой MLP. Размеры меняются при другом observation contract. Это прежний номинальный camera profile; новая выбранная боковая камера/полный16:9 кадр не становятся автоматически совместимыми с этим checkpoint.

Beta head имеет12выходных параметров: по два параметра распределения для каждого из6действий. Это **не12приводов**. Политика выдаёт ограниченные joint-rate actions, существующий executor интегрирует их в position targets. Gripper action в принятой шестимерной adaptation отсутствует.

В прежнем upstream hardware exporter остаются пятиосевые проверки. Название `VisionActor` или наличие export script не доказывает готовый deployment EB300. [Результаты нашей bounded adaptation](2026-11-16-eb300-native-training.md) остаются отдельным доказательством.

## Обучение, продолжение и fine-tuning

Штатный state training начинает с параметров выбранной сети и улучшает их через rollout/reward/PPO. Это не дообучение большой заранее обученной модели. Продолжение собственного checkpoint — дальнейшее обучение той же policy. Для vision есть warmup по действиям frozen teacher, затем PPO по rollout; teacher и critic не обязательны в исполнительном inference.

Наши EB300 checkpoints прошли только минимальные updates и evaluation с0набранных символов. Их нельзя объявлять готовой печатью или качественным генератором демонстраций для GR00T. Успешные заданные движения в MuJoCo — другой результат, не качество этих весов.

## Отличие от быстрой адаптации GR00T

| Метод | Откуда учебный сигнал | Что обновляется |
|---|---|---|
| Наш PPO typing | Новые попытки в sim и reward за подвод/press/release/последовательность | Actor и critic выбранной небольшой архитектуры |
| Few-shot LoRA у foundation model | Записанные показы действий в проверенном robot contract | Небольшие обучаемые adapters предобученной модели по recipe |
| RL-улучшение foundation policy | Rollouts и оценка результата | Зависит от опубликованного RL recipe; не обязательно PPO |

Общая внешняя дисциплина похожа: среда/данные → обучение → отдельная оценка → сохранённый checkpoint. Loss, модель, объём исходных знаний и способ сбора опыта отличаются. Подставить GR00T в RSL-RL typing config вместо CNN без явной адаптации метода нельзя.

Последнее решение владельца17.11: отдельную PPO-policy руки больше не обучаем и не планируем исполнять. Исторические reference/checkpoints сохраняем; будущий optional specialist из предыдущего плана отменён. [Текущий foundation/LoRA маршрут](2026-11-17-foundation-models-lora.md), [план](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-17-foundation-lora.md>); этот документ объясняет уже выполненный PPO smoke.

Сохранённый source audit: `E:\RoboHand\research\2026-11-17-groot-first-plan\typing-7aec2ed`. Предыдущая r6 checkpoint inspection: `E:\RoboHand\runs\2026-11-16-hardware-workcell\checkpoint-inspection-r6.json`; head shape12×128 подтверждена у teacher/vision. Новых GPU runs и изменений модели/контроллера не было.

[Индекс](../index.md) · [Контракт эпизода с инструментом](2026-11-16-typing-tool-acquisition-plan.md).
