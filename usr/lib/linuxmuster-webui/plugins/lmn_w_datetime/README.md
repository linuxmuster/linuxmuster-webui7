# lmn_w_datetime

Dashboard widget for the [linuxmuster.net](https://www.linuxmuster.net) web interface (Ajenti). It contributes a small "Date Time" tile to the Ajenti dashboard that prints the server date and/or time in a chosen format.

This plugin has no HTTP endpoints and no sidebar entry: it is purely a dashboard `Widget` component rendered client-side from a value computed in `widget.py`.

> Note: the original plugin stub was marked **DEPRECATED**.

---

## Features (web interface)

The widget appears in the list of available dashboard widgets as **Date Time**. Once added to the dashboard it shows a single value (the formatted date/time, or `Unknown` / `Not configured` when no format is set).

Its configuration dialog offers a **Format** dropdown with three presets:

- **Date Time** — `%d.%m.%Y %H:%M`
- **Date** — `%d.%m.%Y`
- **Time** — `%H:%M`

The default format is `%d.%m.%Y %H:%M`.

### Backend

`widget.py` registers a `Widget` component (`id = 'datetime'`) whose `get_value(config)` returns the timestamp formatted with the Python `strftime` pattern stored in the widget config, or `Not configured` when no `format` key is present. The two AngularJS controllers (`lm.wdatetime`, `lm.wdatetimeconfig`) render the value and the configuration dropdown.

---

## Requirements / Configuration

- Ajenti `core` and the `dashboard` plugin (dependencies in `plugin.yml`); the widget plugs into `aj.plugins.dashboard.api.Widget`.
- No external service and no configuration file: the only user setting is the format string chosen in the widget's configuration dialog.
