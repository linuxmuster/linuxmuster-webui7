# lmn_permissions

Permission matrix plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It builds, for every webui plugin, a matrix of its HTTP endpoints and sidebar items against the six roles (globaladministrator, schooladministrator, teacher, student, parent, staff) and lets an administrator edit and export the resulting `permissions.yml` files.

The plugin introspects the running Ajenti instance (all `HttpPlugin`, `PermissionProvider` and `SidebarItemProvider` components) and reads/writes each plugin's `permissions.yml` through `linuxmusterTools` (`LMNFile`).

---

## Features (web interface)

The sidebar entry **Permissions** (under *category:tools*, url `/view/permissions`) is only registered when Ajenti runs in dev mode (`if aj.dev` in `main.py`). The view has three tabs:

- **Plugins** — a filter box (by plugin name or role) and, per plugin, a table of its endpoints grouped by URL. Each method row shows an auth icon (locked / unlocked), api/page icons, the HTTP method label and the `permission_id`, with a clickable cell per role (GlobalAdmin / SchoolAdmin / Teacher / Student / Parent / Staff) to toggle the granted value, plus a default column. Methods without a permission show *"No authorization set for this method."* Clicking a role header switches the whole column.
- **Sidebar** — a filter box and a table of sidebar URLs (with the owning plugin and the provider logo), one toggle cell per role.
- **Orphan** — lists entries present in `default-ui-permissions` but no longer used, for the sidebar and for the API permissions, or a success banner when there are none.

A floating-toolbar **Export permissions file** button writes the edited matrix back to the per-plugin `permissions.yml` files.

### Backend

`views.py` exposes two endpoints. `GET /api/lmn/permissions` gathers all sidebar items, all declared permissions, every `HttpPlugin`'s URL patterns (with their `permission_id`, `api`/`auth`/`page` flags, method and docstring) and the existing `permissions.yml` files under `/usr/lib/linuxmuster-webui/plugins`, and returns `(PluginDict, apiPermissionDict, sidebarPermissionDict)`. `POST /api/lmn/permissions/export` writes the posted matrix back to each plugin's `permissions.yml` via `LMNFile`, for the six roles.

Both endpoints answer 403 unless Ajenti runs in dev mode (`aj.dev`) and the user is `root`, like the sidebar entry: no role gets `sidebar:view:/view/permissions`. The export ignores the plugin names that are not a directory of `/usr/lib/linuxmuster-webui/plugins`.

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /permissions` | `lm:schoolsettings` *(# TODO: adapt, not school-scoped)* | Build the full plugins / permissions / sidebar matrix |
| `POST /permissions/export` | `lm:schoolsettings` *(# TODO: adapt, not school-scoped)* | Write the edited matrix back to each plugin's `permissions.yml` |

---

## Requirements

- Ajenti `core` and `lmn_common` (dependencies in `plugin.yml`); the sidebar entry only appears with `aj.dev`.
- `linuxmuster-tools` (`linuxmusterTools.lmnfile.LMNFile`).
- Read/write access to the plugins directory `/usr/lib/linuxmuster-webui/plugins` and each plugin's `permissions.yml`.
