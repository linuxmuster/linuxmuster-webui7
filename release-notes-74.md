# Release Notes – linuxmuster-webui7 7.4

**Package version:** 7.4.2 – 7.4.8

---

## Overview

Version 7.4 is largely a de-duplication cycle for the webui: password
management, LINBO remote/image handling, management-group membership and
file handling all had their own local implementation, diverging from
`linuxmuster-tools`' and `linuxmuster-api`'s more complete versions. All of
them have been migrated to consume the shared library or the API instead,
which also fixed a quota-display bug for fileserver-hosted shares along the
way.

---

## Password management

- Password constraints are now editable from the UI, scoped by role
  (school-admin vs global-admin) and school; new passwords are validated
  against the configured policy.
- All password management (initial/current/random password, first-password
  check and reveal) migrated from `sophomorix-passwd`/`sophomorix-user`
  shell-outs to `linuxmuster-api`, via a new minimal HTTP client.
- Fixed `lmnapi_client` being silently lost after login — Ajenti's
  `authenticate()` runs on a shared restricted worker, not the session's own
  process; the client is now built in `prepare_environment()` instead.

---

## LINBO plugins

- `lmn_linbo_sync` migrated to `linuxmuster-tools`' `LinboRemote`: `api.py`
  now only maps frontend parameters and runs the command, instead of
  duplicating command-building, OS-detection and last-sync logic locally.
- Host online detection now reports a boot state (Off, Linbo, OS Linux, OS
  Windows, OS Unknown) via `classify_host()` instead of shelling out to
  `nmap` directly.
- `lmn_linbo4`'s own 527-line `images.py` removed — image
  listing/renaming/deletion now goes through `linuxmuster-tools`'
  `LinboImageManager`.

---

## Management groups & parents

- Management-group membership (wifi, internet, intranet, webfilter,
  printing) and parent assignment/removal no longer shell out to `lmncli`;
  both now call `linuxmuster-api`.

---

## Shared code centralization

- The plugin's own `LMNFile`/`fieldnames.py` (416 + 65 lines) removed; 8
  plugins (settings, quotas, dhcp, permissions, devices, linbo4,
  setup-wizard, device-manager) now use `linuxmusterTools.lmnfile.LMNFile`
  instead — atomic writes, BOM handling, and a `StartConfLoader` bug fixed
  only in the lmntools version.

---

## Quota display fix

Fixed quota display for users whose home share is hosted on a separate
fileserver (MSDFS): the quota used to be queried locally via
`sophomorix-query`, which cannot see a remote fileserver and showed
`UNLIMITED` instead. Both the landing page and the admin "user details"
modal now proxy `linuxmuster-api`'s `GET /v1/users/{user}/quotas`, which
resolves the correct MSDFS target. A latent divide-by-zero on a
zero-hard-limit share was fixed along the way.

---

## Miscellaneous

- Security fixes in Ajenti and `paramiko`; Python 3.13 compatibility.
- `pdflatex` used as the default for password printing; parents' and
  staff's passwords can now be printed too.

---

Author: Arnaud Kientz
Co-Author: Claude
