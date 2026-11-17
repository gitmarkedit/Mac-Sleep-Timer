#!/usr/bin/env bash
# ==============================================================================
# Mac Sleep Timer — Скрипт автоматической установки на macOS
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Цвета для вывода в терминал
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "╭────────────────────────────────────────────────────────────╮"
echo "│  🌙  MAC SLEEP TIMER  •  УСТАНОВКА ПРОЕКТА                 │"
echo "╰────────────────────────────────────────────────────────────╯"
echo -e "${NC}"

# 1. Проверка операционной системы
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo -e "${RED}❌ Ошибка: Mac Sleep Timer предназначен только для компьютеров Apple Mac (macOS).${NC}"
    exit 1
fi

# 2. Проверка наличия Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Ошибка: Python 3 не обнаружен.${NC}"
    echo -e "Установите Python 3 командой: ${YELLOW}xcode-select --install${NC} или через Homebrew: ${YELLOW}brew install python${NC}"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓${NC} Обнаружен macOS $(sw_vers -productVersion 2>/dev/null || uname -r) и Python ${PY_VER}"

# 3. Определение директорий установки
# Если запущен с sudo или /usr/local/bin доступен на запись — ставим глобально, иначе в ~/.local
if [[ -w "/usr/local/bin" ]] || [[ "$EUID" -eq 0 ]]; then
    BIN_DIR="/usr/local/bin"
    SHARE_DIR="/usr/local/share/sleepmac"
    APPS_DIR="/Applications"
else
    BIN_DIR="$HOME/.local/bin"
    SHARE_DIR="$HOME/.local/share/sleepmac"
    APPS_DIR="$HOME/Applications"
fi

mkdir -p "$BIN_DIR"
mkdir -p "$SHARE_DIR"
mkdir -p "$APPS_DIR"

echo -e "\n${BOLD}1. Установка консольной утилиты (CLI / TUI):${NC}"

# Копируем библиотеку и исполняемый файл
rm -rf "$SHARE_DIR/sleep_timer"
cp -R "sleep_timer" "$SHARE_DIR/"
cp "sleepmac" "$SHARE_DIR/sleepmac"
chmod +x "$SHARE_DIR/sleepmac"

# Создаем символическую ссылку в bin
ln -sf "$SHARE_DIR/sleepmac" "$BIN_DIR/sleepmac"
echo -e "${GREEN}✓${NC} Команда ${CYAN}sleepmac${NC} установлена в: ${BOLD}$BIN_DIR/sleepmac${NC}"

# 4. Сборка и установка нативного macOS приложения
echo -e "\n${BOLD}2. Сборка и установка нативного приложения macOS:${NC}"
if [ -f "build_app.sh" ]; then
    bash build_app.sh > /dev/null 2>&1 || true
fi

APP_SOURCE="Таймер сна.app"
APP_TARGET="$APPS_DIR/Таймер сна.app"

if [ -d "$APP_SOURCE" ]; then
    rm -rf "$APP_TARGET"
    cp -R "$APP_SOURCE" "$APPS_DIR/"
    # Снимаем атрибут карантина Gatekeeper (если репозиторий был скачан архивом)
    xattr -cr "$APP_TARGET" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Приложение установлено в: ${BOLD}$APP_TARGET${NC}"
else
    echo -e "${YELLOW}⚠ Предупреждение: файл '$APP_SOURCE' не найден для копирования в Applications.${NC}"
fi

# 5. Проверка переменной PATH
echo -e "\n${BOLD}3. Проверка настроек окружения:${NC}"
PATH_OK=true
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    PATH_OK=false
    echo -e "${YELLOW}⚠ Каталог $BIN_DIR не добавлен в ваш \$PATH.${NC}"
    echo -e "Чтобы запускать команду ${CYAN}sleepmac${NC} из любого места терминала, добавьте строку в ${BOLD}~/.zshrc${NC}:"
    echo -e "  ${CYAN}export PATH=\"\$PATH:$BIN_DIR\"${NC}"
else
    echo -e "${GREEN}✓${NC} Каталог $BIN_DIR уже находится в вашем \$PATH"
fi

echo -e "\n${GREEN}${BOLD}🎉 Установка успешно завершена!${NC}"
echo -e "────────────────────────────────────────────────────────────"
echo -e "Как пользоваться:"
echo -e "  • В терминале:  введите команду ${CYAN}${BOLD}sleepmac${NC}"
echo -e "  • Напрямую:     ${CYAN}sleepmac 30m${NC}  или  ${CYAN}sleepmac 1h${NC}"
echo -e "  • Через мышку:  откройте ${CYAN}Таймер сна${NC} в папке Программы (Applications) или Spotlight"
echo -e "────────────────────────────────────────────────────────────\n"
