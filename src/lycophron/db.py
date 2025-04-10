#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Database manager for Lycophron."""

import json
import logging
from datetime import datetime
from hashlib import md5

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from .errors import DatabaseAlreadyExists, DatabaseNotFound, DatabaseResourceNotModified
from .models import Community, File, Model, Record, RecordStatus
from .references import ReferenceManager

logger = logging.getLogger("lycophron")


def custom_serializer(o):
    from .template import LazyReference

    if isinstance(o, datetime):
        return str(o)
    elif isinstance(o, LazyReference):
        # Serialize a LazyReference object to a dictionary
        return {
            "type": "lazy_reference",
            "record_id": o.record_id,
            "field": o.field,
            "bidirectional": o.bidirectional,
        }
    else:
        # For all other types, use the default serialization
        return json.dumps(o, default=str)


def file_checksum(filename):
    checksum = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            checksum.update(chunk)
    return f"md5:{checksum.hexdigest()}"


class LycophronDB:
    """Manages a lycophron DB."""

    def __init__(self, uri) -> None:
        self.engine = create_engine(
            uri, json_serializer=custom_serializer, pool_recycle=3600, pool_size=10
        )
        _session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )
        self.session = scoped_session(_session_factory)
        self.reference_manager = ReferenceManager(self.session)

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
            raise DatabaseAlreadyExists()
        create_database(self.engine.url)
        logger.info("Database created.")

    def recreate_db(self) -> None:
        """Drop and recreate database."""
        logger.warning(
            "Recreating database. "
            "THIS WILL DESTROY THE CURRENT DATABASE, PROCEED WITH CAUTION."
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
        """Add a record to the DB.

        :param record: deserialized record
        :type record: dict
        """
        logger.debug("Adding record %s", record.get("id"))
        if not self.database_exists():
            raise DatabaseNotFound("Database not found. Aborting record add.")

        new_record = Record(
            id=record.get("id"),
            input_metadata=record.get("input_metadata"),
            remote_metadata={},
        )
        cleaned_community = [
            community for community in record.get("communities", []) if community
        ]
        cleaned_files = [file for file in record.get("files", []) if file]

        for comm_slug in cleaned_community:
            comm_obj = Community(slug=comm_slug)
            new_record.communities.append(comm_obj)
        for filename in cleaned_files:
            file = File(filename=filename, checksum=file_checksum(f"files/{filename}"))
            new_record.files.append(file)
        self.session.add(new_record)
        repr = record.get("id") or record.get("title")
        try:
            # Extract references from templates in the record metadata
            references = self.reference_manager.extract_references(record)
            logger.debug(
                "Extracted %d references from record %s", len(references), repr
            )

            # First commit the record to get a valid ID
            self.session.commit()

            # Now store the references
            if references:
                self.reference_manager.store_references(record.get("id"), references)

        except Exception as e:
            self.session.rollback()
            logger.debug("Record %s was rejected by database. %s", repr, e)
            raise DatabaseResourceNotModified(
                f"Record {repr} was rejected by database."
            ) from e

    def get_record(self, id: str, resolve_refs: bool = False) -> Record | None:
        """Get a record by ID, optionally resolving references."""
        rec = self.session.get(Record, id)

        if rec and resolve_refs:
            return self.reference_manager.resolve_references(rec)

        return rec

    def update_record(self, record: Record, data: dict):
        logger.debug("Updating record %s", record.id)
        if not self.database_exists():
            raise DatabaseNotFound("Database not found. Aborting record update.")

        if record.published:
            raise DatabaseResourceNotModified(
                f"Record {record.id} is already published, can't be updated."
            )

        input_metadata = data["input_metadata"]
        logger.debug(input_metadata)
        record.input_metadata = input_metadata
        record.status = RecordStatus.TODO

        try:
            # Extract references from templates in the updated record metadata
            references = self.reference_manager.extract_references(data)
            logger.debug(
                "Extracted %d references from updated record %s",
                len(references),
                record.id,
            )

            # Commit the record changes first
            self.session.commit()

            # Now update the references
            if references:
                self.reference_manager.store_references(record.id, references)

        except Exception as e:
            self.session.rollback()
            logger.error("Failed to update record %s: %s", record.id, e)
            raise

        return record

    def get_unpublished_deposits(self, number=None):
        if not self.database_exists():
            raise DatabaseNotFound("Database not found. Aborting record fetching.")
        query = self.session.query(Record).filter(
            Record.status != RecordStatus.PUBLISHED
        )
        if number:
            query = query.limit(number)
        records = query.all()
        return records

    def get_failed_records(self, number=None):
        """Return failed records."""
        query = self.session.query(Record).filter(
            Record.status.in_(RecordStatus.failed_statuses)
        )
        if number:
            query = query.limit(number)
        return query

    def update_record_status(self, record: Record, status: RecordStatus):
        """Update record status."""
        logger.debug("Updating record %s status to %s", record.id, status)
        if not self.database_exists():
            raise DatabaseNotFound("Database not found. Aborting record update.")

        if record.published:
            raise DatabaseResourceNotModified(
                f"Record {record.id} is already published."
            )

        if status not in RecordStatus or not isinstance(status, RecordStatus):
            raise ValueError(f"Invalid status: {status}")

        record.status = status
        self.session.commit()
        return record

    def _record_to_dict(self, record, columns):
        return {c.key: getattr(record, c.key) for c in columns}

    def export(self, fields=None):
        """Export DB contents.

        Example:
        -------
        .. code-block:: python

                db.export(fields=[Record.upload_id, Record.input_metadata])
                # [{'upload_id': '123', 'input_metadata': {'title': 'test'}}]

        """
        if not fields:
            fields = [Record.upload_id, Record.input_metadata]
        q_res = self.session.query(*fields).all()
        return [self._record_to_dict(record, fields) for record in q_res]


# TODO FILE_FAILED: imagine I fix the file name, then how do I retrigger?
