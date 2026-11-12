"""Терминальный интерфейс (TUI) с меню, кнопками, прогресс-баром и горячими клавишами."""

import os
import select
import sys
import termios
import time
import tty
from typing import Optional, Tuple

from .config import Colors, PRESETS
from .parser import parse_duration
from .system import bell, format_seconds, send_notification, sleep_now
from .timer import SleepTimer


class TerminalUI:
    """Управление интерактивным терминальным интерфейсом."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.is_tty = sys.stdin.isatty() and sys.stdout.isatty()
        self._orig_termios = None

    def enter_raw(self) -> None:
        """Переводит терминал в raw-режим и переключается на альтернативный экран."""
        if not self.is_tty:
            return
        try:
            self._orig_termios = termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            # Переключение на альтернативный экран, скрытие курсора
            sys.stdout.write("\033[?1049h\033[?25l")
            sys.stdout.flush()
        except Exception:
            pass

    def exit_raw(self) -> None:
        """Восстанавливает стандартный режим терминала и курсор."""
        if not self.is_tty:
            return
        try:
            # Показать курсор, возврат на основной экран
            sys.stdout.write("\033[?25h\033[?1049l\033[0m")
            sys.stdout.flush()
            if self._orig_termios:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._orig_termios)
        except Exception:
            pass

    def read_key(self, timeout: float = 0.1) -> Optional[str]:
        """Неблокирующее чтение нажатия клавиши.

        Возвращает:
          - 'UP', 'DOWN', 'LEFT', 'RIGHT' для стрелок
          - 'ENTER' для Enter (\n или \r)
          - 'ESC' для Esc
          - 'SPACE' для пробела
          - Символ клавиши (например '1'..'7', 'q', 's', '+', '-')
          - None при отсутствии ввода в течение таймаута
        """
        if not self.is_tty:
            time.sleep(timeout)
            return None

        try:
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if not rlist:
                return None

            ch = sys.stdin.read(1)
            if ch == "\x1b":  # Escape или escape-последовательность
                r2, _, _ = select.select([sys.stdin], [], [], 0.04)
                if r2:
                    seq = sys.stdin.read(2)
                    if seq == "[A":
                        return "UP"
                    if seq == "[B":
                        return "DOWN"
                    if seq == "[C":
                        return "RIGHT"
                    if seq == "[D":
                        return "LEFT"
                    return "ESC_SEQ"
                return "ESC"

            if ch in ("\r", "\n"):
                return "ENTER"
            if ch == " ":
                return "SPACE"
            if ch == "\x03":  # Ctrl+C
                return "CTRL_C"

            return ch.lower()
        except Exception:
            return None

    def draw_menu(self, selected_idx: int) -> None:
        """Отрисовывает главное меню с кнопками быстрого выбора."""
        C = Colors
        lines = []

        # Очистка и позиционирование в верхний левый угол
        lines.append("\033[H\033[2J")

        # Заголовок
        lines.append(f"{C.BRIGHT_CYAN} ╭────────────────────────────────────────────────────────────╮{C.RESET}")
        lines.append(f"{C.BRIGHT_CYAN} │  🌙  {C.BOLD}{C.BRIGHT_WHITE}MAC SLEEP TIMER{C.RESET}{C.BRIGHT_CYAN}  •  {C.WHITE}Таймер перехода в режим сна     {C.BRIGHT_CYAN}│{C.RESET}")
        lines.append(f"{C.BRIGHT_CYAN} ╰────────────────────────────────────────────────────────────╯{C.RESET}")
        lines.append("")
        lines.append(f"  {C.BOLD}{C.WHITE}Выберите готовый вариант или укажите своё время:{C.RESET}")
        lines.append("")

        # Список кнопок / пресетов
        for i, preset in enumerate(PRESETS):
            key = preset["key"]
            label = preset["label"]
            desc = preset["desc"]
            is_sel = (i == selected_idx)

            if is_sel:
                arrow = f"{C.BRIGHT_YELLOW}▸{C.RESET}"
                btn_box = f"{C.BOLD}{C.BRIGHT_WHITE}{C.BG_SELECTED}[ {key} ]{C.RESET}"
                label_txt = f"{C.BOLD}{C.BRIGHT_YELLOW}{label:<22}{C.RESET}"
                desc_txt = f"{C.DIM}{desc}{C.RESET}"
                row = f"  {arrow} {btn_box} {label_txt} {C.BRIGHT_BLACK}│{C.RESET} {desc_txt}"
            else:
                arrow = " "
                btn_box = f"{C.BRIGHT_CYAN}[ {key} ]{C.RESET}"
                label_txt = f"{C.WHITE}{label:<22}{C.RESET}"
                desc_txt = f"{C.DIM}{desc}{C.RESET}"
                row = f"  {arrow} {btn_box} {label_txt} {C.BRIGHT_BLACK}│{C.RESET} {desc_txt}"

            lines.append(row)

        lines.append("")
        # Подвал с подсказками
        lines.append(f"{C.BRIGHT_BLACK} ╭────────────────────────────────────────────────────────────╮{C.RESET}")
        lines.append(
            f"{C.BRIGHT_BLACK} │ {C.RESET}{C.BRIGHT_YELLOW}↑ / ↓{C.RESET} или {C.BRIGHT_YELLOW}[1-7]{C.RESET} — выбор   "
            f"{C.BRIGHT_GREEN}[Enter]{C.RESET} — старт   "
            f"{C.BRIGHT_RED}[Q / Esc]{C.RESET} — выход    {C.BRIGHT_BLACK}│{C.RESET}"
        )
        lines.append(f"{C.BRIGHT_BLACK} ╰────────────────────────────────────────────────────────────╯{C.RESET}")

        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()

    def prompt_custom_duration(self) -> Optional[int]:
        """Окно ввода произвольного времени с валидацией."""
        C = Colors

        # Включаем обычный режим терминала для строкового ввода
        self.exit_raw()

        error_msg = ""
        while True:
            # Очистка экрана
            sys.stdout.write("\033[H\033[2J")
            print(f"{C.BRIGHT_CYAN} ╭────────────────────────────────────────────────────────────╮{C.RESET}")
            print(f"{C.BRIGHT_CYAN} │  ⏱  {C.BOLD}{C.BRIGHT_WHITE}ВВОД СОБСТВЕННОГО ВРЕМЕНИ{C.RESET}{C.BRIGHT_CYAN}                              │{C.RESET}")
            print(f"{C.BRIGHT_CYAN} ├────────────────────────────────────────────────────────────┤{C.RESET}")
            print(f"{C.BRIGHT_CYAN} │{C.RESET}  Поддерживаемые форматы:                                  {C.BRIGHT_CYAN}│{C.RESET}")
            print(f"{C.BRIGHT_CYAN} │{C.RESET}   • Минуты:  {C.BRIGHT_GREEN}25{C.RESET}, {C.BRIGHT_GREEN}45m{C.RESET}, {C.BRIGHT_GREEN}30 мин{C.RESET}                              {C.BRIGHT_CYAN}│{C.RESET}")
            print(f"{C.BRIGHT_CYAN} │{C.RESET}   • Часы:    {C.BRIGHT_GREEN}1h{C.RESET}, {C.BRIGHT_GREEN}1.5h{C.RESET}, {C.BRIGHT_GREEN}2ч{C.RESET}, {C.BRIGHT_GREEN}1 час 20 мин{C.RESET}                    {C.BRIGHT_CYAN}│{C.RESET}")
            print(f"{C.BRIGHT_CYAN} │{C.RESET}   • Формат:  {C.BRIGHT_GREEN}1:30{C.RESET} (1 час 30 мин), {C.BRIGHT_GREEN}0:45{C.RESET}                       {C.BRIGHT_CYAN}│{C.RESET}")
            print(f"{C.BRIGHT_CYAN} ╰────────────────────────────────────────────────────────────╯{C.RESET}")
            print("")

            if error_msg:
                print(f"  {C.BOLD}{C.BRIGHT_RED}❌ {error_msg}{C.RESET}\n")

            try:
                user_val = input(f"  {C.BOLD}{C.WHITE}Введите время (или оставьте пустым для отмены):{C.RESET} ")
                user_val = user_val.strip()
                if not user_val:
                    self.enter_raw()
                    return None

                seconds = parse_duration(user_val)
                self.enter_raw()
                return seconds
            except ValueError as e:
                error_msg = str(e)
            except (KeyboardInterrupt, EOFError):
                self.enter_raw()
                return None

    def draw_timer(self, timer: SleepTimer) -> None:
        """Отрисовывает экран активного отсчета времени."""
        C = Colors
        lines = []

        lines.append("\033[H\033[2J")

        # Статус
        if timer.completed:
            status = f"{C.BG_BLUE}{C.BOLD}{C.BRIGHT_WHITE} 💤 ВРЕМЯ ВЫШЛО — ПЕРЕХОД В СОН {C.RESET}"
        elif timer.is_paused:
            status = f"{C.BG_DARK_GRAY}{C.BOLD}{C.BRIGHT_YELLOW} ⏸  ТАЙМЕР НА ПАУЗЕ {C.RESET}"
        elif timer.remaining_int <= 15:
            status = f"{C.BRIGHT_RED}{C.BOLD} ⚠️  ВНИМАНИЕ: СКОРО В СОН (<15 сек) {C.RESET}"
        else:
            status = f"{C.BRIGHT_GREEN}{C.BOLD} 🟢 ТАЙМЕР АКТИВЕН {C.RESET}"

        # Заголовок
        lines.append(f"{C.BRIGHT_CYAN} ╭────────────────────────────────────────────────────────────╮{C.RESET}")
        lines.append(f"{C.BRIGHT_CYAN} │  🌙  {C.BOLD}{C.BRIGHT_WHITE}MAC SLEEP TIMER{C.RESET}{C.BRIGHT_CYAN}  •  {status:<43} {C.BRIGHT_CYAN}│{C.RESET}")
        lines.append(f"{C.BRIGHT_CYAN} ╰────────────────────────────────────────────────────────────╯{C.RESET}")
        lines.append("")

        # Информация о времени
        rem_str = format_seconds(timer.remaining_int)
        total_str = format_seconds(timer.total_seconds)
        elapsed_str = format_seconds(timer.elapsed_seconds)
        target_str = timer.target_time_str

        # Цвет оставшегося времени
        if timer.remaining_int <= 15:
            rem_color = f"{C.BOLD}{C.BRIGHT_RED}"
        elif timer.remaining_int <= 60:
            rem_color = f"{C.BOLD}{C.BRIGHT_YELLOW}"
        else:
            rem_color = f"{C.BOLD}{C.BRIGHT_GREEN}"

        lines.append(f"  {C.DIM}Осталось времени:{C.RESET}    {rem_color}{rem_str:>10}{C.RESET}    {C.DIM}(всего: {total_str}){C.RESET}")
        lines.append(f"  {C.DIM}Время засыпания:{C.RESET}     {C.BOLD}{C.BRIGHT_WHITE}{target_str:>10}{C.RESET}    {C.DIM}(прошло: {elapsed_str}){C.RESET}")
        lines.append("")

        # Прогресс-бар
        pbar = timer.make_progress_bar(width=36)
        pct = timer.progress_percent
        lines.append(f"  {C.BRIGHT_CYAN}{pbar}{C.RESET}  {C.BOLD}{pct:5.1f}%{C.RESET}")
        lines.append("")

        # Предупреждение если осталось меньше 15 секунд
        if timer.remaining_int <= 15 and not timer.is_paused and not timer.completed:
            lines.append(f"  {C.BOLD}{C.BRIGHT_RED}⚠️  Mac перейдет в режим сна через {timer.remaining_int} сек!{C.RESET}")
            lines.append(f"  {C.DIM}Нажмите {C.RESET}{C.BOLD}[Q]{C.RESET}{C.DIM} или {C.RESET}{C.BOLD}[Пробел]{C.RESET}{C.DIM}, если хотите отменить.{C.RESET}")
            lines.append("")

        # Подвал с кнопками управления
        lines.append(f"{C.BRIGHT_BLACK} ╭────────────────────────────────────────────────────────────╮{C.RESET}")
        lines.append(
            f"{C.BRIGHT_BLACK} │ {C.RESET}{C.BRIGHT_YELLOW}[Space]{C.RESET} Пауза/Пуск   "
            f"{C.BRIGHT_CYAN}[ + ]{C.RESET} +5 мин    "
            f"{C.BRIGHT_CYAN}[ - ]{C.RESET} -5 мин                 {C.BRIGHT_BLACK}│{C.RESET}"
        )
        lines.append(
            f"{C.BRIGHT_BLACK} │ {C.RESET}{C.BRIGHT_MAGENTA}[ S ]{C.RESET}   Усыпить сейчас          "
            f"{C.BRIGHT_RED}[Q / Esc]{C.RESET} Отмена и выход {C.BRIGHT_BLACK}│{C.RESET}"
        )
        lines.append(f"{C.BRIGHT_BLACK} ╰────────────────────────────────────────────────────────────╯{C.RESET}")

        if self.dry_run:
            lines.append(f"\n  {C.BRIGHT_YELLOW}[ РЕЖИМ ТЕСТИРОВАНИЯ (DRY-RUN): сон имитируется ]{C.RESET}")

        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()

    def run_menu(self) -> Optional[int]:
        """Запускает цикл главного меню. Возвращает выбранное количество секунд или None."""
        selected_idx = 1  # По умолчанию выбран 2-й пункт: 30 минут

        self.enter_raw()
        try:
            while True:
                self.draw_menu(selected_idx)
                key = self.read_key(timeout=0.2)
                if not key:
                    continue

                if key in ("q", "esc", "ctrl_c"):
                    return None

                if key == "up":
                    selected_idx = (selected_idx - 1) % len(PRESETS)
                elif key == "down":
                    selected_idx = (selected_idx + 1) % len(PRESETS)
                elif key == "enter":
                    preset = PRESETS[selected_idx]
                    if preset["seconds"] is not None:
                        return preset["seconds"]
                    else:
                        # Пункт "Свое время..."
                        custom_sec = self.prompt_custom_duration()
                        if custom_sec is not None:
                            return custom_sec
                        # Если пользователь отменил ввод, остаемся в меню
                        continue
                elif key in ("1", "2", "3", "4", "5", "6"):
                    idx = int(key) - 1
                    return PRESETS[idx]["seconds"]
                elif key == "7":
                    custom_sec = self.prompt_custom_duration()
                    if custom_sec is not None:
                        return custom_sec
                    continue
        finally:
            self.exit_raw()

    def run_countdown(self, seconds: int) -> bool:
        """Запускает экран активного таймера.

        Возвращает True, если Mac был переведен в сон, или False, если отменен.
        """
        timer = SleepTimer(seconds)

        # Отправляем системное уведомление macOS
        target_str = timer.target_time_str
        mins = seconds // 60
        send_notification(
            title="🌙 Таймер сна запущен",
            message=f"Mac перейдет в спящий режим в {target_str} (через {mins} мин.)",
            subtitle="Нажмите Q в терминале для отмены",
        )

        warned = False

        self.enter_raw()
        try:
            while True:
                is_done = timer.tick()
                self.draw_timer(timer)

                # Предупреждающий сигнал за 15 секунд
                if timer.remaining_int <= 15 and not warned and not timer.is_paused:
                    bell()
                    warned = True

                if is_done:
                    # Время истекло
                    time.sleep(0.5)
                    self.exit_raw()
                    print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}🌙 Время вышло! Перевод Mac в режим сна...{Colors.RESET}\n")
                    sleep_now(dry_run=self.dry_run)
                    return True

                key = self.read_key(timeout=0.15)
                if not key:
                    continue

                if key in ("q", "esc", "ctrl_c"):
                    self.exit_raw()
                    send_notification(title="Таймер сна", message="Таймер сна отменен пользователем.")
                    print(f"\n{Colors.BRIGHT_RED}🛑 Таймер сна отменен пользователем.{Colors.RESET}\n")
                    return False

                elif key == "space":
                    timer.toggle_pause()

                elif key in ("+", "="):
                    timer.add_seconds(300)  # +5 минут
                    warned = False

                elif key in ("-", "_"):
                    timer.add_seconds(-300)  # -5 минут

                elif key == "s":
                    # Усыпить сейчас
                    self.exit_raw()
                    print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}🌙 Немедленный переход в режим сна по запросу...{Colors.RESET}\n")
                    sleep_now(dry_run=self.dry_run)
                    return True

        finally:
            self.exit_raw()
