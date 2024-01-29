# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Main lycophron app."""

import os
import shutil
from functools import cached_property
from urllib import parse as urlparse
from .client import create_session
from .config import Config
from .errors import InvalidDirectoryError
from .logger import init_logging
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
    def __init__(self, name=None) -> None:
        self._name = name

    @property
    def name(self):
        """Get the name of the app."""
        return self._name or ""

    @property
    def root_path(self):
        """Get the root path of the project."""
        return os.path.join(os.getcwd(), self.name)

    @cached_property
    def config(self):
        """Get the config."""
        return self._init_config()

    @cached_property
    def project(self):
        """Get the project."""
        return self._init_project()

    def init(self):
        """Initialize the app.

        This method is responsible for creating the project directory, the config, database and logger files.
        """
        self._create_directory()
        self._init_logging()
        self._init_config()
        self._init_project()

    def _create_directory(self):
        """Create the app directory."""
        os.makedirs(os.path.join(self.root_path, "files"), exist_ok=True)

    def _remove_directory(self):
        """Remove the app directory."""
        shutil.rmtree(os.path.join(self.root_path, "files"), ignore_errors=True)

    def _validate_directory(self):
        """Validate the app directory."""
        if not os.path.exists(os.path.join(self.root_path, "files")):
            raise InvalidDirectoryError(
                f"Directory {self.root_path} does not exist. Create it first."
            )

    def _init_config(self) -> Config:
        """Initialize the config."""
        default_db_location = (
            f"sqlite:///{os.path.join(self.root_path, 'lycophron.db')}"
        )
        c = Config(
            root_path=self.root_path,
            defaults={
                "SQLALCHEMY_DATABASE_URI": default_db_location,
            },
        )
        c.create()
        c.load()
        c.validate()

        return c

    def _init_project(self):
        """Initialize the project."""
        p = Project(self.config["SQLALCHEMY_DATABASE_URI"])
        p.initialize()
        return p

    def _init_logging(self):
        """Initialize logging."""
        init_logging(self.root_path)

    def recreate(self):
        self.config.recreate()
        self.project.recreate()
        self._remove_directory()
        self._create_directory()

    def validate(self):
        self._validate_directory()
        self.config.validate()

    def load_file(self, filename):
        self.project.load_file(filename)

    def publish_records(self, num_records=None):
        publish_url = urlparse.urljoin(
            self.config["ZENODO_URL"], "/deposit/depositions"
        )
        self.project.publish_records(publish_url, self.config["TOKEN"], num_records)

    # TODO not used by now, it can be added later as part of the client validation
    def _is_valid_token(self, config):
        session = create_session(config["TOKEN"])
        url = config["ZENODO_URL"] + "/api/me"
        response = session.get(url)
        if response.status_code != 200:
            raise ValueError(
                f"Invalid token or URL provided. Token: {config['TOKEN']}, URL: {config['ZENODO_URL']}"
            )
