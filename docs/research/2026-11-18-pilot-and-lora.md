---
tags: [eb300, demonstrations, dataset, pi05, lora, evaluation]
type: experiment-record
updated: 2026-11-18
status: official-lora-pilot-evaluated-grasp-not-learned
---

# EB300: разнообразный пилот и штатная LoRA

**Итог:**11качественных train/4отдельных validation episodes подготовлены готовыми средствами;1000official π0.5 LoRA updates, save/cold reload и paired evaluation выполнены на локальной3090. **Learned grasp пока не освоен: base0/4 и LoRA0/4 на validation; обе0/3 на валидных stress cases.** Успешные scripted-expert показы остаются отдельным результатом. [Сравнение и все метрики](evidence/2026-11-18-pilot/comparison.json).

[Индекс](../index.md) · [Предыдущий контактный цикл](2026-11-18-mink-execution.md) · [Разрешённый binding](2026-11-18-eb300-teleop-adaptation.md).

Владелец поручил продолжить после первого контактного цикла. Эта запись фиксирует дизайн до запуска новых случаев, чтобы не выбирать удобные test poses после результатов. Поведение контроллера не меняем: используем принятый Mink/EnvHub binding и штатные LeRobot writer/edit/train/rollout. Положения свободного карандаша и literal target matrices — данные отдельных сцен. Нового randomizer, state machine, data-generation framework или model/controller adaptation не добавляем.

## Готовые пути и границы

- `huggingface/lerobot@7910c20a75834ad3fa6a9792df4d44a614d1bba6`: actual `lerobot_edit_dataset.py`, dataset_tools, `docs/source/peft_training.mdx` и `pi05.mdx` прочитаны. Есть штатные merge по local roots, split по целым episode indices, modify_tasks и recompute_stats; используем их вместо своего формата/конвертера.
- `NVlabs/mimicgen@c0fbff22ba40060f05a917a80817f3f5c20731e7`: прочитаны actual README/setup/custom-environment/getting-started. Для нашей среды требуются новые robomimic wrapper/EnvironmentInterface и action↔EEF hooks. Runtime не установлен и не выдан за готовую интеграцию EB300.
- `isaac-sim/IsaacLab@9d9eff519d1bcb7e62dc5d129d37eea4be51342d`: actual Franka absolute-IK Mimic adapter требует иной environment/action interface. Переноса нашей проверенной физики в новый simulator в этой итерации нет.
- Для небольшого первого пилота достаточно новых standard scene/target data к уже разрешённому runner. Это scripted-expert demonstrations с известными стартами; не human teleop, не learned perception и не доказательство широкого обобщения.

## Предварительно выбранные случаи

Один карандашØ7×110мм/8г, та же поверхность и исходная конфигурация руки, тот же Redmi8A/full640×360. Меняется только начальная XY/yaw свободного карандаша. Все выбранные сцены сохраняют7actions, массы, инерции, gains, torque caps, timestep2ms и nominal optics. Не меняем geometry ради успешности.

| Группа | Случаи | Назначение |
|---|---|---|
| Train anchor | X=−0.08,Y=−0.30м,yaw0° | Свежая запись pickup/hold с правильной annotation; прежние50/990diagnostic frames не включаем |
| Train grid,12 | X∈{−0.11,−0.08,−0.05},Y∈{−0.315,−0.285}м,yaw∈{−8°,8°} | Разные старты в небольшой рабочей области |
| Validation,4 | X∈{−0.095,−0.065},Y=−0.30м,yaw∈{−4°,4°} | Независимые целые эпизоды; допускается оценка для выбора checkpoint, не обучение |
| Stress test,4 | (−0.13,−0.33,−15°),(−0.13,−0.27,15°),(−0.03,−0.33,15°),(−0.03,−0.27,−15°) | Отдельный ограниченный выход за train region; не использовать для настройки policy/targets |

Instruction первого навыка: **“Pick up the pencil and hold it above the table.”** Эпизод завершаем после физического evaluator success, без place/release. Предопределённые длительности подхода/предхвата/подвода/касания/закрытия/подъёма —90/50/40/40/70/80control ticks; при success окончание раньше. Фиксированное hover уточнение из предыдущей итерации не превращаем в новый online controller. Объектная система координат задаёт новые literal poses; runtime не получает функцию поиска карандаша.

