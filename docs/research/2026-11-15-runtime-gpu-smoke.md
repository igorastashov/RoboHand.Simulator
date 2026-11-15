---
tags: [robohand, runtime, docker, wsl, gpu, typing, reuse-first]
type: verification
updated: 2026-11-15
status: cuda-compute-passed-upstream-image-building
---

# После переноса Docker: GPU и pinned typing runtime

Перенос Docker на E: выполнен владельцем и проверен Codex. **Контейнер видит RTX 3090; отдельный официальный CUDA compute benchmark прошёл.** Штатный `./so101 setup` запущен. Завершение сборки, запуск Newton и RTX-камеры пока не подтверждены.

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
3. **Импорты pinned runtime/asset — впереди после setup.** Штатный `./so101 debug` проверяет torch CUDA availability, OVRTX/ovstage imports и наличие Workshop asset. Он ещё не выполняет physics step/render.
4. **Reference Newton physics и teacher smoke — впереди.** Требуется actual rollout, а не просто успешная сборка Docker.
5. **Reference RTX wrist-camera и vision smoke — впереди.** Teacher запускается без wrist renderer; его успех отдельно не доказывает камеру.
6. **EB300 keyboard task — следующий отдельный gate.** До него проверяем 5→6 actions/asset/drive/config hooks. Reference rollout не выдаём за EB300 и тем более за физическую руку.

Машиночитаемый снимок: [runtime-evidence.json](2026-11-15-runtime-evidence.json). Полные логи остаются локально на E:.

## Точный upstream и штатная установка

[NVIDIA/so101-typing-task @ 7aec2ed26dce8c88ae007a2714680cce572e1466](https://github.com/NVIDIA/so101-typing-task/tree/7aec2ed26dce8c88ae007a2714680cce572e1466). Прочитаны actual README, `docs/setup.md`, `docs/tutorial.md`, `scripts/tutorial/cli.py`, Dockerfiles и smoke config.

Источник:

```text
E:\RoboHand\upstream\so101-typing-task-7aec2ed-linux
```

Из существующего локального pinned Git snapshot получен штатный `git archive` с `core.autocrlf=false`, `core.eol=lf`. SHA256 source TAR: `03c59934226b6ea8f89d9e6da1e29aa3c15397ca620f959655cca93e35392a62`. Никаких своих runner/controller/exporter не добавлено. Более ранний CRLF archive сохранён отдельно; Linux-путь выше содержит LF. Попытка local clone из partial/promisor cache не смогла получить отсутствующий blob — это ограничение cache, а не доказательство повреждения upstream.

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

Журналы: `E:\RoboHand\runs\2026-11-15-typing-runtime\setup-plan.log`, `setup.log`. Штатный CLI собирает `so101-typing-public:dev`, затем `so101-tutorial:dev`. Начальный pull большой: в том числе слои 5,09 и 10,58 ГБ, весь unpacked runtime порядка 50 ГБ плюс кэши. Загрузка base digest и pinned внешних source/assets стартовала успешно; итоговое завершение фиксируется отдельно.

## Минимальный следующий прогон

По actual `docs/tutorial.md` штатный сценарий после setup:

```bash
./so101 debug
./so101 train teacher --config configs/tutorial/smoke.json --output output/smoke-teacher
./so101 evaluate teacher --config configs/tutorial/smoke.json --run output/smoke-teacher --suite random --max-steps 2
./so101 train vision --config configs/tutorial/smoke.json --teacher output/smoke-teacher --checkpoint latest --output output/smoke-vision
./so101 evaluate vision --config configs/tutorial/smoke.json --run output/smoke-vision --max-steps 2
```

В smoke config **2 environments, 2 teacher iterations, 2 vision iterations, 1 warmup iteration**, save interval 1. Двух обновлений недостаточно для обученного typing-навыка; усечённая evaluation закономерно не доказывает успех задачи. Нужны выходные checkpoint/config/log и отсутствие runtime ошибок. GPU memory, фактические duration и ошибки записываются после запуска.

Для WSLg `DISPLAY=:0`, но обычного GDM Xauthority нет. `debug --viewer` в этом pin проверяет наличие такого файла. Пустой подставной файл не создаём ради зелёной проверки. Начинаем со штатного headless пути; отдельный интерактивный viewport/replay проверим по поддерживаемой WSLg/X11 конфигурации. Наличие окна MuJoCo не подтверждает RTX viewer NVIDIA.

В `models/` этого snapshot находятся metadata/README, а не готовые `.pt/.onnx` weights. Обучение воспроизводится; наличие текста release manifest за доступные веса не выдаётся. ACT и PPO остаются разными методами.

[Индекс Simulator](../index.md) · [R8: начать здесь](../start-here-r8.md) · [Аудит hooks](2026-11-15-manual-control-and-typing-hooks.md).
