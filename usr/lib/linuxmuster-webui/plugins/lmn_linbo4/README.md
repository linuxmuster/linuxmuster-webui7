# lmn_linbo4

LINBO 4 management plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets administrators edit the LINBO boot configurations (`start.conf.*`), their partitions and OS entries, and manage the LINBO images stored on the server (`/srv/linbo`).

The plugin reads and writes the LINBO files directly on the server through `linuxmusterTools` (`LMNFile`, `LinboImageManager`); the privileged image work runs only in the root worker (`os.getuid() == 0`).

---

## Features (web interface)

Opened from the sidebar as **LINBO 4** (under *Device management*), the view has two tabs:

- **Groups** — a table of every hardware group (one `start.conf.<group>`) with **Group name**, **Used images** (shown as labels, `.qcow2` highlighted) and **Actions** (edit, duplicate, delete). A floating toolbar offers **Download Linbo Boot** (the LINBO ISO), **Import devices** (shown after a config change) and a **Create** dropdown to start an empty config or one copied from an example.
- **Images** — a table of the images found on the server with **Name** / size, **Differential image** (with edit and delete), **Used in group ...** labels and per-row actions: edit extras, show **backups** (history), duplicate, delete. Rows can be checkbox-selected to **Delete selected images**. An info banner is shown when no image exists yet.

Editing happens through several modals:

- **Config editor** (`config.modal.html`) — tabs **General** (root logout timeout, system/download type, start options, LINBO GUI language, background color via colorpicker, kernel options), **Partitions** (add/remove/edit partitions and disks: EFI, MSR, Windows, Linux, Swap, Data, Extended, Cache) and **Virtual Desktop (VDI)** (VM template settings, VM name, BIOS type).
- **Partition editor** (`partition.modal.html`) — label, size, flags, partition type, filesystem, and the attached **OS** (name, version, default, icon, base/differential image, boot buttons, autostart timeout, kernel/initrd and parameters, OPSI options, advanced settings).
- **Image editor** (`image.modal.html`) — tabs **General** (description, info, size), **Registry patch**, **Postsync Script** and **Prestart Script**, each with an insert-example helper.
- **Backups** (`image.backups.modal.html`) — list of backups per image (status, name/size, comment) to restore or delete.
- **Import devices** (`apply.modal.html`) — progress/log view while importing devices.
- **Remove partition** confirmation (`accept.modal.html`).

### Backend

`views.py` exposes the endpoints below, guarded by the plugin permissions. Config files are read/written with `LMNFile`; images are handled by `linuxmusterTools.linbo.LinboImageManager` (list, save extras, delete, rename, duplicate, restore/delete/save backups, delete diff). Config/image names are validated with `NameChecker.check_linbo_conf_name`, and file-serving endpoints guard the path against directory traversal.

---

## Permissions

Declared in `main.py`, all `default: False`:

| Permission | Grants |
|---|---|
| `lm:linbo:configs` | read/write `start.conf` files and restart image services |
| `lm:linbo:images` | read/write images, backups, diff and VDI settings |
| `lm:linbo:examples` | read the example files under `/srv/linbo/examples` |
| `lm:linbo:icons` | read/write the LINBO icons |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /linbo4/groups` | `lm:linbo:configs` | List the LINBO groups (valid `start.conf.*`) |
| `GET /linbo4/configs` | `lm:linbo:configs` | All configs with their images and LINBO settings |
| `GET /linbo4/examples/<type>` | `lm:linbo:examples` | List example files (`config`, `reg`, `postsync`, `prestart`) |
| `GET /linbo4/icons` | `lm:linbo:icons` | List the `.svg` icons |
| `GET /linbo4/icons/<name>` | — (page) | Serve an icon file (path-guarded) |
| `GET /linbo4/vdi/<name>` | `lm:linbo:images` | Read VDI settings for an image |
| `POST /linbo4/vdi/<name>` | `lm:linbo:images` | Write VDI settings for an image |
| `GET /linbo4/config/<name>` | `lm:linbo:configs` | Read a `start.conf` (also from `examples/`) |
| `POST /linbo4/config/<name>` | `lm:linbo:configs` | Write a `start.conf` |
| `DELETE /linbo4/config/<name>` | `lm:linbo:configs` | Back up then delete a `start.conf` and its grub `.cfg` |
| `GET /linbo4/images` | `lm:linbo:images` | List all images with their details |
| `POST /linbo4/images/<image>` | `lm:linbo:images` | Save an image's extras (optionally on the diff) |
| `DELETE /linbo4/images/<image>` | `lm:linbo:images` | Delete an image |
| `POST /linbo4/renameImage/<image>` | `lm:linbo:images` | Rename an image |
| `POST /linbo4/duplicateImage/<image>` | `lm:linbo:images` | Duplicate an image |
| `POST /linbo4/restoreBackupImage/<image>` | `lm:linbo:images` | Restore a backup by date |
| `POST /linbo4/deleteBackupImage/<image>` | `lm:linbo:images` | Delete a backup by date |
| `POST /linbo4/saveBackupImage/<image>` | `lm:linbo:images` | Save a backup's extras with a timestamp |
| `DELETE /linbo4/deleteDiffImage/<image>` | `lm:linbo:images` | Delete an image's differential image |
| `GET /linbo4/restart-services` | `lm:linbo:configs` | Restart the torrent and multicast services |
| `GET /lmn/download/linbo.iso` | — (page) | Download `/srv/linbo/linbo.iso` |

---

## Requirements

- Ajenti `core`, `filesystem`, `lmn_common` and `lmn_devices` (dependencies in `plugin.yml`).
- `linuxmuster-tools` (`linuxmusterTools.lmnfile`, `linuxmusterTools.linbo`, `linuxmusterTools.common.checks`).
- The LINBO tree under `/srv/linbo` (configs, `examples/`, `icons/`, `boot/grub`, `linbo.iso`).
- The `angular-bootstrap-colorpicker` vendor library (bundled under `resources/vendor`).