Критерии принятия одинаковы для всех: оба рабочих pad contacts, отсутствие поддержки другой геометрией при lift≥20мм/hold≥0.5s, отсутствие warnings/reset, peak penetration в pads/другую геометрию≤0.1мм, non-tool penetration≤0.1мм, equality residual≤0.1мм и actuator-force fraction≤1.000001. Последние non-tool/force peaks добавлены как **read-only substep metrics** в существующий evaluator; observations, reward, termination, actuator law не меняются.

Неудачные попытки сохраняем и считаем. Их не включаем в экспертный train merge. Не переносим неудачные validation/test cases в train и не подгоняем по ним targets. Если train пригодных эпизодов меньше10, training campaign по этому плану не начинается до исправления причины или отдельного решения. Даже13успешных записей не обещают достаточность для навыка.

## Данные и обучение

Новые run/assets/datasets — отдельно в `E:\RoboHand\runs\2026-11-18-eb300-pilot`. Старый run/release и LATEST CAD не перезаписываются. Исходная990frame запись может быть исправлена только на копии штатным modify_tasks как reference; она не станет varied pilot от изменения подписи.

Native Windows запись проверяем в отдельном `lerobot-record-win-2026-11-18` environment: готовый extra `lerobot[dataset]`, CPU Torch2.11/torchvision0.26, те же MuJoCo4.0.1/NumPy2.2.6/Gymnasium1.4/Mink pin. Это recorder, не inference GPU setup. Resolver dry-run прошёл; install/smoke фиксируются отдельно. Существующий Linux CUDA environment и shared host не меняются.

Merge/split/recompute — только официальные LeRobot API/CLI. Статистика нормализации считается по train, не по validation/test. Один full wrist key, без crop/zoom/другой камеры, full-frame resize/padding модели допустим. Дляπ0.5 используем прежний base22c30e5, локальный проверенный tokenizer и штатный PEFT LoRA recipe. Architecture/dimensions/controller не переписываем; default PI05 LoRA targets action expert q/v и action/time projections. Обучение/оценка запускаются только после фактической проверки данных.

Короткий запуск на train — pilot, не обещание mastery. Сравниваем base weights с той же train-normalization и fine-tuned checkpoint, отдельно validation/stress cases, closed-loop physical success и failures. Loss и finite forward не заменяют качество исполнения. Baseline с EB300-derived normalization не называем чистым zero-shot переносом.

## Фактические данные и контроль качества

Пререгистрация сохранена до генерации случаев: `E:\RoboHand\runs\2026-11-18-eb300-pilot\preregistration.md`; hash находится в `case-manifest.json`. Все 21 исходная сцена скомпилированы со стандартным контрактом: nq17/nv16/nu7/neq2, timestep2ms. Старые CAD и baseline scene не менялись.

Первая серия: девять качественных train, четыре качественных validation. Для четырёх неудачных **train** сохранена отдельная R2-поправка фиксированных poses, основанная только на training hover. Два случая исправились. Ещё два (`train-11/12`) остаются с физическим столкновением `bottom_row_geom_0` ↔ `ebg20/jawA_013_3`; в expert train не включены. Validation/stress poses не корректировались. Все 25 попыток, включая ошибки, сохранены.

Итоговый набор — **11 train episodes / 3403 frames**, **4 validation episodes / 1238 frames**, 25Hz. Это scripted-expert simulation data, не human teleop и не learned policy. Instruction во всех записях соответствует pickup/hold без последующего release. Старые50/990frame diagnostics не использованы. Из четырёх stress-сцен `stress-03` исключена **до policy evaluation** из-за начального пересечения карандаша с клавиатурой на7мм. Из трёх валидных stress-сцен expert quality_success0/3, raw task_success1/3: это сложные сцены, а не обещание достижимости принятой демонстрацией.

Официальный `lerobot-edit-dataset` прошёл минимальный merge2episodes/619frames; затем merge15episodes/4641frames, split по целым исходным episodes и recompute_stats исключительно по train, включая полные изображения. Принятая нормализация action/state — штатная PI05 **QUANTILES**, image — IDENTITY; все q99−q01 положительны. Отдельная проверка стандартными readers подтвердила точное сохранение исходных действий, положительные std всех7actions, отсутствие пересечения case IDs и правильную instruction. Первые/последние images всех11train episodes после merge/split совпадают побайтно;11начальных кадров имеют разные hashes. Это узкая сетка XY/yaw одного предмета/освещения, не широкая визуальная вариативность.

