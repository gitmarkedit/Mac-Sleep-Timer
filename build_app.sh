#!/usr/bin/env bash
# Сборка нативного приложения macOS «Таймер сна.app»
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔨 Сборка приложения 'Таймер сна.app' из SleepTimer.applescript..."
osacompile -o "Таймер сна.app" SleepTimer.applescript

CLOCK_ICNS="/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/Clock.icns"
if [ -f "$CLOCK_ICNS" ]; then
    echo "🎨 Применение системной иконки часов..."
    cp "$CLOCK_ICNS" "Таймер сна.app/Contents/Resources/applet.icns"
fi

touch "Таймер сна.app"
echo "✅ Приложение 'Таймер сна.app' успешно собрано!"
