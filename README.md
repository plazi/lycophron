# Lycophron

## Development

To install and run the application, run the following:

```shell
# Create a virtualenv and activate it
python3 -m venv venv
source venv/bin/activate

# Install tools to keep Python dependencies fresh
pip install pip-tools

# Install Python requirements
(venv) pip-sync requirements.dev.txt requirements.txt
```

### Dependency management

To manage Python dependencies, we use [`pip-tools`](https://github.com/jazzband/pip-tools). To add a new dependency,
list it in `requirements.in` (production) or `requirements.dev.in` (development). Then, update `*.txt` files
with pinned versions:

```shell
# Update the requirements.txt file
pip-compile -P <new-package>

# Update the requirements.dev.txt file
pip-compile requirements.dev.in -o requirements.dev.txt -P <new-package>
```

The `requirements.txt` and `requirements.dev.txt` files are generated from scratch like so:

```shell
pip-compile # requirements.txt
pip-compile requirements.dev.in -o requirements.dev.txt
```

You should not need to do this, though. More often, you will want to just bump all dependencies to their latest
versions:

```shell
pip-compile -U
pip-compile requirements.dev.in -o requirements.dev.txt -U
```
