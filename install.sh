#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/.local/share/whisper-local"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"


mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -d "$HOME/Applications/whisper/.venv" ]]; then
    echo "Не найден $HOME/Applications/whisper/.venv"
    echo "Скрипт ожидает, что Whisper уже установлен в ~/Applications/whisper/.venv"
    exit 1
fi

cp "$SCRIPT_DIR/app.py" "$APP_DIR/app.py"
chmod 644 "$APP_DIR/app.py"

cat > "$BIN_DIR/whisper-local" <<EOF
#!/usr/bin/env bash
exec "$HOME/whisper/.venv/bin/python" "$APP_DIR/app.py" "\$@"
EOF
chmod +x "$BIN_DIR/whisper-local"

cat > "$DESKTOP_DIR/whisper-local.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Whisper Local
Comment=Локальное распознавание речи через OpenAI Whisper
Exec=$HOME/Applications/whisper/.venv/bin/python $HOME/.local/share/whisper-local/app.py
Icon=audio-input-microphone
Terminal=false
Categories=AudioVideo;Audio;Utility;
StartupNotify=true
EOF
chmod 644 "$DESKTOP_DIR/whisper-local.desktop"

update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true

echo
echo "Готово."
echo "Запускай Whisper Local из меню приложений GNOME."
echo "Также доступна команда: $BIN_DIR/whisper-local"
