# lmn_vdi_administration

VDI administration plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It gives an administrator a read-only overview of the `linuxmuster-linbo-vdi` virtual desktop infrastructure: the master VMs per hardware group and all running clone VMs.

It is a thin front end over the `linuxmuster-linbo-vdi` tools installed on the server: the backend shells out to `/usr/lib/linuxmuster-linbo-vdi/getVmStates.py` via `sudo` and returns its JSON.

---

## Features (web interface)

Opened from the sidebar (**device management** category) as **VDI Administration**, the view is organised in two tabs:

- **Master VMs** — a table of the master VM groups with columns **Group**, **Hostname**, **IP-Address**, **MAC-Address** and **Master VMs**. The Master VMs column shows one button per master VM (disabled when the VM data is null). Clicking a group row opens a **group info** modal (Room, Hostname, MAC, IP, PXE-Boot yes/no, Image Size); clicking a master VM button opens a **master info** modal with a Summary table (Name, Status, Cloop, Build state, OS Type, Image size, Creation date) and a Hardware table (Memory, Cores, BIOS, SCSI, SCSI hardware, Audio, VGA, Network, USB, Spice enhancements).
- **All VMs** — loaded on tab click, a table of every clone VM with columns **Master-Group**, **VM ID**, **Room**, **Hostname**, **IP-Address**, **MAC-Address** and **User** ("No user" when unassigned).

If the VDI tools are not installed on the server, the backend returns an error and the view shows an error notification with an empty table.

### Backend

`views.py` exposes two GET endpoints that run `sudo /usr/lib/linuxmuster-linbo-vdi/getVmStates.py` with `-master` or `-clones`, strip lines containing `*` from the output, parse the remaining JSON and return it. Both first check that `/usr/lib/linuxmuster-linbo-vdi` exists (directory or symlink).

Factually, on both endpoints the `@authorize('lmn_vdi_administration:show')` guard is **commented out** (the dev comment reads "Set the right permissions if necessary, see main.py to activate it"), so VM state is read without any permission check. The matching permission is declared in `main.py` but never enforced, and the plugin ships no `permissions.yml`.

---

## Permissions

Declared in `main.py` but **not enforced** anywhere (the `@authorize` decorators are commented out):

| Permission | Grants |
|---|---|
| `lmn_vdi_administration:show` | intended: VDI administrator access (currently unused) |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /vdi/administration/masterVMs` | none (commented out) | Master VM group states (`getVmStates.py -master`) |
| `GET /vdi/administration/clones` | none (commented out) | All clone VM states (`getVmStates.py -clones`) |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `linuxmuster-linbo-vdi` installed on the server (`/usr/lib/linuxmuster-linbo-vdi/getVmStates.py`), callable via `sudo`.
- `requirements.txt` is present but empty.
