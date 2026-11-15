---
tags: [robohand, runtime, docker, wsl, gpu, typing, reuse-first]
type: verification
updated: 2026-11-15
status: newton-teacher-passed-rtx-camera-unavailable-in-wsl2
---

# После переноса Docker: GPU и pinned typing runtime

Перенос Docker на E: проверен. **Штатная среда собрана; CUDA compute, Newton, два обновления PPO teacher и короткая evaluation прошли на RTX 3090.** Vision smoke остановился при инициализации OVRTX: `ERROR_INCOMPATIBLE_DRIVER` / `vkCreateInstance failed`. Документация NVIDIA подтверждает ограничение local OVRTX в WSL2. Наша EB300 task ещё не перенесена; reference не выдаётся за EB300.

Это продолжение [плана по R8](../start-here-r8.md). CAD остаётся `E:\RoboHand\LATEST\CAD\EB300.a3d`; переделка сборки для проверки Docker не нужна. SO-101 в этом этапе — только upstream reference; наша платформа EB300.

## Хранилище и ПК

Проверены фактические settings, WSL registry path, VHDX и работа daemon:

| Проверка | Результат |
|---|---|
| Docker Desktop `CustomWslDistroDir` | `E:\DockerDesktopWSL` |
| Data VHDX | `E:\DockerDesktopWSL\disk\docker_data.vhdx` |
| WSL main VHDX | `E:\DockerDesktopWSL\main\ext4.vhdx` |
| Старый `%LOCALAPPDATA%\Docker\wsl` | VHDX не найден; данные не остались в старом расположении |
| Docker | Desktop 4.44.2, Engine 28.3.2, `desktop-linux`; доступен также из WSL Ubuntu 22.04 |
| GPU | RTX 3090, 24576 MiB, driver 580.97 |
| Свободное место в начале прохода | C: ~228 GiB, E: ~505 GiB; это моментальный снимок до образа/кэшей |

Существующие посторонние контейнеры и образы не очищались/не останавливались. `prune` не выполнялся.

## Проверка NVIDIA по уровням

