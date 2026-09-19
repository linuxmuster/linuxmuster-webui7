# 🚀 Release Notes – linuxmuster-webui7 7.4

**Package version:** 7.4.2 – 7.4.12

---

## 📋 Overview

Version 7.4 is largely a de-duplication cycle for the webui: password
management, LINBO remote/image handling, management-group and printer
membership and file handling all had their own local implementation,
diverging from `linuxmuster-tools`' and `linuxmuster-api`'s more complete
versions. All of them have been migrated to consume the shared library or the
API instead, which also fixed a quota-display bug for fileserver-hosted
shares along the way. The end of the cycle added API-key scoping to the
settings plugin and a packaging pass that finally gives the webui a venv it
really owns.

---

## 🔑 Password management

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

## 🖥️ LINBO plugins

- `lmn_linbo_sync` migrated to `linuxmuster-tools`' `LinboRemote`: `api.py`
  now only maps frontend parameters and runs the command, instead of
  duplicating command-building, OS-detection and last-sync logic locally.
- Host online detection now reports a boot state (Off, Linbo, OS Linux, OS
  Windows, OS Unknown) via `classify_host()` instead of shelling out to
  `nmap` directly.
- `lmn_linbo4`'s own 527-line `images.py` removed — image
  listing/renaming/deletion now goes through `linuxmuster-tools`'
  `LinboImageManager`.
- Fixed a `KeyError 'diff'` when saving an image without the diff option: it
  defaults to `False` when missing from the POST body. The edit button is
  hidden for images that are in an error state.
- `lmn_device-manager` uses `last_sync` from `linuxmuster-tools` instead of a
  local implementation.

---

## 👥 Management groups, printers and parents

- Management-group membership (wifi, internet, intranet, webfilter,
  printing) and parent assignment/removal no longer shell out to `lmncli`;
  both now call `linuxmuster-api`.
- Enrolling several users or groups into a printer at once had no visible
  effect: the members were written, but the answer of the server was
  malformed and the interface neither notified nor refreshed. Printer
  membership now goes through `linuxmuster-api` in a single call instead of
  one `sophomorix-group` call per entity (reported by @ebert).
- Exam accounts are no longer offered when searching for a member to add: the
  account is temporary, and its label barely differs from the real one.
- New `linuxmuster-api` client methods for printers (`patch_printer_members`,
  `join_printer`, `quit_printer`).

---

## 🔐 API keys and settings

- An API key can be restricted to a list of endpoints, the scope added in
  linuxmuster-api 7.4.13. Entries are added and removed from the key dialog,
  and the dialog documents the syntax and its wildcards. Leaving the scope
  empty keeps the current behaviour: a key reaching the whole API with the
  permissions of its user.
- Saving the API keys no longer drops the fields this tab does not know
  about: keys are merged into the ones already in the API's `config.yml`
  instead of replacing them wholesale, which silently discarded the scope of
  every key at once.
- A failed restart of `linuxmuster-api` is reported instead of being
  swallowed. The service only reads the keys at startup, so until it is
  restarted the change just saved is not active.

---

## ♻️ Shared code centralization

- The plugin's own `LMNFile`/`fieldnames.py` (416 + 65 lines) removed; 8
  plugins (settings, quotas, dhcp, permissions, devices, linbo4,
  setup-wizard, device-manager) now use `linuxmusterTools.lmnfile.LMNFile`
  instead — atomic writes, BOM handling, and a `StartConfLoader` bug fixed
  only in the lmntools version.

---

## 🐛 Quota display fix

Fixed quota display for users whose home share is hosted on a separate
fileserver (MSDFS): the quota used to be queried locally via
`sophomorix-query`, which cannot see a remote fileserver and showed
`UNLIMITED` instead. Both the landing page and the admin "user details"
modal now proxy `linuxmuster-api`'s `GET /v1/users/{user}/quotas`, which
resolves the correct MSDFS target. A latent divide-by-zero on a
zero-hard-limit share was fixed along the way.

---

## 📦 Packaging

- postinst: the deprecated venv migration is dropped, and a system-wide
  Ajenti is uninstalled on install and upgrade. pip skips in a
  `--system-site-packages` venv any requirement the system already satisfies,
  pinned versions included, so a system-wide copy kept the venv from ever
  owning its own and no update would have touched it again.
- New `linuxmuster-venv` dpkg trigger: when `linuxmuster-tools7` rebuilds the
  shared venv after a Python upgrade, the webui reinstalls its requirements
  and restarts.

---

## 🔧 Miscellaneous

- Updated to Ajenti 2.2.17, which fixes three issues reachable without
  authentication (see the Ajenti changelog). Security fixes in `paramiko`;
  Python 3.13 compatibility.
- `pdflatex` used as the default for password printing; parents' and
  staff's passwords can now be printed too.
- Fixed a duplicate "Login" column in the users list management view,
  replaced by the intended "Birthday" column (closes #292).
- Landing page updated to display version 7.4 (merge of PR #290,
  @jolly-jump).
- `setup`: fixed a typo, `setup.ini` is checked before launching
  `linuxmuster-setup`, and errors are caught on the frontend.

---

Author: Arnaud Kientz
Co-Author: Claude
