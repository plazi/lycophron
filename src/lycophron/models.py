#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron data models."""

import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils.models import Timestamp

Model = declarative_base()


class classproperty:
    def __init__(self, func):
        self.fget = func

    def __get__(self, instance, owner):
        return self.fget(owner)


class RecordStatus(str, enum.Enum):
    TODO = "NEW"
    QUEUED = "QUEUED"
    DRAFT_CREATED = "DRAFT_CREATED"
    METADATA_UPDATED = "METADATA_UPDATED"
    FILE_UPLOADED = "FILE_UPLOADED"
    PUBLISHED = "PUBLISHED"

    # Failure states
    DRAFT_FAILED = "DRAFT_FAILED"
    METADATA_FAILED = "METADATA_FAILED"
    FILE_FAILED = "FILE_FAILED"
    PUBLISH_FAILED = "PUBLISH_FAILED"

    # Community states
    COMMUNITIES_FAILED = "COMMUNITY_FAILED"
    COMMUNITIES_ADDED = "COMMUNITIES_ADDED"

    def __repr__(self) -> str:
        return self.value

    @classproperty
    def failed_statuses(self):
        """Set of failed statuses."""
        return {
            RecordStatus.DRAFT_FAILED,
            RecordStatus.METADATA_FAILED,
            RecordStatus.FILE_FAILED,
            RecordStatus.PUBLISH_FAILED,
            RecordStatus.COMMUNITIES_FAILED,
        }


class Record(Model, Timestamp):
    """Local representation of a record."""

    __tablename__ = "record"

    id = Column(String, primary_key=True)

    upload_id = Column(String, default=None)
    # Already validated by marshmallow
    input_metadata = Column(JSON)

    communities = relationship("Community", backref="record")
    files = relationship("File", backref="record")

    # Reference relationships
    outgoing_references = relationship(
        "Reference", foreign_keys="Reference.source_record_id", backref="source_record"
    )
    incoming_references = relationship(
        "Reference", foreign_keys="Reference.target_record_id", backref="target_record"
    )

    # Represents the last known metadata's state on Zenodo
    remote_metadata = Column(JSON, default=None)

    # State
    status = Column(Enum(RecordStatus), default=RecordStatus.TODO)
    response = Column(JSON, default=None)  # TODO response, errors
    error = Column(String, default=None)

    @property
    def failed(self):
        """Check if the record is in a failed state."""
        return self.status in [
            RecordStatus.DRAFT_FAILED,
            RecordStatus.METADATA_FAILED,
            RecordStatus.FILE_FAILED,
            RecordStatus.PUBLISH_FAILED,
            RecordStatus.COMMUNITIES_FAILED,
        ]

    @property
    def published(self):
        """Check if the record is in a published state."""
        return self.status == RecordStatus.PUBLISHED


class FileStatus(str, enum.Enum):
    TODO = "TODO"
    UPLOADED = "UPLOADED"
    FAILED = "FAILED"


class File(Model, Timestamp):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String, ForeignKey("record.id"))
    filename = Column(String)
    status = Column(Enum(FileStatus), default=FileStatus.TODO)
    checksum = Column(String)

    UniqueConstraint(record_id, filename, name="unique_file_per_record")


class CommunityStatus(str, enum.Enum):
    TODO = "TODO"
    REQUEST_CREATED = "REQUEST_CREATED"


class Community(Model, Timestamp):
    __tablename__ = "community"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String, ForeignKey("record.id"))
    slug = Column(String)
    status = Column(Enum(CommunityStatus), default=CommunityStatus.TODO)


class Reference(Model, Timestamp):
    """Record reference that needs to be resolved during serialization."""

    __tablename__ = "reference"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_record_id = Column(String, ForeignKey("record.id"))
    target_record_id = Column(String, ForeignKey("record.id"))
    source_field = Column(String)
    target_field = Column(String)
    bidirectional = Column(Boolean, default=True)
