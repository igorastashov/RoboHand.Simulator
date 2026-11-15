---
type: cad-experiment-ledger
updated: 2026-11-09
status: native-built-reviewed-with-stated-assumptions
---

# Цанга: чтение чертежа, план и проверка

Источник: [source-drawing.png](source-drawing.png), 1009×723, SHA256 `01f8288424ceedbb228f0259e6538d777c20b0a3aabb234becd7495b2288e905`. Работает отдельный CAD-агент; родительский агент независимо прочитал изображение и согласовал профиль. Все размеры ниже — mm, углы — degrees. Ось детали в CAD — X, x=0 на переднем широком торце, x=90 на резьбовом торце; профиль строится в XY как `(x,r)` и вращается вокруг X.

Используются готовые workflows `kompas-modeling`, `kompas-blueprints`, `kompas-api` из `hymaxo/kompas3d-mcp@adef44fdc41401af3b239a5c9b1a4e108e1a237a`, установленный MCP и его штатные tools/SDK. Новый server/exporter/runtime не создаётся. Геометрические args сохраняются как данные в `model-plan.json`; результаты вызовов будут сохранены в tool ledger. Собственный новый M3D документ не связан с EB300; чужие документы не закрываются, не сохраняются и не изменяются.

## Coverage ledger

`Explicit` означает читаемую надпись; `derived` — расчёт по согласованным размерам; `assumed` — явно принятое допущение. `Built` означает создание штатными native features по сохранённым args; фактические измерения, их пределы и evidence приведены в итоговой таблице ниже.

| ID | Элемент / аннотация | Размер и интерпретация | Source coverage | Статус и план проверки |
|---|---|---|---|---|
| G01 | Общая длина | L=90 | [TL quadrant](source-crop-quadrant-tl.png), [bore/thread](source-crop-bore-thread.png) | Explicit; built; см. итоговую проверку; границы X и осевые станции |
| G02 | Передний наружный буртик | Ø52.5, верхнее отклонение0, нижнее−0.1; диапазон52.4…52.5; CAD nominal52.5 | [front lower](source-crop-front-lower.png), [размерная надпись](diameter-labels-horizontal.png) | Explicit nominal/tolerance, подтверждено независимым чтением родителя; built; см. итоговую проверку; радиус profile/цилиндрической поверхности26.25, не только AABB после прорезей |
| G03 | Передний буртик по оси | Теоретическое пересечение x=1.2 | [front lower](source-crop-front-lower.png), [left detail](left-detail-review.png) | Согласованная интерпретация размерной выноски; built; см. итоговую проверку |
| G04 | Переход Ø52.5→Ø50 | **Assumed 60°**; осевая длина 1.25/tan60≈0.721688; конец x≈1.921688 | [left detail](left-detail-review.png) | Угол здесь не задан явно; root принял параллельность задней фаске как допущение; built; см. итоговую проверку |
| G05 | Скругления буртика | Две кромки R0.3 по двум стрелкам | [front lower](source-crop-front-lower.png), [lip review](lip-review.png) | Explicit R и две выноски; native arcs в основном профиле, built; см. итоговую проверку |
| G06 | Основной цилиндр фланца | Ø50 до x14.5 | [front upper](source-crop-front-upper.png), [front lower](source-crop-front-lower.png) | Explicit diameter; осевая станция derived из G07; built; см. итоговую проверку |
| G07 | Задняя фаска фланца | Осевой размер 1, угол 60°; (14.5,25)→(15.5,25−tan60) | [front lower](source-crop-front-lower.png) | Explicit/derived; built; см. итоговую проверку |
| G08 | Уступ фланца | x=15.5, радиальная стенка до R5 | [front lower](source-crop-front-lower.png) | Explicit length; built; см. итоговую проверку |
| G09 | Скругление фланец/хвост | R5; центр(20.5,18.5), касания(15.5,18.5) и(20.5,13.5) | [front upper](source-crop-front-upper.png), [front lower](source-crop-front-lower.png) | Explicit radius; касания derived; native arc, built; см. итоговую проверку |
| G10 | Наружный хвост | Ø27 до правого торца x90, без наружной торцевой фаски | [bore/thread](source-crop-bore-thread.png), [A–A](source-crop-section-aa.png) | Explicit/согласованная интерпретация; built; см. итоговую проверку |
| G11 | Переднее отверстие | Ø12.7 от x0 до x5 | [front upper](source-crop-front-upper.png), [front lower](source-crop-front-lower.png) | Explicit; built; см. итоговую проверку |
| G12 | Внутренняя коническая расточка | Включённый угол 70°; r6.35→9.25, длина 2.9/tan35≈4.141629 | [front upper](source-crop-front-upper.png), [left detail](left-detail-review.png) | Explicit angle/diameters, derived length; built; см. итоговую проверку |
| G13 | Осевое отверстие после конуса | Ø18.5, от x≈9.141629 до входной фаски | [bore/thread](source-crop-bore-thread.png) | Explicit; built; см. итоговую проверку |
| G14 | Входная фаска справа | **Внутренняя** 1.5×45°: (88.5,9.25)→(90,10.75) | [bore/thread](source-crop-bore-thread.png) | Explicit размер, согласованное положение; built; см. итоговую проверку |
| G15 | Резьба Б | M20×1.5−6H, L50 от заднего торца; номинальная зона x40…90 | [bore/thread](source-crop-bore-thread.png) | Explicit; native **cosmetic**, не physical helix; built; см. итоговую проверку. Поле 6H отсутствует в API5 definition: сохраняется в имени feature/ledger |
| G16 | Три продольных паза В | Ширина 1.6…1.8; выбран nominal1.7; 3×120°; длина45 от x0 | [end slots](source-crop-end-slots.png), [front upper](source-crop-front-upper.png) | Explicit range/count/length; nominal midrange выбран явно; built; см. итоговую проверку; три disjoint contours и три радиальных cuts до x45 |
| G17 | Лыски A–A | Две противоположные плоскости, размер между ними24, осевая длина10: x80…90 | [A–A](source-crop-section-aa.png), [bore/thread](source-crop-bore-thread.png) | Explicit; built; см. итоговую проверку; плоскости CAD Y=±12; относительная фаза к пазам на чертеже не задана и выбрана как допущение |
| A01 | Общая шероховатость | Ra3.2 с указанным на чертеже знаком | [notes/title](source-crop-notes-title.png), [TR quadrant](source-crop-quadrant-tr.png) | Annotation only; не имитируется mesh-шероховатостью |
| A02 | Твёрдость и контроль | 40…45 HRC; группа контроля4 по ОСТ1 00021−78 | [notes/title](source-crop-notes-title.png) | Annotation/process requirement; CAD material assignment не подтверждает термообработку |
| A03 | Неуказанные допуски | Размеры/форма/расположение по ОСТ1 00022−80 | [notes/title](source-crop-notes-title.png) | Annotation; численные таблицы стандарта не подменяются догадками |
| A04 | Материал | Сталь40Х, ГОСТ4543−2016 | [notes/title](source-crop-notes-title.png) | Label explicit; плотность **7.85 g/cm³ estimated** для расчётной массы; не сертификация материала |
| A05 | Основная надпись | «Цанга», справочная масса0.38kg, масштаб2:1, форматA3 | [notes/title](source-crop-notes-title.png), [BR quadrant](source-crop-quadrant-br.png) | Масса не цель подгонки; pixels/scale не заменяют размеры |

