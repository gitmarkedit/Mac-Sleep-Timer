"""Тестирование CLI интерфейса sleepmac."""

import os
import subprocess
import sys
import unittest

# Динамически определяем корень репозитория для запуска на любом компьютере
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SLEEPMAC_BIN = os.path.join(REPO_ROOT, "sleepmac")


class TestCLI(unittest.TestCase):
    """Тестирование CLI аргументов и флагов."""

    def test_help_flag(self):
        res = subprocess.run(
            [sys.executable, SLEEPMAC_BIN, "--help"],
            capture_output=True,
            text=True,
            check=False,
            cwd=REPO_ROOT,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("sleepmac", res.stdout)
        self.assertIn("--dry-run", res.stdout)

    def test_invalid_duration(self):
        res = subprocess.run(
            [sys.executable, SLEEPMAC_BIN, "invalid_time"],
            capture_output=True,
            text=True,
            check=False,
            cwd=REPO_ROOT,
        )
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Ошибка", res.stdout)

    def test_dry_run_execution(self):
        # 1 секунда в режиме dry-run без TUI
        res = subprocess.run(
            [sys.executable, SLEEPMAC_BIN, "1s", "--dry-run", "--headless"],
            capture_output=True,
            text=True,
            check=False,
            cwd=REPO_ROOT,
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("Таймер сна запущен", res.stdout)
        self.assertIn("Время вышло", res.stdout)


if __name__ == "__main__":
    unittest.main()
