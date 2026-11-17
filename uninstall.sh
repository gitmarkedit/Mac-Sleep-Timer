#!/usr/bin/env bash
# ==============================================================================
# Mac Sleep Timer — Скрипт удаления программы с macOS
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${RED}${BOLD}Удаление Mac Sleep Timer...${NC}"

# Удаление CLI утилит
rm -f "/usr/local/bin/sleepmac" "$HOME/.local/bin/sleepmac"
rm -rf "/usr/local/share/sleepmac" "$HOME/.local/share/sleepmac"

# Удаление приложений
rm -rf "/Applications/Таймер сна.app" "$HOME/Applications/Таймер сна.app"
rm -rf "/Applications/Sleep Timer.app" "$HOME/Applications/Sleep Timer.app"

echo -e "${GREEN}✓ Mac Sleep Timer полностью удален из системы.${NC}"
