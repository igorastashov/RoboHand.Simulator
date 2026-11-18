---
tags: [eb300, pi05, lora, continuation, calibration, evaluation]
type: experiment-record
updated: 2026-11-18
status: first-clean-learned-grasp-repeatability-open
---

# EB300: продолжение LoRA и знакомая сцена

[Индекс](../index.md) · [Первый пилот и0/4+0/3](2026-11-18-pilot-and-lora.md).

**Итог итерации:** на gentle checkpoint200 при штатном execution horizon50 получен первый neural grasp, прошедший все прежние physics gates. Три cold calibration rollouts: **raw2/3, quality1/3**; один успешный захват сам по себе не означает устойчивый навык. Первый episode: lift58,93мм/hold0,538s, pad0,0282мм, other0,0991мм, non-tool0,0468мм, equality0,0219мм, force-cap fraction0,956. Other peak относится к desktop; до лимита0,1мм остаётся около0,0009мм номинальной sim penetration, запаса устойчивости этим не доказано. Это известная train-00, не visual search/generalization и не real hardware.

Владелец поручил продолжить. Первая цель — физически воспроизвести знакомый train-00; новый навык/typing/агент-координатор пока не добавляем. Архив предыдущего пилота, CAD, сцены, dataset и его normalization сохраняются.

| Сохранённый вариант | Execution/denoising steps | Raw /3 | Quality /3 |
|---|---|---|---|
| Main500, прежние11train |10/10|1|0|
| Main500, только больше denoising |10/50|0|0|
| Main500, execution horizon50 |50/10|2|0|
| Episode0-400, прежние данные |10/10|3|0|
| Gentle200, новые мягкие показы |10/10|0|0|
| Gentle200, execution horizon50 |50/10|2|1|
| Gentle500, final-budget endpoint |50/10|3|0|

Все строки — calibration на одном знакомом старте с одним правилом seeds и неизменными quality gates, не независимые held-out benchmarks. Изменения данных и горизонта вместе не позволяют приписать улучшение одному фактору. Final-budget500 выбран до его оценки и проверен отдельно; все результаты сохранены.

## Готовый upstream путь

`huggingface/lerobot@7910c20a75834ad3fa6a9792df4d44a614d1bba6`: actual `policies/factory.py:386–447` поддерживает загрузку существующего PEFT adapter с `is_trainable=True`; `lerobot_train.py:637–650` пропускает повторное оборачивание PeftModel. Стандартный trainer поддерживает `env_eval_freq` и HubEnvConfig: создаёт временную среду, вызывает `eval_policy_all`, закрывает её и восстанавливает train mode. `configs/default.py:191` задаёт штатные eval fields.

Это **fine-tuning от сохранённых весов с новым optimizer/scheduler**, не точный resume прежнего optimizer/RNG. Parent — `pi05-lora-quantiles-v2/checkpoints/001000/pretrained_model`, adapter SHA256 `70f55eab7522e2a3b1b844d64cdff2e51d13b6c3b3bd54af694f2526e8c12331`. Старый scheduler завершил decay на1000updates; новый план имеет отдельный output/config и явно заданный budget. Новых model dimensions, layers/controller/solver не создаём.

## Дизайн до запуска

- Сначала stock CLI smoke:1optimizer update, batch16,1полный train-00 rollout через встроенный env evaluation. При CUDA OOM сохраняем failed log и выбираем меньший batch отдельным config; не считаем resolver GPU smoke.
- Основной стартовый budget:2000дополнительных updates/batch16, lr2.5e-4, warmup50, cosine decay2000до2.5e-5, rank64/alpha64. Это32000sample draws вместо4000в первом пилоте, около9,4draws на исходный frame дополнительно. Оптимальный budget/достаточность этим не утверждаются.
- Save и встроенная проверка train-00 каждые250updates; n_episodes1, eval batch1,450ticks, seed1000. Это training calibration, не held-out score. Во время обучения validation/stress не используются.
- Встроенный `eval_policy_all/eval_one` сохраняет raw success/video, но отбрасывает произвольные physics metrics. Его успех — только screening. Для принятия checkpoint нужен отдельный cold reload и stock `eval_policy` с прежними penetration/equality/force/hold gates; затем validation и отдельно stress.
- После успешного screening допустимо остановить на сохранённом checkpoint для строгой проверки. В случае отсутствия успеха на всём budget фиксируем результат и исследуем конкретную причину до следующего изменения, без новой самописной runtime adaptation.

Данные прежние:11train/3403frames; один полный Redmi8A640×360, state/action7absolute radians, QUANTILES train-only, без augmentation/zoom/crop/других камер. Четыре validation и три stress остаются отдельными. Счётчик импульсов реального MCU не выдаётся за измеренное положение: hardware в этой итерации не подключён.