Данные: `datasets/splits/train` и `datasets/splits/validation` внутри run. Evidence: `data-quality-audit.json`, `dataset-verification.json`, `visual-data-verification.json`, `showcase/pilot-wrist-inputs.png`.

| Split | Episodes | Frames | SHA256 исходных action sequences |
|---|---:|---:|---|
| train |11|3403|`274bcc6b1061c8d903413415b308c37603802ae27acb4446f617dfa521fdd22c`|
| validation |4|1238|`baf53a22d9eba303410f65e1832b04506ebab5659f3e3cfa3dacb2a806860ca9`|

## База и штатное обучение

Оценка использует **штатный `lerobot.scripts.lerobot_eval.eval_policy`**, policy/processor/env factories. По450ticks на четырёх validation и трёх валидных stress-сценах; seeds1000–1006. Mink и target JSON не участвуют в inference; case coordinates используются только для стандартного reset сцены. Вход — только state7, полный wrist frame и instruction. Перед baseline прошёл standard EnvHub preprocessing/reset/step smoke. Base weights используют **train-only EB300 normalization**, поэтому это не pure zero-shot.

**Изменение конфигурации до оценки основного кандидата:** первый запуск использовал MEAN_STD. Actual pinned `configuration_pi05.py:92` задаёт QUANTILES; `processor_pi05.py:79,151` дискретизирует состояние на диапазоне[−1,1]. Проверка train-only данных показала, что mean/std выводит9–40% state values разных осей за этот диапазон; агент остановил вариант на625reported updates и выбрал default QUANTILES для основного пилота. Checkpoint500/logs и исторический mean/std baseline0/4+0/3 сохранены. **Прежняя формулировка агента «неверная/несовместимая нормализация» была слишком категоричной:** полный `pi05.mdx:102,128` явно поддерживает MEAN_STD в LIBERO example и как альтернативу. Измеренное отличие представления не доказывает несовместимость или причину неудачного хвата; незавершённый кандидат не доказывает преимущество QUANTILES. Его baseline9,437GB allocated не является главным QUANTILES сравнением. Evidence: `normalization-audit.json`, `normalization-correction.json`.

Основной `train-pi05-quantiles-config.json` задаёт официальный `lerobot-train`:1000updates, batch4, rank64/alpha64, lr2.5e-4, warmup50, cosine decay1000до2.5e-5, save250, seed1000, bf16/CUDA/gradient checkpointing; QUANTILES action/state. Используются штатные PI05 LoRA targets action expert q/v и action/time projections. Image augmentation выключена; vision encoder заморожен. Train root — отдельный ext4 cache проверенного набора; исходные данные и outputs остаются наE. WSL VHD находится наC; это уже существующий runtime/cache, не перенесённый Docker. Shared host не задействован.

Основное paired comparison использует один холодно загруженный PEFT checkpoint и одни сохранённые processors. Штатный PEFT0.21.3 `disable_adapter()` context отключает только LoRA для base-прогона; затем тот же `eval_policy` вызывается с включённым adapter на тех же сценах/seeds. Это вызовы готовых API, без собственного action loop, solver или model adaptation. Все80adapter tensors и train-only mean/std/q01/q99 в processors проверяются на точное совпадение с сохранёнными файлами/исходными statistics. Конечные результаты фиксируются ниже по факту.

Для штатного загрузчика сохранённого base processor подготовлен отдельный offline HF cache из семи ранее проверенных owner tokenizer files, namespace `google/paligemma-3b-pt-224`, revision `35e4f46485b4d07967e7e9935bc3786aad50687c`. Загрузка `AutoTokenizer.from_pretrained(..., local_files_only=True)` прошла; base weights/processors/upstream code не редактировались. Это поддерживаемый cache, не обход gated download. Никакие файлы не загружались на Hub.

Окружения: native Windows recording использует официальный `lerobot[dataset]` extra и CPU Torch2.11; Linux inference/training — существующий Torch2.11+cu128/PEFT0.21.3.13проверок binding/contract прошли на Windows и Linux. Новая13-я проверка задаёт физически неверную позу и подтверждает, что read-only collision observer обнаруживает проникновение без изменения состояния/приводов. EGL fallback в WSL и TorchCodec→PyAV fallback задокументированы; рендер не объявляется GPU/realtime.

