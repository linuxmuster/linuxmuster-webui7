# lmn_setup_wizard

First-run setup wizard for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). On a freshly installed, not-yet-provisioned server it walks the administrator through the initial configuration (school, server/domain, admin password, external services) and then launches the real provisioning.

It is a front end that collects answers into `/tmp/setup.ini` through `linuxmusterTools.lmnfile`, then runs `linuxmuster-setup` on the server to configure every service.

---

## Features (web interface)

The wizard has no sidebar entry: when a logged-in user opens the webui and the server is not yet configured (`is-configured` returns false, i.e. `/var/lib/linuxmuster/setup.ini` is missing), the app redirects to `/view/lmn/init/welcome`. It is a linear sequence of steps, each saving its fields to `/tmp/setup.ini` before moving on:

1. **Welcome** (`init-welcome.html`) — choose the system language (applied live) and read/accept the GNU GPL licence; **Next** is disabled until the licence box is ticked.
2. **School** (`init-school.html`) — school name, location, state, country/language, and server & domain information: server name (`[a-zA-Z0-9-]`), domain name (pattern-validated), with a note that the part before the first dot becomes the Samba domain (max 15 chars) and a read-only **Server FQDN** preview. Empty or malformed fields are highlighted red.
3. **Account** (`init-account.html`) — the global-admin / root password with confirmation, validated live for character set, strength (min 7 chars, upper/lower/special or digit) and matching confirmation; no `#` allowed.
4. **External Services** (`init-externalServices.html`) — toggles for external services (e.g. **Skip Firewall Configuration**); disabled services are written back as `null` so they are removed from `setup.ini`.
5. **Summary** (`init-summary.html`) — read-only recap of school, server/domain and firewall choices, with **Start provisioning**.
6. **Setup** (`init-setup.html`) — runs the provisioning: posts to `provision`, shows a working spinner, and **Finish** once done.
7. **Done** (`init-done.html`) — confirms completion, offers to **Close**, which restarts the webui master (`/api/core/restart-master`) and redirects to the SSL URL of the freshly configured server (built from the server IP/host and domain read back from the setup config).

Each step has **Back** / **Next** navigation.

### Backend

`views.py` reads and writes the wizard's scratch file `/tmp/setup.ini` (`RawConfigParser` / `LMNFile`), reports whether the server is already configured, and launches provisioning. The `provision` endpoint first re-checks that `/tmp/setup.ini` still holds the required fields (`schoolname`, `domainname`, `servername`, `adminpw`) — guarding against a stale/blank file after a reload or a second run, since `linuxmuster-setup`'s first module overwrites that file and clears `adminpw` — then runs `linuxmuster-setup -u -c /tmp/setup.ini`.

---

## Permissions

The plugin declares no `main.py` and no Ajenti permission. The setup endpoints use `@endpoint(auth=True)` (authenticated user required); `is-configured` is readable to decide whether to launch the wizard.

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Auth | Description |
|---|---|---|
| `GET /setup-wizard/setup` | authenticated | Read the collected settings from `/tmp/setup.ini` |
| `POST /setup-wizard/setup` | authenticated | Write/merge settings into `/tmp/setup.ini` (`null` removes a key) |
| `GET /setup-wizard/is-configured` | — | Whether `/var/lib/linuxmuster/setup.ini` exists |
| `POST /setup-wizard/provision` | authenticated | Validate the setup file, then run `linuxmuster-setup` |

The *Done* step additionally calls `/api/lmn/read-config-setup` (from `lmn_common`) and `/api/core/restart-master` (from `core`).

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `linuxmuster-tools` (`linuxmusterTools.lmnfile`).
- `linuxmuster-setup` on the server (does the actual provisioning); writes logs to `/tmp/linuxmuster-setup.log`.
- Writable `/tmp/setup.ini`; presence of `/var/lib/linuxmuster/setup.ini` marks the server as already configured.