Рабочая папка: `E:\RoboHand\runs\2026-11-18-eb300-continuation`. Existing pinned Linux CUDA environment используется повторно, пакеты/драйверы/remote services не меняются. Результаты и фактический batch/compute будут дописаны после запусков.

## Проверки и условное уточнение после250updates

Stock smoke прошёл:1update/batch16, peak11,14GiB,5 410 816trainable params; saved checkpoint и встроенный450tick rollout. Double wrapping штатно пропущен. В основном запуске первые125–250updates занимают≈2,4s/update, peak≈11,2GiB. Первый train-00 screening на250 — raw0/1.

Read-only I/O audit прошёл: recorded/live initial joint state exact0rad; state/task tokens exact; teacher action→stock normalization→unnormalization roundtrip error1,30e-8rad. Full images[1,3,360,640], float[0,1]; mean difference Windows/native recording и Linux/eval render≈1,30e-7, max1/255. Явного расхождения формата не найдено; причина провала этим не установлена. Actual PI05 loss обрезается до семи действительных action dimensions, не усредняется по25пустым координатам.

**Уточнение до наблюдения500screening:** если первые две calibration-проверки250/500 имеют raw0, остановить длинный11episode вариант на сохранённом checkpoint и выполнить отдельный overfit diagnosis на episode0. `DatasetConfig.episodes` и `datasets/factory.py:145` поддерживают штатный `episodes=[0]`; нового sampler/конвертера нет. Budget отдельной проверки500updates/batch16, save/eval100, исходные parent1000weights, те же full-train normalization/action/scene. Это8000draws/309frames,≈25,9повторов одного показанного эпизода. Критерии физики остаются прежними; возможный успех будет только calibration, не доказательство visual generalization. Невыполненный остаток прежнего2000budget не выдавать за завершённый run.

## Первый успешный screening

На additional step500 stock evaluator получил **raw success1/1** на train-00. Episode завершился за290ticks,11,6simulation seconds. Video показывает карандаш между губками; физический evaluator подтверждает lift≥20mm/hold≥0,5s. Проникновения/усилия этим stock aggregator не сохранены, поэтому acceptance пока не объявлен.

По заранее указанному правилу выполнена контролируемая остановка: последний progress565, выбран сохранённый **checkpoint500**, SHA256 `9920f87526689f60ab5dd9314c9980984856ee6d69034573eb83f78e5b602508`. Это parent1000updates/batch4 +500updates/batch16, всего12000sample draws; не завершённый2000additional budget. Checkpoints250/500/optimizer state и полный interrupted log сохранены. Single-episode config **не запускался**: условие двух нулевых screenings не выполнено.

Следом запущен cold reload checkpoint500 и stock `eval_policy` на3rollouts train-00 с прежними quality gates. Torch seed1000 выставляется после загрузки; env seeds1000–1002. Это независимая проверка повторяемости, не побайтное воспроизведение stochastic in-training sample: там CUDA RNG уже продвинут обучением. Если known calibration пройдена, затем оцениваются четыре прежние validation poses отдельно от training и stress.

Strict result при default10inference steps: **raw1/3, quality0/3**. Успешный raw episode поднял предмет61,77мм/hold0,534s, но peak other penetration0,317мм и non-tool0,110мм превысили0,1мм gate. Два других эпизода без удержания.80adapter tensors после cold reload exact; это частичный прогресс, не принятый навык.

До следующего обучения проверяется одна готовая inference-настройка: `PI05Config.num_inference_steps=50` вместо10, тот же checkpoint500, n_action_steps10 и те же3calibration rollouts. Actual `modeling_pi05.py:943–1012` передаёт этот параметр в штатный flow sampler. Число control steps/fps, модель/weights, кадр и критерии контактов не меняются. Это проверка возможной численной погрешности sampling, не утверждение её причины; выбор не использует held-out сцены. В output дополнительно проверяется фактическое значение config в загруженной model.

## Следующая узкая калибровка

После default10strict0/3 и первых двух нулевых raw runs при50steps готовится **отдельное продолжение от main500 на episode0**. Это уточнение первоначального условия: даже появившийся raw grasp не прошёл quality/repeatability gate. Новый config `calibration-episode0-config.json`: штатный `dataset.episodes=[0]`, parentmain500,500updates/batch16, save/eval100, lr2.5e-4/warmup50/decay500. Sampling возвращается к default10, давшему первый raw grasp. Нового controller/сцен/физики/архитектуры нет; full-train normalization сохраняется.

Цель — проверить достижимость известной демонстрации при≈25,9draws/frame вместо одновременного выбора11траекторий. Даже полный успех здесь будет overfit calibration, не доказательство зрительного поиска или обобщения. Восстановление parent500, исходный11episode вариант и его невыполненный остаток budget сохраняются. При первом raw success выполняется прежняя строгая cold проверка; criteria не ослабляются.

