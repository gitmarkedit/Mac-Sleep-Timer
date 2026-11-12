"""Тестирование CLI интерфейса sleepmac."""

import subprocess
import sys
import unittest


class TestCLI(unittest.TestCase):
    """Тестирование CLI аргументов и флагов."""

    def test_help_flag(self):
        res = subprocess.run(
            [sys.executable, "sleepmac", "--help"],
            capture_output=True,
            text=True,
            check=False,
            cwd="/Users/mark/.gemini/antigravity/scratch/mac-sleep-timer",
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("sleepmac", res.stdout)
        self.assertIn("--dry-run", res.stdout)

    def test_invalid_duration(self):
        res = subprocess.run(
            [sys.executable, "sleepmac", "invalid_time"],
            capture_output=True,
            text=True,
            check=False,
            cwd="/Users/mark/.gemini/antigravity/scratch/mac-sleep-timer",
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Ошибка", res.stdout)

    def test_dry_run_execution(self):
        # 1 секунда в режиме dry-run без TUI
        res = subprocess.run(
            [sys.executable, "sleepmac", "1s", "--dry-run", "--headless"],
            capture_output=True,
            text=True,
            check=False,
            cwd="/Users/mark/.gemini/antigravity/scratch/mac-sleep-timer",
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Таймер сна запущен", res.stdout)
        self.assertIn("Время вышло", res.stdout)


if __name__ == "__main__":
    unittest.main()
