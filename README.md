# Lycophron

TODO

## Getting started

- [Installation](#installation)
- [Examples](#examples)
- [Development](#development)

## Requirements

- `python` version `3.7.2`

## Installation

### Linux

> It is recommended to use a virtual environment to install and run the application.
>
> To create a virtual environment named `lycophron`, run the following command in your terminal:
>
> ```shell
> python3 -m venv lycophron
> source lycophron/bin/activate
> ```

To install the application, use [pip-tools](https://github.com/jazzband/pip-tools):

```shell
# Install pip-tools for dependency management
python -m pip install pip-tools

# Install Python requirements
pip-sync requirements.dev.txt requirements.txt

# Install lycophron 
python -m pip install .
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

Make sure that it is installed:

```shell
# Install pip-tools
python -m pip install pip-tools
```

and validate the installation:

```console
$ python -m piptools --help

Usage: python -m piptools [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  compile  Compiles requirements.txt from requirements.in,...
  sync     Synchronize virtual environment with requirements.txt.
```

#### Generate dependency files

> You should not need to do this. More often, you will want to just bump all dependencies to their latest versions. See [upgrading dependencies](#upgrade-a-dependency)

Two major files are used by `pip-tools`:

- `requirements.in`, used for production
- `requirements.dev.in`, used for development

The files are generated from scratch like so:

```shell
# Generate requirements.txt
pip-compile

# Generate requirements.dev.txt
pip-compile requirements.dev.in -o requirements.dev.txt  
```

#### Add a new dependency

To add a new dependency, add it in either `requirements.in` or `requirements.dev.in`. Then, update `*.txt` files with pinned versions:

```shell
# Update the requirements.txt file
pip-compile --upgrade-package <new-package>

# Update the requirements.dev.txt file
pip-compile requirements.dev.in -o requirements.dev.txt --upgrade-package <new-package>
```

#### Upgrade all dependencies

To upgrade all dependencies in development, run the following command in your terminal:

```shell
pip-compile --upgrade
pip-compile requirements.dev.in -o requirements.dev.txt --upgrade
```

and for production:

```shell
pip-compile --upgrade
pip-compile requirements.in -o requirements.txt --upgrade
```