50denoising steps завершили3rollouts:raw0/3,quality0/3; улучшения нет. Отдельно проверяется **execution horizon50** при прежних10denoising steps на неизменных main500weights. Это другой параметр: `PI05Config.n_action_steps` default50; `select_action:1503–1508` исполняет очередь предсказанных действий, прежде чем обновлять observation-conditioned прогноз.10было явным LIBERO-reference override. В наших показах есть stationary intervals (episode0:51,9% consecutive command deltas<1e-4rad); гипотеза — частое replanning может обрезать предсказанный переход. Это не доказанная причина. Новый тест сохраняет seeds/3rollouts/physics gates и не использует held-out data; обучение episode0 продолжается независимо. Concurrency меняет wall-time measurements, поэтому performance benchmark из этих запусков не выводится.

## Контакты и следующий показ

Main500/horizon50:raw2/3,quality0/3. Instrumented rerun первого episode сохранил все прежние physics metrics **точно**. Максимум non-pad tool penetration относится к **pencil↔desktop**,0,427мм, нормальная сила в этой contact point1,054Н, t8,968s. Max non-tool — desktop↔jawB_013_5,0,085мм. Это установлено новым **read-only** observer: geom IDs/time/force записываются в metrics, не входят в policy observation и не меняют control/reward/termination/physics.14tests прошли Windows7,224s/Linux19,480s, включая реальную опору карандаша на desktop и reset provenance. Старый runtime сохранён, instrumented copy отдельная.

Single-episode training завершило500updates. Первый raw success на400, на500screening0; checkpoint400 выбран по заранее указанному first-success rule. Его cold calibration дала **raw3/3,quality0/3**, lift63,2–66,1мм/hold0,518–0,524s. Все non-pad tool peaks опять desktop:0,160–0,324мм,0,214–0,725Н в contact point. Non-tool≤0,092мм, equality≤0,029мм, force caps≤0,984. Один pad peak0,106мм тоже чуть выше0,1мм. Удержание выучено для этого старта, требование к качеству подвода пока не принято; обобщение не проверено.

Следующий **data-only** показ использует тот же approved Mink/stock writer, те же arm poses/durations/scene, но final gripper target−0,40rad вместо−0,60rad. Контактный servo angle предыдущих данных≈−0,355rad: уменьшается заданный механический overtravel, а не torque caps/solver stiffness/friction. Это проверяемая демонстрация мягкого закрытия для данного карандаша, не новый force controller и не runtime clamp. Сначала требуется physical expert quality gate, затем официальный fine-tune на новом корректно подписанном dataset. Исходный dataset/weights/критерии не переписываются; сравнительные новые normalizer stats фиксируются явно.

## Демонстрации с мягким закрытием

Для train-00 первый новый expert показ прошёл прежние gates: lift65,48мм, hold0,504s, pad0,017мм, other0,055мм, non-tool0, equality0,0078мм, force-cap fraction0,873. На прежних11обучающих позициях получено **10/11качественных expert episodes**. Train-03 не удержал предмет и получил non-pad penetration1,517мм; сохранён отдельно и исключён. Это проверка эксперта, ещё не результат neural policy. Validation/stress для выбора показов не использовались.

Stock `lerobot-edit-dataset` выполнил merge десяти прошедших datasets и `recompute_stats` со всеми изображениями: **10episodes/3094frames,25Hz**, state/action7, один полный640×360wrist frame. MG995 action q01 изменился с−0,600000до−0,400000rad; остальные статистики измерены заново, не придуманы вручную. Полный новый dataset хранится отдельно в `gentle-demonstration/dataset-merged`; исходные данные не перезаписаны. Его шесть файлов скопированы в disposable native Linux cache и побайтно сверены SHA256. Stats SHA256 `6e5ff7b0528e01a0b00f893193d9a449a136245b1237a0e0d30b036a1dfe1ec9`.

Следующий config использует только episode0 для sampling и статистики всех десяти принятых train episodes. Это проверка известного train-00, не обучение на validation. Parent — previous episode0 checkpoint400, adapter SHA256 `2197ce7cd2a732cdd7d5dc7f6130136c17126ec98fb19ea976c088a57101244a`. Штатный trainer при non-resume (`lerobot_train.py:666–692`) подставляет measured new dataset stats в сохранённые normalizer/unnormalizer processors. Budget500updates/batch16, save/eval100, default10denoising и10execution steps; новый optimizer/scheduler. Первый raw-positive saved checkpoint проверяется cold3с прежними quality gates. Результат и фактическая остановка фиксируются ниже после выполнения.

При записи первые два запуска прервала оболочка PowerShell, трактовав upstream FFmpeg fallback warning в stderr как terminating error. Их незавершённые папки сохранены; повтор выполнен в новых output paths с проверкой exit code и фактического report. Использован штатный PyAV fallback; packages/драйверы/physics не менялись.

