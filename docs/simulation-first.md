---
tags: [robohand, simulator, eb300, plan]
type: plan
updated: 2026-11-14
status: planned-not-implemented
---

# Виртуальная EB300 — первый исполняемый backend

**Текущая очерёдность 14.11:** [задачи владельца, ближайшие недели и gates](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-14-next-steps.md>). MCP установлен и проверен на отдельной цанге; аудит CAD EB300 и GPU/physics smoke typing recipe ещё не подтверждены. Использовать runtime принятого pinned проекта. Полный Isaac Sim, отдельное подключение YAML и новый SimBackend не являются обязательными предварительными deliverables.

**Последнее решение владельца:** [reuse-first](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/reuse-first-policy.md>). Сначала [готовый typing recipe](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/keyboard-typing-reuse.md>) и smallest smoke, затем CAD/asset/hooks EB300. Full Isaac Sim и новая собственная инфраструктура не являются обязательным первым шагом.

Решение владельца 08.11: только EB300; сначала весь virtual learning pipeline, физическая прошивка позже. CAD доступен, владелец — конструктор; путь/ревизию ещё зарегистрировать.

Системные документы: [архитектура](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/simulation-first.md>), [календарь](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-08-simulation-first.md>), [совместимость стека](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/stack-2026-2027.md>).

## Текущее состояние

ROS2 description/RViz, приблизительные размеры. config_file объявлен, но YAML не загружается xacro; внешняя конфигурация пока не меняет геометрию. Нет physics task, камер или обученной EB300. Это отдельные задачи, не завершённая симуляция.

## Предыдущий перечень задач, уточнённый планом 14.11

1. Окружение/versions принятого typing recipe, physics + saved camera frame + peak VRAM. Чистая установка Lab 3.0 не заменяет patched runtime проекта; Windows/Docker/GPU/место проверить до большого setup.
2. Asset manifest: CAD revision, per-link meshes, units, joint origins/axes/limits, TCP, masses/COM/inertias с источником.
3. Заполнить существующий Xacro/URDF данными EB300 и зафиксировать ревизию/производные meshes. Отдельное подключение YAML опционально; новый pipeline ради него не нужен.
4. Физическая EB300: J1–J6 + gripper, collision meshes, ограниченная динамика приводов, table/object/tray/reset.
5. Применить готовый runner/backend выбранного проекта; проверить observation/action/time/frames. Новый SimBackend не создавать без отдельного решения после фиксации gap; не зависеть от готовности Mega/serial.
6. Cameras, teacher/teleop, запись, task evaluator и reproducible seed.
7. Domain randomization после рабочего nominal baseline; sim2sim и identification позже.

## Приёмка S2

Все оси имеют верные знаки/нули/пределы; 10 resets воспроизводимы, physics стабильна; захват удерживает предмет контактом; log/config/versions и видео сохранены. Неизвестные dynamics отмечены estimated. CAD-correct proxy до измерений не называем идентифицированным twin.

Наверх: [индекс](index.md). Firmware/OneMotor сохраняются для будущего physical transfer.
