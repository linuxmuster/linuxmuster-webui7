# lmn_common

Shared foundation plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It is not a feature page of its own but the common layer every other `lmn_*` plugin depends on: the webui/Samba configuration, the multischool school context, the `linuxmuster-api` HTTP client, the sophomorix connector, the sidebar categories, and a set of shared Angular directives, services and the school switcher.

Most of it is backend/library code consumed via `from aj.plugins.lmn_common.api import …`; the few HTTP endpoints it mounts are generic file/version/school helpers used across the webui.

---

## Features (web interface)

`lmn_common` has no sidebar entry of its own. What it contributes to the UI:

- **Application skeleton** (`resources/content/main_view.html`) — the "School Console" page template: top navbar (logo, page title, quick search, session timer, profile menu with TFA / logout, machine name) and the current-school badge with a **(change)** link when the setup is multischool.
- **School switcher** (route `/view/lmn/change-school`) — a panel showing the **Current** school, a **Filter** search box and a list of all schools; clicking one switches the active school. Shown only when `school_show` is set (multischool and allowed); otherwise an info banner explains it is not a multischool setup.
- **Sidebar categories** — `main.py` registers the top-level sidebar groups other plugins attach to: *User Management*, *List Management*, *Quota*, *Device Management*, *Classroom*, *Settings*, *Global Settings*.
- **Shared Angular directives** used as access guards and widgets throughout the webui:
  - `admin-access`, `global-admin-access`, `teacher-access`, `samba-access` — replace a restricted page with a warning banner depending on `sophomorixRole` (the `samba-access` one also points a root user to the setup wizard).
  - `lm-log` — live tail of a server log file (polls `/api/lmn/log`), with an autoscroll toggle.
  - `lm-drag-upload` — drag-and-drop file upload widget.
- **Shared services / modals** — `lmFileEditor` (ace-based config editor with the `lmFileEditor.modal`), `lmFileBackups` (backup list and diff modals), `lmnNotify` (persistent notifications), `validation`, `wait`.

### Backend

- `api.py` loads `/etc/linuxmuster/webui/config.yml` once (LDAP config, password-reset config, samba override, display options, `allowed_roles`), reads `linuxmuster-api`'s host/port from `/etc/linuxmuster/api/config.yml`, reads the realm/workgroup/netbios from `/etc/samba/smb.conf`, and exposes the sophomorix connector `lmn_getSophomorixValue` (runs `sophomorix-* -j`, prefixed with `sudo` when not root, and parses the JSON output).
- `multischool.py` (`SchoolManager`) holds the active-school context: list of schools, config paths, custom fields, holidays, DFS shares, share prefix, `Drives.xml` (`DriveManager`/`GPOManager`), school long name, and the per-role share list / home path. `switch()` reloads everything for another school.
- `lmnapi_client.py` (`LmnapiClient`, instantiated per session in `lmn_auth`) is the authenticated HTTP client to `linuxmuster-api` (JWT from `GET /v1/auth/`), with helpers for passwords, quotas, management-group members, parents and printers, plus the `LmnapiUnavailable` / `LmnapiError` / `LmnapiTimeout` exceptions.
- `tools.py` provides `sort_schoolclasses` and `testSSH`.
- `views.py` mounts the generic HTTP endpoints below. The file/diff/log/setup endpoints are restricted to root at runtime (`os.getuid() != 0` → forbidden), which in Ajenti means admins only. The school and version endpoints carry no guard.

---

## HTTP API

Mounted under `/api/lmn/`. None of these use an `@authorize` guard; the file-related ones enforce a root-only check in the handler.

| Method & path | Guard | Description |
|---|---|---|
| `GET /log<path>` | root only | Return a log file from a given offset (for `lm-log`) |
| `POST /remove-file` | root only | Delete a file |
| `GET /read-config-setup` | root only | Read `/var/lib/linuxmuster/setup.ini` |
| `POST /diff` | root only | Unified diff between two files |
| `GET /version` | — | Installed `linuxmuster-*` / `sophomorix` package versions (`dpkg`) |
| `GET /activeschool` | — | Current active school |
| `GET /list-schools` | — | All schools with their long name |
| `POST /change-school` | — | Switch the active school |
| `POST /get-schoolname` | — | School long name for a given school |
| `GET /display_options` | — | Display options from the webui config |

> Note: `POST /change-school` currently has no permission guard or target-school membership check (known open item).

---

## Requirements

- Ajenti `core`, `ace` and `filesystem` plugins (dependencies in `plugin.yml`).
- `linuxmusterTools` (`lmnfile`, `ldapconnector`, `samba_util`, `common`) and `paramiko`, `dpath`, `configobj`.
- Config files read at import time: `/etc/linuxmuster/webui/config.yml`, `/etc/linuxmuster/api/config.yml`, `/etc/samba/smb.conf`, `/var/lib/linuxmuster/setup.ini`, and the per-school configs under `/etc/linuxmuster/sophomorix/<school>/`.
- A reachable `linuxmuster-api` for the `LmnapiClient` helpers, and `sophomorix` on the server for `lmn_getSophomorixValue`.
- `permissions.yml` here only sets role defaults for core/sidebar permissions; the plugin declares no permission of its own.
