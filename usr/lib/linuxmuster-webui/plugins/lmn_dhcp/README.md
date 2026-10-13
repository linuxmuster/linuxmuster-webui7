# lmn_dhcp

DHCP leases plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It shows the current DHCP leases of the server and lets an administrator register an unknown host directly into the school's `devices.csv`.

The plugin reads the lease file with the `isc_dhcp_leases` library and reads/writes `devices.csv` through `linuxmusterTools.lmnfile`; it does not go through `linuxmuster-api`.

---

## Features (web interface)

Opened from the sidebar as **DHCP** (software category), the view is a single **DHCP Leases** table.

- **Leases table** — columns **Mac address**, **IP**, **Start**, **End**. For each lease already present in `devices.csv` a red **Already registered!** note is shown instead of the add button.
- **Register a device** — the **+** button (shown only for leases not yet registered) opens an *Add device* modal pre-filled with the lease MAC. Fields: **Room**, **Mac**, **IP** (flagged if already used), **Hostname** (flagged if already used), **Group**, **PXE Boot** and **Sophomorix role**. IP and hostname are validated before saving.
- **Save** / **Save & import** — *Save* appends the device to `devices.csv`; *Save & import* also opens the device import modal reused from `lmn_devices` (live log `/tmp/import_devices.log`).

### Backend

`views.py` reads the lease file `/var/lib/dhcp/dhcpd.leases` (via `IscDhcpLeases`) and cross-checks it against the devices file `/etc/linuxmuster/sophomorix/default-school/devices.csv` (hardcoded path) with `LMNFile`, returning both the leases and the already-used devices. Registering appends the new device to that CSV.

---

## Permissions

The plugin declares no permission of its own in `main.py` (only the sidebar entry). Its endpoints reuse the `lm:devices` / `lm:devices:import` permissions defined by `lmn_devices`.

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /dhcp/leases` | `lm:devices` | Current DHCP leases plus the registered devices (MAC/IP/hostname) from `devices.csv` |
| `POST /dhcp/register` | `lm:devices:import` | Append the posted device to `devices.csv` |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- The `isc_dhcp_leases` Python library.
- The DHCP lease file `/var/lib/dhcp/dhcpd.leases` and the devices file `/etc/linuxmuster/sophomorix/default-school/devices.csv`.
- The `lmn_devices` plugin, whose permissions and import modal are reused here.