Выполнено чтение полного source и десяти overlapping/detail crops через штатный `blueprint_view`; PNG image blocks сохранены без вывода base64. Метаданные crops и safe SDK search — [source-inspection-evidence.json](source-inspection-evidence.json). Первая попытка передать Cyrillic path внутри PowerShell stdin дала ошибку encoding; повтор с Unicode environment path прошёл, исходное изображение не менялось.

## План штатных операций

1. `connect` и `create_part` с уникальным именем собственной цанги; все последующие запросы только с возвращённым document_id. `attach_active_model` и операции над EB300 не используются.
2. `create_sketch` на XY: именованный осевой профиль, native arcs G05/G09, одно construction-axis ребро; `revolve`360°. `inspect_model`: bounds, volume, body_count. Сравнить объём с независимым расчётом профиля.
3. Три радиальных прямоугольных контура ширины1.7 в YZ, внутренний радиус начала5 внутри существующего bore, внешний30 вне детали; `extrude` cut45. Три контура не пересекаются. Направление нормали YZ подтвердить placement/результатом измерений, не по экранной картинке.
4. Два прямоугольных контура для лысок на XY с offsetZ=−20, Y за ±12 и X80…91; cut40 по Z. В solid останется требуемая длина10. Прорези и лыски не пересекаются по X.
5. Native cosmetic thread через готовый `create_feature`/`ksThreadDefinition` на собственных bore/rear-face handles; SDK-план отдельно согласован родителем. Прочитать dr/p/length/outside и ссылки на topology. Витки не вырезаются; STEP/STL не содержат helical thread geometry.
6. `set_material` с label40Х и estimated density7.85, `inspect_model`, несколько собственных previews/детальных crops, native `.m3d`, штатный STEP/STL export с `overwrite=false`. Другие CAD-документы оставить открытыми.

## Приёмка и текущие неизвестные

