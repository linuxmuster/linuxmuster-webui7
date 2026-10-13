# lmn_clients

Client configuration plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets an administrator edit the custom logon/boot scripts run by Samba on the clients and manage the network drive letters (`Drives.xml`) of the current school.

Like every webui plugin it is only a front end: it reads and writes the files through its own `views.py`, which uses `linuxmusterTools` (`DriveManager` via the multischool `SchoolManager`) and the Samba sysvol on the server.

---

## Features (web interface)

Opened from the sidebar as **Client configuration** (category *Device Management*), the view is organised in tabs:

- **Custom scripts** — edit the per-school custom scripts that Samba runs when a client boots, in root context, after Linbo's postsync (a warning banner reminds that this runs as root and must be handled with caution). Two lists are shown:
  - **Linux**: `sessionstart.sh`, `logon.sh`, `sysstart.sh`, `sysstop.sh`
  - **Windows**: `logoff.bat`, `logon.bat`, `sysstart.bat`, `sysstop.bat`

  Each entry has an edit button opening a large modal with an **ace-editor**; **Save** writes the file back, **Close** dismisses it.
- **Drives** — manage the logon drives read from the school's `Drives.xml` policy. A warning is shown when no `Drives.xml` is found. Otherwise a table lists each drive with **Label**, a **Show letter** checkbox (`useLetter`), a **Letter** selector (free letters only, computed against the letters already in use) and a **Disable** checkbox. A floating **Save** toolbar pushes the configuration back.

The whole view is wrapped in a `samba-access` guard (hidden when the webui runs as root).

### Backend

`views.py` exposes four endpoints, all guarded by `lmn:clients:config`: read/write the custom scripts under `/var/lib/samba/sysvol/<realm>/scripts/<school>/custom/<linux|windows>/`, and read/write the drives through `self.context.schoolmgr.drivemgr` (`DriveManager` from `linuxmusterTools.samba_util`). The available-letter list is built from `string.ascii_letters`.

---

## Permissions

Declared in `main.py`, `default: False` (role defaults in `permissions.yml`):

| Permission | Grants |
|---|---|
| `lmn:clients:config` | read and write the custom scripts and the drive configuration |

---

## HTTP API

Mounted under `/api/lmn/`. All endpoints run in the authenticated user's worker.

| Method & path | Permission | Description |
|---|---|---|
| `GET /clients/scripts` | `lmn:clients:config` | Custom Linux/Windows scripts for the current school, with their content |
| `POST /clients/scripts` | `lmn:clients:config` | Write a script back to its path |
| `GET /samba/drives` | `lmn:clients:config` | Drives from `Drives.xml` plus the list of available drive letters |
| `POST /samba/drives` | `lmn:clients:config` | Save the drive configuration |

---

## Requirements

- The `lmn_common` plugin (dependency in `plugin.yml`), which provides the multischool `SchoolManager` / `drivemgr` and the Samba realm from `smb.conf`.
- `linuxmusterTools` (`samba_util.DriveManager`).
- A readable/writable Samba sysvol (custom scripts) and a group policy holding `Drives.xml`.
