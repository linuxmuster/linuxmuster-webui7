# lmn_landingpage

Landing page ("Home") plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It is the welcome screen shown after login: a dashboard of the current user's account, quotas, groups and optional mobile/VPN access.

The plugin has no backend of its own (`views.py` is empty); the frontend consumes endpoints provided by other plugins (`lmn_quotas`, `lmn_common`, `lmn_auth`, webdav).

---

## Features (web interface)

Opened from the sidebar as **Home** (general category, available to every role). It greets the user by name with a role-specific message (teachers are pointed at the Enroll module, administrators get a "with great power…" note) and shows a set of info cards:

- **Account Information** — name, mail, school and role, plus a **Change password** button (links to `/view/lmn/change-password`).
- **Quotas** — one progress bar per share (used / total MiB, colored by usage), plus the calculated cloud and mail quotas. Data from `/api/lmn/quota/user/<user>`.
- **My informations** — custom LDAP fields for the user; a **Change my data** button (hidden for students) opens a modal to edit single-value and multi-value attributes, including `proxyAddresses`.
- **Mobile access** — shown when `show_webdav` is enabled; opens a QR/setup modal (iOS guide, QR code from `/api/webdav/qrcode`).
- **Groups** — the user's linuxmuster groups derived from `memberOf` (classes, teachers, printers, projects; management groups are hidden).
- **Wireguard VPN** — shown when `show_wireguard` is enabled; client download links (Windows/Linux/Android/iOS), a QR code, a config download and a live connection status (endpoint, last handshake, transfer). Data from `/api/lmn/wireguard`.

Display of the mobile/VPN cards is driven by `/api/lmn/display_options`.

### Backend

None. `views.py` is empty; all data is fetched from other plugins' endpoints and from the shared `customFields` Angular service of `lmn_common`.

---

## Permissions

The plugin declares no permission of its own. `permissions.yml` only grants the sidebar entry (`sidebar:view:/view/lmn/landingpage`) to every role.

---

## Requirements

- Ajenti `core`, and the `lmn_common`, `lmn_auth` and `lmn_quotas` plugins (dependencies in `plugin.yml`).
- The endpoints it calls: `/api/lmn/display_options` and the `customFields` service (`lmn_common`), `/api/lmn/quota/user/<user>` (`lmn_quotas`), `/api/lmn/wireguard` (`lmn_auth`) and `/api/webdav/qrcode`.
