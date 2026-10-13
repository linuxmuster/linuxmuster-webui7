# lmn_users

User management plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It is the central place to browse and manage all account types (teachers, students, parents, staff, school-admins, global-admins), import/update user lists from CSV, manage passwords (including printing), edit per-user custom fields, and link parents to students.

It is a front end that reads accounts from LDAP via `linuxmusterTools` and performs privileged operations through `linuxmuster-api` (the `lmnapi_client` password calls) and `sophomorix-*` commands; it also reads/writes the sophomorix CSV import lists and `school.conf` directly.

---

## Features (web interface)

The plugin adds several entries under the **user management** sidebar category (plus one under **class**):

- **Teachers**, **Students**, **Parents**, **Staff**, **School-Admins**, **Global-Admins** — one list view per role.
- **Listmanagement** — CSV import/edit of users.
- **Print Passwords** (under **class**) — class-wide password printing.

### Role list views (teachers / students / parents / staff / school-admins / global-admins)

Each role view shows a filterable, sortable, paginated table of accounts (sort menu, rows-per-page menu of 10/50/100/500/1000, search/filter box). Columns include the login, name / DN / comment, and a colored **Status** badge derived from the sophomorix lifecycle letter (Activated, Usable, Permanent, Locked, Deactivated, Frozen, Removable, Killable, Exam, Managed, …). Per row and in batch (on the selection) the user can:

- **Show / print passwords** — show the first password, **Set initial password**, **Set random password**, **Set custom password** (first or current), **Reset first password**, and **Print passwords** for the selected rows. Batch variants exist (`batchResetFirstPassword`, `batchSetRandomFirstPassword`, `batchSetCustomFirstPassword`, `printSelectedPasswords`).
- **User details** (`userInfo`) — opens the **User Details** modal: properties (Loginname, Role, Class, Schoolname, Birthday, Sophomorix Status, Creation/Deactivation/Toleration dates), group membership, quota (Cloudquota / Mailquota in MiB), the user's **custom fields** (Custom 1–5 and Custom-Multi, editable when configured) and **proxy addresses** (e-mail aliases, add/remove), and the student's **parents** list (search & add, remove).
- The **Teachers** view additionally has a **Quota** column with a **Show quota** action (`getQuotas`, via the `lmn_quotas` plugin).
- The **Students** view has a second **Attic** tab (archived/old students) with its own password/print batch actions (`batchAttic…`, `printAtticSelectedPasswords`).
- The **School-Admins** and **Global-Admins** views also manage **bind users**: add/delete school/global binduser, edit a binduser comment, and show the bind password (`showBindPW`). Admins are created with `addSchoolAdmin` / `addGlobalAdmin` and deleted with `deleteSchoolAdmin` / `deleteGlobalAdmin`.

Supporting modals: `addUser`, `addAdmin`, `customPassword` ("Change Password", with the minimal-length / complexity note), `showPassword`, `showBindPassword` (with copy), `check`, `apply`, `result`.

### Listmanagement

A tabbed view (**Students**, **Parents**, **Teachers**, **Extra-Students**, **Extra-Courses**, **Staff**) to edit the sophomorix CSV import lists directly as editable tables: per tab the user can **add** a row, **remove** a row, **save** the list, **save and check** (runs `sophomorix-check`), view **backups** of the CSV, and **edit CSV** / **upload** a CSV. The **Upload CSV** modal warns that it replaces the current CSV and offers "Check columns" (open the **Sort List** modal to map which CSV column is lastname/firstname/class/birthday/login/id/password) or "Save directly". After saving changes, the **Report** modal (tabs: Summary, Report, Added users, Moved users, Killed users, Errors) shows what `sophomorix-add` / `sophomorix-update` / `sophomorix-kill` will do, and **Apply** commits them.

### Print Passwords

Lists the classes the user may print for (teachers see their own classes; admins see all classes plus teachers/parents and an "all users" entry). A class can be printed directly via its icon, or several classes selected and printed at once. The **options** modal lets the user choose format (PDF / CSV), one-per-page vs. passwords-per-page, whether to run `pdflatex`, language, and a LaTeX template (individual / multiple).

