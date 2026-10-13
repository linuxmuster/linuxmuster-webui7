# lmn_links

Links plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It shows the current user a list of external links (title, icon, description, URL) configured by the administrator, filtered to the links allowed for the user's role.

The plugin is a thin front end: it only reads a local YAML list file on the server; there is no linuxmuster-api call.

---

## Features (web interface)

Opened from the sidebar as **Links** (under *category:class*), the view renders one info card per link, each with its **icon**, **title**, a **description** in the card body, and an **Open** button linking to the target URL. When no link is defined (or the config file is missing), an info banner *"Currently no links defined!"* is shown.

The controller fetches the list once, then keeps only the entries whose `permissions` include the logged-in user's `sophomorixRole` (globaladministrator, teacher, student, …), so each role sees only its own links.

### Backend

`views.py` exposes a single read-only endpoint; `api.py` (`loadList`) loads the YAML file `/etc/linuxmuster/webui/links/links_list.json` and returns `{status, data}` (or an error if the file is missing).

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /links` | — | Return the configured link list from `links_list.json` |

The endpoint carries no `@authorize` guard; role filtering is done client-side in the controller.

---

## Requirements

- Ajenti `core` and `lmn_common` (dependencies in `plugin.yml`).
- The config file `/etc/linuxmuster/webui/links/links_list.json` (YAML), where each entry provides `title`, `icon`, `link`, `description` and a `permissions` list of sophomorix roles.
