---
tags: [robohand, assets, publication, recovery]
type: reference
updated: 2026-11-15
---

# Что сохраняется в публичном Git

RoboHand.Simulator — публичный репозиторий. В нём сохраняются наши URDF/MJCF, численные контракты, настройки штатных инструментов, исследования и результаты проверок. CAD, STL, STEP, изображения и полные журналы обращений к SDK остаются в локальных архивах владельца. Среди исходных assets есть EBG20 с уведомлением Attribution–NonCommercial–NoDerivatives; автоматическую публичную раздачу преобразованных meshes не выполняем. Уведомления и происхождение сохранены в [mesh attribution](../robohand_ws/src/robohand_description/meshes/eb300_cad2/ATTRIBUTION.md) и соседнем каталоге `licenses`.

**Свежий clone без локального комплекта геометрии не является запускаемой сценой.** На текущем ПК meshes уже находятся в `robohand_ws/src/robohand_description/meshes/eb300_cad2/`; `.gitignore` сохраняет их локальными. Ссылки на preview и CAD в технических отчётах также ведут к локальным приложениям. Это не удалённые результаты проверки.

Для восстановления использовать [принятый R8 recovery package](latest-artifacts.md). Внутри ZIP пакет находится в `payload/RoboHand.Simulator/robohand_ws/src/robohand_description/`: восстанавливать его содержимое в `robohand_ws/src/robohand_description/`, сохраняя относительные пути. Перед заменой проверить структуру и manifest архива и сохранить более новые рабочие файлы. У native CAD отдельные абсолютные зависимости; порядок восстановления описан в указателе R8. Не загружать весь recovery ZIP в публичный репозиторий.

До подготовки публикации отдельно сохранён полный снимок Simulator: `E:\RoboHand\releases\RoboHand-Simulator-prepublish-2026-11-15\RoboHand-Simulator-prepublish-2026-11-15.zip`, зеркало `D:\RoboHand-Backups\RoboHand-Simulator-prepublish-2026-11-15.zip`. SHA256: `e91844642084fdd76fd57a0fa1becdfd3199e9cf5fb8c6befac8fe865e866434`. Проверены CRC ZIP, SHA256 каждого из 310 файлов и совпадение зеркала.

В публикуемых JSON удалены только массивы `calls`, содержавшие полные ответы инструментов, включая справочные тексты SDK. Численные результаты, позы, измерения и выводы вне этих массивов сохранены. Поле `_public_summary` указывает SHA256 полного исходного JSON и архив для сверки; полные журналы доступны владельцу в снимке. Контракты робота и независимый `root-acceptance.json` не сокращались.

[Индекс](index.md) · [С чего начать](start-here-r8.md).
