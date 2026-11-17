.PHONY: help run test build install uninstall clean

help:
	@echo "🌙 Mac Sleep Timer — Доступные команды:"
	@echo "  make run        — Запустить интерактивное меню (TUI)"
	@echo "  make test       — Запустить все 18 юнит-тестов"
	@echo "  make build      — Собрать нативное приложение macOS (.app)"
	@echo "  make install    — Установить утилиту 'sleepmac' и приложение в систему"
	@echo "  make uninstall  — Удалить 'sleepmac' и приложение из системы"
	@echo "  make clean      — Очистить временные файлы и кэш Python"

run:
	@./sleepmac

test:
	@python3 -m unittest discover tests

build:
	@./build_app.sh

install:
	@./install.sh

uninstall:
	@./uninstall.sh

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf build dist *.egg-info .pytest_cache
