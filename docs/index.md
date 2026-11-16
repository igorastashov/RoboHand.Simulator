---
tags: [robohand, simulator, index]
type: index
updated: 2026-11-16
---

# Документация Simulator

| Документ | Назначение |
|---|---|
| [Рабочий стол EB300 R1](desktop-workcell-r1.md) | Рука слева спереди, PC справа сзади; шесть номинальных приводов, камера и 10/10 заданных нажатий A |
| [Разрешённая адаптация обучения EB300](research/2026-11-16-eb300-training-adaptation.md) | Решение владельца16.11, точные ограничения upstream и приёмка six-axis teacher/vision |
| [Native обучение EB300: результаты](research/2026-11-16-eb300-native-training.md) | Исправленный drive/contact asset,6actions,100stable steps, teacher/vision PPO, evaluation и replay; навык ещё не обучен |
| [Интеграция с NVIDIA typing](../integrations/nvidia_typing/README.md) | Патч к7aec2ed, штатный Docker overlay и конфигурация EB300 без нового framework |
| [Обзор и точное зрение Redmi 8A](research/2026-11-16-camera-coverage.md) | Телефон подтверждён владельцем; отдельного ширика нет, полный кадр/crop и готовая практика обзорная+wrist |
| [Native Linux: камера и обучение](research/2026-11-15-native-linux-runtime.md) | Дополнительный GPU-host, pinned runtime/source, камера, teacher/vision PPO, оценки и MP4 проверены; SO-101 только reference |
| [Рабочий план EB300 от15.11](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-15-execution-plan.md>) | Последовательность сервер/reference → шесть осей EB300 → нажатие → PPO/vision, спринты и участие владельца |
| [Локальная разработка и дополнительный GPU-сервер](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/remote-gpu-workspace-2026-11-15.md>) | Частный план ресурсов/переключения стенда; работа остаётся на этом ПК; обслуживание завершено, GPU-проверки пройдены, возврат стенда описан |
| [Docker на E: и CUDA smoke](research/2026-11-15-runtime-gpu-smoke.md) | Docker/CUDA/Newton и два PPO teacher updates прошли; RTX vision получил Vulkan error в WSL2, нужен совместимый host |
| [URDF и MuJoCo простыми словами](urdf-mujoco-explained.md) | Как из CAD получены звенья/суставы, что содержит текущая сцена и как начать ручной осмотр |
| [Отдельная рабочая сборка LATEST](cad-reviews/2026-11-15-latest-package/cad-agent-report.md) | Один корневой A3D, 23 внутренние зависимости, повторное открытие и сохранность исходников |
| [Ручное управление и typing hooks](research/2026-11-15-manual-control-and-typing-hooks.md) | Геймпад необязателен; готовые MuJoCo/Isaac/MoveIt пути и actual source 5→6 joints |
| [Начать здесь: EB300 на этом ПК](start-here-r8.md) | Простое объяснение готовности R8, команда просмотра, ближайшие шаги и участие владельца |
| [Что публикуется в Git](publication-scope.md) | Локальная геометрия, полные журналы, лицензии и восстановление assets |
| [Актуальные файлы: R8](latest-artifacts.md) | Открывать эту сборку; URDF/MJCF без стержня, архивыE/D, восстановление и hashes |
| [R8: логические узлы и обычная губка](cad-reviews/2026-11-15-logical-r8/root-review.md) | 7узлов,3native подсборки,49состояний crosscheck, jaw-contact, известная окклюзия камеры |
| [CAD-2: результат ревью и физический asset](cad-reviews/2026-11-14-cad2/root-review.md) | Полное запястье, шесть joints, native motion, независимые25 поз, nominal physics и границы готовности |
| [Открыть EB300 на текущем ПК](cad-reviews/2026-11-14-cad2/viewing-and-next-step.md) | Готовые native/URDF/MuJoCo файлы, штатный viewer, что измерить и какой следующий gate |
| [CAD-2: выполненное поручение и приёмка](cad-reviews/2026-11-14-cad2/task.md) | Независимая workcopy, rigid links/запястье/J1–J6/tool/Redmi, проверки и standard robot-description handoff |
| [Первая сборка EB300: 1part.a3d, 14.11](cad-reviews/2026-11-14-1part-c2133b98/root-review.md) | Переданный CAD, snapshot/хеши, реальное дерево/сопряжения, ограничения аудита и следующий проход |
| [Ближайшие действия с 14.11](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/plans/2026-11-14-next-steps.md>) | Что требуется владельцу сейчас, даты 14–29.11, текущие ограничения ПК и этапы до обучения |
| [Задание отдельному CAD-агенту](cad-agent-task.md) | Входы, ожидаемые выходы, MCP/read-only этап, приёмка и prompt для нового окна |
| [Настройка MCP 09.11](research/2026-11-09-kompas-mcp-setup.md) | Installed pinned server, SDK/protocol/COM smoke, project-scoped Codex config и границы проверки |
| [Тест CAD-агента: цанга по чертежу](../cad-experiments/collet-2026-11-09/review-notes.md) | Принята R7: M3D/STEP/STL/preview, проверки, допущения, длительность27:20/36:34 |
| [Что хранится в каком репозитории](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/agent-harness-plan.md>) | Simulator — CAD/среды/configs, Control — исполнение skills/policy, общие recipes и глобальные планы отдельно |
| [Typing reference и EB300 gaps](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/keyboard-typing-reuse.md>) | Project-pinned PPO recipe, kit-less runtime, missing weights, 5→6 actions |
| [КОМПАС/MCP/URDF](<../../../../../_ПЛАНЫ_/embedded-robotics-market-research/research/projects/robohand/kompas-mcp-and-urdf.md>) | Existing MCP candidates, actual local state, стандартный CAD handoff |
| [CAD-комплект для импорта](cad-handoff.md) | STL-first; пошаговое сопряжение двух STL-компонентов в v25, оси/опоры, joints/masses, захват/Redmi |
| [Стол, EB300, Redmi 8A и предметы](workcell-scene.md) | Состав виртуального рабочего места, camera/IMU profiles, physical assets |
| [Simulation-first EB300, 08.11](simulation-first.md) | Действующий план: CAD, физическая среда, камеры, данные и обучение до готовности железа |
| [Исследование 07.11.2026](research/2026-11-07-state.md) | Что собирается, что моделируется, что ещё не реализовано |
| [WSL и ROS 2](wsl-ros2-setup.md) | Ранние инструкции установки; пути требуют адаптации |
| [Геометрический YAML](../robohand_ws/src/robohand_description/config/kine_eb300_approx.yaml) | Приблизительные параметры; пока не загружается из xacro |
| [R8 URDF](../robohand_ws/src/robohand_description/urdf/eb300_jaw_typing_r8.urdf) | Актуальный default:6суставов, штатная губка, телефон и frames |
| [Исторический Xacro](../robohand_ws/src/robohand_description/urdf/robohand.urdf.xacro) | Ранняя приблизительная модель; не геометрия принятойR8 |
| [Launch](../robohand_ws/src/robohand_description/launch/display.launch.py) | robot_state_publisher, GUI суставов, RViz |

Наверх: [README](../README.md). Сборка description и физическая симуляция учитываются как разные результаты.
