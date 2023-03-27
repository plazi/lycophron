# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Database manager for lycophron. Provides basic functionalities to create a database."""

import json
import logging
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists, drop_database
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from .errors import DatabaseAlreadyExists, DatabaseNotFound, DatabaseResourceNotModified
from .app import app
from .models import Record, Model

logger = logging.getLogger("lycophron")
dev_logger = logging.getLogger("lycophron_dev")


def custom_serializer(o):
    if isinstance(o, datetime.datetime):
        return str(o)
    else:
        # raises TypeError: o not JSON serializable
        return json.dumps(o, default=str)


class CustomJSONEncoder(json.JSONEncoder):
    """ """

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return str(o)
        else:
            # raises TypeError: o not JSON serializable
            return json.JSONEncoder.default(self, o)


class LycophronDB(object):
    """Manages a lycophron DB."""

    def __init__(self, uri) -> None:
        self.engine = create_engine(uri, json_serializer=custom_serializer, pool_recycle=3600, pool_size=10)
        _session_factory = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.session = scoped_session(_session_factory)

    def init_db(self) -> None:
        """Initializes the lycophron database."""
        self._create_database()
        Model.metadata.create_all(self.engine)
        logger.info("Database initialized.")

    def _drop_database(self) -> None:
        """Drops the database"""
        drop_database(self.engine.url)
        logger.info("Database was destroyed.")

    def _create_database(self) -> None:
        """Creates a database"""
        if self.database_exists():
            raise DatabaseAlreadyExists("A database is already created.")
        create_database(self.engine.url)
        logger.info("Database created.")

    def recreate_db(self) -> None:
        """Drop and recreate database."""
        logger.warn(
            "Recreating database. THIS WILL DESTROY THE CURRENT DATABASE, PROCEED WITH CAUTION."
        )
        self._drop_database()
        create_database(self.engine.url)
        Model.metadata.create_all(self.engine)

    def database_exists(self) -> bool:
        """Check if database exists

        :return: True if exists, False otherwise
        :rtype: bool
        """
        return database_exists(self.engine.url)

    def add_record(self, record: dict) -> None:
        """Adds a record to the DB.

        :param record: deserialized record
        :type record: dict
        """
        if not self.database_exists():
            raise DatabaseNotFound("Database not found. Aborting record add.")
        self.session.add(
            Record(
                doi=record.get("doi", None),
                deposit_id=record.get("deposit_id", None),
                remote_metadata={},
                response={},
                original=record["metadata"],
                files=record["files"],
            )
        )
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            dev_logger.error(e)
            record_rep = record.get('doi') or record.get('title')
            raise DatabaseResourceNotModified(
                f"Record {record_rep} was rejected by database."
            )
        else:
            repr = record.get("doi", record["id"])
            logger.info(f"Record {repr} was added.")

    def update_record_remote_metadata(self, record_id: int, metadata: dict) -> None:
        """Updates a record's metadata in the DB.

        :param record_id: local record id.
        :type record_id: int
        :param metadata: remote's record metadata (e.g. current metadata on Zenodo)
        :type metadata: dict
        """
        if not self.database_exists():
            raise DatabaseNotFound("Database not found. Aborting record update.")

        rec = self.session.query(Record).get(record_id)
        rec.remote_metadata = metadata
        self.session.commit()
        logger.info(f"Record {rec.doi} was updated.")

    def update_record_response(self, doi: str, response: dict) -> None:
        """Updates a record's last remote response status.

        :param doi: record's doi
        :type doi: str
        :param response: response retrieved from the remote (e.g. Zenodo)
        :type response: dict
        """
        if not self.database_exists():
            raise DatabaseNotFound("Database not found.  Aborting record update.")

        rec = self.session.query(Record).filter_by(doi=doi)
        rec.response = response
        rec.deposit_id = response["id"]
        self.session.commit()
        logger.info(f"Record {rec.doi} was updated.")

    def update_record_doi(self, record_id, doi):
        rec = self.session.query(Record).get(record_id)
        rec.doi = doi
        self.session.commit()
        logger.info(f"Record {rec.doi} was updated.")

    def update_record_status(self, id, status):
        # TODO doi is not guaranteed
        if not self.database_exists():
            raise DatabaseNotFound("Database not found.  Aborting record update.")

        # TODO sql alchemy yields an error

        rec = self.session.query(Record).get(id)

        if not rec:
            raise DatabaseResourceNotModified(f"Record with {id} not found in database.")

        rec.status = status
        self.session.commit()
        logger.info(f"Record {rec.doi} status was updated.")

    def get_all_records(self):
        if not self.database_exists():
            raise DatabaseNotFound("Database not found.  Aborting record fetching.")

        records = self.session.query(Record).all()
        return records
    
    def get_n_records(self, number):
        if not self.database_exists():
            raise DatabaseNotFound("Database not found.  Aborting record fetching.")

        records = self.session.query(Record).limit(number).all()
        return records

db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
db = LycophronDB(uri=db_uri)
