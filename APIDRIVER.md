# valohai-cli as API driver

> :warning: This is an advanced topic.

`valohai-cli` can also be used as a non-interactive "API driver" for the Valohai platform.

It supports a handful of command-line options (also available as environment variables)
that let you use a pre-acquired API token and use the tool without a linked project directory.

| Option | Environment variable | Description |
|--------|----------------------|-------------|
| `--valohai-token` | `VALOHAI_TOKEN` | The API authentication token |
| `--valohai-host` | `VALOHAI_HOST` | The Valohai host (only required with private installations) |
| `--valohai-project` | `VALOHAI_PROJECT` | The Valohai project UUID |
| `--valohai-project-mode` | `VALOHAI_PROJECT_MODE` | Force project mode (`local`/`remote`); optional, see below |
| `--valohai-project-root` | `VALOHAI_PROJECT_ROOT` | The project root directory; defaults to the current working directory |

* You can acquire the token from the Authentication view in the Valohai app, or get it from your local
  valohai-cli configuration file if you've already logged in using `vh login`.

* You can get your project ID from the Valohai API (`/api/v0/projects`), or, again, by looking at your
  configuration file.

* If you do not set `VALOHAI_PROJECT_MODE`, the CLI will attempt to sniff around for `valohai.yaml`
  in the project root directory.  If it finds one, it assumes the project is local. See below.
  Otherwise the project is assumed to be remote.


Modes
-----

* In Local mode, the CLI will use local git history and `valohai.yaml` files. Ad-hoc runs are available.
* In Remote mode, all configuration (incl. the contents of `valohai.yaml` files per-commit)
  is fetched from the Valohai server. Ad-hoc runs are not available in this mode.

Example
-------

```bash
$ cd $(mktemp -d)  # go to an empty directory
$ export VALOHAI_TOKEN=obviouslyfaketokenreplacethis
$ export VALOHAI_PROJECT=CAD69D74-0E9C-4F8A-A960-07C0DBE34935
$ export VALOHAI_TABLE_FORMAT=json
$ vh exec list
[
  {
    "counter": 1,
    [...]
$ vh exec run Train
```
