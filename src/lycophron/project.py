# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron project classes (business logic layer)."""
from functools import cached_property

from .db import LycophronDB
from .errors import DatabaseAlreadyExists, ErrorHandler
from .loaders import LoaderFactory
from .schemas.record import RecordRow
from .tasks.tasks import process_record


class Project:
    def __init__(self, db_uri):
        self.errors = []
        self._db_uri = db_uri

    @cached_property
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

    def load_file(self, filename, config):
        data = self.process_file(filename, config)
        for record in data:
            self.add_record(record)
        if len(self.errors):
            ErrorHandler.handle_error(self.errors)

    def process_file(self, filename, config):
        factory = LoaderFactory()
        loader = factory.create_loader(filename)
        row_schema = RecordRow(context=config)
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