### Backend

Four view files under `views/`:

- `sophomorixUsers.py` — LDAP reads of each role (with lifecycle-status decoration), create/delete school & global admins and bindusers, add user comment, add/remove parent (via `lmnapi_client`), and direct `sophomorix-kill` of a user.
- `passwords.py` — get/set first & current passwords, random passwords and reset (via `linuxmuster-api` `lmnapi_client`, with a server-side password-policy validation and a role-rank permission check `_checkPasswordPermissions`), the class list, PDF/CSV printing via `sudo sophomorix-print`, PDF download, first-password-still-set check, and binduser password readout (guarded by `os.getuid()`).
- `customFields.py` — read/write sophomorix custom fields, custom-multi fields and proxy addresses via `sophomorix-user` (each write also checks `user == self.context.identity` unless root).
- `listmanagement.py` — read/write the role CSV lists (`LMNFile`), import a CSV (`sophomorix-newfile`), read `school.conf`, run `sophomorix-check` and apply add/update/kill.

---

## Permissions

Declared in `main.py` (all `default: False`); `permissions.yml` ships role defaults (globaladministrator, schooladministrator, teacher, student, parent, staff).

| Permission | Grants |
|---|---|
| `lm:users:students:read` / `:write` | read / write students |
| `lm:users:teachers:read` / `:list` / `:write` | read / list / write teachers |
| `lm:users:parents:read` / `:write` | read / write parents |
| `lm:users:staff:read` / `:write` | read / write staff |
| `lm:users:schooladmins:read` / `:create` / `:delete` | read / add / delete school admins |
| `lm:users:globaladmins:read` / `:create` / `:delete` | read / add / delete global admins |
| `lm:users:extrastudents:read` / `:write` | read / write extra students |
| `lm:users:extraclasses:read` / `:write` | read / write extra courses |
| `lm:users:users:delete` | delete (kill) non-admin users |
| `lm:users:check` | run `sophomorix-check` |
| `lm:users:apply` | apply user changes (add/update/kill), read `school.conf` |
| `lm:users:passwords` | read/write passwords, print, list classes |
| `lm:users:customfields:read` / `:write` | read / change custom field values |

---

## HTTP API

Mounted under `/api/lmn/`. `(/<user>)?` means the route optionally takes a single user to return just that account.

### Users & admins (`views/sophomorixUsers.py`)

| Method & path | Permission | Description |
|---|---|---|
| `GET /sophomorixUsers/teachers(/<user>)?` | `lm:users:teachers:read` | Teachers list / one teacher |
| `GET /sophomorixUsers/students(/<user>)?` | `lm:users:students:read` | Students list / one student (+ parents) |
| `GET /sophomorixUsers/parents(/<user>)?` | `lm:users:parents:read` | Parents list / one parent |
| `GET /sophomorixUsers/staff(/<user>)?` | `lm:users:staff:read` | Staff list / one staff |
| `GET /sophomorixUsers/schooladmins(/<user>)?` | `lm:users:schooladmins:read` | School admins list / one |
| `GET /sophomorixUsers/globaladmins(/<user>)?` | `lm:users:globaladmins:read` | Global admins list / one |
| `POST /sophomorixUsers/schooladmins` | `lm:users:schooladmins:create` | Create school admin(s) |
| `PATCH /sophomorixUsers/schooladmins` | `lm:users:schooladmins:delete` | Delete (kill) school admin(s) |
| `POST /sophomorixUsers/globaladmins` | `lm:users:globaladmins:create` | Create global admin(s) |
| `PATCH /sophomorixUsers/globaladmins` | `lm:users:globaladmins:delete` | Delete (kill) global admin(s) |
| `POST /sophomorixUsers/<user>/comment` | `lm:users:schooladmins:create` | Set a user's comment |
| `GET /sophomorixUsers/bindusers/<level>` | `lm:users:globaladmins:create` | List school/global bindusers |
| `POST /sophomorixUsers/bindusers/<level>` | `lm:users:globaladmins:create` | Create a school/global binduser |
| `POST /sophomorixUsers/add-parent` | `lm:users:parents:write` | Link a parent to a student (lmnapi) |
| `POST /sophomorixUsers/remove-parent` | `lm:users:parents:write` | Unlink a parent (lmnapi) |
| `POST /sophomorixUsers/killuser` | `lm:users:users:delete` | `sophomorix-kill` a user |

