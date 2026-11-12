"""Логика таймера сна, учет времени, расчет прогресса и изменение интервала."""

from datetime import datetime, timedelta
import time
from typing import Optional


class SleepTimer:
    """Управление состоянием таймера сна."""

    def __init__(self, duration_seconds: int):
        if duration_seconds <= 0:
            raise ValueError("Длительность должна быть больше нуля")

        self.initial_seconds = duration_seconds
        self.total_seconds = duration_seconds
        self.remaining_seconds = float(duration_seconds)
        self.is_paused = False
        self._last_tick = time.monotonic()
        self.completed = False

    @property
    def remaining_int(self) -> int:
        """Оставшееся время в целых секундах (не меньше 0)."""
        return max(0, int(round(self.remaining_seconds)))

    @property
    def elapsed_seconds(self) -> int:
        """Прошедшее время в секундах."""
        elapsed = self.total_seconds - self.remaining_int
        return max(0, elapsed)

    @property
    def progress(self) -> float:
        """Доля выполнения от 0.0 до 1.0."""
        if self.total_seconds <= 0:
            return 1.0
        p = self.elapsed_seconds / float(self.total_seconds)
        return min(1.0, max(0.0, p))

    @property
    def progress_percent(self) -> float:
        """Процент выполнения от 0.0% до 100.0%."""
        return self.progress * 100.0

    @property
    def target_time_str(self) -> str:
        """Время ухода в сон в формате ЧЧ:ММ:СС."""
        target = datetime.now() + timedelta(seconds=self.remaining_int)
        return target.strftime("%H:%M:%S")

    def toggle_pause(self) -> bool:
        """Переключает режим паузы. Возвращает новое состояние is_paused."""
        now = time.monotonic()
        if not self.is_paused:
            # Ставим на паузу — учитываем прошедшие до этого момента доли секунды
            dt = now - self._last_tick
            self.remaining_seconds = max(0.0, self.remaining_seconds - dt)
            self.is_paused = True
        else:
            # Снимаем с паузы
            self._last_tick = now
            self.is_paused = False
        return self.is_paused

    def add_seconds(self, delta: int) -> int:
        """Добавляет или вычитает секунды (например, +300 или -300 для 5 мин).

        Минимальный остаток — 5 секунд.
        """
        new_rem = self.remaining_seconds + delta
        if new_rem < 5:
            new_rem = 5.0

        diff = new_rem - self.remaining_seconds
        self.remaining_seconds = new_rem
        self.total_seconds = max(int(round(new_rem)), self.total_seconds + int(round(diff)))
        self._last_tick = time.monotonic()
        return self.remaining_int

    def tick(self) -> bool:
        """Обновляет состояние таймера на текущий момент.

        Возвращает True, если время вышло (таймер завершился).
        """
        now = time.monotonic()
        if not self.is_paused and not self.completed:
            dt = now - self._last_tick
            self.remaining_seconds -= dt
            if self.remaining_seconds <= 0.0:
                self.remaining_seconds = 0.0
                self.completed = True
                return True
        self._last_tick = now
        return self.completed

    def make_progress_bar(self, width: int = 34, filled_char: str = "█", empty_char: str = "░") -> str:
        """Формирует графическую полосу прогресса заданной ширины."""
        filled_len = int(round(width * self.progress))
        filled_len = min(width, max(0, filled_len))
        empty_len = width - filled_len
        return f"[{filled_char * filled_len}{empty_char * empty_len}]"
