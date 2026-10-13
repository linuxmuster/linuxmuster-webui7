# lmn_wireguard

WireGuard VPN manager for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets administrators list, create, delete and inspect WireGuard peers, show a peer's configuration or QR code, bulk-import peers from the AD users, and restart the WireGuard server.

The plugin is a thin proxy: its single backend endpoint forwards requests to an **external WireGuard service** described by a `config.json` (service URL + shared secret), and the frontend drives that service through `/api/wireguard/...` calls. The sidebar/landing-page visibility is gated by the `show_wireguard` display flag.

---

## Features (web interface)

Opened from the sidebar as **Wireguard** (category *software*):

- A warning banner **Connection to wireguard server is not possible!** is shown when peers cannot be loaded.
- **Peer list** — one card per peer, with a green/red left border reflecting its connection status. Each entry shows **Public-Key**, **IP-Address**, **Routes** (badges), and, when connected, **Endpoint**, **Last Handshake** (seconds ago) and transferred data (received / sent in MiB).
- Per peer: **Configuration** (opens the raw `.conf` in a modal), **Show QR-Code** (base64 PNG in a modal) and **Delete** (with confirmation).
- Floating toolbar: **＋** create a peer (prompts for a name), **Import** (bulk import modal), **Restart** the server (confirmation, warns all clients must reconnect) and **Query status** (reload live status). Creating or deleting a peer also asks whether to restart the server.

### Import users modal

Loads students and teachers (via `/api/lmn/sophomorixUsers/students` and `/teachers`). **Check users** compares AD accounts against existing peers using the `lmn-user_<sAMAccountName>` naming prefix, then lists **Users to import** (accounts without a peer) and **Peers to delete** (`lmn-user_` peers with no matching account). A progress bar tracks the run. **Import** creates the missing peers; **Import + Delete** also removes the orphaned peers.

### Backend

`views.py` exposes a single `POST /api/lmn/wireguard` endpoint. It refuses non-root workers (`os.getuid() != 0` → HTTP 403), reads `/etc/linuxmuster/webui/wireguard/config.json`, and relays the requested `method` (GET/POST/PUT/DELETE) and `url` to `config["url"] + url`, adding the `LMN-API-Secret: <config["secret"]>` header (TLS verification disabled). It returns the upstream JSON on HTTP 200, otherwise `False`. All the concrete WireGuard operations (`/api/wireguard/peers`, `.../status`, `.../<peer>/config`, `.../<peer>/qr/b64`, `/api/wireguard/restart`) live on the external service.

---

## Permissions

No `PermissionProvider` is declared (the example block in `main.py` is commented out). Access is controlled only through the sidebar entry in `permissions.yml` (`sidebar:view:/view/lmn/wireguard`): `true` for `globaladministrator` and `schooladministrator`, `false` for the other roles. The root-worker check in the endpoint additionally restricts who can actually reach the backend.

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Guard | Description |
|---|---|---|
| `POST /api/lmn/wireguard` | root worker only (403 otherwise) | Proxy a `{url, method, data?}` call to the external WireGuard service, signed with the config secret |

---

## Requirements / Configuration

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- An external WireGuard management service reachable at the configured URL, and the `requests` library.

Config file `/etc/linuxmuster/webui/wireguard/config.json`:

```json
{
    "url": "http://10.0.0.3:8000",
    "secret": "1234567890"
}
```

The plugin's entry on the landing page is gated by the `show_wireguard` display flag (read by `lmn_common`, defaults to `False`). Enable it in `/etc/linuxmuster/webui/config.yml`:

```yaml
linuxmuster:
    [...]
    display:
        show_wireguard: true
```
