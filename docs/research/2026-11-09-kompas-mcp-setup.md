---
tags: [robohand, kompas, mcp, setup, evidence]
type: research
updated: 2026-11-09
status: installed-protocol-and-app-connect-passed
review: root-reviewed
---

# КОМПАС MCP: установка и безопасная протокольная проверка

[Индекс](../index.md) · [Задание CAD-агенту](../cad-agent-task.md) · [CAD handoff](../cad-handoff.md).

Поручение владельца: настроить готовый MCP, пока он самостоятельно работает в CAD; родительский агент ставит задачи и принимает результат. Установлен pinned hymaxo/kompas3d-mcp. Пройдены реальный stdio handshake, обнаружение инструментов, чтение установленной SDK-справки и одно подключение к уже запущенному v25 Study для app metadata. **Документы не открывали, не переключали, не сохраняли и не проверяли.** Пользовательские конфиги Codex, `.codex/`, индексы и CAD-сборку этот агент не менял; регистрацию MCP выполнил родитель, его evidence отмечено отдельно.

## Фактическая среда

Read-only проверены каталоги/версии файлов, ProgID/CLSID/LocalServer32 и процессы. COM-объект для этого не создавался.

| Проверка | Результат |
|---|---|
| Работоспособная CAD-установка по файлам | `C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin\kStudy.exe`, FileVersion **25.0.0.2735**, ProductVersion `v25` |
| Процесс | `kStudy`, PID **36512** до и после protocol smoke и отдельного COM connect; новый процесс не появился. Путь соответствует v25 Study. Активный документ и его содержимое не запрашивались |
| Каталог v24 Study | Присутствует, но содержит **0 файлов**; установленный рабочий v24 этим каталогом не подтверждён |
| COM | `HKCR\KOMPAS.Application.5\CLSID` = `{6B0B5194-4ACD-4095-9BC1-11179FBBB05A}`; `LocalServer32` указывает на `"C:\Program Files\ASCON\KOMPAS-3D v25 Study\Bin\kStudy.Exe"` |
| SDK | v25 Study `SDK`; найдены `lib/kAPI5.tlb`, `kAPI7.tlb`, `ksConstants.tlb`, `ksConstants3D.tlb`; архив `Help/KOMPAS_SDK_ru-RU.zip`, **403359119 bytes** |
| Python | **3.12.10**, `C:\Users\igora\AppData\Local\Programs\Python\Python312\python.exe`; отдельно установленный default `python` 3.10 для сервера не использовался |
| uv | **0.11.3**, `C:\Users\igora\.local\bin\uv.exe` |
| .NET | Runtime 10.0.7 x64 уже присутствует, SDK только 8.0.403; выбранный Python MCP от .NET не зависит |

Наличие процесса до/после — вспомогательное evidence; оно не доказывает неизменность CAD-документа. Для текущей проверки просмотрен source path; из CAD-related инструментов вызван только `connect` без document operations. Содержимое редактируемых владельцем документов до/после не сравнивалось.

## Выбор готового решения и pin

