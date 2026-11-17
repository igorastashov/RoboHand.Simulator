---
tags: [eb300, ebg20, cad, gripper, mujoco, contact]
type: execution-report
updated: 2026-11-17
status: bounded-standalone-prepositioned-candidates-for-review
---

# EBG-20: управляемые губки и контактное удержание

Получены отдельные стандартные MJCF/config candidates: один вращательный выход сервопривода, две связанные линейные каретки, реальные поверхности губок и свободный карандаш. Раскрытие, закрытие, подъём, удержание и выпуск выполнены штатным MuJoCo. Предпочтительный осевой случай начинается с заранее вертикально поставленного предмета. Это проверка отдельного захвата; подбор лежащего карандаша, полная физическая приёмка EB300 и grasp policy не выполнены.

Принятые 24 native-файла LATEST и 51 файл исходного комплекта не изменены. Root `E:\RoboHand\LATEST\CAD\EB300.a3d` сохранил SHA256 `3b919e9642686f2194ca007484ad860229b4fccadf0ea7517d40e6c2383254db`. [Evidence и команды](evidence.json).

## Источник и реальная механика

Использован установленный `hymaxo/kompas3d-mcp@adef44fdc41401af3b239a5c9b1a4e108e1a237a`, SDK КОМПАС v25 Study25.0.0.2735 и готовый stock MCP-клиент. Requirements upstream: Python≥3.12, MCP≥1.29.1<2, Pydantic≥2.12<3, pywin32≥311, Pillow≥11, PyMuPDF≥1.26. Native audit выполнялся в собственном read-only документном контексте без Save/Rebuild/CalcMass; проверены 8 occurrences и 25/25 Valid mates.

