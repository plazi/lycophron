# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron project classes (business logic layer)."""

import os
from functools import cached_property
from pathlib import Path

from .db import LycophronDB
from .errors import RecordValidationError
from .loaders import LoaderFactory
from .logger import logger
from .models import Record, RecordStatus
from .schemas.record import RecordRow
from .serializers import CSVSerializer


class Project:
    def __init__(self, db_uri):
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
            try:
                self.add_or_update_record(record)
            except Exception as e:
                logger.error(f"Error adding record: {e}")

    def process_file(self, filename, config):
        factory = LoaderFactory()
        loader = factory.create_loader(filename)
        row_schema = RecordRow(context=config)
        records = []
        for data in loader.load(filename):
            try:
                record = row_schema.load(data)
            except Exception as e:
                logger.error(e)
            else:
                records.append(record)
        return records

    def add_or_update_record(self, record):
        db_record = self.db.get_record(record["id"])
        if not db_record:
            self.db.add_record(record)
        else:
            self.db.update_record(db_record, record)

    def initialize(self):
        """Initialize the project."""
        self.db.init_db()

    def recreate(self):
        """Recreate the project."""
        self.db.recreate_db()

    def _file_exists(self, filename):
        """Check if the file exists."""
        return os.path.exists(filename)

    def validate(self, filename=None, config=None, directory=None):
        """Validate the project."""
        if not (filename and config and directory):
            return True
        factory = LoaderFactory()
        loader = factory.create_loader(filename)
        row_schema = RecordRow(context=config)
        for data in loader.load(filename):
            try:
                record = row_schema.load(data)
            except Exception as e:
                logger.debug(f"Record {data} validation failed.")
                raise RecordValidationError(str(e))
            fnames = record["files"]
            logger.debug(f"Validating files: {fnames}")
            for fname in fnames:
                if not self._file_exists(Path(directory) / fname):
                    raise FileNotFoundError(f"File {fname} not found in {directory}.")

        return True

    def export(self, config, serializer=CSVSerializer, full=False):
        """Export the records to a file."""
        if full:
            raise NotImplementedError("Full export is not implemented yet.")
        res = []
        BASE_URL = config["ZENODO_URL"].replace("/api", "").rstrip("/")
        records = self.db.export(
            fields=[
                Record.id,
                Record.upload_id,
                Record.input_metadata,
                Record.status,
                Record.remote_metadata,
                Record.response,
                Record.error,
            ]
        )
        logger.debug(f"Exporting {len(records)} records.")
        for record in records:
            metadata = record["input_metadata"]["metadata"]
            response = record["response"]
            if record["status"] == RecordStatus.PUBLISHED:
                zenodo_url = f"{BASE_URL}/records/{record['upload_id']}"
            elif record["upload_id"]:
                zenodo_url = f"{BASE_URL}/uploads/{record['upload_id']}"
            else:
                zenodo_url = ""
            _r = {
                "id": record["id"],
                "title": metadata.get("title"),
                "doi": metadata.get("doi"),
                "zenodo_url": zenodo_url,
                "status": record["status"],
                "zenodo_error": "",
            }
            if isinstance(response, dict) and response.get("status") == 400:
                _r["zenodo_error"] = f"{response.get('message')} : {response.get('errors')}"
            res.append(_r)
        return serializer().serialize(res)

    def retry_failed(self):
        """Reset status of failed records to `TODO`."""
        records = self.db.get_failed_records()
        n_records = 0
        for record in records:
            self.db.update_record_status(record, RecordStatus.TODO)
            n_records += 1
        return n_records
