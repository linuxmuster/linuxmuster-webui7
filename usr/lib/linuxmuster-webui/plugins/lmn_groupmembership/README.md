# lmn_groupmembership

Group membership ("Enroll") plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets teachers and administrators manage schoolclasses, projects and printer groups: join or leave them, edit their members and admins, create or delete projects, and toggle their options.

The plugin reads groups through `linuxmusterTools` LDAP (`ldapreader`), performs most writes through `sophomorix` (`sophomorix-project`, `-class`, `-query`, …) and handles printer members through `linuxmuster-api`; project/class writers (`LMNProject`, `LMNSchoolclass`, `LMNPrinter`) from `linuxmusterTools` are used when running as root.

---

## Features (web interface)

Opened from the sidebar as **Enroll** (class category), the view is split into three sections — **Schoolclasses**, **Printer** and **Projects** — each toggled from an *Objectsfilter* dropdown, with a **Filter** search box and a **sort** dropdown.

- **Membership** — each group is a line with a checkbox to join/leave it (shown when the group is joinable, or the user is already a member/admin). Labels show counts (students/teachers for classes; admins, members and member-groups for projects) and a warning icon flags a project with no admin.
- **New Project** — a button creates a project (owned by the current user).
- **Reset all memberships** — an admin-only button per section resets the admins of all classes or all projects.
- **Session renewal notice** — a banner warns that membership changes only take effect after a Kerberos ticket refresh (with a **Do it now** action).
- **Group details modal** — opened by clicking a group:
  - Properties table (creation date, type, schoolname, sophomorix status) and editable **Joinable / Hidden / Maillist** checkboxes.
  - **Admins** panel (project users + admin groups, or class teachers) and **Members** panel (users + member groups), with per-entry actions: remove, promote member to admin (elevate), demote admin to member, and remove a whole group.
  - **Add members and/or groups** dialog with typeahead search: a teacher (for classes), any user, a student picked from a class, or a whole group; project additions can be flagged *Add as admin*.
  - **Delete Project** action, and a prompt to delete an empty class.

### Backend

`views.py` exposes the endpoints below. Projects and schoolclasses go through `sophomorix` (which carries the real business logic: home directories, quotas, exam mode); printer members go through `linuxmuster-api` (`patch_printer_members`, `join_printer`, `quit_printer`), where a teacher may only join/quit a joinable printer while an admin edits the full list. Exam accounts are filtered out of user search results.

---

## Permissions

Declared in `main.py`, both `default: False` (granted to teachers and administrators in `permissions.yml`):

| Permission | Grants |
|---|---|
| `lmn:groupmembership` | list groups and edit their memberships (join/leave, members, create/delete projects, options) |
| `lmn:groupmemberships:write` | read a group's full details (`sophomorix-query`) |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /groupmembership/projects` | `lmn:groupmembership` | Projects visible to the current user, with membership/admin flags |
| `GET /groupmembership/all_members_project/<project>` | `lmn:groupmembership` | All members of a project |
| `GET /groupmembership/printers` | `lmn:groupmembership` | All printer groups with membership flag |
| `GET /groupmembership/schoolclasses` | `lmn:groupmembership` | Schoolclasses with the user's membership |
| `GET /groupmembership/groups/<groupName>` | `lmn:groupmemberships:write` | Full details of a group (`sophomorix-query`) |
| `POST /groupmembership/projects/<project>` | `lmn:groupmembership` | Create a project |
| `DELETE /groupmembership/projects/<project>` | `lmn:groupmembership` | Kill a project (admin or project admin) |
| `POST /groupmembership/groupoptions/<group>` | `lmn:groupmembership` | Toggle `sophomorixJoinable`/`Hidden`/`MailList` |
| `POST /groupmembership/membership` | `lmn:groupmembership` | Add/remove members, admins and member/admin groups |
| `POST /groupmembership/resetadmins` | `lmn:groupmembership` | Reset the admins of all projects or classes |
| `DELETE /groupmembership/schoolclass/<schoolclass>` | `lmn:groupmembership` | Kill a schoolclass (admin only) |
| `POST /find/user` | `lmn:groupmembership` | Search users by name (exam accounts excluded) |
| `GET /find/teacher/<login>` | `lmn:groupmembership` | Search teachers |
| `GET /find/usergroup/<group>` | `lmn:groupmembership` | Search members of a group |
| `GET /find/group/<group>` | `lmn:groupmembership` | Search groups and rooms |
| `GET /find/computer/<computer>` | `lmn:groupmembership` | Search computers |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `linuxmuster-tools` (`linuxmusterTools.ldapconnector`) for LDAP reads and the group writers.
- `sophomorix` (`sophomorix-project`, `sophomorix-class`, `sophomorix-query`) on the server.
- A reachable `linuxmuster-api` for printer-member changes.
