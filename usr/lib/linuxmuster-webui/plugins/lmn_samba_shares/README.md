# lmn_samba_shares

Personal file-browser plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It gives every user a web view of their own Samba shares (home, and any share published to them), where they can navigate, upload, download, rename, move/copy and delete files.

It has no backend of its own: the whole view is a front end over the [`lmn_smbclient`](../lmn_smbclient) plugin's `smbclient` service and its `/api/lmn/smbclient/*` endpoints, which do the actual CIFS access on the server.

---

## Features (web interface)

Opened from the sidebar as **My files** (under *General*), at `/view/lmn/home`:

- **Share switcher** — a row of buttons, one per share returned for the logged-in user (the `Home` share is selected on load); the active share is highlighted. A share whose name is `null` (manually removed from the admin's `Drives.xml`) is ignored.
- **Breadcrumb** — the current path inside the active share, each segment clickable to navigate back up.
- **File listing** — directories first, then files; each row shows the file-type icon and, for files, the size. Per-item actions: **download**, **rename**, **delete** (file or directory), and a **selection** checkbox. The `transfer` and `.upload` entries of the home share are treated as protected (no rename/delete).
- **Upload** — drag-and-drop onto the list or the **Upload** button (chunked upload via `flow`), with a live per-file progress area.
- **Floating toolbars** — **New file**, **New directory** and **Upload**; a clipboard (**Cut** / **Copy** then **Paste here**) and a bulk **Delete** that appear once items are selected. The clipboard is kept in `$localStorage` and can be reviewed/cleared in a **Clipboard** modal.
- **Dialogs** — *New file* and *New directory* name prompts.
- The `root` user gets an empty view (loading simply stops): the browser is meant for domain users.

A **file-properties** partial (`properties.html`) is also shipped: name, full path, type, read/write/execute access, size, modified time, owner/group (uid/gid), octal mode with a **permission-bits** editor, and an **Edit in Notepad** shortcut for small files.

### Backend

None. `plugin.yml` has no `views.py`; `main.py` only registers the sidebar entry. Every file operation (`shares`, `list`, `move`, `copy`, `delete_file`, `delete_dir`, `createFile`, `createDirectory`, upload, download) is delegated to the `lmn_smbclient` service.

---

## Permissions

The plugin declares no Ajenti permission in `main.py`. Access is controlled by `permissions.yml`, which grants the sidebar entry `sidebar:view:/view/lmn/home` to every role (globaladministrator, schooladministrator, teacher, student, staff, parent).

---

## HTTP API

The plugin mounts no endpoint of its own. It consumes the `lmn_smbclient` API (`/api/lmn/smbclient/...`).

---

## Requirements

- Ajenti `core` and the `lmn_smbclient` plugin (dependencies in `plugin.yml`); `lmn_smbclient` provides the `smbclient` Angular service and the server-side CIFS access.
