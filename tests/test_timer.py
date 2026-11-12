"""Юнит-тесты для класса SleepTimer."""

import time
import unittest

from sleep_timer.timer import SleepTimer


class TestSleepTimer(unittest.TestCase):
    """Тестирование управления состоянием таймера."""

    def test_init(self):
        timer = SleepTimer(1800)
        self.assertEqual(timer.total_seconds, 1800)
        self.assertEqual(timer.remaining_int, 1800)
        self.assertEqual(timer.elapsed_seconds, 0)
        self.assertFalse(timer.is_paused)
        self.assertFalse(timer.completed)

    def test_invalid_init(self):
        with self.assertRaises(ValueError):
            SleepTimer(0)
        with self.assertRaises(ValueError):
            SleepTimer(-100)

    def test_progress(self):
        timer = SleepTimer(100)
        self.assertAlmostEqual(timer.progress, 0.0)
        self.assertAlmostEqual(timer.progress_percent, 0.0)

        # Симулируем уменьшение остатка
        timer.remaining_seconds = 50.0
        self.assertAlmostEqual(timer.progress, 0.5)
        self.assertAlmostEqual(timer.progress_percent, 50.0)

        timer.remaining_seconds = 0.0
        self.assertAlmostEqual(timer.progress, 1.0)
        self.assertAlmostEqual(timer.progress_percent, 100.0)

    def test_progress_bar(self):
        timer = SleepTimer(100)
        pbar_start = timer.make_progress_bar(width=10)
        self.assertEqual(pbar_start, "[░░░░░░░░░░]")

        timer.remaining_seconds = 50.0
        pbar_mid = timer.make_progress_bar(width=10)
        self.assertEqual(pbar_mid, "[█████░░░░░]")

        timer.remaining_seconds = 0.0
        pbar_end = timer.make_progress_bar(width=10)
        self.assertEqual(pbar_end, "[██████████]")

    def test_pause_resume(self):
        timer = SleepTimer(100)
        self.assertFalse(timer.is_paused)

        is_p = timer.toggle_pause()
        self.assertTrue(is_p)
        self.assertTrue(timer.is_paused)

        is_p = timer.toggle_pause()
        self.assertFalse(is_p)
        self.assertFalse(timer.is_paused)

    def test_add_seconds(self):
        timer = SleepTimer(600)  # 10 минут
        timer.add_seconds(300)  # +5 минут
        self.assertEqual(timer.remaining_int, 900)
        self.assertEqual(timer.total_seconds, 900)

        timer.add_seconds(-300)  # -5 минут
        self.assertEqual(timer.remaining_int, 600)

        # Вычитаем слишком много — должен сработать нижний порог 5 секунд
        timer.add_seconds(-1000)
        self.assertEqual(timer.remaining_int, 5)

    def test_tick_completion(self):
        timer = SleepTimer(1)
        timer.remaining_seconds = 0.01
        time.sleep(0.02)
        done = timer.tick()
        self.assertTrue(done)
        self.assertTrue(timer.completed)
        self.assertEqual(timer.remaining_int, 0)


if __name__ == "__main__":
    unittest.main()
