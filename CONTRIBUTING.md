# Contributing to Kestrel

**Read this in: [English](#english) · [Español](#español)**

---

## English

Thanks for taking the time to contribute! This document covers the basics for
reporting bugs, suggesting features, and submitting code changes.

By participating in this project you agree to follow our
[Code of Conduct](CODE_OF_CONDUCT.md).

### Reporting bugs

Search [existing issues](../../issues) first to avoid duplicates, then open a
new one using the **Bug report** template. Include your OS, how you installed
Kestrel (installer/AppImage/from source), steps to reproduce, and — if
the app crashed — the relevant log from `~/.kestrel/logs/kestrel.log`
(Windows: `%USERPROFILE%\.kestrel\logs\`).

### Suggesting features

Open an issue with the **Feature request** template. Explain the problem
you're trying to solve, not just the solution you have in mind — it makes it
easier to discuss alternatives.

### Development setup

```bash
git clone https://github.com/elementos123/Kestrel-File-Manager.git
cd Kestrel-File-Manager
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+ and PyQt6 (Qt 6.6+).

### Making changes

1. Fork the repo and create a branch off `main` (`git checkout -b fix/short-description`).
2. Keep changes focused — a bug fix shouldn't also refactor unrelated code.
3. Match the existing style: no unrelated formatting churn, prefer the
   patterns already used in the file you're editing.
4. If you touch user-facing strings, add both the `es` and `en` entries in
   `src/i18n.py` (`STRINGS` dict) — don't hardcode text in dialogs/widgets.
5. There's no automated test suite yet. Run the app (`python main.py`) and
   manually exercise the feature/fix you changed, including both themes'
   light/dark variants if you touched styling.
6. Commit with a clear, descriptive message explaining *why*, not just *what*.

### Submitting a pull request

- Open the PR against `main` and fill in the PR template.
- Reference the issue it fixes/relates to, if any (`Fixes #123`).
- Keep the PR scoped to one change — smaller PRs get reviewed faster.
- Be ready to iterate on feedback; it's a normal part of the process, not a
  rejection.

### Building the installers

See the [README](README.md#building-the-installers) for Windows (PyInstaller
+ Inno Setup) and Linux (AppImage) build instructions — useful if your change
affects packaging.

---

## Español

¡Gracias por dedicar tiempo a contribuir! Este documento cubre lo básico para
reportar errores, sugerir funciones y enviar cambios de código.

Al participar en este proyecto aceptas seguir nuestro
[Código de Conducta](CODE_OF_CONDUCT.md).

### Reportar errores

Busca primero en los [issues existentes](../../issues) para evitar duplicados,
y luego abre uno nuevo usando la plantilla **Bug report**. Incluye tu sistema
operativo, cómo instalaste Kestrel (instalador/AppImage/código fuente),
pasos para reproducirlo y, si la app se cerró inesperadamente, el log
correspondiente en `~/.kestrel/logs/kestrel.log` (Windows:
`%USERPROFILE%\.kestrel\logs\`).

### Sugerir funciones

Abre un issue con la plantilla **Feature request**. Explica el problema que
quieres resolver, no solo la solución que tienes en mente — así es más fácil
discutir alternativas.

### Configurar el entorno de desarrollo

```bash
git clone https://github.com/elementos123/Kestrel-File-Manager.git
cd Kestrel-File-Manager
pip install -r requirements.txt
python main.py
```

Necesita Python 3.10+ y PyQt6 (Qt 6.6+).

### Hacer cambios

1. Haz un fork del repo y crea una rama a partir de `main`
   (`git checkout -b fix/descripcion-breve`).
2. Mantén los cambios acotados — una corrección de error no debería incluir
   también un refactor de código sin relación.
3. Sigue el estilo ya existente: sin cambios de formato innecesarios, prefiere
   los patrones que ya usa el archivo que estás editando.
4. Si tocas texto visible para el usuario, añade las entradas `es` y `en` en
   `src/i18n.py` (diccionario `STRINGS`) — no dejes texto hardcodeado en
   diálogos/widgets.
5. Todavía no hay suite de tests automatizados. Ejecuta la app
   (`python main.py`) y prueba manualmente la función/corrección que
   cambiaste, incluyendo las variantes claro/oscuro si tocaste estilos.
6. Escribe un mensaje de commit claro y descriptivo que explique el *por qué*,
   no solo el *qué*.

### Enviar un pull request

- Abre el PR contra `main` y completa la plantilla del PR.
- Referencia el issue que soluciona/relaciona, si aplica (`Fixes #123`).
- Mantén el PR enfocado en un solo cambio — los PRs pequeños se revisan más
  rápido.
- Prepárate para iterar según los comentarios; es parte normal del proceso,
  no un rechazo.

### Construir los instaladores

Consulta el [README](README.md#construir-los-instaladores) para las
instrucciones de compilación en Windows (PyInstaller + Inno Setup) y Linux
(AppImage) — útil si tu cambio afecta al empaquetado.
