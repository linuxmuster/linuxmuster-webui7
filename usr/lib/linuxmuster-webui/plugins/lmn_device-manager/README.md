# lmn_device-manager

> **Deprecated.** This plugin was contributed by Netzint and is no longer maintained. Its `/run` route — which executed any command sent by the client as root — has been removed, so the "Run" button of the Linbo-Remote modal no longer works. Use the **Linbo synchronization** plugin ([`../lmn_linbo_sync/README.md`](../lmn_linbo_sync/README.md)) for remote LINBO actions. The view shows a deprecation banner and will be removed in a future release. The rest is documented below for reference.

Device manager for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti): it lists the devices of the current school room by room, shows their online/OS status and offers power actions and (now broken) LINBO-Remote controls.

It is a front end over its own `views.py`, which reads the devices CSV through `linuxmusterTools` (`LMNFile`, `last_sync`), scans the network with `nmap`, and runs `linbo-remote`, `ssh`, `net rpc` as subprocesses.

---

## Features (web interface)

Opened from the sidebar as **Device-Manager** (category *Device Management*), the page shows a deprecation warning, then a two-pane layout:

- **Device list** (left) — a tile per device in the selected rooms, with a selection checkbox, an online dot (green/red/grey), an OS icon (Linux / Windows / Linbo / Unknown), the hostname and IP. Each tile has an **Options** dropdown (**Start**, **Shutdown**, **Reboot**, **Linbo-Remote**, **Linbo-Remote (Prestart)** — enabled or disabled depending on the device's OS, online state and `remoteBlock`), and an **Infos** dropdown showing room, hostname, IP, MAC, group, type, OS and online state. Servers and domain controllers are `remoteBlock`ed.
- **Sidebar** (right) — **LR-Processes** (count + modal listing the currently running `linbo-remote` commands with a live log), **LR-Prestart's** (count + modal to view, edit or delete the stored prestart commands), a **Refresh** button, an **Auto-Refresh** toggle with a configurable interval and countdown, the current school, and the list of **Rooms** as checkboxes to filter the device list.
- **Floating toolbar** — bulk **Start**, **Shutdown**, **Reboot** on the selected devices (opening a progress modal with success/error counters), and a select-all/count button.
- **Modals** — `linboremote.modal` (compose a `linbo-remote` command from per-OS format/sync/start plus global options — its **Run** button is the removed endpoint), `runningprocesses.modal`, `prestartcommands.modal`, `actionForAllDevices.modal`.

### Backend

`views.py` exposes the endpoints below. It reads the devices from the school's `devices.csv` via `LMNFile`, probes hosts with `python-nmap` (ping scan for online, ports 22/135/2222 for Linux/Windows/Linbo), triggers power actions (`linbo-remote` for Linbo, `ssh … init 0/6` for Linux, `net rpc … shutdown` with the administrator secret for Windows), parses `start.conf.<group>` for the LINBO config, reports the last sync via `linuxmusterTools.linbo.last_sync`, and reads/writes the prestart command files under `/srv/linbo/linbocmd/`. The former `POST /api/lmn/device-manager/run` has been removed.

---

## Permissions

Declared in `main.py`, all `default: False` (role defaults in `permissions.yml`):

| Permission | Grants |
|---|---|
| `lm:device-manager:read` | view the status and LINBO config of the devices |
| `lm:device-manager:modify` | manage the devices (power actions, prestart commands) |

---

## HTTP API

Mounted under `/api/lmn/device-manager/`.

| Method & path | Permission | Description |
|---|---|---|
| `POST /getdevices` | `lm:device-manager:read` | Devices read from the school's `devices.csv` |
| `POST /checkOnline` | `lm:device-manager:read` | nmap ping scan: `up` / `down` |
| `POST /checkOS` | `lm:device-manager:read` | Detect Linux / Windows / Linbo / Unknown by open port |
| `POST /shutdown` | `lm:device-manager:modify` | Shut down (linbo-remote / ssh / net rpc) |
| `POST /reboot` | `lm:device-manager:modify` | Reboot (linbo-remote / ssh / net rpc) |
| `POST /start` | `lm:device-manager:modify` | Wake / start via `linbo-remote -w 0` |
| `POST /getlinboconfig` | `lm:device-manager:read` | Parse `start.conf.<group>` OS sections |
| `POST /getlastsync` | `lm:device-manager:read` | Last sync date + freshness status for an image |
| `POST /getlinboremotelog` | `lm:device-manager:read` | Tail of the host's `.linbo-remote` log |
| `GET /getrunninglinboremotecommands` | `lm:device-manager:read` | Running `linbo-remote -l` processes |
| `GET /getPrestartCommands` | `lm:device-manager:read` | Prestart command files under `/srv/linbo/linbocmd/` |
| `POST /removePrestartCommands` | `lm:device-manager:modify` | Delete a prestart command file |
| `POST /editPrestartCommands` | `lm:device-manager:modify` | Overwrite a prestart command file |

The former `POST /run` (arbitrary command as root) has been removed.

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `linuxmusterTools` (`lmnfile.LMNFile`, `linbo.last_sync`) and `python-nmap`.
- On the server: `linbo-remote`, `ssh`, `net` (Samba), the devices CSV under `/etc/linuxmuster/sophomorix/<school>/`, `start.conf.<group>` and prestart files under `/srv/linbo/`, logs under `/var/log/linuxmuster/linbo/`, and the administrator secret `/etc/linuxmuster/.secret/administrator` (Windows power actions).
