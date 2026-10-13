# lmn_settings

Settings plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It holds the two configuration hubs of the server: the per-school **School Settings** (mostly `sophomorix`'s `school.conf` and related files) and the server-wide **Global Settings** (webui/API config, subnets, SMTP relay, allowed roles, API keys, external services).

It is a front end that reads and writes config files through `linuxmusterTools.lmnfile` (`school.conf`, `subnets.csv`, `holidays.yml`, `custom_fields.yml`, `password_constraints.yml`, the webui and `linuxmuster-api` `config.yml`), and shells out to `sophomorix-check`, `linuxmuster-import-subnets` and `systemctl` where needed.

---

## Features (web interface)

Two sidebar entries (under *School settings / defaults*).

### School Settings (`/view/lmn/schoolsettings`)

Reads/writes the active school's `school.conf` (and related files) in tabs:

- **General** — school long name, per-role mail domains (students, teachers, adminclass, teacherclass, project) and the print server.
- **Listimport** — username/password generation per user file (students / teachers / extrastudents): reverse surname/firstname, surname/firstname chars, password length, random password, tolerance & deactivation days, slash-to-hyphen in class names; CSV **encoding** (with detected encoding via `sophomorix-check`); and a custom **filter script** path per file.
- **Quota** — default global/school quota, cloud-quota percentage and mail-quota default, per role (student / teacher / schooladministrator).
- **Printing data** — password-sheet header (school name, admin description), landing-page / webui / Moodle / webmail URLs and comments printed on the sheets, and the choice of **LaTeX templates** (one-per-page and multiple-per-page) discovered under the school's and the global sophomorix template directories.
- **Custom fields** — per role (students/teachers/school- and global-administrators): configure the sophomorix *custom*, *customMulti* and *proxyAddresses* fields (title, show in user details, user-editable) and which custom values appear in user lists.
- **Holidays** — table of holiday ranges (name, start, end) with date validation, add/remove.
- **Password constraints** — per-role password rules: a **default** block (all schools, editable only by global administrators) and an optional **per-school override** (minimum length, required character classes, required count).

A floating toolbar offers context-sensitive actions per tab: **Save**, **Save & check** (General), **Save & Apply Quota** (Quota), **Save** for holidays/custom fields/password constraints, plus a **backups** button.

### Global Settings (`/view/lmn/globalsettings`)

Server-wide configuration in tabs:

- **General** — language, max session time, SSL certificate / FQDN certificate paths, force SSL, trusted domains and proxies. Buttons: **Save**, **Restart WebUI**.
- **Subnets** — editable table of `subnets.csv` (network/prefix, router IP, lease range, nameserver, tftp server, setup flag) with a danger warning; **Save & Apply Subnets** runs `linuxmuster-import-subnets`.
- **Smtp relay** — enable the mail relay and set SMTP host/port (TLS 587 / SSL 465), user, password (show/hide), and the reset-email template.
- **Allowed roles** — which roles may log into the webui (globaladministrator is forced on).
- **Api Keys** — manage `linuxmuster-api` host keys: enable host-key auth, add/edit/delete keys with IPs, scope (method+path globs, `*` / `**`), associated user context, and reveal the generated secret once. Shows a notice when `linuxmuster-api` is not installed.
- **2FA** — list and delete registered second-factor tokens.
- **Edulution UI** — status checks (API installed, API running, bind-user exists), create the edulution bind user, set the external domain, and generate/copy the edulution setup token.
- **About Linuxmuster.net** — table of installed package versions.

### Backend

`views.py` exposes the endpoints below. School-settings reads/writes `school.conf`, `custom_fields.yml`, `password_constraints.yml` and `holidays.yml` via `LMNFile` (and `setup.ini` on school rename); password-constraint rules are validated with `linuxmusterTools.passwords.PasswordRules` and scoped by the caller's real `sophomorixRole`. Subnet save shells out to `linuxmuster-import-subnets`. The edulution, allowed-roles and API-key endpoints are guarded by an `os.getuid() != 0` check (valid in Ajenti, where workers are forked per role) rather than `@authorize`; API-key changes restart `linuxmuster-api` via `systemctl`.

---

## Permissions

Declared in `main.py`, all `default: False`:

| Permission | Grants |
|---|---|
| `lm:schoolsettings` | configure the per-school settings |
| `lm:globalsettings` | configure the server-wide (global) settings |

---

## HTTP API

Mounted under `/api/lmn/`. Endpoints without an `@authorize` guard are restricted by an `os.getuid() != 0` check instead (403 for non-root/non-admin workers).

| Method & path | Permission | Description |
|---|---|---|
| `GET /schoolsettings` | `lm:schoolsettings` | Read `school.conf` |
| `POST /schoolsettings` | `lm:schoolsettings` | Write `school.conf` (and `setup.ini` schoolname) |
| `POST /schoolsettings/determine-encoding` | `lm:schoolsettings` | Detect a CSV file's encoding |
| `GET /schoolsettings/latex-templates` | `lm:schoolsettings` | List the LaTeX password templates |
| `GET /config/customfields/<role>` | `lm:schoolsettings` | Read the custom-fields config |
| `POST /config/customfields` | `lm:schoolsettings` | Save the custom-fields config |
| `GET /config/passwordconstraints` | `lm:schoolsettings` | Read password constraints (scoped by role) |
| `POST /config/passwordconstraints` | `lm:schoolsettings` | Validate & save password constraints |
| `GET /holidays` | `lm:schoolsettings` | Read `holidays.yml` |
| `POST /holidays` | `lm:schoolsettings` | Write `holidays.yml` |
| `GET /subnets` | `lm:globalsettings` | Read `subnets.csv` |
| `POST /subnets` | `lm:globalsettings` | Write `subnets.csv` and run `linuxmuster-import-subnets` |
| `GET /edulution/api-status` | *(getuid n/a — no secret)* | Edulution API install/run status |
| `POST /edulution/generate` | *(getuid root-only)* | Generate the edulution setup hash |
| `GET /webuisettings/allowed_roles` | *(getuid root-only)* | Read the webui allowed roles |
| `POST /webuisettings/allowed_roles` | *(getuid root-only)* | Save the webui allowed roles |
| `GET /apisettings` | *(getuid root-only)* | Read `linuxmuster-api` host keys |
| `POST /apikeys` | *(getuid root-only)* | Save host keys (restarts the API) |
| `PUT /apikeys` | *(getuid root-only)* | Generate a secret for a new key (restarts the API) |
| `DELETE /apikeys/<keyname>` | *(getuid root-only)* | Delete a host key (restarts the API) |

Several tabs of the Global Settings page also call endpoints owned by other plugins (ajenti config, 2FA, SMTP config, package versions, `/api/lmn/read-config-setup`), which are not part of this plugin.

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`); `lmn_common` provides `allowed_roles`, `ALL_ROLES`, `config_path` and the school manager context.
- `linuxmuster-tools` (`linuxmusterTools.lmnfile`, `linuxmusterTools.passwords`).
- `sophomorix` (`sophomorix-check`, LaTeX template dirs) and `linuxmuster-import-subnets` on the server.
- Config files: `school.conf`, `/etc/linuxmuster/subnets.csv`, `/etc/linuxmuster/sophomorix/<school>/{holidays.yml,custom_fields.yml,latex-templates/}`, `/etc/linuxmuster/tools/password_constraints.yml`, the webui `config.yml` and (optionally) `/etc/linuxmuster/api/config.yml`.