### Passwords (`views/passwords.py`)

| Method & path | Permission | Description |
|---|---|---|
| `GET /users/passwords/<user>` | `lm:users:passwords` | Get the user's first password |
| `POST /users/passwords/reset-first` | `lm:users:passwords` | Reset current back to first password |
| `POST /users/passwords/set-random` | `lm:users:passwords` | Set a random (policy-valid) password |
| `POST /users/passwords/set-first` | `lm:users:passwords` | Set initial password (also current) |
| `POST /users/passwords/set-current` | `lm:users:passwords` | Set the current password |
| `GET /users/classes` | `lm:users:passwords` | Classes available for printing |
| `POST /users/passwords/print` | `lm:users:teachers:read` (TODO) | Print selected users' passwords, one per page |
| `POST /users/print` | `lm:users:passwords` | Print passwords as PDF (template/class) |
| `POST /users/print_csv` | `lm:users:passwords` | Print passwords as CSV |
| `GET /users/passwords/download/<name>` | `lm:users:passwords` | Download a generated print file |
| `GET /users/<user>/first-password-set` | `lm:users:passwords` | Whether the first password is still set |
| `GET /users/<binduser>/bindpassword` | `lm:users:globaladmins:create` | Read a binduser's password (root only) |

### Custom fields (`views/customFields.py`)

| Method & path | Permission | Description |
|---|---|---|
| `GET /users/<user>/customfields` | `lm:users:customfields:read` | Displayable custom fields of a user |
| `POST /users/<user>/custom/<index>` | `lm:users:customfields:write` | Set custom field 1–5 |
| `POST /users/<user>/custommulti/<index>` | `lm:users:customfields:write` | Add a custom-multi value |
| `PATCH /users/<user>/custommulti/<index>` | `lm:users:customfields:write` | Remove a custom-multi value |
| `POST /users/<user>/proxyaddresses` | `lm:users:customfields:write` | Add a proxy address (e-mail) |
| `PATCH /users/<user>/proxyaddresses` | `lm:users:customfields:write` | Remove a proxy address |

### List management (`views/listmanagement.py`)

| Method & path | Permission | Description |
|---|---|---|
| `GET /users/lists/<role>` | `lm:users:<role>:read` (inner `authorize`) | Read a role's CSV list |
| `POST /users/lists/<role>` | `lm:users:<role>:write` (inner `authorize`) | Write a role's CSV list |
| `POST /users/lists/import` | inner `authorize` per role | Parse / save an imported CSV |
| `POST /users/lists/csv` | `lm:users:passwords` | Apply a custom uploaded CSV (`sophomorix-newfile`) |
| `GET /users/schoolconf` | `lm:users:apply` | Read `school.conf` |
| `GET /users/lists/check` | `lm:users:check` | Run `sophomorix-check` |
| `POST /users/lists/apply` | `lm:users:apply` | Apply add / update / kill |

---

## Requirements

- Ajenti `core`, `lmn_common` and `lmn_quotas` (dependencies in `plugin.yml`; `lmn_quotas` powers the teacher quota column).
- A reachable `linuxmuster-api` (via `lmnapi_client`) for all password operations and parent linking.
- `linuxmusterTools` (`ldapconnector` for reads, `lmnfile` for the CSV lists, `print.LatexTemplates` for print templates).
- `sophomorix-*` tools on the server (`sophomorix-admin`, `sophomorix-user`, `sophomorix-kill`, `sophomorix-check`, `sophomorix-add`, `sophomorix-update`, `sophomorix-newfile`, `sophomorix-print` via `sudo`, `sophomorix-query`).
- The sophomorix CSV import lists and `school.conf` under the school config path, and `/etc/linuxmuster/.secret/` for binduser passwords.
