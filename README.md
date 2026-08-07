# UltraExplorer — Next-Gen File Manager for Power Users

A fast, keyboard-first file manager built with Python 3 and PyQt6, combining
the muscle memory of classic file managers with a modern Fluent Design
interface. Non-blocking file operations, a dual-panel mode, an integrated
terminal, instant fuzzy search, and full English/Spanish support out of the
box.

**Read this in: [English](#english) · [Español](#español)**

---

## English

### Why UltraExplorer

Most file manager side-projects are a thin skin over `QFileSystemModel`.
UltraExplorer instead treats the everyday friction points — slow copies that
freeze the UI, no keyboard-only workflow, no accessibility story, nothing to
help a first-time user find their footing — as the actual product. It ships
with logging and a crash handler instead of silent failures, a high-contrast
theme and full keyboard navigation instead of an afterthought, and installers
for both Windows and Linux instead of "clone and hope `pip install` works."

### Features

- **Non-blocking transfers** — copy/move runs on background threads with a
  floating, resizable transfer panel: live progress, pause/resume per
  transfer, and it keeps going past a single failed file instead of aborting
  the whole batch.
- **Spotlight (Ctrl+K)** — a global command bar with fuzzy search across
  folders, files, and app commands, VS Code / macOS Spotlight–style.
- **Dual-panel mode (Ctrl+L)** — a synced split view for fast operations
  between two directories, with reliable drag-and-drop between panels and
  active-panel tracking that follows real keyboard focus.
- **Integrated terminal** — a real PowerShell/Bash session embedded in the
  window, synced to your current folder.
- **Rich preview panel** — Markdown rendering, syntax highlighting for 50+
  languages, and instant image/CSV preview, no external app required.
- **14 themes**, including a WCAG-AA-oriented **high-contrast** theme, live
  accent colors, adjustable density/fonts/row height — and a responsive
  layout: the sidebar and toolbar adapt instead of clipping on narrow
  windows.
- **Onboarding & accessibility** — a first-run welcome tour, a searchable
  shortcuts reference, visible keyboard-focus rings, logical tab order, and
  accessible names for screen readers.
- **English / Spanish UI**, switchable from Settings.
- **Optional default file manager integration** — one click in Settings to
  make double-clicking a folder (and, on Windows, the Win+E shortcut) open
  UltraExplorer instead of the system file manager. Entirely opt-in, and one
  more click removes it and restores exactly what you had before.

### Installing

**Windows** — download `UltraExplorer_Setup.exe` from the
[latest release](../../releases/latest) and run it. No dependencies needed.

**Linux** — download `UltraExplorer-x86_64.AppImage` from the
[latest release](../../releases/latest):

```bash
chmod +x UltraExplorer-x86_64.AppImage
./UltraExplorer-x86_64.AppImage
```

Needs `libfuse2` on the system (already present on most desktop distros).
Prefer a plain install without AppImage/FUSE? See
[`linux/README.md`](linux/README.md) for the `install.sh` alternative (works
on any architecture pip has wheels for).

**From source** (any platform):

```bash
git clone https://github.com/elementos123/UltraExplorer-Next-Gen-File-Manager-for-Power-Users.git
cd UltraExplorer-Next-Gen-File-Manager-for-Power-Users
pip install -r requirements.txt
python main.py
```

### Key shortcuts

| Action | Shortcut |
|---|---|
| Spotlight command bar | `Ctrl+K` |
| Dual-panel mode | `Ctrl+L` |
| Toggle terminal | ``Ctrl+` `` |
| Toggle preview | `Ctrl+P` |
| Recursive search | `Ctrl+Shift+F` |
| Rename / multi-rename | `F2` / `Ctrl+R` |
| Full reference | Help → Keyboard shortcuts, or the Spotlight bar |

### Tech stack

Python 3.10+ · PyQt6 (Qt 6.6+) · QThreads for async file operations ·
QtAwesome icon set · `send2trash` for safe deletes.

### Building the installers

- Windows: `pyinstaller UltraExplorer.spec` then compile
  `installer_config.iss` with Inno Setup 6.
- Linux: `./linux/build_appimage.sh` (Ubuntu/Debian; installs its own build
  dependencies).

### License

No license has been chosen for this project yet — all rights reserved by
default until one is added.

---

## Español

### Por qué UltraExplorer

La mayoría de exploradores de archivos "de proyecto personal" son una capa
fina sobre `QFileSystemModel`. UltraExplorer trata en cambio los problemas
reales del día a día — copias lentas que congelan la interfaz, nada de
flujo por teclado, cero accesibilidad, nada que ayude a un usuario nuevo a
orientarse — como el producto en sí. Trae logging y un manejador de errores
en vez de fallos silenciosos, un tema de alto contraste y navegación
completa por teclado en vez de un añadido de última hora, e instaladores
para Windows y Linux en vez de "clona el repo y espera que `pip install`
funcione".

### Características

- **Transferencias sin bloqueo** — copiar/mover corre en hilos en segundo
  plano con un panel de transferencias flotante y redimensionable: progreso
  en vivo, pausa/reanudar por transferencia, y sigue adelante si un archivo
  falla en vez de abortar todo el lote.
- **Spotlight (Ctrl+K)** — barra de comandos global con búsqueda difusa
  instantánea entre carpetas, archivos y comandos de la app, al estilo
  VS Code / Spotlight de macOS.
- **Modo panel dual (Ctrl+L)** — vista dividida sincronizada para operar
  rápido entre dos carpetas, con arrastrar y soltar fiable entre paneles y
  detección del panel activo basada en el foco real del teclado.
- **Terminal integrada** — una sesión real de PowerShell/Bash empotrada en
  la ventana, sincronizada con la carpeta actual.
- **Panel de vista previa completo** — renderizado de Markdown, resaltado de
  sintaxis para más de 50 lenguajes, y vista previa instantánea de imágenes
  y CSV, sin depender de apps externas.
- **14 temas**, incluido uno de **alto contraste** orientado a WCAG-AA,
  color de acento en vivo, densidad/fuentes/altura de fila ajustables — y un
  diseño responsivo: el sidebar y la barra de herramientas se adaptan en vez
  de recortarse en ventanas estrechas.
- **Onboarding y accesibilidad** — tour de bienvenida en el primer arranque,
  referencia de atajos, anillo de foco visible por teclado, orden de
  tabulación lógico y nombres accesibles para lectores de pantalla.
- **Interfaz en español e inglés**, cambiable desde Ajustes.
- **Integración opcional como explorador predeterminado** — un clic en
  Ajustes para que hacer doble clic en una carpeta (y, en Windows, el atajo
  Win+E) abra UltraExplorer en vez del explorador del sistema. Totalmente
  opcional, y otro clic lo quita y restaura exactamente lo que tenías antes.

### Instalación

**Windows** — descarga `UltraExplorer_Setup.exe` desde la
[última versión](../../releases/latest) y ejecútalo. Sin dependencias que instalar.

**Linux** — descarga `UltraExplorer-x86_64.AppImage` desde la
[última versión](../../releases/latest):

```bash
chmod +x UltraExplorer-x86_64.AppImage
./UltraExplorer-x86_64.AppImage
```

Necesita `libfuse2` en el sistema (ya presente en la mayoría de distros de
escritorio). ¿Prefieres una instalación sin AppImage/FUSE? Mira
[`linux/README.md`](linux/README.md) para la alternativa `install.sh`
(funciona en cualquier arquitectura para la que pip tenga ruedas).

**Desde el código fuente** (cualquier plataforma):

```bash
git clone https://github.com/elementos123/UltraExplorer-Next-Gen-File-Manager-for-Power-Users.git
cd UltraExplorer-Next-Gen-File-Manager-for-Power-Users
pip install -r requirements.txt
python main.py
```

### Atajos principales

| Acción | Atajo |
|---|---|
| Barra de comandos Spotlight | `Ctrl+K` |
| Modo panel dual | `Ctrl+L` |
| Mostrar/ocultar terminal | ``Ctrl+` `` |
| Mostrar/ocultar vista previa | `Ctrl+P` |
| Búsqueda recursiva | `Ctrl+Shift+F` |
| Renombrar / renombrado múltiple | `F2` / `Ctrl+R` |
| Referencia completa | Menú Ayuda → Atajos de teclado, o la barra Spotlight |

### Stack tecnológico

Python 3.10+ · PyQt6 (Qt 6.6+) · QThreads para operaciones asíncronas ·
Iconos QtAwesome · `send2trash` para borrado seguro.

### Construir los instaladores

- Windows: `pyinstaller UltraExplorer.spec` y luego compila
  `installer_config.iss` con Inno Setup 6.
- Linux: `./linux/build_appimage.sh` (Ubuntu/Debian; instala sus propias
  dependencias de compilación).

### Licencia

Este proyecto todavía no tiene una licencia elegida — todos los derechos
reservados por defecto hasta que se añada una.