Протокол приёмки включает один solid body, каждую осевую станцию и радиус, native arcs/фаски, bore/конус, count/phase/length/width пазов, две плоскости лысок и их расстояние, параметры cosmetic thread, bounds/volume/mass и существование непустых native/export/preview файлов. AABB после прорезей может быть меньше nominalØ52.5; диаметр проверяется также по профилю/поверхностям. Скругления, bore и пазы должны проверяться численно и по нужным видам, не одним общим preview.

Открытые ограничения: угол60° переднего перехода — принятое допущение; фазировка лысок относительно пазов — выбранная; 6H хранится обозначением без отдельного API5 tolerance field; density estimated; native/cosmetic thread не моделирует витки. При этих ограничениях модель нельзя объявлять безоговорочно соответствующей всему чертежу или manufacturing-ready.

## Фактические результаты R7

Финальные [M3D](collet-r7.m3d), [STEP](collet-r7.step), [STL](collet-r7.stl), [PNG 300 dpi](preview-r7-300dpi.png); [краткий технический отчёт](technical-report.md). Все файлы созданы штатными save/export с новыми именами; native документ оставлен открытым. Полные размеры/хеши — [manifest](artifact-manifest-r7.json).

| Coverage | Фактическая проверка | Evidence |
|---|---|---|
| G01–G14, осевой профиль/радиусы/отверстия/конус/фаски | Native arcs/lines + revolve360°; bounds до прорезей X0…90 и Y/Z±26.25; один body; V=50520.98393442727 против независимых50520.98393442725mm³ | [model-plan](model-plan.json), [attempt1](tool-ledger-r1.json) |
| G16, три паза | Прямые radial edges на x45: ширины1.6999999999999975/1.7/1.7000000000000024; интервалы120.00000000000001/120/120°. Начало0, конец45 | [геометрические проверки R5](tool-ledger-r5.json) |
| G17, лыски | Две planar faces Y=±12, осевой диапазон80…90; размер между плоскостями24, длина10 | [R5 faces](tool-ledger-r5.json) |
| G15, резьба | Native cosmetic feature M20x1.5-6H L50: dr20, p1.5, length50, outside=false; base cylinder r9.25; begin face planar, её ребро xmin=xmax90 | [R5](tool-ledger-r5.json), [R6 refs](tool-ledger-r6.json), [begin-plane check](highres-preview-ledger-r6.json) |
| Solid/volume/mass | V=48247.789214051445mm³; area19183.262040831796mm²; mass0.3787451453303038kg при estimated density7.85; один body; COM=(27.98561702488027,0,0)mm | [R5](tool-ledger-r5.json), [финальная R7](tool-ledger-r8.json) |
| Visibility | Скрыты только свои sketches, offset plane, default planes/axes; V/body/mass не изменились | [R6](tool-ledger-r6.json), [default auxiliaries](tool-ledger-r7.json), [R7 save/preview](tool-ledger-r8.json) |
| Native/STEP/STL/PNG | Успешные save/export и непустые файлы; PNG968×1001; STEP1 MANIFOLD_SOLID_BREP и mm; STL1728 facets, boundary/nonmanifold/degenerate0, payload идентичен R5 | [manifest](artifact-manifest-r7.json), [независимое ревью root](stl-review-final.json) |

Окончательный native объём отличается от приближённого независимого расчёта48247.41950328539 на0.369710766055mm³. Исходный client check≤0.1mm³ оказался чрезмерным и сохранён как failed assertion в attempt4; после прямой проверки размеров root принял≤1mm³ для этого approximate volume check. Геометрия и плотность под результат не менялись. STL-volume48174.649539211394mm³ ниже native на0.151592% из-за штатной тесселяции; STL не используется как источник точных CAD-размеров.

История ошибок сохранена отдельно: [attempt1](tool-ledger-r1.json) выявил обратную нормаль YZ (reverse=false не снимал материал); [attempt2](tool-ledger-r2.json) остановился на Document.Name gate без изменений; [attempt3](tool-ledger-r3.json) — на нераспакованном FastMCP JsonValue wrapper без изменений; [attempt4](tool-ledger-r4.json) сохранил исходный progress, удалил только rediscovered own failed cut и успешно построил пазы reverse=true. В последующих generic reads использованы штатный unwrap и structuredContent для списков. При финальной display-очистке вызов RebuildModelEx был сначала ошибочно адресован document; исправлен на own part по pinned state() в [attempt8](tool-ledger-r8.json). Неудачные попытки не перезаписывались и не выдаются за успешные CAD-операции.

Не выполнены: physical helical thread, отдельное formal API5 поле6H, создание полностью dimension-constrained эскиза, повторное открытие M3D/STEP в CAD, метрология/производство. Ra/HRC/материал по стандарту и допуски сохранены требованиями; их физическое выполнение CAD-модель не подтверждает. Передний переход60° и фазировка лысок остаются явно принятыми допущениями, density — оценкой.
