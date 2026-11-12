"""Парсер строк времени для таймера сна."""

import re


def parse_duration(s: str) -> int:
    """Преобразует строку времени в количество секунд.

    Поддерживает:
      - Числа по умолчанию (минуты): "30", "45"
      - Суффиксы минут: "30m", "30min", "30мин", "30 минут", "1 минута"
      - Суффиксы часов: "1h", "1hr", "1ч", "1 час", "1.5h", "1,5 часа"
      - Суффиксы секунд: "45s", "45sec", "45сек"
      - Формат ЧЧ:ММ: "1:30" (1 час 30 минут), "0:45"
      - Составные строки: "1h 30m", "1 час 15 минут"

    Возвращает количество секунд (целое число > 0).
    Вызывает ValueError при некорректном формате или времени <= 0.
    """
    if not isinstance(s, str):
        raise ValueError("Входное значение должно быть строкой")

    clean = s.strip().lower().replace(",", ".")
    if not clean:
        raise ValueError("Время не может быть пустым")

    # Проверка на отрицательные числа или недопустимые знаки в начале
    if clean.startswith("-") or "-" in clean:
        raise ValueError(f"Время не может быть отрицательным: '{s}'")

    # Формат ЧЧ:ММ (например, 1:30 или 0:45)
    if ":" in clean:
        parts = clean.split(":")
        if len(parts) == 2:
            try:
                hours = int(parts[0].strip())
                minutes = int(parts[1].strip())
                if hours < 0 or minutes < 0 or (hours == 0 and minutes == 0):
                    raise ValueError("Время должно быть больше нуля")
                return hours * 3600 + minutes * 60
            except ValueError as e:
                if "больше нуля" in str(e):
                    raise
                raise ValueError(f"Некорректный формат времени ЧЧ:ММ: '{s}'")
        else:
            raise ValueError(f"Некорректный формат времени: '{s}'")

    # Регулярное выражение для поиска всех блоков времени
    pattern = (
        r"(\d+(?:\.\d+)?)\s*"
        r"(h|hr|hours?|ч|час|часа|часов|"
        r"m|min|mins|minutes?|м|минута|минуту|минуты|минут|мин|"
        r"s|sec|secs|seconds?|секунда|секунду|секунды|секунд|с|сек)?(?:\s+|$)"
    )

    matches = re.findall(pattern, clean)
    if not matches:
        raise ValueError(f"Не удалось распознать формат времени: '{s}'")

    residual = re.sub(pattern, "", clean).strip()
    if residual:
        raise ValueError(f"Некорректные символы во времени: '{residual}' в '{s}'")

    total_seconds = 0.0
    matched_any = False

    for val_str, unit in matches:
        if not val_str:
            continue
        try:
            val = float(val_str)
        except ValueError:
            continue

        matched_any = True
        unit = unit.strip()

        if unit in ("h", "hr", "hour", "hours", "ч", "час", "часа", "часов"):
            total_seconds += val * 3600
        elif unit in ("s", "sec", "secs", "second", "seconds", "секунда", "секунду", "секунды", "секунд", "с", "сек"):
            total_seconds += val
        else:
            # По умолчанию (или если указана единица минут) считаем минутами
            total_seconds += val * 60

    if not matched_any or total_seconds <= 0:
        raise ValueError(f"Время должно быть больше 0 секунд: '{s}'")

    return int(round(total_seconds))
