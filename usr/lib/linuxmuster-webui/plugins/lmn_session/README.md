# lmn_session

Teacher session plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It is the classroom console a teacher uses during a lesson: pick a group of students (the current room, a schoolclass, a project, or a saved ad-hoc group), then share and collect files with them, start/stop exam mode, toggle their management groups (wifi, internet, printing...), and reset their passwords.

It is a front end that drives `sophomorix` (via `linuxmuster-common`'s `lmn_getSophomorixValue`) and `linuxmuster-api` (management-group membership through `lmnapi_client`), and reuses other webui plugins for the heavy work: file transfer goes through [`lmn_smbclient`](../lmn_smbclient), password actions through [`lmn_users`](../lmn_users), and class/project enrolment through [`lmn_groupmembership`](../lmn_groupmembership).

---

## Features (web interface)

Opened from the sidebar as **Session** (under *Class*). The plugin has two pages.

### Session list (`/view/lmn/sessionsList`)

A dashboard of the groups a teacher can start, with a live **Filter** box and card tiles showing each group's member count:

- **This Room** — the room the teacher is currently logged into (detected via `sophomorix-query --smbstatus`); clicking it starts an auto-generated session of the users in that room. An info banner is shown when the room cannot be determined.
- **My Classes** — the teacher's schoolclasses (and extraclasses); clicking one starts a generated session from its members. A banner links to the *Enroll* page when the teacher belongs to none.
- **My groups** — the teacher's saved sessions. **New group** creates one; each tile offers **rename**, **duplicate (clone)** and **delete**.
- **My projects** — the teacher's projects, each startable as a generated session.

### Session (`/view/lmn/session`)

The working view for the selected group:

- **Add participants** — two typeahead inputs to add a single student or a whole schoolclass, a **sort** dropdown, and an **Edit group** dropdown (rename / duplicate / delete) for saved groups; generated groups instead offer **Save group as**. For the room session, **Start/Stop autorefresh** periodically re-reads who is in the room. A **Websession** dropdown (shown when enabled) starts/stops a web session and shows its running state.
- **Participants table** — one row per student with surname/first name, login, admin class and (when known) the computer they sit at. Teacher members are shown a banner ("not possible to create share directory in other teacher's home..."). Columns:
  - **Transfer** — **Share** files to the student, and **Collect** (Copy or Move) their `_collect` directory. The working directory is `transfer/<teacher>/_collect`, with a **refresh / auto-refresh** toggle. When a student is not joined to the required class, a **Join ... to share** button fixes the membership; otherwise the collected files are listed inline.
  - **Exam** — per-student and whole-group **start / stop exam mode** (graduation-cap buttons); a running exam shows the supervising teacher and can be stopped.
  - **Management groups** — per-student checkboxes and per-column *toggle-all* buttons for **wifi**, **internet** and **printing** (buttons colour by how many members have each).
  - **Password cog menu** — show / restore the default (initial) password, set a random default password, set a custom default or current password, including the paired `-exam` account when the student is in exam mode.
  - **Remove** the participant from the group.
- **Floating toolbar** — **Share to all**, **Collect from all** (Copy/Move the `_collect` dir of every member), **Browse collected files**, and **Close**.
- **Modals** — *Select file* (`selectFile.modal.html`): a mini file browser used to pick files to share/collect, with upload, new folder, rename and delete; *Room details* (`roomDetails.modal.html`): the users currently logged into the room with their computer/IP.

### Backend

`views.py` exposes the session endpoints below. Session lifecycle, participants and exam mode are run through `sophomorix-session` / `sophomorix-exam-mode` / `sophomorix-query` / `sophomorix-transfer` (via `lmn_getSophomorixValue`); management-group changes go to `linuxmuster-api` through `self.context.lmnapi_client`; class/project/session membership and user details are read from LDAP (`self.context.ldapreader`). File share/collect, password actions and class enrolment are delegated to the `lmn_smbclient`, `lmn_users` and `lmn_groupmembership` endpoints respectively.

---

## Permissions

Declared in `main.py`, all `default: False`:

| Permission | Grants |
|---|---|
| `lm:users:teachers:write` | *Write students* (declared by this plugin) |
| `lmn:session:trans` | *Transfer Files in Session* (declared by this plugin) |

Note: the endpoints below are actually guarded by `lm:users:students:read` (declared by `lmn_users`); the two permissions above are declared here but not used as route guards in `views.py`.

---

## HTTP API

Mounted under `/api/lmn/`. All routes are guarded by `@authorize('lm:users:students:read')` except `moveFileToHome`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /session/sessions` | `lm:users:students:read` | The teacher's saved sessions (from their profile) |
| `GET /session/schoolclasses` | `lm:users:students:read` | The teacher's schoolclasses/extraclasses with members |
| `GET /session/projects` | `lm:users:students:read` | The teacher's projects with members |
| `POST /session/userinfo` | `lm:users:students:read` | LDAP details for a list of users (exam account resolved) |
| `POST /session/exam/userinfo` | `lm:users:students:read` | LDAP details for exam users |
| `PUT /session/sessions/<session>` | `lm:users:students:read` | Create a session (`sophomorix-session --create`) |
| `DELETE /session/sessions/<session>` | `lm:users:students:read` | Kill a session (`--kill`) |
| `POST /session/sessions` | `lm:users:students:read` | Rename / set the comment of a session |
| `POST /session/participants` | `lm:users:students:read` | Add participants (`--add-participants`) |
| `PATCH /session/participants` | `lm:users:students:read` | Remove participants (`--remove-participants`) |
| `PATCH /session/exam/start` | `lm:users:students:read` | Start exam mode (`sophomorix-exam-mode --set`) |
| `PATCH /session/exam/stop` | `lm:users:students:read` | Stop exam mode and collect to `transfer/collected/...` |
| `POST /managementgroup` | `lm:users:students:read` | Add/remove members of a management group (wifi, internet, intranet, webfilter, printing) via lmnapi |
| `GET /session/userInRoom` | `lm:users:students:read` | Users logged into the teacher's room (`sophomorix-query --smbstatus`) |
| `GET /session/user-search/<query>` | `lm:users:students:read` | LDAP student search |
| `GET /session/schoolClass-search/<query>` | `lm:users:students:read` | LDAP schoolclass search |
| `POST /session/moveFileToHome` | **none** | Transfer a unix path into a user's home (`sophomorix-transfer`); flagged deprecated, has a `TODO authorize` and no guard |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `sophomorix` on the server (`sophomorix-session`, `sophomorix-exam-mode`, `sophomorix-query`, `sophomorix-transfer`).
- A reachable `linuxmuster-api` (`lmnapi_client`) for management-group membership; an unavailable API surfaces `LMNAPI_UNAVAILABLE_MESSAGE`.
- `linuxmuster-tools` (`linuxmusterTools.common.natural_key`, `ldapreader`).
- The `lmn_smbclient`, `lmn_users` and `lmn_groupmembership` plugins for file transfer, password actions and class/project enrolment.
