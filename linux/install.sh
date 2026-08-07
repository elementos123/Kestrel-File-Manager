#!/bin/bash
# Lightweight install for Kestrel on Linux: no PyInstaller/AppImage
# involved, just a private virtualenv plus a launcher and a menu entry.
# Works on any architecture pip has wheels for, unlike the x86_64-only
# AppImage. Safe to re-run (updates the venv and shortcuts in place).
#
# Usage:
#   ./linux/install.sh            # install for the current user
#   ./linux/install.sh --uninstall

set -euo pipefail
cd "$(dirname "$0")/.."   # repo root
ROOT="$(pwd)"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/kestrel"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"

if [ "${1:-}" = "--uninstall" ]; then
    echo "Removing Kestrel..."
    rm -rf "$INSTALL_DIR"
    rm -f "$BIN_DIR/kestrel"
    rm -f "$DESKTOP_DIR/kestrel.desktop"
    rm -f "$ICON_DIR/kestrel.png"
    echo "Done."
    exit 0
fi

echo "==> Installing Kestrel to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"
cp -r "$ROOT/src" "$ROOT/main.py" "$ROOT/requirements.txt" "$INSTALL_DIR/"
find "$INSTALL_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "==> Creating virtualenv"
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip -q
pip install -r "$INSTALL_DIR/requirements.txt" -q
deactivate

echo "==> Writing launcher"
cat > "$BIN_DIR/kestrel" << LAUNCHER
#!/bin/bash
exec "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/main.py" "\$@"
LAUNCHER
chmod +x "$BIN_DIR/kestrel"

if [ -f "$ROOT/assets/kestrel.png" ]; then
    cp "$ROOT/assets/kestrel.png" "$ICON_DIR/kestrel.png"
fi

sed "s|Exec=Kestrel|Exec=$BIN_DIR/kestrel|" "$ROOT/linux/kestrel.desktop" \
    > "$DESKTOP_DIR/kestrel.desktop"

if command -v update-desktop-database >/dev/null; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo "Note: $BIN_DIR is not on your PATH — add it, or launch from your app menu." ;;
esac

echo "==> Done. Launch it from your applications menu, or run: kestrel"
