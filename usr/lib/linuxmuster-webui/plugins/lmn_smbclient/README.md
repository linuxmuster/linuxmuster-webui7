# lmn_smbclient

Samba share access plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It gives the webui read/write access to the user's Samba shares (home, class, project, global shares) over SMB, and additionally exposes those shares through a WebDAV server.

Unlike most lmn plugins, `lmn_smbclient` does not call `linuxmuster-api`: it talks to Samba directly with the Python `smbclient` library, under the identity (Kerberos ticket) of the logged-in user. It is mostly a **service/library plugin** — it ships no view of its own, but provides the backend endpoints and the Angular `smbclient` service used by the file manager and other plugins (e.g. the session/exam views).

---

## Features (web interface)

The plugin registers no sidebar entry and no standalone page (its `main.py` only imports the provider base classes and declares nothing). What it provides to the rest of the webui is:

- **`smbclient` Angular service** (`resources/js/services/smbclient.service.es`) — the client-side file API consumed by other plugins: `shares(user)`, `list(path)`, `stat(path)`, `createFile`, `createDirectory`, `move(src, dst)`, `copy(src, dst)`, `delete_file`, `delete_dir`, chunked upload (`startFlowUpload`), and `refresh_krbcc()` (prompts the user for their password to renew the Kerberos ticket).
- **`<smb-upload>` directive** (`resources/js/directives/smbupload.directive.coffee`) — a drag-and-drop / "Upload file" widget built on ng-flow that uploads files in 1 MiB chunks to a share, shows a per-file progress bar, and can append the new files to the parent view's listing without a full reload.

Through these, the user can browse a share, create files and folders, rename/move, copy, delete, upload (chunked) and download. A single file downloads directly; a directory is streamed as a generated ZIP. Overwrite is avoided on upload by auto-numbering `name (1).ext`, `name (2).ext`, etc. A `STATUS_DISK_FULL` from Samba is surfaced to the user as a quota-full message.

Two helpers support the classroom "collect/handout" workflow of other plugins: `createSessionWorkingDirectory` creates `HOME/transfer/<teacher>/_collect` for each participant, and `listCollectDir` lists what each participant dropped there.

### WebDAV

`views/lmnwebdav.py` implements a full WebDAV server under `/webdav/` (OPTIONS, PROPFIND, GET, PUT, DELETE, MKCOL, MOVE, COPY), backed by the same Samba shares and the custom `davxml.py` PROPFIND response builder. GET supports HTTP range requests and zips directories on the fly. The root PROPFIND lists the user's shares; paths are mapped to the school / global Samba share according to the caller's `sophomorixRole`. `/api/webdav/qrcode` returns a QR code (server name, WebDAV URL, username) to configure an external WebDAV client.

### Backend

Two view files, both wrapping `smbclient` calls in a `credit_wrapper` retry (handles the SMB "0 credits are available" error):

- `views/lmnsmbclient.py` — the `/api/lmn/smbclient/*` REST endpoints (listing, file ops, chunked upload, download, Kerberos ticket refresh, collect dirs).
- `views/lmnwebdav.py` — the `/webdav/*` WebDAV methods plus `/api/webdav/list` and `/api/webdav/qrcode`; uses `linuxmusterTools.quotas.samba_root_tree` for the full file tree.

Shares, home paths and school/global share roots are resolved through `self.context.schoolmgr`.

---

## HTTP API

Mounted on the Ajenti worker of the authenticated user. None of these endpoints carry an `@authorize(...)` guard (the only one present, `# @authorize('smbclient:write')` on `finish-upload`, is commented out); access control relies on the per-user Samba/Kerberos identity and the WebDAV OPTIONS being `auth=False`.

### SMB REST (`/api/lmn/smbclient/`)

| Method & path | Description |
|---|---|
| `GET /shares/<user>` | Hard-coded list of shares for the user's role |
| `POST /list` | List files/directories of a posted `path` |
| `POST /directory` | Create a directory |
| `POST /file` | Create an empty file |
| `POST /move` | Rename/move `src` to `dst` |
| `POST /copy` | Copy a file or (recursively) a directory |
| `POST /rmdir` | Delete a directory recursively (TODO: should be DELETE) |
| `POST /unlink` | Delete a file (TODO: should be DELETE) |
| `GET /stat/<path>` | POSIX stat of a path |
| `GET /upload` | Check whether an upload chunk is already present |
| `POST /upload` | Write one upload chunk to `HOME/.upload/` |
| `POST /finish-upload` | Reassemble chunks into the final file(s) |
| `GET /download` | Download a file, or a directory as ZIP (base64 path) |
| `POST /refresh_krbcc` | Renew the user's Kerberos ticket (kdestroy + kinit via pexpect) |
| `POST /createSessionWorkingDirectory` | Create `transfer/<teacher>/_collect` for users |
| `POST /listCollectDir` | List the collect dir of each participant |

### WebDAV (`/webdav/` and `/api/webdav/`)

| Method & path | Description |
|---|---|
| `GET /api/webdav/list` | Full Samba file tree for the user (`samba_root_tree`) |
| `GET /api/webdav/qrcode` | QR code + metadata to set up an external WebDAV client |
| `OPTIONS /webdav`, `/webdav/<path>` | DAV capabilities (`auth=False`) |
| `PROPFIND /webdav`, `/webdav/<path>` | List shares (root) or a directory/file's properties |
| `GET /webdav/<path>` | Download a file or zipped directory (range support) |
| `PUT /webdav/<path>` | Upload/overwrite a file |
| `DELETE /webdav/<path>` | Delete a file or directory recursively |
| `MKCOL /webdav/<path>` | Create a directory |
| `MOVE /webdav/<path>` | Move (with `Destination` header, overwrite aware) |
| `COPY /webdav/<path>` | Copy (with `Destination` header, overwrite aware) |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- Python `smbclient`/`smbprotocol`, `pexpect`, `qrcode`, `lxml`, and `linuxmusterTools` (`linuxmusterTools.quotas`).
- A valid per-user Kerberos ticket for Samba access; the `/srv/.webdav` temp directory for zipped WebDAV directory downloads.
- `aj.plugins.lmn_common.mimetypes` and `aj.plugins.lmn_common.api` (`samba_realm`, `samba_netbios`) for MIME handling and realm info.
