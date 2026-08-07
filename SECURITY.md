# Security Policy

**Read this in: [English](#english) · [Español](#español)**

---

## English

### Supported versions

Only the latest [release](../../releases/latest) receives security fixes.
Older releases are not patched — please update before reporting an issue to
confirm it still applies.

| Version | Supported |
|---|---|
| Latest release | ✅ |
| Older releases | ❌ |

### Reporting a vulnerability

Please **do not open a public issue** for security vulnerabilities.

Instead, report it privately using one of these two channels:

1. [GitHub Security Advisories](../../security/advisories/new) for this
   repository (preferred — keeps the discussion private until a fix ships), or
2. Email **yubalalberto1962@gmail.com** with details.

Please include:

- A description of the vulnerability and its potential impact.
- Steps to reproduce it (a minimal example helps a lot).
- The version/commit and platform (Windows/Linux) affected.

You should get an acknowledgment within a few days. Once a fix is confirmed,
a new release will be published and the reporter credited (unless you'd
rather stay anonymous) in the release notes.

### Scope notes

Kestrel is a desktop file manager. Things particularly worth flagging:

- Any file operation (copy/move/delete/rename) that could escape its intended
  target path (path traversal, symlink handling).
- The opt-in "set as default file manager" integration
  (`src/system_integration.py`) — it only ever writes to
  `HKEY_CURRENT_USER` on Windows or `~/.config/mimeapps.list` on Linux, never
  to system-wide locations; a bug that changed this behavior would be a
  security issue.
- The integrated terminal spawning unintended commands.

---

## Español

### Versiones soportadas

Solo la última [release](../../releases/latest) recibe correcciones de
seguridad. Las versiones anteriores no se parchean — por favor actualiza
antes de reportar un problema para confirmar que sigue presente.

| Versión | Soportada |
|---|---|
| Última release | ✅ |
| Releases anteriores | ❌ |

### Reportar una vulnerabilidad

Por favor **no abras un issue público** para vulnerabilidades de seguridad.

En su lugar, repórtala en privado usando uno de estos dos canales:

1. [GitHub Security Advisories](../../security/advisories/new) de este
   repositorio (preferido — mantiene la conversación privada hasta que se
   publique una corrección), o
2. Correo a **yubalalberto1962@gmail.com** con los detalles.

Por favor incluye:

- Una descripción de la vulnerabilidad y su impacto potencial.
- Pasos para reproducirla (un ejemplo mínimo ayuda mucho).
- La versión/commit y plataforma (Windows/Linux) afectada.

Deberías recibir una confirmación en pocos días. Una vez validada la
corrección, se publicará una nueva release y se acreditará a quien reportó el
problema (salvo que prefiera mantenerse anónimo) en las notas de la release.

### Notas de alcance

Kestrel es un explorador de archivos de escritorio. Aspectos
especialmente relevantes para reportar:

- Cualquier operación de archivos (copiar/mover/borrar/renombrar) que pueda
  salirse de la ruta prevista (path traversal, manejo de symlinks).
- La integración opcional "explorador predeterminado"
  (`src/system_integration.py`) — solo escribe en `HKEY_CURRENT_USER` en
  Windows o en `~/.config/mimeapps.list` en Linux, nunca en ubicaciones a
  nivel de sistema; un fallo que cambiara ese comportamiento sería un
  problema de seguridad.
- La terminal integrada ejecutando comandos no previstos.