| Кандидат | Решение |
|---|---|
| [hymaxo/kompas3d-mcp@adef44fdc41401af3b239a5c9b1a4e108e1a237a](https://github.com/hymaxo/kompas3d-mcp/tree/adef44fdc41401af3b239a5c9b1a4e108e1a237a) | Выбран: upstream проверял v25 Home/Python 3.12; локальные COM и SDK — v25. Подключение к приложению **Study прошло**; document/geometry/mates/export API ещё не проверены |
| [SergeySklyarov/Kompas3D-MCP@450772b60700c31964abe1104febcb190795f468](https://github.com/SergeySklyarov/Kompas3D-MCP/tree/450772b60700c31964abe1104febcb190795f468) | По [pinned setup](https://github.com/SergeySklyarov/Kompas3D-MCP/blob/450772b60700c31964abe1104febcb190795f468/docs/operator-guide/codex-setup.md) требует лицензированный v24 x64 и .NET 10 Runtime x64. Рабочий v24 не найден, зарегистрирован v25; сервер не устанавливался и не запускался. COM-регистрацию не меняли |

Перед установкой прочитаны pinned README, `pyproject.toml`, `uv.lock`, startup/lifespan, worker, backend, SDK handlers и регистрация advanced tools выбранного сервера. `pyproject.toml`: Python >=3.12; зависимости MCP <2, Pydantic <3, pywin32, Pillow, PyMuPDF. Версии фактического окружения ниже получены после `uv sync --locked`, не из предположений.

## Проверка lifecycle по source

- [server.py](https://github.com/hymaxo/kompas3d-mcp/blob/adef44fdc41401af3b239a5c9b1a4e108e1a237a/src/kompas_mcp/server.py#L14): создаёт `ComWorker`, регистрирует tools; `main()` запускает stdio. [L43](https://github.com/hymaxo/kompas3d-mcp/blob/adef44fdc41401af3b239a5c9b1a4e108e1a237a/src/kompas_mcp/server.py#L43): lifespan на выходе вызывает `worker.close()`.
- [worker.py](https://github.com/hymaxo/kompas3d-mcp/blob/adef44fdc41401af3b239a5c9b1a4e108e1a237a/src/kompas_mcp/worker.py#L12): constructor создаёт executor с `backend=None`; backend и COM thread инициализируются лишь в `_run`, когда вызывается `worker.call`. `close()` при `backend=None` завершает executor без CAD-вызовов. Прочитанный startup/import path не вызывает `Dispatch`.
- [sdk_search/sdk_read](https://github.com/hymaxo/kompas3d-mcp/blob/adef44fdc41401af3b239a5c9b1a4e108e1a237a/src/kompas_mcp/server.py#L80) вызывают [sdk.py](https://github.com/hymaxo/kompas3d-mcp/blob/adef44fdc41401af3b239a5c9b1a4e108e1a237a/src/kompas_mcp/sdk.py): чтение ZIP/HTML через стандартную библиотеку, без `worker.call`, COM и исполнения HTML. Именно этот путь проверен фактически.
- `blueprint_view` читает image/PDF без CAD по просмотренному source; в текущем smoke не вызывался.
- [backend.connect](https://github.com/hymaxo/kompas3d-mcp/blob/adef44fdc41401af3b239a5c9b1a4e108e1a237a/src/kompas_mcp/backend.py#L38) загружает type libraries, вызывает `client.Dispatch("KOMPAS.Application.5")` и **присваивает `app.Visible = visible`**. Подтверждённого выбора изолированного CAD-экземпляра у этого пути нет. По уточнению ревьюера этот путь вызван один раз только после `GetActiveObject` preflight с исходным `Visible=True`; document operations не вызывались.
- [list_documents](https://github.com/hymaxo/kompas3d-mcp/blob/adef44fdc41401af3b239a5c9b1a4e108e1a237a/src/kompas_mcp/documents.py#L72), [api_catalog/api_describe_interface](https://github.com/hymaxo/kompas3d-mcp/blob/adef44fdc41401af3b239a5c9b1a4e108e1a237a/src/kompas_mcp/bridge.py#L87) способны вызвать `connect`; их названия не делают весь путь read-only. `api_constants` входит в worker, но сам handler не вызывает `connect`; до подключения его constants пусты. Эти tools также не вызывались.

Это аудит указанного source и проверенного ограниченного lifecycle, не гарантия read-only поведения всех 41 tools. `api_invoke/api_batch` предоставляют широкий COM-доступ; их нельзя включать в безопасный начальный набор автоматически. Health/status tools этого сервера в полученном списке отсутствуют; результаты другого MCP ему не приписываются.

## Установка и команды

Постоянный checkout и `.venv`:

```text
C:\Users\igora\AppData\Local\RoboHand\tools\kompas-mcp\hymaxo-adef44fdc41401af3b239a5c9b1a4e108e1a237a
```

Выполнены штатные git/uv команды:

```powershell
git clone --no-checkout https://github.com/hymaxo/kompas3d-mcp.git <checkout>
git checkout --detach adef44fdc41401af3b239a5c9b1a4e108e1a237a
git rev-parse HEAD
uv sync --locked --python 'C:\Users\igora\AppData\Local\Programs\Python\Python312\python.exe'
uv pip check --python '.\.venv\Scripts\python.exe'
```

Все перечисленные команды завершились exit **0**; последняя проверила совместимость **40 установленных packages**. `git status --short` в upstream checkout пуст. SHA256 неизменённого `uv.lock`: `77F37E6BD74D010C5692BF76F93682CC7538320DC2660A9C8E434039DC6FD088`.

Установлено: `kompas3d-mcp=0.1.0`, `mcp=1.29.1`, `pywin32=312`, `pydantic=2.13.5`. Импорты `pythoncom` и `win32com.client` отдельно прошли без `Dispatch`. Первая проверка импортов через PowerShell `python -c` получила SyntaxError из-за quoting; повтор через stdin прошёл exit 0. Это ошибка диагностической команды, CAD при ней не вызывался.

`scripts/install.py` и `install.ps1` **не запускались**: они регистрируют сервер/копируют skills в пользовательский `.codex`, что оставлено родительскому агенту. Использован документированный direct stdio entrypoint; новый wrapper, MCP или exporter не создавался. CAD/ОС/драйверы не обновлялись; ребут и закрытие CAD не потребовались.

Параметры для project-scoped конфигурации родителем:

```text
command = C:\Users\igora\AppData\Local\RoboHand\tools\kompas-mcp\hymaxo-adef44fdc41401af3b239a5c9b1a4e108e1a237a\.venv\Scripts\python.exe
args = ["-m", "kompas_mcp.server"]
cwd = C:\Users\igora\AppData\Local\RoboHand\tools\kompas-mcp\hymaxo-adef44fdc41401af3b239a5c9b1a4e108e1a237a
env.KOMPAS_SDK_PATH = C:\Program Files\ASCON\KOMPAS-3D v25 Study\SDK
env.PYTHONUTF8 = 1
```

Начальный набор без обращения к CAD: `sdk_search`, `sdk_read` (runtime passed); `blueprint_view` (source-reviewed, runtime not-run). `connect` отдельно прошёл при условиях preflight ниже и не является чисто read-only: он присваивает app property. Остальные CAD-related tools в этой настройке не проверялись; их не включать автоматически. Upstream рекомендует startup timeout 30 s/tool timeout 180 s; протокольный smoke завершился за несколько секунд, COM connect — менее чем за минуту.

**Отдельное parent-reported evidence:** родитель создал project-scoped `RoboHand.Simulator/.codex/config.toml` с server name `kompas3d`, указанными command/args/cwd/env, `startup_timeout_sec=30`, `tool_timeout_sec=60` и `enabled_tools=[sdk_search,sdk_read,blueprint_view,connect,list_documents]`. По его проверке `codex mcp get kompas3d --json` завершился exit 0 и подтвердил enabled/allowlist/env. Machine-specific config исключён через `.gitignore`; родитель добавил trust только для Simulator repo в пользовательский config с backup и проверкой сохранения остальных parsed settings. Этот агент конфиги не читал и не менял; наличие `list_documents` в allowlist **не означает его выполнения или проверки документного API**. Доступность этих tools в новом активном чате Codex — отдельная проверка после загрузки конфигурации.

## Реальный минимальный smoke

Одноразовая stdin-диагностика через установленный **официальный MCP Python SDK**: `stdio_client(StdioServerParameters(...))` → `ClientSession` → вызовы ниже → выход из context managers. Постоянный диагностический runtime в проект не добавлялся. Использован прямой server command из предыдущего раздела с указанными cwd/env.

| Вызов | Фактический ответ |
|---|---|
| `initialize` | protocol **2025-11-25**, `serverInfo.name=kompas3d`, `serverInfo.version=1.29.1`; capabilities tools/prompts/resources присутствуют |
| `tools/list` | **41 tool**, полный список в sanitized evidence |
| `prompts/list` | **2**: `model_from_blueprint`, `model_from_description` |
| `sdk_search(query="ksdocument3d", limit=3)` | `isError=false`, total **135**; первым возвращён `ksdocument3d.html` |
| `sdk_read(topic="ksdocument3d.html", length=240)` | `isError=false`, total_chars **2550**, returned_chars **240**, links **29** |
| Завершение stdio | Context managers закрылись штатно; диагностический процесс exit **0** |

`serverInfo.version=1.29.1` — значение FastMCP/SDK handshake; версию установленного приложения отдельно фиксирует metadata `kompas3d-mcp=0.1.0` и точный git pin.

Sanitized [JSON evidence](<C:/Users/igora/AppData/Local/RoboHand/tools/kompas-mcp/hymaxo-adef44fdc41401af3b239a5c9b1a4e108e1a237a/artifacts/robohand-protocol-2026-11-09.json>) содержит версии, команду/cwd/явные env, capabilities, список tools и результаты двух SDK-вызовов. SHA256: `6D76412E3EFD25B15419D5AB257E99839333BE26A50A19EEA52573947F255A0B`. Содержимое пользовательских документов, секретные env/config и большие ответы справки в evidence не записывались.

## Дополнительный COM smoke после ревью

Ревьюер разрешил один штатный app-level `connect`, если предварительно подтверждены уже запущенный COM-объект и его исходная видимость. Preflight использовал готовый `pythoncom.GetActiveObject(pywintypes.IID("KOMPAS.Application.5"))`, API5 wrapper из установленной type library и чтение `Visible`/`ksGetSystemVersion()`; **без `Dispatch`, присваиваний и методов документа**. Прочитана реализация установленного `win32com.client.GetActiveObject`: она получает существующий объект, затем `QueryInterface`; создание приложения для preflight не использовалось.

| Проверка | Фактический результат |
|---|---|
| Read-only `GetActiveObject` preflight | Объект найден, `Visible=True`, version **[1,25,0,0,0]**, exit **0** |
| Один MCP `connect(visible=True)` | `isError=false`, `connected=true`, version **[1,25,0,0,0]**, application/API7 handles возвращены |
| App property | Штатный backend присвоил `Visible=True` при исходном `True`; значение осталось прежним. Это присваивание app property, не document edit |
| Завершение MCP | Штатный stdio shutdown, exit **0**; один и тот же `kStudy` PID **36512** до/после, новых `kStudy` нет |
| Документы | Не вызывались `list_documents`, `attach_active_model`, create/open/save/close, переключение документов и другие document tools; валидация содержимого **not-run** |

Sanitized evidence сохранены рядом с первым JSON: [preflight](<C:/Users/igora/AppData/Local/RoboHand/tools/kompas-mcp/hymaxo-adef44fdc41401af3b239a5c9b1a4e108e1a237a/artifacts/robohand-com-preflight-2026-11-09.json>), SHA256 `5E3FB0A7E7DC3864793D80904C675D078138F26F02D6999D40C9584994156AC8`, и [connect](<C:/Users/igora/AppData/Local/RoboHand/tools/kompas-mcp/hymaxo-adef44fdc41401af3b239a5c9b1a4e108e1a237a/artifacts/robohand-com-connect-2026-11-09.json>), SHA256 `1F4B908C4A83BF021DD6839CADFFBEC0D9D718C9D9F2582941955CCEE752BA48`. Подключение состоялось к уже работающему приложению; после закрытия тестового MCP client CAD остался запущен. Это не постоянно открытая server-сессия и не проверка assembly/geometry API.

## Статусы и точный следующий шаг

| Уровень | Статус |
|---|---|
| Pinned source + dependencies installed | **passed** |
| Package consistency/imports | **passed** |
| Real MCP startup/initialize/tools/list/shutdown | **passed** |
| Чтение локальной SDK через MCP | **passed** |
| Project-scoped Codex registration | **passed, root-reviewed**, CLI exit 0; новый активный MCP-сеанс Codex не проверялся |
| COM/app connect к работающему v25 Study | **passed**, ограничено версией и app handles |
| Study document/geometry/mates/export compatibility | **not-run** |
| Документ/сборка EB300 validated | **not-run**, путь и сохранённая ревизия ещё неизвестны |
| Per-link export / URDF / physics / training / real | **not-run** |

Настройка и ограниченная проверка COM завершены без необходимости закрыть CAD или перезагрузить систему. Blocker следующей CAD-проверки — неизвестны путь/сохранённая ревизия сборки и идентифицированная независимая копия; document API и безопасный путь работы с копией пока не проверены. `connect` не выбирает копию и не подтверждает корректность сборки. Live validation и test-document launch не запускались.

Следующий доступный шаг — после загрузки уже подготовленной родителем конфигурации проверить этот entrypoint из нового MCP-сеанса Codex. Для CAD-проверки затем нужны сохранённая сборка/STL и идентифицированная независимая копия по [brief](../cad-agent-task.md); отдельно подтвердить готовый способ обращения к ней без вмешательства в редактируемый исходник. Если готового безопасного пути не будет, зафиксировать gap/варианты без нового server/exporter.

## Ревью родительского агента, 09.11

Прочитаны source paths connect/worker lifecycle и весь отчёт. Независимо сверены git HEAD, SHA256 lockfile и трёх JSON evidence: 4/4 совпали. Project TOML разобран, executable/cwd/SDK paths существуют; `codex mcp get kompas3d --json` фактически прошёл exit0 в Simulator и подтвердил registration/allowlist. Новых CAD/tool calls для повторения пройденного smoke не делали.

[Локальная конфигурация](../../.codex/config.toml) привязана только к этому компьютеру и исключена из Git. Для восстановления использовать command/args/cwd/env выше, allowlist из config evidence и текущий путь установленного pin. В пользовательском config добавлен trust только точного Simulator repo; до изменения создан backup `C:/Users/igora/.codex/backups/config.toml.before-kompas-2026-11-09-77e933da.bak`. Проверка parsed settings подтвердила сохранение остальных настроек. Формат project-scoped config/STDIO/cwd/enabled_tools сверен с [официальной документацией OpenAI](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

При новом CAD-сеансе открыть рабочую папку `RoboHand.Simulator`, чтобы загрузилась её project-scoped конфигурация. CLI registration и SDK smoke не подменяют проверку активных tools конкретного клиента. Пять начальных tools ограничивают интерфейс инспекцией; добавление моделирования/экспорта выполняется по фактической задаче на копии после ревью нужных handlers, не включением всех 41 tools сразу.

## Последующий эксперимент по отдельному поручению

После setup владелец явно поручил построить цангу по приложенному чертежу. Для этого root поэтапно расширил локальный allowlist до25 tools: typed modeling/save/export/preview, выбранные SDK introspection/create_feature/api_invoke и scoped delete_feature/set_entity_state для своей детали. Generic calls разрешены только для собственных handles новой детали и согласованных thread/проверок/вида; чужие документы не изменяются. Это следующий этап [CAD-эксперимента](../../cad-experiments/collet-2026-11-09/review-notes.md), а не часть первоначального app-connect smoke и не аудит EB300. Результаты создания/экспорта проверяются отдельно; наличие их tools в config не означает успешного выполнения.
