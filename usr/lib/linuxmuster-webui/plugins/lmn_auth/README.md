# lmn_auth

Authentication and identity provider for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It logs users in against the Samba 4 Active Directory (LDAP), builds their session and exposes the "Change password" page.

Unlike most webui plugins, `lmn_auth` is not a view over `linuxmuster-api`: it is the Ajenti `AuthenticationProvider` itself. It reads the directory through `linuxmusterTools` (`LMNLdapReader`) and only delegates the actual password write to `linuxmuster-api` (through the per-session `LmnapiClient` set up in `lmn_common`).

---

## Features (web interface)

The plugin has almost no page of its own. Its only view is the **Change password** form (route `/view/lmn/change-password`, also reachable from the user profile menu):

- **Current password**, **New password** (with a show/hide eye toggle) and **Repeat password** fields.
- Inline help listing the password rules (minimal length 7, upper/lower/special characters or numbers, allowed character set) and a reminder that all fields are required.
- Live check that the two new passwords match; the **Change password** button stays disabled until all fields are filled and the two new entries are identical.
- On success the user is redirected to the landing page; on failure a permanent error with the message returned by the backend is shown.

Everything else the plugin does is invisible to the user: it is the login backend behind Ajenti's login screen.

### Backend

`api.py` implements the heavy part:

- **`LMAuthenticationProvider`** (id `lm`, "Linux Muster LDAP"): checks credentials by binding to the LDAP server, refuses users whose `sophomorixRole` is not in the configured `allowed_roles`, and loads `sophomorixWebuiPermissionsCalculated` into the session for `authorize()`. `root` falls back to the OS authentication provider.
- **Per-user isolation**: `get_isolation_uid` / `get_isolation_gid` return the uid/gid for the forked worker, so each authenticated session runs a worker with the user's own uid/gid (admins run as uid 0). `prepare_environment` initialises the multischool `SchoolManager`, the `LMNLdapReader`, the identity profile, the `PasswordPolicyProvider` and the session's `LmnapiClient`, and renames the Kerberos ticket to `/tmp/krb5cc_<uid>`.
- **Kerberos**: `_get_krb_ticket` runs `kinit` via `pexpect` at login, `signout` runs `kdestroy`.
- **`change_password`**: re-authenticates, validates the new password against the password policy, then writes it through `LmnapiClient.set_current_password`.
- **`check_mail` / `check_password_complexity` / `update_password`**: helpers used by the password-reset flow when it is activated in the config.
- **`UserLdapConfig`** (`UserConfigProvider`): stores the per-user dashboard config in `sophomorixWebuiDashboard` in LDAP (in `/root/.config/ajenti.yml` for root). Marked as currently unused/to be updated.

`views.py` exposes a single HTTP endpoint, `POST /api/lmn/change-password`, which just calls `change_password` on the active authentication provider.

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- `linuxmusterTools` (`ldapconnector`, `common`, `passwords`) for LDAP access and the password policy.
- A reachable Samba 4 AD / LDAP server, Kerberos (`kinit`/`kdestroy`), and the webui config `/etc/linuxmuster/webui/config.yml` (LDAP connection, `allowed_roles`, optional `pw_reset`) read through `lmn_common.api`.
- `linuxmuster-api` for the actual password change (via the session `LmnapiClient`).