1. **Discovery/NVML — прошёл.** `docker run --rm --gpus all ubuntu:24.04 nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader` вернул RTX 3090 / 24576 MiB / 580.97.
2. **Реальный CUDA kernel — прошёл.** Повторён [официальный Docker Desktop GPU example](https://docs.docker.com/desktop/features/gpu/):

   ```bash
   docker run --rm --gpus all nvcr.io/nvidia/k8s/cuda-sample:nbody nbody -gpu -benchmark
   ```

   Exit 0, compute capability 8.6, 83968 bodies, 10 iterations, 72.119 ms. Это проверка работоспособности вычислений; CUDA Samples сами предупреждают, что не предназначены для надёжного сравнительного benchmark.
3. **Импорты pinned runtime/asset — прошли.** Штатный `./so101 debug` проверяет torch CUDA availability, OVRTX/ovstage imports и наличие Workshop asset. Он ещё не выполняет physics step/render.
4. **Reference Newton physics и teacher smoke — прошли.** Две среды на `cuda:0`, два обновления, 128 суммарных steps, сохранены два checkpoints и sidecars. Отдельная held-out evaluation завершилась с exit 0; два усечённых эпизода дают 0% успеха, что не является оценкой обученного навыка.
5. **Reference RTX wrist-camera — проверена попытка, не работает в текущем WSL2.** Vision остановился до warmup/PPO на `vkCreateInstance` / `createDevices`. Кадров и vision checkpoints нет. Teacher запускается без wrist renderer; его успех отдельно не доказывает камеру.
6. **EB300 keyboard task — следующий отдельный gate.** До него проверяем 5→6 actions/asset/drive/config hooks. Reference rollout не выдаём за EB300 и тем более за физическую руку.

Машиночитаемый снимок: [runtime-evidence.json](2026-11-15-runtime-evidence.json). Полные логи остаются локально на E:.

## Точный upstream и штатная установка

[NVIDIA/so101-typing-task @ 7aec2ed26dce8c88ae007a2714680cce572e1466](https://github.com/NVIDIA/so101-typing-task/tree/7aec2ed26dce8c88ae007a2714680cce572e1466). Прочитаны actual README, `docs/setup.md`, `docs/tutorial.md`, `scripts/tutorial/cli.py`, Dockerfiles и smoke config.

Источник:

```text
E:\RoboHand\upstream\so101-typing-task-7aec2ed-posix
```

Из существующего локального pinned Git snapshot получен штатный `git archive` с `core.autocrlf=false`, `core.eol=lf`. SHA256 source TAR: `03c59934226b6ea8f89d9e6da1e29aa3c15397ca620f959655cca93e35392a62`. Никаких своих runner/controller/exporter не добавлено. Более ранний CRLF archive сохранён отдельно; Linux-путь выше содержит LF. Попытка local clone из partial/promisor cache не смогла получить отсутствующий blob — это ограничение cache, а не доказательство повреждения upstream.

**Исправлена подготовка source:** первоначальное извлечение TAR через Windows сохранило LF, но превратило upstream symlink `source/isaaclab_tasks/.../so101` в неполную directory copy. Первый teacher остановился на `ModuleNotFoundError: ...so101.agents` до физики. Это ошибка локального извлечения, не установленный дефект NVIDIA. Тот же hash-checked TAR извлечён штатным Linux `tar -xpf` в новый каталог `-posix`; проверены все **289 файлов и 2 symlinks**, mismatches 0. [Source validation](2026-11-15-posix-source-validation.json). Штатные `./so101 build` и `./so101 setup --build` пересобирают затронутые слои; повторный teacher учитывается отдельно. Старые source folders сохранены для диагностики, текущий путь — `-posix`.

Основные зависимости из Dockerfiles:

| Компонент | Pin |
|---|---|
| NVIDIA base image | `nvcr.io/nvidia/isaac-lab@sha256:970621075d00059c309f847fa835709de3fa634537407a7009c586c97893d218` |
| Isaac Lab ancestor источников benchmark | `ooctipus/IsaacLab@6f991d4becf764b151e0a1c775561ddd9c406f72`, затем upstream `benchmark-runtime.patch` |
| Newton | `ooctipus/newton@5205aa49fb900e124f06122bf7e82ed7686a1fde` |
| Python packages | hydra-core 1.3.4, llvmlite 0.46.0, numba 0.63.1, numpy 2.3.1, rsl-rl-lib 5.4.1 |
| Warp / RTX wheels | upstream `runtime/warp.lock`, `runtime/renderer.lock`, hash-checked downloads |
| Robot USD | pinned Anchor-Lab asset `647edd5787cd764cdc041103ad282dc59214d919`, checksum проверяет штатный Dockerfile |

Это benchmark-specific fork/runtime. Установка latest Isaac Lab или произвольного Isaac Sim поверх него не является тем же сценарием. Upstream проверял RTX PRO 6000 Blackwell с другим driver; это не minimum и не подтверждение совместимости 3090. На нашем ПК совместимость устанавливается фактическими smoke tests.

Запущены из WSL в LF source directory:

```bash
./so101 setup --plan
./so101 setup
```

Журналы: `E:\RoboHand\runs\2026-11-15-typing-runtime\setup-plan.log`, `setup.log`. Штатный CLI собирает `so101-typing-public:dev`, затем `so101-tutorial:dev`. Начальный pull большой: в том числе слои 5,09 и 10,58 ГБ, весь unpacked runtime порядка 50 ГБ плюс кэши. После исправления extraction оба образа собраны с exit 0; актуальные image IDs и source label сохранены в evidence JSON. Журналы исправленного прохода: `base-posix-rebuild.log`, `setup-posix.log`.

## Ограничение WSL2 для RTX-камеры

Во время установки дополнительно прочитан [официальный NVIDIA USD Content Agents README @0709377e](https://github.com/NVIDIA-Omniverse/usd-content-agents/blob/0709377ed35fb066361a0d6735d21984b885fe36/README.md#wsl2-rendering). Его раздел WSL2 Rendering прямо указывает: local OVRTX внутри WSL2 не работает из-за отсутствия требуемого Vulkan driver; локальный Warp/CUDA renderer возможен, OVRTX предлагается запускать на совместимом native Linux RTX/Vulkan host.

Это документация другого приложения, использующего ту же библиотеку, а не результат нашего physics/render запуска. Вывод для планирования: **CUDA success недостаточен для camera gate; локальный RTX-этап pinned Linux container в WSL2 нельзя считать поддержанным только по наличию 3090**. На текущем pin debug/teacher/evaluation прошли, а vision воспроизвёл ошибку Vulkan instance/device. Для vision рассматриваем совместимый native Linux host; удалённый OVRTX из другого проекта не объявляется готовым drop-in adapter для typing.

Сам [OVRTX SDK](https://github.com/NVIDIA-Omniverse/ovrtx) публикует и Windows binaries. Это не означает, что Linux/Docker tutorial `so101-typing-task` автоматически получил штатный Windows-native workflow. `usd-content-agents` не устанавливался; его README использован только как первичный источник платформенного ограничения. Драйверы и ОС не изменялись.

## Выполненный минимальный прогон и результаты

По actual `docs/tutorial.md` выполнены debug, teacher и teacher evaluation. Vision запущен и остановился до обучения; последняя команда evaluation vision ниже остаётся невыполненной, поскольку vision checkpoint не создан:

```bash
./so101 debug
./so101 train teacher --config configs/tutorial/smoke.json --output output/smoke-teacher
./so101 evaluate teacher --config configs/tutorial/smoke.json --run output/smoke-teacher --suite random --max-steps 2
./so101 train vision --config configs/tutorial/smoke.json --teacher output/smoke-teacher --checkpoint latest --output output/smoke-vision
./so101 evaluate vision --config configs/tutorial/smoke.json --run output/smoke-vision --max-steps 2
```

В smoke config **2 environments, 2 teacher iterations, 2 vision iterations, 1 warmup iteration**, save interval 1. Двух обновлений недостаточно для обученного typing-навыка; усечённая evaluation закономерно не доказывает успех задачи. Нужны выходные checkpoint/config/log и отсутствие runtime ошибок. Измерено: simulation start teacher 154,185534 с (CUDA graph 98,435125 с), два learning iterations 2,58 и 0,90 с. Model `model_0.pt` и `model_1.pt` — по 2 549 067 байт; SHA256 в evidence JSON. Evaluation startup 151,851079 с; 2/2 эпизода завершились как `step_limit` при лимите 2 шага, success 0%.

Для WSLg `DISPLAY=:0`, но обычного GDM Xauthority нет. `debug --viewer` в этом pin проверяет наличие такого файла. Пустой подставной файл не создаём ради зелёной проверки. Начинаем со штатного headless пути; отдельный интерактивный viewport/replay проверим по поддерживаемой WSLg/X11 конфигурации. Наличие окна MuJoCo не подтверждает RTX viewer NVIDIA.

В `models/` этого snapshot находятся metadata/README, а не готовые `.pt/.onnx` weights. Обучение воспроизводится; наличие текста release manifest за доступные веса не выдаётся. ACT и PPO остаются разными методами.

[Индекс Simulator](../index.md) · [R8: начать здесь](../start-here-r8.md) · [Аудит hooks](2026-11-15-manual-control-and-typing-hooks.md).

## Что воспроизводить дальше

Текущий source: `E:\RoboHand\upstream\so101-typing-task-7aec2ed-posix`. Результаты teacher: `output\smoke-teacher`, evaluation: путь в evidence JSON. Логи находятся в `E:\RoboHand\runs\2026-11-15-typing-runtime`.

Первый `debug` после большой сборки получил 20-секундный timeout Docker; повтор прошёл. При запуске evaluation второй командой той же WSL-сессии был host `FileNotFoundError` для current working directory. Новый WSL shell с явным `cd` по абсолютному пути успешно выполнил evaluation; root cause на уровне DrvFS этим не установлен. Следующие CLI-команды запускать из заново выбранного существующего absolute source directory. Эти ошибки не выдаются за отказ GPU.

Для выбранного Linux/Docker recipe рабочий дальнейший вариант — **native Ubuntu 22.04 x86_64 с RTX/Vulkan**: на этом ПК отдельной загрузкой либо на другом Linux RTX-хосте. Конкретный driver на новом host сверить с требованиями; покупка другой GPU из текущей ошибки не следует. Переустановка/разметка дисков, обновление display driver и платный GPU instance не выполнялись. Выбор host требует решения владельца. До него допустимо продолжать EB300 asset/config/source review и Newton без камеры; новый renderer adapter или Windows-native port автоматически не создаётся.

После выбора host повторяем тот же pinned smoke, затем отдельно проверяем поддерживаемое подключение шести осей EB300, actuator limits, jaw TCP и wrist camera. Ни CUDA/numeric smoke, ни reference checkpoints не заменяют эту работу.

## Последующее решение владельца 15.11

**Историческое состояние до согласованного обслуживания.** Разработка остаётся на текущем Windows-ПК; для RTX-камеры/обучения по необходимости выбран дополнительный native Linux сервер. Восстановлен SSH-доступ, read-only аудит подтвердил Ubuntu 24.04.3, две RTX 3090 через PCI/`/proc`, 8 ядер/16 потоков, около 125,5 GiB RAM и работающий стенд генерации 3D. Аккуратное обратимое переключение ресурсов разрешено, по команде владельца стенд имеет приоритет. Найдено существующее препятствие: загруженный NVIDIA module 580.159.03 не совпадает с NVML 580.178.04 после обновления13.11. Для уже установленного следующего ядра найден matching module; maintenance reboot ещё не согласована. Серверный GPU/RTX smoke не запускался, пакеты и сервисы не изменялись. Это не меняет результаты локальных тестов выше. [Частный операционный план](<../../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/remote-gpu-workspace-2026-11-15.md>), [актуальный маршрут работы](../start-here-r8.md).

## Продолжение на native Linux — проверено 15.11

Владелец разрешил обслуживание; одна reboot загрузила согласованные kernel/module/NVML без переустановки пакетов. Сохранность и реальная работа соседнего стенда проверены. На отдельном native Linux runtime получены wrist-camera PNG, выполнены по два teacher/vision PPO updates и обе короткие evaluations. Обученная печать и EB300 task этим не подтверждены. Полный актуальный результат — в [отдельном отчёте native Linux](2026-11-15-native-linux-runtime.md). История WSL2 и его Vulkan error выше сохраняется.
