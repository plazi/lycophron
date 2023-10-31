# Lycophron

CLI tool for managing Zenodo uploads.

## Getting started

- [Installation](#installation)
- [Examples](#examples)
- [Development](#development)

## Requirements

- Python v3.9+

## Installation

### Linux/macOS

> It is recommended to use a virtual environment to install and run the application.
>
> To create a virtual environment named `lycophron`, run the following command in your terminal:
>
> ```shell
> python3 -m venv lycophron
> source lycophron/bin/activate
> ```

To install the CLI tool just run:

```shell
# For using the tool
python -m pip install -r requirements.txt

# For local development
python -m pip install requirements-dev.txt
```

## Examples

TODO

## Features

TODO

## Known issues

TODO

## Development

### Dependency management

To manage Python dependencies, lycophron uses [`pip-tools`](https://github.com/jazzband/pip-tools).

#### Generate dependency files

> You should not need to do this. More often, you will want to just bump all dependencies to their latest versions. See [upgrading dependencies](#upgrade-a-dependency)

Two major files are used by `pip-tools`:

- `requirements.in`, used for production
- `requirements-dev.in`, used for development

The files are generated from scratch like so:

```shell
# Generate requirements.txt
pip-compile requirements.in

# Generate requirements-dev.txt
pip-compile requirements-dev.in
```

#### Add a new dependency

To add a new dependency, add it in the `dependencies` section of the `pyproject.toml` file. Add testing/development dependencies under `[project.optional-dependencies]` section's `tests` extra.

```shell
# Update the requirements.txt file
pip-compile requirements.in --upgrade-package <new-package>

# Update the requirements.dev.txt file
pip-compile requirements-dev.in --upgrade-package <new-package>
```

#### Upgrade all dependencies

To upgrade all dependencies in development, run the following command in your terminal:

```shell
pip-compile requirements-dev.in --upgrade
```

and for production:

```shell
pip-compile --upgrade
pip-compile requirements.in --upgrade
```
