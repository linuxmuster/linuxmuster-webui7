# lmn_samba_dns

DNS management plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets an administrator read and edit the DNS records of the Samba Active Directory zone.

Unlike most webui plugins it does not go through `linuxmuster-api`: it calls `linuxmusterTools.samba_util.SambaToolDNS`, which wraps `samba-tool dns` directly on the server.

---

## Features (web interface)

Opened from the sidebar as **Samba DNS** (under *System*), the view shows the managed zone:

- **Zone informations** — the zone name, followed by a table of the zone-root records (**Type / TTL / Value**).
- **Subdomains** — a table of the sub-records with **Host / Type / TTL / Value**, plus per-row **edit** and **delete** buttons. For `MX` records the priority is shown next to the host.
- **Add an entry** — opens a *New DNS entry* modal to create a record: subdomain, type (`AAAA`, `A`, `PTR`, `CNAME`, `NS`, `MX`, `TXT`), value and, for `MX`, a priority.
- **Modify DNS entry** — the edit modal lets the value (and `MX` priority) be changed; host and type are read-only.
- Deletion asks for confirmation before removing the record.

### Backend

`views.py` exposes four endpoints on the same `/api/lmn/dns` path (one per HTTP verb), each delegating to `SambaToolDNS` (`list`, `zone`, `add`, `update`, `delete`). The handler is built once with a `SambaToolDNS()` instance; if it raises `PermissionError` the instance is left as `None`.

---

## Permissions

Declared in `main.py`, all `default: False`:

| Permission | Grants |
|---|---|
| `lm:samba_dns:read` | show the DNS entries and zone |
| `lm:samba_dns:write` | add, update and delete DNS entries |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /dns` | `lm:samba_dns:read` | List the DNS entries and the zone name |
| `PUT /dns` | `lm:samba_dns:write` | Add a DNS entry (`samba-tool`) |
| `POST /dns` | `lm:samba_dns:write` | Update an existing entry (old → new) |
| `PATCH /dns` | `lm:samba_dns:write` | Delete an entry (`sub`, `type`, `value`) |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `linuxmuster-tools` (`linuxmusterTools.samba_util.SambaToolDNS`) and a working `samba-tool` on the server, running as a user allowed to manage the AD DNS zone.