На gentle checkpoint100 saved processor mean/std/q01/q99 exact для state/action в обоих pipelines. Первая stock execution проверка100 — raw0/1; на200 — raw1/1. Для200 запущен cold3evaluator, training продолжает прежний budget независимо. Offline audit checkpoint100 вызвал штатный `predict_action_chunk` на пяти **expert observations**: frames0/150/210/260/300. На300MG995 first command−0,378rad против−0,400rad в записи; MAE первых10команд по суставам≈0,0016–0,026rad. Это не closed-loop score и не установленная причина срыва на100; ни эти observations, ни expert targets не передаются модели при автономной оценке.

Численные приложения: [I/O](2026-11-18-lora-continuation-evidence/io-audit.json), [contact provenance](2026-11-18-lora-continuation-evidence/contact-diagnosis.json), [cold episode0-400](2026-11-18-lora-continuation-evidence/episode0-400-calibration.json), [новые expert gates](2026-11-18-lora-continuation-evidence/gentle-expert-quality.json), [датасет/stats](2026-11-18-lora-continuation-evidence/gentle-dataset-audit.json), [точность merge](2026-11-18-lora-continuation-evidence/gentle-merge-content-audit.json), [offline predictions](2026-11-18-lora-continuation-evidence/gentle100-offline-prediction-audit.json). Картинки, geometry, веса и полные traces остаются в локальном private recovery packet.

## Завершённый budget и следующий gate

Новый gentle run завершил все500updates/batch16,8000sample draws на309frames выбранного episode0. Stock screenings100/200/300/400/500: raw0/1/0/1/0 из одного episode на каждом checkpoint; это не quality/repeatability score. Cold final500/horizon50: **raw3/3, quality0/3**, lift63,0–72,6мм, hold0,516–0,536s. Other peaks во всех случаях desktop0,113–0,214мм; один pad peak0,143мм. Equality≤0,029мм, force-cap fraction≤0,962. Дополнительные updates улучшили повтор подъёма в этой проверке, но не обеспечили прежний строгий контактный gate. Преимущество перед другими настройками на малой calibration выборке не является generalization benchmark.

Исследовательский указатель сохраняет gentle200/horizon50 как первый profile со strict passing episode (adapter SHA256 `c76b3325b4acd4217a46f2fbca830b011601b01bb14c71984b4715c82d6edccc`). Final500 и все optimizer checkpoints сохранены рядом. Устойчивый known-start gate не пройден; новые validation/stress rollouts не запускались, прежние четыре validation и три valid stress остались вне этой настройки. [Полная матрица/checkpoint hashes](2026-11-18-lora-continuation-evidence/final-result.json), [final500 cold](2026-11-18-lora-continuation-evidence/gentle500-horizon50-calibration.json), [завершение обучения](2026-11-18-lora-continuation-evidence/gentle-training-result.json), [lineage](2026-11-18-lora-continuation-evidence/runline.json).

[GIF первого чистого neural grasp](<E:/RoboHand/LATEST/SIMULATION/EB300-LORA-CONTINUATION/EB300-pi05-learned-grasp.gif>) сравнивает первый episode прежнего400 и gentle200/horizon50; это реальные stock wrist recordings. На панели указаны **все три** raw/quality outcomes, первый справа проходит strict gate.58frames×200ms, полный кадр уменьшен целиком, без crop; источник/frames/SHA в [provenance](<E:/RoboHand/LATEST/SIMULATION/EB300-LORA-CONTINUATION/learned-grasp-provenance.json>). Этот GIF не показывает checkpoint500 и не подменяет его отрицательную quality оценку.

Следующий рабочий этап: квалифицированные показы точного подвода и восстановления после промаха через уже разрешённый Mink binding; стандартный multi-episode fine-tune на расширенном train coverage. До typing и LLM supervisor нужны повторяемый чистый известный старт, затем независимые положения предмета и recovery. В этой итерации новый controller/архитектура/камеры не создавались. Nominal sim параметры ещё требуют измерений на железе.

Рабочая CAD `E:\RoboHand\LATEST\CAD\EB300.a3d` и прежний baseline scene сохранены по исходным SHA256;25чужих dirty files глобального репозитория проверяются побайтно. Shared GPU host/стенд не использовался. Private continuation ZIP наE с зеркаломD содержит datasets, все удачные/ошибочные попытки, checkpoints/optimizer, actual videos, exact configs/source pins и проверенный способ восстановления с предыдущим пилотным пакетом. [Human index и recovery receipt](<E:/RoboHand/LATEST/SIMULATION/EB300-LORA-CONTINUATION/README.md>); Git содержит численные evidence и исходники observer, геометрия/видео/веса остаются локальными.
