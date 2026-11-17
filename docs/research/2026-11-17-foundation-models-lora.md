---
tags: [eb300, foundation-models, groot, pi05, molmoact2, lora, roadmap]
type: research
updated: 2026-11-17
status: source-audited-models-not-installed-or-executed
---

# EB300: доступные foundation models и LoRA

**Позднейшая итерация17.11:** [π0.5 установлен, веса скачаны/проверены и raw GPU forward прошёл на нашей3090](2026-11-17-pi05-first-run.md). Ниже сохранён предшествующий source-only audit; его формулировки «не устанавливались/не скачивались» относятся к моменту того исследования. Text preprocessor, LoRA update и EB300 grasp ещё не проверены.

Уточнение владельца17.11: локальные3090 предпочтительны, но внешние GPU/VM допустимы. Модель выбирается по качеству и поддерживаемому workflow;24GB не являются потолком. Начальный π0.5 smoke — технический baseline, не выбор более слабой модели ради памяти. Для тяжёлого кандидата переносим тот же pinned workflow на подходящий GPU и измеряем ресурсы, не изобретаем memory hacks.

**Последнее решение владельца17.11: отдельный PPO typing actor исключён из дальнейшего обучения и исполнения EB300.** Существующие checkpoints, сцены и результаты сохраняются как история. Основной маршрут — предобученная language-conditioned motor policy, адаптация по демонстрациям и затем Codex coordinator. [Действующий план](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-17-foundation-lora.md>).

Срез сделан17ноября2026. Релизы/результаты2027 ещё нельзя считать известными. «SOTA» из чужого benchmark не определяет победителя на EB300: нужны одинаковые исходные условия и независимые эпизоды нашей задачи. Ни одной из перечисленных моделей в этом проходе не устанавливали, веса не скачивали, GPU inference/training не запускали.

## LoRA простыми словами

