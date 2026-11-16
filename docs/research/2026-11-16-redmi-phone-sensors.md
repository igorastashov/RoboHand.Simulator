---
tags: [robohand, redmi8a, sensors, telemetry, reuse-first]
type: research
updated: 2026-11-16
status: source-inspected-device-inventory-pending
---

# Redmi 8A: использовать все доступные датчики

Решение владельца16.11: кроме полного кадра основной камеры собирать доступные датчики телефона. Начинаем с инвентаризации реального экземпляра и записи телеметрии. **Гироскоп пока не подтверждён:** [Xiaomi](https://www.mi.com/in/redmi-8a/specs/) перечисляет акселерометр, компас, освещённость и приближение, но не gyro. Это не окончательный ответ о составе конкретной прошивки.

## Каналы и польза

| Канал | Что проверяем/собираем | Для чего |
|---|---|---|
| Accelerometer | Три оси, м/с²; raw включает гравитацию | Наклон в покое, вибрации, движение телефона |
| Gyroscope | Только если реально найден, рад/с | Угловое движение и диагностика |
| Magnetometer/compass | Поле по осям, µT, accuracy | Дополнительный ориентир; моторы/магниты и сталь искажают поле |
| Gravity/linear acceleration/rotation vector | Если доступны, записать vendor/type и признак software sensor | Производные оценки; rotation vector сам по себе не доказывает аппаратный gyro |
| Light/proximity | Доступность, единицы и значения модели | Освещение/закрытие телефона, вспомогательная диагностика |
| Location, microphone | Отдельные Android API/разрешения; GPS в помещении может не давать fix | Внешняя локализация в будущем, голос; не подменяют wrist vision |
| Остальные SensorManager types | Полный список, поддерживаемые диапазоны/частоты/accuracy | Сохраняем доступный состав, а не выдумываем обязательные каналы |

Не каждую телеметрию нужно включать во вход policy. Например, детектор шагов не даёт положение руки, а компас рядом с приводами не является достоверным абсолютным yaw. Телефон не заменяет шесть выходных энкодеров, измерение усилия или датчик контакта.

## Готовые приложения вместо собственного bridge

Проверен [SensorServer](https://github.com/UmerCodez/SensorServer) на commit **`5ae401780d99debcabb8dc259256c2652dada0a6`**: README, GPL-3.0 LICENSE, `app/build.gradle.kts`, `AndroidManifest.xml` сохранены локально с SHA256. Gradle задаёт minSdk23/targetSdk36; Android нашего телефона ещё не проверен. Приложение **не установлено и не протестировано на Redmi**.

Штатный минимальный путь из README: открыть Available Sensors, запустить сервер и подключить готовый WebSocket client к `/sensor/connect?type=android.sensor.accelerometer`. Сообщения содержат `accuracy`, `timestamp`, `values`. Есть штатный multiple-sensor endpoint и отдельный GPS endpoint. SensorServer не предоставляет этим же путём видеокамеру: upstream ссылается на отдельное приложение. Совместная работа video/sensors и timestamps пока не принята.

Альтернатива для первоначального ручного эксперимента — [phyphox, поддерживаемые входы](https://phyphox.org/sensors/). Наличие поддержки в приложении не означает наличие сенсора в Redmi. Собственное Android-приложение, сервер или harness не разрабатываем.

## Контракт записи и проверка экземпляра

Согласно [Android Sensor framework](https://developer.android.com/develop/sensors-and-location/sensors/sensors_overview), доступность зависит от устройства; hardware/software sensors нужно различать. Оси устройства фиксированы относительно его стандартной ориентации и не должны произвольно поворачиваться вместе с UI. Screen/device frame отличается от rear-camera optical frame; сохраняем отдельные transforms к wrist3.

Для каждой записи сохранять model/Android/MIUI, sensor name/vendor/type/version, units, max range/resolution, requested и фактическую частоту, accuracy, device timestamp, PC arrival timestamp, пропуски. `SensorEvent.timestamp` — наносекунды на шкале времени устройства; PC wall clock к нему автоматически не приравнивается. Источник camera timestamps и связь с этой шкалой проверяются отдельно.

Минимальная приёмка: перечень датчиков → неподвижный телефон → поворот вокруг трёх осей → запись рядом с выключенными и работающими приводами → видео и телеметрия одновременно → оценка задержек/пропусков/нагрева. Сохранять сырьё и описание frames, затем выбирать полезные каналы. Сейчас ADB в PATH не обнаружен; инвентаризация физического телефона в этой сессии не выполнялась.

Существующий native input `proprio[60]` и checkpoints **не расширены**. Добавление датчиков как policy input — отдельная версия наблюдений и обучение, после подтверждения доступности/синхронизации. В sim можно создавать только явно номинальные аналоги с отдельно заданным шумом; не выдавать их за измерения реального Redmi.

Локальные исходники исследования: `E:\RoboHand\runs\2026-11-16-redmi-wrist-camera-study\sensorserver-upstream\provenance.json`.

[Крепление камеры](2026-11-16-redmi-wrist-mount-study.md) · [Индекс](../index.md).
