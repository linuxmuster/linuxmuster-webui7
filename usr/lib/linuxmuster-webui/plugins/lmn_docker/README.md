# lmn_docker

Docker monitoring plugin for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It lists the containers and images of a remote Docker host and lets an administrator start, stop or remove them.

The plugin talks to the Docker host over SSH (`ssh <host> docker ...`) via `subprocess`; it does not go through `linuxmuster-api`. The host address is currently hardcoded to `10.0.0.3` (a `TODO` in the code plans to read it from `/var/lib/linuxmuster/setup.ini`).

---

## Features (web interface)

Opened from the sidebar as **Docker** (software category). If Docker cannot be reached on the host, an info banner **Docker is not installed on this host.** is shown; otherwise the view has two tabs.

- **Container** tab — a table with **Name (Hash)**, **Memory usage**, **Cpu usage**, **Network used**, a start/stop toggle and a remove button. Usage figures auto-refresh every 5 seconds. Clicking a container name opens a details dialog (full id, creation date, IP per network, port mappings, volume mounts). Removing a container asks for confirmation.
- **Images** tab — a table with **Repository**, **Created**, **Tag**, **Size** and a remove button (removal asks for confirmation). A "start new container" action exists in the markup but is commented out.

### Backend

`views.py` builds every command as `['ssh', '10.0.0.3', 'docker', ...]` and runs it with `subprocess`. It uses `docker stats`, `docker inspect`, `docker images` (all with `--format '{{json .}}'`), `docker start/stop/rm` for containers and `docker rmi` for images. The `which` endpoint tests the SSH connection and that `docker` is installed.

---

## Permissions

Declared in `main.py`, all `default: False`:

| Permission | Grants |
|---|---|
| `lm:docker:list` | list images and running containers |
| `lm:docker:change` | remove images and change running containers |

---

## HTTP API

Mounted under `/api/lmn/`.

| Method & path | Permission | Description |
|---|---|---|
| `GET /docker/which` | `lm:docker:list` | Test the SSH connection and that Docker is installed |
| `GET /docker/containers` | `lm:docker:list` | `docker stats` (memory/cpu/network) per container |
| `GET /docker/container/<container_id>` | `lm:docker:list` | `docker inspect` of one container |
| `POST /docker/container_command` | `lm:docker:change` | `start`, `stop` or `rm` the posted container |
| `GET /docker/images` | `lm:docker:list` | `docker images` on the host |
| `DELETE /docker/image/<image_id>` | `lm:docker:change` | `docker rmi` the given image |

---

## Requirements

- Ajenti `core` (only dependency in `plugin.yml`).
- SSH access from the server to the Docker host (hardcoded `10.0.0.3`), with `docker` installed there.
