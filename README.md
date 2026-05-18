🚀 UltraExplorer: Next-Gen File Manager for Power Users

  UltraExplorer es un explorador de archivos de alto rendimiento construido con Python 3 y PyQt6, diseñado para
  combinar la potencia de los administradores de archivos clásicos con la estética moderna de Windows 11 (Fluent
  Design).

  Este proyecto no es solo un clon del explorador nativo; es una herramienta de productividad optimizada para
  desarrolladores y usuarios avanzados que buscan velocidad, multitarea real y una interfaz libre de fricciones.

  💎 Características Principales

   * ⚡ Arquitectura Non-Blocking: Gestión de transferencias (copiar/mover) en segundo plano con hilos independientes.
     Sigue navegando mientras tus archivos se procesan sin congelar la UI.
   * 🌓 Interfaz Spotlight (Ctrl+K): Barra de comandos global con búsqueda fuzzy instantánea para saltar entre
     carpetas, archivos y comandos del sistema al estilo macOS o VS Code.
   * 👥 Modo Panel Dual (Ctrl+L): Vista dividida sincronizada para operaciones rápidas entre directorios, ideal para
     flujos de trabajo "Command-style".
   * 💻 Terminal Integrada: Consola real (PowerShell/Bash) empotrada que se sincroniza automáticamente con tu
     navegación actual.
   * 👁️ Previsualización de Próxima Generación:
       * Renderizado real de Markdown.
       * Resaltado de sintaxis (+50 lenguajes como Rust, Go, C++, Python, JS).
       * Previsualización instantánea de imágenes y datos CSV.
   * 🎨 Fluent Design 2.0: Temas dinámicos (Dark/Light), efectos de elevación, sombras y bordes reactivos para una
     experiencia visual premium.
   * 📂 Sidebar Inteligente: Secciones colapsables e indicadores visuales de capacidad de disco en tiempo real.

  🛠️ Stack Tecnológico

   * Lenguaje: Python 3.10+
   * Framework UI: PyQt6 (Qt 6.6+)
   * Procesamiento: QThreads para operaciones asíncronas.
   * Iconografía: QtAwesome (Material Design & FontAwesome).
   * Seguridad: Integración nativa con send2trash.

  📦 Instalación Rápida

   1 git clone https://github.com/elementos123/ultraexplorer.git
   2 cd ultraexplorer
   3 pip install -r requirements.txt
   4 python main.py

  ---

  💡 ¿Por qué UltraExplorer?
  A diferencia de los exploradores convencionales, UltraExplorer prioriza la visibilidad de datos y la eficiencia del
  teclado. Cada rincón del código ha sido refactorizado para garantizar que la memoria se gestione de forma óptima y
  que la búsqueda de archivos sea instantánea mediante el uso de os.scandir y algoritmos de debouncing.
