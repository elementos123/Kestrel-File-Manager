#!/bin/bash
# Build a self-contained Kestrel-x86_64.AppImage from source.
#
# Run this on a real Linux machine (or WSL with WSLg/an X server available
# for interactive use — the build itself doesn't need a display). Tested on
# Ubuntu 22.04. Needs: python3, python3-venv, and the Qt runtime libraries
# below (only required to *build*; the AppImage bundles them for end users).
#
# Usage:
#   cd linux && ./build_appimage.sh
#
# Output: Kestrel-x86_64.AppImage in the repo root.

set -euo pipefail
cd "$(dirname "$0")/.."   # repo root
ROOT="$(pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "==> Installing system dependencies (requires sudo)"
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3-venv python3-pip \
    libgl1 libegl1 libxkbcommon0 libxkbcommon-x11-0 \
    libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 \
    libxcb-xkb1 libdbus-1-3 libfontconfig1 libfreetype6 \
    fuse libfuse2 wget file desktop-file-utils

echo "==> Creating build venv"
python3 -m venv "$WORK/venv"
source "$WORK/venv/bin/activate"
pip install --upgrade pip -q
pip install -r requirements.txt pyinstaller -q

echo "==> Rendering a Linux-sized app icon"
python3 -c "
from PIL import Image
Image.open('Kestrel.ico').convert('RGBA').resize((256, 256), Image.LANCZOS).save('assets/kestrel.png')
"

echo "==> Building with PyInstaller"
rm -rf build dist
pyinstaller Kestrel-linux.spec --noconfirm

echo "==> Assembling AppDir"
APPDIR="$WORK/AppDir"
mkdir -p "$APPDIR/usr/bin"
cp -r dist/Kestrel/* "$APPDIR/usr/bin/"
cp linux/kestrel.desktop "$APPDIR/"
cp linux/AppRun "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"
cp assets/kestrel.png "$APPDIR/kestrel.png"

echo "==> Fetching appimagetool"
if [ ! -f "$WORK/appimagetool" ]; then
    wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O "$WORK/appimagetool"
    chmod +x "$WORK/appimagetool"
fi

echo "==> Packaging AppImage"
rm -f Kestrel-x86_64.AppImage
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$WORK/appimagetool" "$APPDIR" Kestrel-x86_64.AppImage

echo "==> Done: $ROOT/Kestrel-x86_64.AppImage"
