# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Main lycophron app."""

import os
from .config import Config
from .errors import ErrorHandler
from .project import Project


class SingletonMeta(type):
    """Represents a singleton."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class LycophronApp(object, metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.config = self.init_config()
        self.project = Project()

    def init_config(self) -> Config:
        config = Config(root_path=os.getcwd())
        config.create()
        config.load()
        config.validate()
        return config

    def init_project(self):
        self.project.initialize()

    def update_app_config(self, config, persist=False) -> None:
        if not self.config:
            # TODO
            raise ValueError("Config not found")
        try:
            self.config.update_config(config, persist)
        except Exception as e:
            ErrorHandler.handle_error(e)

    def is_config_persisted(self, config_key):
        return self.config.is_config_persisted(config_key)

    def recreate_project(self):
        if not self.project.is_project_initialized():
            raise ValueError("Project is not initialised!")
        self.project.recreate_project()

    def validate_project(self):
        if not self.project.is_project_initialized():
            raise ValueError("Project is not initialised!")
        self.project.validate_project(self.config)

    def is_project_initialized(self):
        return self.project and self.project.is_project_initialized()

    def load_file(self, filename):
        self.project.load_file(filename)

    def publish_records(self, num_records=None):
        publish_url = self.config["ZENODO_URL"] + "/api/deposit/depositions"
        self.project.publish_records(publish_url, self.config["TOKEN"], num_records)


app = LycophronApp()
