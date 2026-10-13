# lmn_crontab

Crontab editor for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets a global administrator read and edit the `global-admin` and `root` crontabs of the server from the browser, with a per-job "disable during holidays" helper.

It is a thin front end: `views.py` parses and writes the crontab through its `CronManager`, which simply shells out to the system `crontab` command.

---

## Features (web interface)

Opened from the sidebar as **Cron** (category *System*), the whole view is wrapped in a `global-admin-access` guard. At the top a selector chooses **which crontab to edit**: *As globaladministrator* or *As root*. Below, three tabs:

- **Jobs** (normal tasks) — a table with **Disable holidays** (a checkbox plus the school the holiday guard targets), **Minute**, **Hour**, **Day (month)**, **Month**, **Day (week)** and **Command**, with per-row **Modify** (cog) and **Remove** (trash) buttons, and an **Add** button. "There is no cronjob." is shown when empty.
- **Special** — special tasks (`@reboot`, `@yearly`, `@annually`, `@monthly`, `@weekly`, `@daily`, `@hourly`): table with **Disable holidays**, **Special** and **Command**, same Modify/Remove/Add actions.
- **Environment variables** — table with **Name** and **Value**, same Modify/Remove/Add actions.

**Modify** opens a dialog with the full fields for the chosen type (including a free-text **Comment** and, for tasks, the **Disable holidays** checkbox). A floating **Save** toolbar commits the whole crontab.

When "Disable holidays" is set, the backend prefixes the command with `/usr/sbin/linuxmuster-holiday -s <school> && …` so the job is skipped on holidays; the frontend decodes that prefix back into the checkbox and the displayed school.

### Backend

`views.py` (guarded by `lm:crontab:read` / `lm:crontab:write`) loads the `global-admin` and `root` tabs for global administrators, parses the holiday prefix, and on save rebuilds the crontab from the posted `normal_tasks` / `special_tasks` / `env_settings`. `manager.py` (`CronManager`) reads with `crontab -l -u <user>` and writes with `crontab - -u <user>`, using `reconfigure`'s `CrontabConfig` to parse the file.

---

## Permissions

Declared in `main.py`, all `default: False` (role defaults in `permissions.yml`, granted only to the global administrator):

| Permission | Grants |
|---|---|
| `lm:crontab:read` | read the user's crontab |
| `lm:crontab:write` | modify the user's crontab |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /crontab` | `lm:crontab:read` | Parsed `global-admin` and `root` crontabs plus the active school |
| `POST /crontab` | `lm:crontab:write` | Rebuild and save both crontabs |

---

## Requirements

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`), which provides the school context and `sophomorixRole`.
- The `reconfigure` library (`CrontabConfig`, crontab item classes).
- The system `crontab` command and `/usr/sbin/linuxmuster-holiday` on the server.
