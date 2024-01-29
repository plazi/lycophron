# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron project classes (business logic layer)."""

from .client import create_session
from .config import required_configs
from .errors import (
    DatabaseAlreadyExists,
    ErrorHandler,
)
from .loaders import LoaderFactory
from .schemas.record import RecordRow
from .db import LycophronDB


class Project:
    def __init__(self, db_uri):
        self.errors = []
        self._db_uri = db_uri

    @property
    def db(self):
        """Get the database."""
        return LycophronDB(uri=self.db_uri)

    @property
    def db_uri(self):
        return self._db_uri

    @db_uri.setter
    def db_uri(self, uri):
        self._db_uri = uri

    @property
    def is_initialized(self):
        return self.db.database_exists()

    def load_file(self, filename):
        data = self.process_file(filename)
        for record in data:
            self.add_record(record)
        if len(self.errors):
            ErrorHandler.handle_error(self.errors)

    def process_file(self, filename):
        factory = LoaderFactory()
        loader = factory.create_loader(filename)
        row_schema = RecordRow()
        records = []
        for data in loader.load(filename):
            try:
                record = row_schema.load(data)
            except Exception as e:
                self.errors.append(e)
            else:
                records.append(record)
        return records

    def add_record(self, record):
        # TODO record data integrity is missin validation
        try:
            self.db.add_record(record)
        except Exception as e:
            self.errors.append(e)

    def initialize(self):
        """Initialize the project"""
        try:
            self.db.init_db()
        except DatabaseAlreadyExists as e:
            ErrorHandler.handle_error(e)

    def recreate(self):
        """Recreate the project"""
        self.db.recreate_db()

    def publish_records(self, url, token, num_records=None):
        from .tasks.tasks import publish_records

        publish_records.apply_async(
            args=[url, token, num_records],
        )
