"""Взаимодействие с системой macOS (перевод в сон, уведомления, звук)."""

import subprocess
import sys
import time


def sleep_now(dry_run: bool = False) -> bool:
    """Переводит Mac в режим сна через pmset sleepnow.

    Если dry_run=True, действие имитируется без фактического сна.
    """
    if dry_run:
        return True

    try:
        # pmset sleepnow доступен обычному пользователю без root-прав
        res = subprocess.run(["pmset", "sleepnow"], check=False)
        return res.returncode == 0
    except Exception:
        # Запасной вариант через AppleScript System Events
        try:
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to sleep'],
                check=False,
            )
            return True
        except Exception:
            return False


def send_notification(title: str, message: str, subtitle: str = "") -> None:
    """Отправляет системное всплывающее уведомление macOS через osascript."""
    try:
        sub_clause = f'subtitle "{subtitle}"' if subtitle else ""
        script = f'display notification "{message}" with title "{title}" {sub_clause}'
        subprocess.run(["osascript", "-e", script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def bell() -> None:
    """Воспроизводит терминальный звуковой сигнал предупреждения."""
    sys.stdout.write("\a")
    sys.stdout.flush()


def format_seconds(seconds: int) -> str:
    """Форматирует секунды в ЧЧ:ММ:СС или ММ:СС."""
    if seconds < 0:
        seconds = 0
    hrs = seconds // 3600
    rem = seconds % 3600
    mins = rem // 60
    secs = rem % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"
