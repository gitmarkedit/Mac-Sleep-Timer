#!/usr/bin/env bash
# ==============================================================================
# Сборка нативного приложения macOS «Таймер сна.app»
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="Таймер сна.app"

echo "🔨 Сборка приложения '$APP_NAME' из SleepTimer.applescript..."
osacompile -o "$APP_NAME" SleepTimer.applescript

# Поиск системной иконки часов для красивого отображения в Dock и Finder
ICON_CANDIDATES=(
    "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/Clock.icns"
    "/System/Applications/Clock.app/Contents/Resources/AppIcon.icns"
    "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/SidebarTimeCapsule.icns"
)

APPLIED_ICON=false
for icon_path in "${ICON_CANDIDATES[@]}"; do
    if [ -f "$icon_path" ]; then
        cp "$icon_path" "$APP_NAME/Contents/Resources/applet.icns"
        APPLIED_ICON=true
        break
    fi
done

if [ "$APPLIED_ICON" = true ]; then
    echo "🎨 Применена системная иконка часов."
fi

# Снимаем карантин и обновляем метку времени
xattr -cr "$APP_NAME" 2>/dev/null || true
touch "$APP_NAME"

echo "✅ Приложение '$APP_NAME' успешно собрано и готово к запуску!"
