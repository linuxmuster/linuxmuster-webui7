# lmn_websession

Web-session (BigBlueButton) plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lets teachers create, start, join and stop BBB web conferences for selected users and school classes, and gives external attendees a public join page.

The plugin talks directly to a BigBlueButton instance over its HTTP API (checksum-signed calls built in `api.py`); it does not go through `linuxmuster-api` for the conference calls. The session list is persisted as a local JSON file on the server.

---

## Features (web interface)

Opened from the sidebar as **Websession** (category *class*), the view is reserved to the teacher workflow:

- If the module is not configured, an info banner **Websession-Module not enabled! Please check Config-File!** is shown instead of the list.
- **Running Websession** panel — a table of the conferences the current user moderates or participates in, with columns **Sessionname**, **Moderator**, **Password**, **Participants** (count, click to open a participants modal), **Status** (`started` / `stopped`). A lock / open-lock icon marks whether the current user owns the session.
- Per row the owner (moderator) can **Start** (play), **Join as moderator / attendee** (play, when running), **Stop**, **Delete** (trash), **Show URL** and **Copy URL** (clipboard). Non-owners see these actions disabled. Joining opens the BBB meeting in a new browser tab.
- A **＋** button (visible only to users whose `sophomorixRole == 'teacher'`) opens the **Create new session** modal, and a **sync** button refreshes the list.

### Create new session modal

- **Name**, **Type** (**Public** or **Password**, with a password field shown for the password type).
- **Add User** and **Add Class** typeahead fields (search users / school classes), feeding a selectable **Users** participant list that can be built up and trimmed before creating the session.

### Public join page

`GET /websession/<name>` serves a standalone HTML page (`public.html`, German UI) for external attendees. It polls the backend for the session name, whether a password is required, and whether the meeting is running; once the conference is started it enables the **Start** button, checks the entered password, and redirects the visitor into the BBB meeting.

### Backend

`views.py` exposes the endpoints below. Conference lifecycle calls (create/start/join/end/isMeetingRunning) are delegated to the BBB API through `api.py` (`bbbApiCall`, `getURL`, `bbbGenerateChecksum`). On create, the handler generates the meeting id, the attendee password and the moderator password with `secrets.choice(string.ascii_lowercase + string.digits)` (20-char attendee/moderator passwords, a 10-char random suffix for the id), runs the names through `replaceSpecialChars` (German umlaut transliteration), sets the moderator to the calling identity, and appends the entry to the session list JSON. Several read endpoints and the join/public endpoints are declared `auth=False` so the public page can reach them.

---

## Permissions

No `PermissionProvider` is declared. Access is controlled only through the sidebar entry in `permissions.yml` (`sidebar:view:/view/lmn/websession`, `false` by default for every role). Within the view, creating sessions is further limited client-side to the `teacher` role.

---

## HTTP API

Mounted under `/api/lmn/`. Endpoints marked *public* use `auth=False`.

| Method & path | Auth | Description |
|---|---|---|
| `GET /api/lmn/websession/webConferenceEnabled` | authenticated | `true` if the config/list files load successfully |
| `GET /api/lmn/websession/webConferences` | authenticated | Sessions the current user moderates or joins, with live `started`/`stopped` status |
| `GET /api/lmn/websession/webConferences/<sessionname>` | authenticated | A single session by name, with live status |
| `POST /api/lmn/websession/webConferences` | authenticated | Create a session (generates ids/passwords, appends to the list file) |
| `POST /api/lmn/websession/startWebConference` | authenticated | `create` the meeting on the BBB instance |
| `POST /api/lmn/websession/joinWebConference` | public | Return the BBB `join` URL for the given id/password/name |
| `POST /api/lmn/websession/endWebConference` | authenticated | `end` the meeting on the BBB instance |
| `DELETE /api/lmn/websession/webConference/<id>` | authenticated | Remove a session from the list file |
| `POST /api/lmn/websession/session/hasPassword` | public | Session type (`public`/`password`) for an id |
| `POST /api/lmn/websession/session/name` | public | Session display name for an id |
| `POST /api/lmn/websession/session/checkPassword` | public | Return the attendee password if the submitted password matches, else `error` |
| `POST /api/lmn/websession/session/isRunning` | public | `true`/`false` from BBB `isMeetingRunning` |
| `GET /websession/<name>` | public (page) | Serve the public join page (`public.html`) |

---

## Requirements / Configuration

- Ajenti `core` and the `lmn_common` plugin (dependencies in `plugin.yml`).
- A reachable **BigBlueButton** instance; `api.py` requires `requests` and `xmltodict`.
- Settings file `/etc/linuxmuster/webui/websession/websession_config.json`:

```json
{
  "settings": {
    "bbbInstance": "https://bbb.example.com/bigbluebutton/api/",
    "bbbSecret": "herecomesthesecretkey"
  }
}
```

- Session store `/etc/linuxmuster/webui/websession/websession_list.json`, initialised empty:

```json
[]
```
