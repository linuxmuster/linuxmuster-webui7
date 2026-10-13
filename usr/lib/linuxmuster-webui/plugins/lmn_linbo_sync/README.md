# lmn_linbo_sync

LINBO synchronization plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It shows, per hardware group, when each workstation last synced its image and lets an administrator trigger a remote sync/start.

The plugin is a front end over `linuxmusterTools.linbo` (last-sync parsing, workstation list) and `linbo-remote`; the heavy lifting lives in `linuxmuster-tools`, not here.

---

## Features (web interface)

Opened from the sidebar as **Linbo synchronization**, the view is grouped by hardware group (one block per group). For each group it shows a table of its workstations with **Hostname**, **IP**, **Mac address** and **Last sync**, where the last-sync date carries a freshness color (green / orange / red, or "No date found."). From there the administrator can:

- **Check online** — test which hosts are up and show their detected OS ("Online ?").
- **Power management** — halt or reboot the selected hosts.
- **Run linbo-remote command** — trigger a remote action (format / sync / start) on the hosts, with **Global options** applying to the whole group; the output comes back in **Result command**.
- **Apply** — launch the composed `linbo-remote` run.

### Backend

`views.py` exposes the endpoints below; `api.py` builds the `linbo-remote` command from the posted parameters (actions `format`, `sync`, `start`, plus an `acpi` halt/reboot). Depends on `lmn_linbo4` for the shared LINBO helpers.

---

## Permissions

Declared in `main.py`, all `default: False`:

| Permission | Grants |
|---|---|
| `lm:sync:list` | list the last syncs of the workstations |
| `lm:sync:online` | test whether a workstation is up |
| `lm:sync:sync` | run a remote sync on a workstation |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /linbosync/last_syncs` | `lm:sync:list` | Workstations dict with their LINBO last-sync info |
| `GET /linbosync/isOnline/<host>` | `lm:sync:online` | OS type if the host is online, `off` otherwise (`classify_host`) |
| `POST /linbosync/run` | `lm:sync:sync` | Run `linbo-remote` with the posted actions; returns `0` on success or an error string |

---

## Requirements

- Ajenti `core`, `lmn_common` and `lmn_linbo4` (dependencies in `plugin.yml`).
- `linuxmuster-tools` (`linuxmusterTools.linbo`) and a working `linbo-remote` on the server.