**Low-Rank Adaptation** сохраняет большую исходную матрицу весов и обучает небольшую поправку из двух матриц: `W_new = W_base + scale × B × A`. У них мало внутренних измерений — rank. Это уменьшает число обучаемых параметров и память под gradients/optimizer; большая базовая модель всё равно нужна для inference. Поддерживаемый exporter может объединить поправку с базовыми весами. [PEFT: LoRA](https://huggingface.co/docs/peft/v0.21.0/en/conceptual_guides/lora).

**Few-shot** означает мало показов, **LoRA** — способ изменения весов. Одно не гарантирует другого. Для робота дополнительно могут обучаться обычные action/state projections, connector или весь action expert. Это не обязательно «все компоненты заморожены, меняется только маленький файл».

Например, в [официальном MolmoAct2 recipe](https://github.com/allenai/molmoact2/blob/6070080a20321b4f498ab30f28e1d09ac465edb7/experiments/README.md#lora-fine-tuning) LoRA применяется к LLM/ViT, connector/action expert могут обучаться полностью. Для inference нужен полный merged checkpoint с этими компонентами. [LeRobot PEFT](https://huggingface.co/docs/lerobot/peft_training) имеет готовые настройки LoRA, включая π0.5 и MolmoAct2; конкретные targets и формат checkpoint проверяются до запуска.

Не требуется отдельная модель/LoRA на каждую клавишу или tool координатора. Начальный вариант — одна база и одна адаптация EB300 на несколько инструкций и режимов. Отдельные task adapters рассматриваются только по результатам оценки, чтобы не создавать лишнее переключение моделей.

PPO — другой вопрос: алгоритм RL по rollout/reward. LoRA может сочетаться с supervised learning или RL. Выход из PPO для руки — решение о нашем маршруте, а не доказательство устаревания RL вообще.

## Кандидаты: веса, память и готовность

Цифры ниже принадлежат авторам и конкретным runtime. Это не наши замеры RTX3090; GB/GiB сохраняют смысл источника. Размер файлов модели на диске не равен peak VRAM.

| Кандидат | Доступность и лицензия | Память/адаптация по опубликованному пути | Решение для EB300 |
|---|---|---|---|
| **GR00T2** | Research page ноября: «Code Available in December». Released weights/license не подтверждены | Опубликован опыт5показов/30мин LoRA на одной RTX5090. Полный peak VRAM и работа на3090 не установлены | Целевой кандидат после фактического релиза, не блокирует сегодняшнюю подготовку |
| **GR00T N1.7-3B** | HF weights существуют, ungated. Код Apache2; веса NVIDIA Open Model License | Официальный inference от16GB; fine-tuning от40GB рекомендуется. Default обучает projector/action head, не весь LLM | Доступный GR00T reference. Не подменять им GR00T2 и не обещать stock few-shot LoRA |
| **π0.5 / OpenPI, LeRobot** | Опубликованы checkpoints. Код OpenPI Apache2; присутствуют Gemma terms, HF `lerobot/pi05_base` помечен `gemma` | OpenPI даёт ориентиры inference >8GB, LoRA >22.5GB, full >70GB. Эти значения нельзя автоматически переносить на LeRobot | Первый кандидат для штатного reference smoke и доступного PEFT path; не объявлен победителем EB300 |
| **MolmoAct2** | Official base + robot/task checkpoints опубликованы. README проекта заявляет Apache2; у просмотренных HF cards нет license tag, source/card snapshot сохранены | Official BF16 server описывает YAM inference <16GB; CUDA graph добавляет примерно2GB. LoRA recipe опубликован, peak обучения на3090 не подтверждён | Второй кандидат после первого stock smoke либо при выявленном gap; YAM/DROID views/actions не являются EB300 |
| **LingBot-VLA2.0-6B** | Official code/base/post-training weights опубликованы; проект Apache2 | Авторы приводят ~130ms/inference на4090D с10denoising steps. Это не3090benchmark и не minimum VRAM. FP32 release evaluation и BF16 могут существенно различаться | Watchlist для следующего сравнения; не начинаем третью training campaign |
| **π0.7** | Research опубликован; в проверенном OpenPI нет такого checkpoint. Pi API beta — hosted fine-tune/inference, доступ ограничен | Нельзя назначить нашей машине VRAM requirement по имени модели или считать beta точной локальнойπ0.7 | Frontier reference; не выбран offline backend |

Источники: [GR00T2](https://research.nvidia.com/labs/gear/gr00t-2/#dexter50), [N1.7 hardware guide](https://github.com/NVIDIA/Isaac-GR00T/blob/3b49067943eb1ab2eb2203b93d461c4390c78da3/getting_started/hardware_recommendation.md), [OpenPI](https://github.com/Physical-Intelligence/openpi/tree/215abfb217dbac7d5f1273282331b9b1866c0479), [π0.5 model card](https://huggingface.co/lerobot/pi05_base), [MolmoAct2 server README](https://github.com/allenai/molmoact2/blob/6070080a20321b4f498ab30f28e1d09ac465edb7/README.md), [LingBot2](https://github.com/Robbyant/lingbot-vla-v2/tree/be969b8fd117fb70550c5d4bf4bc328211b5b1b6), [π0.7](https://www.pi.website/blog/pi07), [Pi API](https://www.pi.website/blog/api-beta).

### Три несовместимости, которые нельзя скрывать

1. **N1.7 ≠ GR00T2 LoRA.** В pinned NVIDIA `finetune_config.py` доступны flags выбора обучаемых частей, отдельного LoRA workflow нет. [Issue568](https://github.com/NVIDIA/Isaac-GR00T/issues/568) сообщает об удалении прежней поддержки; community fork не принят вместо официального пути. В текущем [LeRobot configuration_groot.py](https://github.com/huggingface/lerobot/blob/7910c20a75834ad3fa6a9792df4d44a614d1bba6/src/lerobot/policies/groot/configuration_groot.py) старые LoRA fields описаны как never-wired/deprecated. Наличие `peft` в requirements или общих PEFT flags не доказывает проверенный GR00T-specific recipe.
2. **OpenPI JAX ≠ OpenPI PyTorch ≠ LeRobot.** У inspected OpenPI PyTorch LoRA/FSDP ещё listed unsupported; JAX имеет LoRA/filter и `fsdp_devices`. LeRobot имеет отдельный PEFT путь π0.5. Для первого PEFT smoke выбираем готовый LeRobot tutorial; численные требования OpenPI оставляем ориентиром до собственного замера. Не смешиваем checkpoints и команды этих implementations.
3. **Две3090 ≠ одна48GB карта.** Каждая имеет24GB. Обычный DDP реплицирует модель. У OpenPI есть явный model-sharding path; у текущего LeRobot MolmoAct2 port оригинальный `fsdp_devices` path не экспортирован. Любое FSDP/PEFT сочетание квалифицируется отдельно, а не обещается по сумме памяти. Рендерер и соседние процессы тоже занимают VRAM.

У GR00T2 результат5показов относится к уже исследованным robot embodiments и задачам. Для новой EB300 ещё нужны gripper/action contract, наблюдения, data normalization и возможный embodiment head;30минут не являются сроком всей интеграции.

## Что именно сравниваем на нашей руке

Вход: одна выбранная боковая wrist camera Redmi8A, один полный кадр; joint state, gripper state после его описания, instruction, согласованные timestamps. Только resize/padding с сохранением кадра; никаких новых внешних камер, ROI/crops, zoom или privileged object pose на входе исполнителя. Ненаблюдаемый предмет требует обзорного движения руки.

Base checkpoint не гарантирует zero-shot управление новым роботом. Сначала штатный forward на штатном sample; затем отдельный gap audit по image keys, missing-view masks, units, frames, state/action dimensions, ranges и timing. Не выдавать копирование одного wrist кадра в несколько camera slots за готовую многокамерную систему. Если допустимой конфигурации мало и нужен исполняемый adapter/controller — предъявить конкретный scope до нового кода.

Нынешний gripper фиксирован по раскрытию. Pregrasped preview — предмет с жёстким attachment,3/3 заданных нажатий, не навык поиска/хвата. Следующий физический gate — управляемый EBG20 и свободный инструмент с контактным удержанием. Без него нельзя собрать честные demonstrations «взять карандаш» для любой большой модели.

Данные: RGB/state/action/language/время, действительные press/release/key events и terminal outcome; исходные показы сохраняются до model-specific преобразований. Начинаем с пилотных10–20качественных эпизодов как инженерного бюджета, не гарантии достаточности. Сначала отделяем test poses/scenes от train. Кривые5/10/20/...доступных demonstrations оцениваем только при достаточной независимой выборке; мало данных само по себе не цель.

Метрики: найти подходящий предмет; взять/удержать/поднять; правильный рабочий конец; letter/word success; press/release; ошибочные контакты/потеря; success и latency на новых положениях. На первом gate — одна клавиша; затем несколько и NEWTON, режим губки и отсутствие инструмента. Никакой программной подстановки текста в ОС.

## Штатные проверки перед EB300

Команды/сценарии изучены по source, **не исполнялись** в этом проходе:

- π0.5: quick-start `select_action` на настоящем batch из [HF card](https://huggingface.co/lerobot/pi05_base), затем [LeRobot PEFT tutorial](https://huggingface.co/docs/lerobot/peft_training) с π0.5 и подходящими target modules. Готовый пример tutorial на SmolVLA остаётся reference другой модели; не выдаётся за выполненный π0.5 smoke.
- N1.7: `uv run python scripts/deployment/standalone_inference_script.py --model-path nvidia/GR00T-N1.7-3B --dataset-path demo_data/droid_sample --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT --traj-ids 1 2 --inference-mode pytorch --execution-horizon 8`. Это open-loop DROID, не наша камера/рука.
- MolmoAct2: `uv run python examples/yam/host_server_yam.py --host 127.0.0.1 --port 8202 --dtype bfloat16`. Проверка требует released YAM sample/request и измерения actual peak; один запущенный server без ответа не считается smoke. Для small-data tuning существует официальный LoRA section в `experiments/README.md`.

Requirements прочитаны: N1.7 Python3.12/Torch2.9/Transformers4.57.3, FFmpeg4–7; OpenPI Python≥3.11/JAX0.5.3/Torch2.7.1; MolmoAct2 Python3.11–3.12/Torch2.11/CUDA12.8; current LeRobot Python≥3.12 и собственный lock/extras. Среды должны быть изолированы; existing typing/prod runtime не обновляется ради нового пакета.

## Source evidence и статус

| Source | Commit |
|---|---|
| NVIDIA/Isaac-GR00T | `3b49067943eb1ab2eb2203b93d461c4390c78da3` |
| Physical-Intelligence/openpi | `215abfb217dbac7d5f1273282331b9b1866c0479` |
| allenai/molmoact2 | `6070080a20321b4f498ab30f28e1d09ac465edb7` |
| huggingface/lerobot | `7910c20a75834ad3fa6a9792df4d44a614d1bba6` |
| Robbyant/lingbot-vla-v2 | `be969b8fd117fb70550c5d4bf4bc328211b5b1b6` |

HF metadata подтвердил ungated weights файлов: N1.7 revision `373d34e2723d928870157d07dc216a19a624b5bb`; π0.5 LeRobot `22c30e5b34f9e7ab738b1b34fc2fc5ecfe2d28f0`; MolmoAct2 `e432d85f6e039edca44afb93c262f3084ab72a9c`; LingBot2 `11c703bf6a5c1f45b3b69168482da11fdbba53d7`. Весовые tensors не скачаны; availability не равно загрузка/исполнение.

Локальный пакет: `E:\RoboHand\research\2026-11-17-frontier-models-lora` — pinned README/requirements/configs/licenses, model metadata, issue/page snapshots и SHA manifest. [Публичная evidence-сводка](../../evidence/2026-11-17-foundation-models-lora.json). [Роли coordinator и policy](../../../RoboHand.Control/docs/typing-tool-agent-plan.md). Робособака имеет отдельный [разбор границ locomotion](<../../../../../РОБОСОБАКА/RoboDog/research/2026-11-17-foundation-models-and-locomotion.md>).
