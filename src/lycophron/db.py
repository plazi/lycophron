# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Database manager for lycophron. Provides basic functionalities to create a database."""

import datetime
import json
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from .errors import DatabaseAlreadyExists, DatabaseNotFound, DatabaseResourceNotModified
from .models import Model, Record, RecordStatus, Community, File

logger = logging.getLogger("lycophron")
dev_logger = logging.getLogger("lycophron_dev")


def custom_serializer(o):
    if isinstance(o, datetime.datetime):
        return str(o)
    else:
        # raises TypeError: o not JSON serializable
        return json.dumps(o, default=str)


class LycophronDB(object):
    """Manages a lycophron DB."""

    def __init__(self, uri) -> None:
        self.engine = create_engine(
            uri, json_serializer=custom_serializer, pool_recycle=3600, pool_size=10
        )
        _session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )
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

        new_record = Record(
            id=record.get("id"),
            input_metadata=record.get("input_metadata"),
            remote_metadata={},
        )
        cleaned_community = [
            community for community in record.get("communities") if community
        ]
        cleaned_files = [file for file in record.get("files") if file]

        for community in cleaned_community:
            community = Community(slug=community)
            new_record.communities.append(community)
        for file in cleaned_files:
            file = File(filename=file)
            new_record.files.append(file)
        self.session.add(new_record)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            dev_logger.error(e)
            record_rep = record.get("doi") or record.get("title")
            raise DatabaseResourceNotModified(
                f"Record {record_rep} was rejected by database."
            )
        else:
            repr = record.get("id", record["id"])
            logger.info(f"Record {repr} was added.")

    def get_record(self, id):
        rec = self.session.query(Record).get(id)
        return rec

    def update_record(self, record):
        self.session.commit()

    def get_unpublished_deposits(self, number):
        if not self.database_exists():
            raise DatabaseNotFound("Database not found. Aborting record fetching.")
        query = self.session.query(Record).filter(
            Record.status == RecordStatus.TODO # TODO Update this to fetch any state if not errored
        )
        if number:
            query = query.limit(number)
        records = query.all()
        return records
