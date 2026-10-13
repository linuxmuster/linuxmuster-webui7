# lmn_nextcloud

Nextcloud embedding plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It opens an external Nextcloud instance inside the webui in an iframe, optionally in fullscreen and pre-filled with the current user's login.

The plugin is a thin front end: it reads a local YAML config file for the Nextcloud URL and options, probes that URL, then loads it in an iframe; there is no linuxmuster-api call.

---

## Features (web interface)

Opened from the sidebar as **Nextcloud** (under *category:class*), the view loads the configured Nextcloud instance into a full-height **iframe**. While probing it shows a spinner; if the URL is missing or unreachable it shows the warning *"URL not found or not valid! Please check config file."*

Behaviour is driven by the config options returned by the backend:

- `toggleFullscreen` — when set, the controller hides the navigation and switches to widescreen before showing the iframe.
- `askForUser` — when set, the current user's login is appended as `/index.php/login?user=<user>` so Nextcloud opens on the right account.

### Backend

`views.py` exposes a single endpoint; `api.py` (`loadSettings`) reads the YAML file `/etc/linuxmuster/webui/nextcloud/nextcloud_config.json`. The endpoint then does a `GET` on the configured `nextcloudURL` with `urllib3` (TLS verification disabled, `cert_reqs='CERT_NONE'`) and returns `[http_status, url, fullscreen, askuser]`, or `[0, None, None, None]` on error or missing config.

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /nextcloud` | — | Read the config, probe the Nextcloud URL and return `[status, url, fullscreen, askuser]` |

The endpoint carries no `@authorize` guard.

---

## Requirements

- Ajenti `core` and `lmn_common` (dependencies in `plugin.yml`).
- `urllib3` (used to probe the Nextcloud URL).
- The config file `/etc/linuxmuster/webui/nextcloud/nextcloud_config.json` (YAML) with a `settings` block providing `nextcloudURL`, `toggleFullscreen` and `askForUser`.
- A reachable external Nextcloud instance at the configured URL.
