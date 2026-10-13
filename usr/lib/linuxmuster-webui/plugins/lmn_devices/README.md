# lmn_devices

Device management plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets administrators edit the school's `devices.csv` (the list of workstations, servers, printers and other hosts) and trigger the device import into the system.

The plugin reads and writes the CSV directly through `linuxmusterTools.lmnfile` and launches the import with `linuxmuster-import-devices` via `subprocess`; it does not go through `linuxmuster-api`.

---

## Features (web interface)

Opened from the sidebar as **Devices** (device management category), the view is a large editable spreadsheet of the devices registered in `devices.csv`.

- **Editable table** — one row per device, columns are editable inline: **Room**, **Hostname**, **Group** (LINBO group, with a typeahead fed by `/api/lmn/linbo4/groups`), **MAC**, **IP**, **Office Key**, **Windows Key**, **DHCP-Options**, **Sophomorix-Role** (dropdown: classroom-student/teachercomputer, staffcomputer, faculty-teachercomputer, server, router, switch, printer, thinclient, byod, voip, wlan, iponly, mobile, addc), **PXE** (No PXE / Linbo-PXE / Linbo-PXE + OPSI-MGMT / OPSI-PXE), and the reserved fields **LMN-Reserved 10/12/13/14** and **Sophomorix-Comment**.
- **Field selector** — a *Fields* dropdown toggles which columns are shown (several are hidden by default); the view also has a **Filter** search box, a **sort** dropdown (Room / Group / Hostname / MAC / IP) and a **Rows** per-page selector (10/25/50/100/500 or custom).
- **Add a device** / **Duplicate** / **Remove** — a modal adds a new row (Room, Hostname, Group, MAC, IP, Sophomorix role, PXE Boot); each row can be duplicated or deleted.
- **Inline validation** — MAC, hostname, IP and room are validated per cell; empty cells and errors are counted and highlighted, and saving is blocked while errors remain. Hostname length is not enforced for server/router/printer/switch/iponly roles.
- **Floating toolbar** — **Save**, **Save & import** (saves then opens the import modal, which streams the live log `/tmp/import_devices.log`), **Edit CSV** (raw file editor) and a **backups** history button. Hotkeys: `Ctrl+S` save, `Ctrl+I` save & import, `Ctrl+B` backups.

The CSV path depends on the active school (`/etc/linuxmuster/sophomorix/default-school/devices.csv` for the default school, otherwise `.../<school>/<school>.devices.csv`).

### Backend

`views.py` reads/writes `<configpath>devices.csv` with `LMNFile` and runs the import. The import endpoint calls `linuxmuster-import-devices -s <school>` through `subprocess` (`shell=True`, output redirected to `/tmp/import_devices.log`).

---

## Permissions

Declared in `main.py`, all `default: False`:

| Permission | Grants |
|---|---|
| `lm:devices` | read and write `devices.csv` |
| `lm:devices:import` | run the device import into the system |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /devices` | `lm:devices` | Content of `devices.csv` (creates the file if missing) |
| `POST /devices` | `lm:devices` | Overwrite `devices.csv` with the posted rows |
| `POST /devices/import` | `lm:devices:import` | Run `linuxmuster-import-devices` for the active school, log to `/tmp/import_devices.log` |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `linuxmuster-tools` (`linuxmusterTools.lmnfile`) for CSV access.
- The `linuxmuster-import-devices` command on the server.
- The `lmn_linbo4` plugin endpoint `/api/lmn/linbo4/groups` for the group typeahead.
