# lmn_vdi_dashboard

VDI classroom dashboard plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets a user (teacher/student) pick an available VDI group and start a virtual desktop session, downloading the connection file to open it.

It is a front end over the `linuxmuster-linbo-vdi` tools on the server: the backend shells out to `/usr/lib/linuxmuster-linbo-vdi/getConnection.py` via `sudo` to create the session and hands back the generated connection file.

---

## Features (web interface)

Opened from the sidebar (**class** category) as **VDI Classroom**, the view (**VDI Desktops**) lists the **VDI Groups** as cards. Each card shows the group name and its number of **Available VMs**. If a group has at least one VM available, the card is clickable (play icon) and starting it creates a session and triggers the download of the VDI connection file (`vdi-session.vv`); if none is available, the card is disabled with a "No VMs available!" indicator.

The list of groups is loaded from the `lmn_vdi_administration` clones endpoint (`/api/lmn/vdi/administration/clones`); on error it shows a notification and an empty list.

### Backend

`views.py` exposes two endpoints:

- `GET /api/lmn/vdi/dashboard/vdiSession/<group>` runs `sudo /usr/lib/linuxmuster-linbo-vdi/getConnection.py <group> <username>` (username taken from `self.context.identity`), parses the returned JSON and returns the config file name.
- `GET /api/lmn/vdi/dashboard/download/<name>` serves the generated `/tmp/vdi/<name>` file as a download (`vdi-session.vv`), or responds forbidden if it does not exist.

Factually, neither endpoint carries an `@authorize(...)` guard, although the permission `lmn_vdi_dashboard:show` is declared in `main.py`; it is never enforced and the plugin ships no `permissions.yml`. The `<group>` segment uses the regex `.+` and is passed straight into the `sudo` command argv.

---

## Permissions

Declared in `main.py` but **not enforced** anywhere (no `@authorize` on the endpoints):

| Permission | Grants |
|---|---|
| `lmn_vdi_dashboard:show` | intended: access to the VDI dashboard (currently unused) |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /vdi/dashboard/vdiSession/<group>` | none | Create a VDI session for the current user and return the config file name (`getConnection.py`) |
| `GET /vdi/dashboard/download/<name>` | none | Download the generated connection file from `/tmp/vdi/<name>` |

The group listing it displays comes from `GET /api/lmn/vdi/administration/clones`, provided by the `lmn_vdi_administration` plugin.

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `linuxmuster-linbo-vdi` installed on the server (`/usr/lib/linuxmuster-linbo-vdi/getConnection.py`), callable via `sudo`.
- The `lmn_vdi_administration` plugin for the clones listing endpoint.
- `requirements.txt` is present but empty.
