import os
import types
from abc import ABC, abstractmethod
import logging
from .errors import ConfigNotFound, ErrorHandler

logger = logging.getLogger(__name__)


class Defaults:

    SQLALCHEMY_DATABASE_URI = "sqlite:///lycophron.db"


required_configs = ["TOKEN", "SQLALCHEMY_DATABASE_URI"]


class Config(dict):
    def __init__(self, root_path, defaults: dict = None) -> None:
        super().__init__(defaults or {})
        self.root_path = root_path
        self.defaultsLoader = DefaultsLoader()
        self.cfgLoader = CFGLoader(root_path=root_path)
        self.loaders = [self.cfgLoader, self.defaultsLoader]

    def __setitem__(self, __key, __value) -> None:
        if not str(__key).isupper():
            logger.warn(f"Key {__key} is not upper cased. Ignoring it.")
            return
        return super().__setitem__(__key, __value)

    def load(self):
        for loader in self.loaders:
            configs = loader.load()
            self.update(**configs)

    def create(self):
        if not self.cfgLoader.exists():
            self.cfgLoader.create()

    def validate(self):
        errors = []
        for conf in required_configs:
            if not self.get(conf):
                errors.append(ConfigNotFound(conf))
        ErrorHandler.handle_error(errors)
        return True

    def update_config(self, value, persist=False):
        if type(value) is not dict:
            raise TypeError("Config must be a dictionary with pair key/value")
        super().update(value)
        if persist:
            self.cfgLoader.update(value)

    def is_config_persisted(self, key):
        upper_key = key.upper()
        return self.cfgLoader.key_exists_in_file(upper_key)


class ConfigLoader(ABC):
    def load_from_object(self, obj) -> dict:
        otp = {}
        for key in dir(obj):
            if key.isupper():
                otp[key] = getattr(obj, key)
        return otp

    @abstractmethod
    def load() -> dict:
        pass


class DefaultsLoader(ConfigLoader):
    def load(self) -> dict:
        return self.load_from_object(Defaults)


class CFGLoader(ConfigLoader):
    def __init__(self, root_path) -> None:
        self.file_name = "lycophron.cfg"
        self.root_path = root_path
        self.cfg_path = os.path.join(self.root_path, self.file_name)

    def exists(self) -> bool:
        return os.path.exists(self.cfg_path)

    def deserialize(self, key, val):
        return f"{key.upper()} = '{val}'"

    def dump(self, dump_data) -> None:
        if type(dump_data) is not dict:
            raise TypeError("Dump data must be a dictionary")
        with open(self.cfg_path, "w") as fp:
            for key, value in dump_data.items():
                fp.write(self.deserialize(key, value))
            fp.close()

    def key_exists_in_file(self, key):
        file_contents = self.load()
        return key in file_contents.keys()

    def update(self, input_dict) -> bool:
        if type(input_dict) is not dict:
            raise TypeError("Config must be a dictionary with pair key/value")

        if not self.exists():
            return False

        file_contents = self.load()

        for key, value in input_dict.items():
            upper_key = str(key).upper()
            if self.key_exists_in_file(upper_key):
                logger.warn(
                    f"Config '{upper_key}' already exists in {self.file_name} file. Overriding."
                )
            file_contents[upper_key] = value
        self.dump(file_contents)
        return True

    def create(self) -> bool:
        if self.exists():
            return False

        open(self.cfg_path, "w").close()
        return True

    def load(self) -> dict:
        if not self.exists():
            return {}

        d = types.ModuleType("config")
        d.__file__ = self.cfg_path
        try:
            with open(self.cfg_path, mode="rb") as config_file:
                exec(compile(config_file.read(), self.cfg_path, "exec"), d.__dict__)
        except OSError as e:
            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise
        loaded_configs = self.load_from_object(d)
        return loaded_configs