Источники/snapshots/pins: `E:\RoboHand\research\2026-11-18-demonstrations\source-audit.json`. Primary workflow: [LeRobot PEFT](https://github.com/huggingface/lerobot/blob/7910c20a75834ad3fa6a9792df4d44a614d1bba6/docs/source/peft_training.mdx), [штатный dataset editor](https://github.com/huggingface/lerobot/blob/7910c20a75834ad3fa6a9792df4d44a614d1bba6/src/lerobot/scripts/lerobot_edit_dataset.py), [штатная оценка](https://github.com/huggingface/lerobot/blob/7910c20a75834ad3fa6a9792df4d44a614d1bba6/src/lerobot/scripts/lerobot_eval.py). [MimicGen custom environment](https://github.com/NVlabs/mimicgen/blob/c0fbff22ba40060f05a917a80817f3f5c20731e7/docs/tutorials/datagen_custom.md) рассмотрен как будущий путь с отдельным adapter gap; runtime в эту итерацию не добавлялся.

## Обучение выполнено

Штатный QUANTILES кандидат завершил **1000optimizer updates / batch4 / 4000sample draws** за12мин39с training loop. Это≈1,175sample draws на исходный frame; targets имеют штатный50step chunk.5 410 816trainable parameters,80LoRA tensors,21 656 800байт. SHA256 `70f55eab7522e2a3b1b844d64cdff2e51d13b6c3b3bd54af694f2526e8c12331`. Checkpoints250/500/750/1000 сохранены с optimizer/RNG/scheduler state. Основной результат оценивается по заранее выбранному финальному1000checkpoint, без выбора лучшего stress результата.

Логируемый train loss (округлённые25step aggregates) снизился с0,267на step25 до0,013на step1000. Logged peak allocated9,40GiB; последние update_s0,727/step_s0,760. Эти данные не являются оценкой action error или качества захвата. Evidence: [training-summary.json](evidence/2026-11-18-pilot/training-summary.json).

Холодная загрузка через штатную LeRobot/PEFT factory прошла: **все80adapter tensors совпали точно**, все конечны, все LoRA B обновились; сохранённые processors совпадают с train-only statistics. Полный checkpoint: `E:\RoboHand\runs\2026-11-18-eb300-pilot\training\pi05-lora-quantiles-v2\checkpoints\001000\pretrained_model`.

## Воспроизведение и границы

Численные [case manifest](evidence/2026-11-18-pilot/case-manifest.json), [качество всех попыток](evidence/2026-11-18-pilot/data-quality-audit.json), [контракт датасетов](evidence/2026-11-18-pilot/dataset-verification.json), [конфигурация обучения](evidence/2026-11-18-pilot/train-pi05-quantiles-config.json) и installed-package inventories сохранены в Git. Полные сцены/геометрия, записи/изображения, weights, raw logs и одноразовые вызовы готовых API остаются в частном packet наE/D.

Официальные команды на данном ПК:

```powershell
& 'E:\RoboHand\tools\lerobot-record-win-2026-11-18\.venv\Scripts\lerobot-edit-dataset.exe' --config_path 'E:\RoboHand\runs\2026-11-18-eb300-pilot\cli-configs\pilot-merged.json'
# Для split/recompute_stats — сохранённые split.json/recompute-train-stats.json.
# Не повторять поверх уже существующих output datasets.
wsl -d Ubuntu-22.04 -- bash /mnt/e/RoboHand/runs/2026-11-18-eb300-pilot/train-pi05-quantiles.sh
```

Обучение в existing output не перезапускать: для новой итерации задать отдельный output или применить штатный resume recipe с сохранённым training state. Paired evaluation использует одноразовый `evaluate-paired-stock-policy.py`/`evaluate-paired-quantiles.sh` из private run; они вызывают stock factories, PEFT context и `eval_policy`, без своего inference/action loop. Для точного восстановления сохраняются code pins, пакетные версии, main config и исходные данные.

Пилот покрывает только pickup/hold одного карандаша, одну instruction и небольшую сетку стартов. Ни image grounding, ни разные предметы/освещение, ни recovery после ошибок, ни ориентация для typing ещё не доказаны. Даже успех на всех четырёх validation poses не будет универсальным grasp benchmark. Sim camera/actuator/friction параметры номинальны; physical hardware и runtime LLM supervisor не подключались. Покупки и real MCU motion эта итерация не включает.

## Результаты closed-loop evaluation

| Группа | Сцен | Expert raw / quality | Base raw / quality | LoRA1000 raw / quality |
|---|---:|---:|---:|---:|
| Validation |4|4 / 4|0 / 0|0 / 0|
| Valid stress |3|1 / 0|0 / 0|0 / 0|

Главное сравнение использует один сохранённый QUANTILES processor и те же seeds. Ни teacher, ни целевые joint/EEF trajectories не подаются policy. Оба neural-варианта завершили все семь сцен без bootstrap exceptions. LoRA peak allocated9 458 912 256байт; baseline держит в памяти отключённые adapter tensors, поэтому это не чистый сравнительный memory benchmark. Wall time включает WSL raster rendering и video,25Hz означает simulation clock, не подтверждённый realtime control.

В метриках LoRA не подтверждён подъём/двусторонний удерживаемый хват; low train loss не стал task success. Этот результат не устанавливает причину: малый optimization budget, narrow demonstrations, неподходящее покрытие contact/recovery states и степень заморозки модели остаются гипотезами. Upstream PI05 tutorial использует30kupdates/batch64 в другом LIBERO/full-expert setup; generic PEFT guide — иной SmolVLA example. Их бюджеты/результаты не являются обещанием успеха EB300 и не сравниваются напрямую с нашим1000/batch4 pilot.

Сохранены14полных фактических wrist MP4. [GIF base / LoRA](<E:/RoboHand/LATEST/SIMULATION/EB300-PILOT-LORA/EB300-pi05-base-vs-lora.gif>) показывает именно неудавшиеся neural rollouts validation-00, не успешный expert trace.75frames/18s/1024×338, SHA256 `57fbf5afef70e4e5162549e9333b593585a831ee1dcd59aae9e43e46ca6797bb`. Правило выбора сцены, source video hashes и отсутствие crops/teacher записаны в `policy-comparison-provenance.json`; GIF не заменяет таблицу всех случаев.

Рабочий human index: `E:\RoboHand\LATEST\SIMULATION\EB300-PILOT-LORA\README.md`; datasets/runtime/checkpoints остаются в независимом run. Это исследовательский кандидат, не принятый motor runtime. Native CAD, baseline scene и25посторонних dirty files глобального репозитория проверены по прежним hashes и сохранены.

**Дополнительная диагностика выполнена:** stock eval на знакомой **train-00 тоже неуспешен**, raw/qualityFalse, held0s, final lift≈−0,78м. Max pad penetration0,043мм, other penetration7,137мм, non-tool0,170мм: известный показ не воспроизведён. [Данные](evidence/2026-11-18-pilot/training-calibration-result.json). Это отдельная in-distribution проверка; в семь held-out scores не включена. Её первый bootstrap остановился до управления на слишком строгом сравнении float64 metadata с сохранёнными float32 stats; R2 использует то же dtype-aware сравнение, что успешно прошедший paired eval. Начальные source/log сохранены; это не дополнительный неудачный robot episode.

Следующий gate — **сначала повторить известный показ**. Увеличить budget официального обучения с сохранённым data/action contract и проверять одну calibration-сцену до принятия; при сохраняющемся провале проверить семантику state/action/chunk и обучаемые компоненты по upstream, без нового controller. Затем расширять contact/recovery demonstrations и вновь оценивать visual coverage на отдельных сценах. Текущий1000/batch4 —≈1,175sample draws на frame, а не исчерпывающее обучение. По measured0,76s/step бюджет5000updates на том же batch — ориентировочно около часа плюс init/checkpoint/eval; это оценка compute, не обещание выученного хвата. Не переходить к typing или агенту-координатору при0успехов; не менять модель/метод лишь по train loss. Новая архитектура/controller/adapter по-прежнему требует отдельного конкретного scope.

Все artifacts сохранены отдельным private packet `EB300-PILOT-LORA-2026-11-18` наE иD; [путь/receipt и восстановление](../latest-artifacts.md). Full base weights/venvs и посторонние dirty files исключены; LoRA checkpoints/optimizer, dataset, все попытки, source pins, full videos и raw diagnostics включены. SHA/CRC/каждый file hash и Git commits фиксируются в receipt/manifest. CAD R8 остаётся принятой отдельной сборкой.