Manufacturer [EBG-20/Thingiverse6460227](https://www.thingiverse.com/thing:6460227), локальный README и [официальный FAQ](https://toolboxrobotics.com/faq) указывают один MG995 или более мощный servo. Два сохранённых exploded drawings прямо показывают передачу «шестерня015 → противоположные рейки005/010 → каретки/пальцы»:

- `9df9eddf-a825-4d55-ba5d-d695bf7114ae.jpg`, лист1/2: корпус, servo, pinion015.
- `94d357c9-f2ec-4ab4-a9dc-5b6640df3671.jpg`, лист2/2: рейки и крепление пальцев.

Их SHA256 записаны в evidence. Локальный snapshot — `E:\RoboHand\runs\2026-11-17-ebg20-motion\source`; vendor LICENSE сохранён. Геометрические и графические binaries остаются вне Git.

| Жёсткая группа candidate | Native occurrence indices и детали |
|---|---|
| Base | 0=`002`, 1=`003` |
| Jaw A | 2=`007`, 3=`013`, 7=`014` |
| Jaw B | 6=`007`, 5=`013`, 4=`014` |

Оси направляющих — ±X исходной детали003; +Z совпадает с продольным направлением захвата. Межгрупповые plane-distance/coincidence normals перпендикулярны rail-X, max dot≈`2.01e−15`: native mates допускают две независимые линейные координаты. Servo, pinion и rack coupling в принятой native assembly отсутствуют. [Native-карта](native-kinematics.json), [точные mesh→canonical и canonical→output transforms](candidate-config.json).

Source pinion имеет 18 зубьев. Для каждой рейки найдены 23 вершины зубьев/22 интервала: pitch005=`2.387602 мм`, pitch010=`2.387611 мм`, RMS линейного fit=`0.000207/0.000167 мм`, max residual<`0.000430 мм`. Идеальный коэффициент передачи `r=N·pitch/(2π)≈6.83999 мм/рад`. Это численный fit STL, не метрология изготовленной передачи: profile repeat error18-fold≈0.0386 мм RMS; backlash, servo neutral и hardware tolerances неизвестны.

В MJCF задано `q_A=q_B=r·theta`, направления A=−X, B=+X, положительная theta раскрывает губки. Native captured pose соответствует theta=0; абсолютный угол/PWM/sign реального servo требует калибровки. Demo target range `[-0.75,2] рад` не является механическими пределами. Пальцы сохранены жёсткими; отдельная адаптивная compliance/pivot-модель не заявляется. Точные omitted rack→carriage attachment transforms остаются gap; рейки не вставлялись по догадке. Pinion axial visual offset6.25 мм — nominal, зубчатый контакт заменён идеальными constraints.

## Геометрия, привод и ограничения численной модели

Применены штатные [MJCF equality joints и position actuators](https://mujoco.readthedocs.io/en/stable/XMLreference.html), [параметры solver](https://mujoco.readthedocs.io/en/stable/modeling.html). MuJoCo-core4.0.1, Trimesh5.2.1, SciPy1.18.1. Пять binary meshes переиспользованы из подготовленных assets; ASCII015 переведён готовым `Trimesh.export` в отдельный binary STL, max coordinate rounding≈`3.81e−6 мм`. Исходники не переписаны. Новый exporter/controller/adapter/framework не создан.

В reference pose восемь source-mesh AABB воспроизводятся до `1.832e−9 м`. В65 статических poses и no-object range test не обнаружены контакты представленных внутренних деталей, включая проверку с отключённым parent filter. Минимальный межгубочный зазор≈1.28 мм, block→003 Z-clearance≈0.500 мм; у крайнего раскрытия X-margin блока≈3.796 мм. Для R2 soft limits дают transient gap≥1.067 мм. [Проверка](range-and-source-geometry-check.json). Это не проверка отсутствующих реек, cover004, всех fasteners или контактов зубьев. MuJoCo использует convex hull mesh collisions; отверстия/вогнутости не считаются точной triangle collision surface.

Nominal: массы base150г, jaw25г каждая, pinion8г, pencil8г; servo force limit±0.25Нм, friction0.6. В standalone две позиции actuator: **один gripper servo и одна отдельная вертикальная fixture**. Fixture заменяет движение основания тестовым стендом; это не дополнительный привод EB300. Pencil — freejoint; обе equality относятся только к внутренним суставам, weld/перестановки предмета во время эпизода нет. Указанные параметры не измерены на hardware.

## Выполненные контактные проверки

| Candidate / timestep | Проверенный случай | Gear peak, мкм | Pad penetration peak, мкм | Floor impact peak, мкм |
|---|---|---:|---:|---:|
| [R1 horizontal](ebg20_standalone_candidate.xml),50мкс | transverse pencil, lift59.996мм, hold3с, release | 15.773 | 42.049 | 784.743 |
| [R1 axial](ebg20_axial_prepositioned_candidate.xml),50мкс | upright prepositioned, lift59.996мм, hold3с, release | 15.773 | 42.049 | 784.318 |
| [R2 axial](ebg20_axial_prepositioned_candidate_r2.xml),0.5мс | upright prepositioned, lift39.996мм, hold1.5с, release | 101.566 | 156.719 | 1179.185 |
| R2 axial,2мс | тот же nominal test | 112.102 | 149.581 | 1262.794 |

Здесь maxima накоплены **на каждом physics step**. Прежние sampled maxima сохранены в raw evidence и заменены в итоговой оценке. Оба actual014 pad контакта присутствуют при hold; после раскрытия предмет падает. Для axial rod110мм начальная позиция centerZ55мм, основание захватаZ160мм: pads перекрывают верхние21мм предмета, headroom до housing≈29.5мм. Это отдельная начальная постановка, не изменение внутренней ориентации хвата вращением wrist.

R1 с жёстким direct-solref нельзя просто вставить в desktop R1 с timestep2мс: независимый root stress при0.5мс получил BADQACC servo DOF1 околоt=0.3035с. Оба R1 XML сохранены неизменными.

R2 сохраняет геометрию, массы, friction и torque limit; использует positive-solref0.004/1 с refsafe≥2dt, stock filtered position timeconst0.05с и effective output armature0.001кг·м². Последнее выбрано как численный tradeoff из bounded sweep, не измеренная инерция servo. На0.5/2мс время монотонно, warnings отсутствуют. [Численные результаты](R2-numerics-review.json).

Root независимо повторил R2 с μ0.35, close−0.60рад, другим lift30мм/1.2с и hold2с: оба timestep удерживают и выпускают свободный предмет, warnings/internal contacts отсутствуют. Но общий strict penetration gate250мкм **FAIL** из-за удара отпущенного предмета о floor; в собственном профиле R2 true gear peak также немного превышает пробный gate100мкм. Это остаётся открытым ограничением, а не полной физической приёмкой. [Контактная сводка](contact-review.json).

## Воспроизведение и следующий gate

Из корня workspace:

```powershell
& 'E:\RoboHand\tools\cad-validation-2026-11-14\.venv\Scripts\python.exe' 'E:\RoboHand\runs\2026-11-17-ebg20-motion\validate-R2-axial-once.py'
```

Для0.5мс — `validate-R2-halfms-once.py`; R1 — `validate-contact-once.py` и `validate-axial-once.py`. Полные traces, snapshots, failed attempts, исходные images и service PNG находятся только в указанном run-каталоге. Service renderer не является дополнительной policy camera; вход Redmi/full-frame здесь вообще не проверялся и не менялся.

Следующий gate: проверить omitted drivetrain attachment, actual servo zero/angle/limits/dynamics, массу, friction/backlash и допуски контакта; затем отдельное объединение с6-axis EB300 и выбранным camera/action/data contract. Ни fullarm интеграция, ни ML action adapter, ни обучение/поиск лежащего инструмента этим поручением не выполнялись.
