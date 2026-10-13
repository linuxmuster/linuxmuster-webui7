# lmn_quotas

Quota management plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets administrators read and set the disk quotas of users, schoolclasses and projects, and apply them on the file server.

Like every webui plugin, `lmn_quotas` is only the front end: it reads and writes quotas through [`linuxmuster-api`](https://github.com/linuxmuster/linuxmuster-api) (which calls `sophomorix` and `linuxmusterTools`), never by touching the file server directly.

---

## Features (web interface)

Opened from the sidebar as **Extra-Quotas**, the view is organised in tabs:

- **Teachers / Students / Schooladmins / Classes / Projects** — one tab per object type, each listing the entries that carry a special quota (name, login for users, and the value against the school's default). "There is no special quota here" is shown when a tab is empty.
- **Add special quota** — a search box ("Search & add user") to pick an entry and give it a quota that overrides the default.
- **Configure default quota** — set the default applied when no special quota exists.
- **Quota check** — for a chosen user, lists the main directories and their size (Directory / Size / Total), i.e. the real disk usage behind the quota. This tab is flagged in the UI as *under development*: values are approximate and it does not handle DFS shares or a multischool setup.

Editing goes through an **Add special quota** modal; **Apply** pushes the registered values to the file server.

### Backend

`views.py` exposes the HTTP endpoints below, each guarded by an Ajenti permission; the privileged work is delegated to `linuxmuster-api`.

---

## Permissions

Declared in `main.py`, all `default: False` (granted per role in the webui permission settings):

| Permission | Grants |
|---|---|
| `lm:quotas:ldap-search` | search the LDAP tree to pick a user/group |
| `lm:quotas:configure` | read the quota configuration of users, classes and projects |
| `lm:quotas:apply` | set and apply quota values |

---

## HTTP API

Mounted under `/api/lmn/`. All endpoints run in the authenticated user's worker.

| Method & path | Permission | Description |
|---|---|---|
| `GET /quota/user/<user>` | — | Quota of a single user (via lmnapi) |
| `GET /quota/usermap/<user>` | `lm:users:passwords` | Samba share limits for a user's groups |
| `GET /quota/quotas` | `lm:quotas:configure` | All quotas from `school.conf` and LDAP |
| `GET /quota/groups` | `lm:quotas:configure` | Quotas of projects and schoolclasses |
| `POST /quota/save` | `lm:quotas:configure` | Register new quota values (through sophomorix) |
| `POST /ldap-search` | `lm:quotas:ldap-search` | Search the LDAP tree |
| `POST /quota/apply` | `lm:quotas:apply` | Apply the registered quotas |
| `GET /quota/check/<user>` | `lm:quotas:apply` | Current applied quota of a user |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- A reachable `linuxmuster-api`, which performs the privileged quota operations.
