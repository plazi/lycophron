# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron project classes (business logic layer)."""

import csv
import os

from .errors import (
    DatabaseAlreadyExists,
    ErrorHandler,
    InvalidRecordData,
)
from .loaders import LoaderFactory
from .schemas.record import RecordRow


class Project:
    def __init__(self, project_folder=os.getcwd()):
        self.project_folder = project_folder
        self.errors = []

    def load_file(self, filename):
        data = self.process_file(filename)
        for record in data:
            self.add_record(record)
        if len(self.errors):
            ErrorHandler.handle_error(self.errors)

    def process_file(self, filename):
        if not self.is_project_initialized():
            raise Exception("Project is not initialised.")
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
        # TODO fix too many "from .db import db"
        # TODO record data integrity is missing validation
        from .db import db

        try:
            db.add_record(record)
        except Exception as e:
            self.errors.append(e)

    def initialize(self):
        """Initialize the project"""
        from .db import db

        try:
            db.init_db()
        except DatabaseAlreadyExists as e:
            ErrorHandler.handle_error(e)

    def recreate_project(self):
        from .db import db

        db.recreate_db()

    def validate_project(self):
        # Configs exist
        # Configs are valid
        raise NotImplementedError("Project validation not implemented yet")

    def is_project_initialized(self):
        from .db import db

        return db.database_exists()

    def publish_all_records(self, url, token):
        from .db import db
        from .tasks.tasks import create_deposit

        records = db.get_all_records()

        for record in records:
            create_deposit.delay(record.files, record.original, token, url)
