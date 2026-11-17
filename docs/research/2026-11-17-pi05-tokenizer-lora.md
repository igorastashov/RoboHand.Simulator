---
tags: [eb300, pi05, tokenizer, lora, gpu, checkpoint, execution]
type: execution-note
updated: 2026-11-17
status: reference-text-inference-lora-update-and-cold-reload-passed
---

# π0.5: текстовый вход, LoRA update и повторная загрузка

На локальной RTX3090 пройден следующий этап после [raw GPU forward](2026-11-17-pi05-first-run.md): настоящий текст, изображения и состояние из готового LIBERO dataset → действия; один шаг штатного LoRA-дообучения; сохранение и загрузка адаптера в новом процессе. Это **проверка инфраструктуры на reference**, не обученный хват EB300.

## Токенизатор подключён

Владелец скачал файлы PaliGemma в Downloads. Семь файлов JSON/model скопированы в `E:\RoboHand\models\paligemma-tokenizer-owner-2026-11-17`, оригиналы сохранены. Их SHA256/Git blob IDs совпали с `google/paligemma-3b-pt-224@35e4f46485b4d07967e7e9935bc3786aad50687c`. Токенизатор загружается с `local_files_only=True`; повторный доступ к gated Hub не нужен.

`pick up the pencil` прошёл encode/decode round-trip. Это проверка кодирования текста, а не понимания команды роботом. Gated assets, веса и данные аккаунта в Git не публикуются.

## Проверенные source и workflow

- `huggingface/lerobot@7910c20a75834ad3fa6a9792df4d44a614d1bba6`, ранее прочитанные requirements и установленный LeRobot0.7.1.
- `lerobot/pi05_base@22c30e5b34f9e7ab738b1b34fc2fc5ecfe2d28f0`; исходный checkpoint14 467 165 872bytes, SHA256 `0eb11ca9587678c1d2ef8cf32807c29f8ce53a2bfdfc1aa4a4c96f16fca59b0f`.
- `lerobot/libero@a1aaacb7f6cd6ee5fb43120f673cebb0cfea7dd4`, episode0. Reference task про размещение кружек; state8, action7, две reference камеры256×256. Эти камеры **не добавляются к EB300**: её контракт остаётся одной wrist Redmi8A и полным кадром.
- Использованы stock `LeRobotDataset`, `DataLoader`, `make_policy`, `make_pre_post_processors`, `select_action`, `wrap_with_peft`, optimizer preset и `save_pretrained`. Основание: [model-card quick-start](https://huggingface.co/lerobot/pi05_base), [LeRobot PEFT](https://huggingface.co/docs/lerobot/peft_training), pinned `pretrained.py`/PI05 source и trainer.

Для LoRA выбран опубликованный PI05 default target pattern: q/v projections action expert и action/time projections. Rank64, alpha64. VLM/vision backbone не обучались. Обучаемых параметров5 410 816, около0,13% от instantiated model; это не полное дообучение всей foundation model.

## Измеренные результаты

BF16, batch1, horizon50, gradient checkpointing, Torch2.11.0+cu128/Transformers5.22.2/PEFT0.21.3. Значения относятся к одному reference batch, не являются универсальным memory budget для любой training campaign.

| Проверка | Результат |
|---|---|
| Text/images/state → postprocessed action |3/3finite; state `[1,8]`, text `[1,200]`, action `[1,7]` |
| Прогретые inference calls |0,304/0,359s; каждый reset заставлял пересчитать chunk, не просто извлечь следующий cached action |
| Inference peak allocated / reserved |9 478 051 328 /9 799 991 296bytes |
| Один LoRA optimizer step |0,516s, finite loss0,393889, finite gradient norm0,319490 |
| Изменение проверяемой LoRA-B матрицы |max abs delta≈2,49986e−5; положительное, не только успешный backward |
| LoRA peak allocated / reserved |9 648 877 056 /9 963 569 152bytes |
| Adapter tensor file |21 656 800bytes; SHA256 `8d1e2876268c60c7914c3b9ac2768c832f433d48a89800497d87d384ef26d5fc` |
| Загрузка в новом процессе |Stock factory восстановила PeftModel; все80adapter tensors совпали с сохранёнными побайтно |
| Inference после восстановления |3/3finite; два прогретых вызова0,416/0,409s |

**Один update не доказывает улучшения навыка.** Сохранённый adapter называется `reference-lora-smoke` и не объявляется политикой EB300. Первые7выходов generic architecture нельзя автоматически считать нашими шестью суставами и MG995: reference action semantics и новый robot contract различаются.

Первый диагностический training вызов ошибочно передал action `[50,7]` из отдельного кадра. Исправлен сам one-off вызов: stock DataLoader даёт `[1,50,7]`, как в trainer. Ни архитектура, ни model code, ни controller не менялись. Неуспешная попытка сохранена отдельно; memory failure или невозможность LoRA ей не приписываются.

## Файловая система и воспроизводимость

Основные source/weights/tokenizer/data/results остаются наE. Для ускорения повторных прогонов создан ограниченный рабочий cache в native ext4 существующей Ubuntu: `/var/tmp/robohand-pi05-7910c20-2026-11-17`. Этот Ubuntu VHD находится **наC:**; это временная рабочая копия, а не перенос основного проекта или Docker обратно наC.

Окружение воспроизведено штатным `uv pip sync` по прежнему freeze;93version pins и source URI LeRobot совпали (94packages). CUDA/CPU PyTorch indexes перечислены явно, чтобы сохранить CPU TorchCodec вместе с CUDA Torch. Checkpoint в кэше снова проверен по SHA256. Драйверы, службы и shared GPU server не изменялись.

В native cache model loading заняло91,2s, при отдельном восстановлении93,6s; предшествующий прогон с Windows-mounted files занял245,5s. Это наблюдение разных запусков, не изолированный filesystem benchmark. Основное время cold start по-прежнему отделяется от warmed inference/update.

## Артефакты и следующий шаг

- `E:\RoboHand\runs\2026-11-17-pi05-text-and-gripper\tokenizer-upstream-verification.json` — происхождение всех семи файлов.
- `attempt2\reference-result.json` — успешные real-batch inference/update/save; `attempt2\reference-lora-smoke` — отдельный checkpoint.
- `reload\reload-result.json` — новый процесс, inference и совпадение80tensors.
- Первая неуспешная попытка, commands, native environment inventory и logs сохранены рядом. Одноразовые диагностические вызовы находятся вне Git; новый project runtime/controller/model adapter не добавлен.
- [Публичная evidence-сводка](../../evidence/2026-11-17-pi05-tokenizer-lora.json).
- Приватный восстановительный пакет этой итерации: `E:\RoboHand\releases\EB300-PI05-LORA-EBG20-2026-11-17\EB300-PI05-LORA-EBG20-2026-11-17.zip`, зеркало `D:\RoboHand-Backups\EB300-PI05-LORA-EBG20-2026-11-17.zip`. В пакет входят adapter/tokenizer, physics/source evidence, model data и документы; полный14,5GBbase checkpoint и environments не дублируются, их revisions/hashes/requirements сохранены. SHA256/CRC/manifest фиксируются в соседнем receipt.

От владельца файлы токенизатора больше не требуются. Следующий рабочий этап — подвижный EBG20 и свободный инструмент в нашей scene, затем совместимый готовый recorder/rollout path и demonstrations EB300. Необходимо сохранить единицы/порядок joints, один wrist-view, timestamps и честную проверку контакта/подъёма. [Физическая задача](2026-11-16-typing-tool-acquisition-plan.md), [актуальный план](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-17-foundation-lora.md>), [индекс](../index.md).
