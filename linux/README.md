# Instalación en Linux

Dos formas de instalar UltraExplorer, según lo que prefieras:

## Opción 1 — AppImage (recomendada)

Descarga `UltraExplorer-x86_64.AppImage` desde `user_installer/`, dale permiso de
ejecución y lánzala. No necesita instalación ni root:

```bash
chmod +x UltraExplorer-x86_64.AppImage
./UltraExplorer-x86_64.AppImage
```

Todo (Python, PyQt6, fuentes de iconos) va empaquetado dentro — solo necesitas
`libfuse2` instalado en el sistema (`sudo apt install libfuse2` en Debian/Ubuntu;
casi todas las distros de escritorio ya lo traen). Solo funciona en x86_64.

Para reconstruirla desde el código fuente tras cambios: `./linux/build_appimage.sh`
(requiere sudo para instalar dependencias de sistema la primera vez).

## Opción 2 — Instalación con venv (`install.sh`)

Sin PyInstaller ni AppImage de por medio: crea un entorno virtual privado,
un lanzador y una entrada en el menú de aplicaciones. Funciona en cualquier
arquitectura para la que pip tenga ruedas (ARM incluido), a costa de necesitar
Python 3 instalado en el sistema.

```bash
./linux/install.sh              # instala para el usuario actual
./linux/install.sh --uninstall  # desinstala
```

## Archivos de esta carpeta

- `ultraexplorer.desktop` — entrada de escritorio (freedesktop).
- `AppRun` — punto de entrada que usa el AppImage.
- `build_appimage.sh` — reconstruye la AppImage desde cero.
- `install.sh` — instalador alternativo basado en venv.
