# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron config classes."""

import logging
import logging
import os
import types
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from .errors import ConfigNotFound, ErrorHandler, InvalidConfig, ConfigError

logger = logging.getLogger("lycophron")


class Defaults:
    SQLALCHEMY_DATABASE_URI = "sqlite:///lycophron.db"
    ZENODO_URL = "https://sandbox.zenodo.org/api"
    TOKEN = "CHANGEME"


required_configs = ["TOKEN", "SQLALCHEMY_DATABASE_URI", "ZENODO_URL"]


class Config(dict):
    def __init__(self, root_path, defaults: None) -> None:
        self.defaults = defaults
        self.root_path = root_path

    def __setitem__(self, __key, __value) -> None:
        if not str(__key).isupper():
            logger.warn(f"Key {__key} is not upper cased. Ignoring it.")
            return
        return super().__setitem__(__key, __value)

    @property
    def is_initialized(self):
        return self.cfgLoader.exists()

    @property
    def defaultsLoader(self):
        return DefaultsLoader(self.defaults)

    @property
    def cfgLoader(self):
        return CFGLoader(root_path=self.root_path)

    def recreate(self):
        """Recreate the config file."""
        if self.cfgLoader.exists():
            os.remove(self.cfgLoader.cfg_path)
        self.create()

    def load(self):
        for loader in [self.defaultsLoader, self.cfgLoader]:
            configs = loader.load()
            self.update(**configs)

    def create(self):
        if not self.cfgLoader.exists():
            self.cfgLoader.create()

    def validate(self):
        """Validate the config."""
        self._all_configs_required_set()
        self._is_zendodo_url_valid()

    def _all_configs_required_set(self):
        """Check if all required configs are set."""
        errors = []
        for conf in required_configs:
            if not self.get(conf):
                errors.append(ConfigNotFound(conf))
        if errors:
            ErrorHandler.handle_error(errors)
            raise errors[0]

    def _is_zendodo_url_valid(self):
        """Check if the URL is valid."""
        parsed_url = urlparse(self["ZENODO_URL"])
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise InvalidConfig(f"Invalid URL provided: {self['ZENODO_URL']}.")

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
    def __init__(self, defaults=None) -> None:
        _defaults = defaults or {}
        self.defaults = _defaults

    def load(self) -> dict:
        dfs = self.load_from_object(Defaults)
        if self.defaults:
            dfs.update(self.defaults)
        return dfs


class CFGLoader(ConfigLoader):
    def __init__(self, root_path) -> None:
        self.file_name = "lycophron.cfg"
        self.cfg_path = os.path.join(root_path, self.file_name)

    def exists(self) -> bool:
        return os.path.exists(self.cfg_path)

    def deserialize(self, key, val):
        return f"{key.upper()} = '{val}'\n"

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
