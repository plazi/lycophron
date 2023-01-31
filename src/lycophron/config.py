import os
import types

# TODO load configs from a .cfg e.g. Zenodo tokens
# TODO load from .cfg dynamically and, if needed, override.
# TODO allow only configs prefixed with LYCOPHRON

class Config(dict):
    def __init__(self, root_path, defaults: dict = None) -> None:
        super().__init__(defaults or {})
        self.root_path = root_path
        self.load_from_py_file("lycophron.cfg")

    def load_from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def load_from_env(self, var_name):
        # TODO
        pass

    def load_from_py_file(self, filename):
        filename = os.path.join(self.root_path, filename)
        d = types.ModuleType("config")
        d.__file__ = filename
        try:
            with open(filename, mode="rb") as config_file:
                exec(compile(config_file.read(), filename, "exec"), d.__dict__)
        except OSError as e:
            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise
        self.load_from_object(d)
        return True
