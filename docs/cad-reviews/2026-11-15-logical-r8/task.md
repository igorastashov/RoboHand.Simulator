---
tags: [robohand, eb300, cad, logical-tree, jaw-typing, release]
type: execution-brief
updated: 2026-11-15
status: completed-accepted-jaw-profile
---

# R8: понятное дерево и нажатие обычной губкой

**Завершено:** [root review](root-review.md), [актуальные файлы/архивы](../../latest-artifacts.md). `IUserFolder` не принялcomponents; применён проверенный официальный `IParts7.CreateSubAssembly`. Получены3новые rigid подсборки и7узловroot, стержень/держатель удалены,6axes сохранены. Root независимо проверил49состояний, jaw/camera frames и manifest. Ни один из23R7S files не изменён.

[Индекс](../../index.md) · [R7 acceptance](../2026-11-14-cad2/root-review.md).

## Прямые требования владельца15.11

- Организовать разрозненные компоненты в логические узлы/сборку.
- Сохранить финальную версию, чтобы она не потерялась.
- Убрать стержень: учить обычный универсальный захват нажимать кромкой губки, подбирая ориентацию руки.
- Уточнить следующие шаги/входы владельца, докупаемое железо и необходимость фирменного приложения.
- Подтверждено наличие всего базового комплекта:6двигателей с редукторами,6драйверов, Mega и блока питания. Концевики и Redmi8A подтверждены ранее.

## Сначала сохранение

Рабочая R7 после пересохранения уже отличается тремя файлами от прежнего byte manifest. Ничего не откатываем. [Read-only audit R7S](current-r7s-readonly-audit.json) подтвердил сохранённое состояние:28+25Validmates,17poses отличаются от прежнего accepted reference менее0.001мм; dirty documents отсутствуют,23hash до/после чтения совпали. Ни Save, ни Rebuild не выполнялись.

Снимок текущих23native files, description package и прежних evidence сохранён штатным `Compress-Archive` в [E-архив](<E:/RoboHand/releases/EB300-R7S-2026-11-15/EB300-R7S-2026-11-15.zip>) и [D-копию](<D:/RoboHand-Backups/EB300-R7S-2026-11-15.zip>). [Проверка ZIP/204manifest files/SHA256](r7s-release-verification.json). Это recovery archive: native ссылки сохраняют прежний work-root path; не обещаем переносимость A3D при произвольном перемещении каталога.

## Выбранный ready путь

Исследуется официальный v25 `IPart7.UserFolders` / `IUserFolders.Add` / `IUserFolder.SetObjects`, тип612. Это логические папки дерева; они сохраняют physical component hierarchy и интерфейсы шести суставов. Не объединять всю руку в rigid solid. Настоящие subassemblies нужны только если обнаружится практическая необходимость и проверенный штатный путь, а не ради внешнего вида дерева.

MCP остаётся `hymaxo/kompas3d-mcp@adef44fdc41401af3b239a5c9b1a4e108e1a237a`; используется установленный SDK и существующий api_invoke. Новый server/exporter/framework не создаётся.

## Разрешённые изменения

Новый root A3D — `E:\RoboHand\data\cad-work\2026-11-14-eb300-c2133b98\outputs\EB300-R8-jaw-typing.a3d`. Допустим стандартный root SaveAs рядом с исходным:23R7S files остаются shared read-only dependencies. Нельзя сохранять/переписывать их; сравнить SHA256 до/после. Не использовать SaveAll и не закрывать чужие unsaved документы.

1. Smallest isolated user-folder smoke на собственной R8-копии → save/close/reopen → проверить имя/состав/poses/mates.
2. Удалить только2root dependent-position mates и2typing components: `Typing-holder-NOMINAL-R2.m3d`, `Typing-stylus-NOMINAL-R1.m3d`. Старые файлы сохранить как историю, активная assembly и sim profile ими не пользуются.
3. Логически сгруппировать rigid links, запястье, захват и3компонента телефона. Ожидается15top components и26root mates; механизмgripper25mates неизменен.
4. Выбрать контактную кромку реальной губки по source mesh/native frame, явно указать выбранную jaw/pose. TCP — semantic frame, не добавленный стержень/кнопка/концевик. Раскрытие захвата пока captured; обобщённая motor adaptation захвата не прячется под данными.
5. Save/close/reopen и поосевые±5°checks, latest references/closure/preview. Root обновляет стандартные URDF/MJCF/config данные и проводит независимые проверки.

Итоговая R8 получает отдельный проверенный архив и постоянный latest index. До приёмки R8 рабочей точкой восстановления остаётся R7S. Шесть физических осей не блокируются ради аккуратного дерева; UI folders не меняют robot-description links.
