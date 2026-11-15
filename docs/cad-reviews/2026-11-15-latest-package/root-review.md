---
tags: [robohand, eb300, latest, review, recovery]
type: review
updated: 2026-11-15
status: accepted-at-current-path
---

# Принят отдельный рабочий комплект LATEST

Открывать `E:\RoboHand\LATEST\CAD\EB300.a3d`. Главный файл один, остальные 23 native-файла в `CAD\components`. Геометрия/сопряжения R8 сохранены. [Отчёт CAD-агента](cad-agent-report.md), [пофайловый manifest](native-closure.json).

Root независимо запросил штатный `GetExternalFilesNamesEx(True)` в новой MCP-сессии: получено 23 существующих пути, все внутри LATEST. Проверены SHA256 всех 24 файлов. Источники не переписывались; после упаковки наблюдалось позднее пересохранение старого root. Отдельное read-only сравнение подтвердило 26 прежних матриц и 18 прежних корректных root сопряжений, без изменений 23 геометрических зависимостей. [Независимый readback](root-readback.json), [сравнение пересохранения](source-resave-review.json).

При первом разборе MCP был прочитан только bool-блок, затем обнаружено flattening текстовых outputs. Для доказательства использован `structuredContent.result = [success, paths, types]`; первый текстовый блок `true` сам по себе не является списком зависимостей. CAD из-за этого не пересохранялась и не менялась.

В `E:\RoboHand\LATEST` добавлены памятка и стандартный Windows-ярлык `ПОСМОТРЕТЬ-В-MuJoCo.lnk` на уже установленный viewer/сцену. Проверены target, arguments и существование путей. Ярлык использует Python на E: и описание/meshes в Simulator на D:; новый UI или исполняемый controller не создавался. Геометрия/nominal physics текущего MJCF не менялись.

Комплект LATEST сохранён в `E:\RoboHand\releases\EB300-LATEST-R8-2026-11-15\EB300-LATEST-R8-2026-11-15.zip` и `D:\RoboHand-Backups\EB300-LATEST-R8-2026-11-15.zip`, SHA256 `6f88147021f3bbcf818b1878b62da3b84a766833affd1eff6d5443686735fc5a`. Проверены CRC ZIP, SHA256 26 членов (24 native + памятка/ярлык), совпадение зеркала. [Запись проверки](archive-verification.json). Прежние R8/R7S archives сохранены.

`CURRENT.json` на E:/D: указывает на новую рабочую сборку и хранит исторические пути/hashes отдельно. При восстановлении сохранять весь layout `E:\RoboHand\LATEST`; другой путь/ПК не тестировался. Это принятие упаковки существующей модели, не проверка новых движений, приводов, GPU, обучения или реального железа.

[Актуальные файлы](../../latest-artifacts.md) · [Индекс](../../index.md).
