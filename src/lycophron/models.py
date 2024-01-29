# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron data models."""

import enum
from sqlalchemy import Column, String, JSON, Enum, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils.models import Timestamp

Model = declarative_base()

class RecordStatus(str, enum.Enum):
    TODO = "TODO"
    QUEUED = "QUEUED"
    DRAFT_CREATED = "DRAFT_CREATED"
    METADATA_UPDATED = "METADATA_UPDATED"
    FILE_UPLOADED = "FILE_UPLOADED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    COMMUNITIES_ADDED = "COMMUNITIES_ADDED"

class Record(Model, Timestamp):
    """Local representation of a record."""

    __tablename__ = "record"

    id = Column(Integer, primary_key=True)

    upload_id = Column(String, default=None)
    # Already validated by marshmallow
    input_metadata = Column(JSON)

    communities = relationship("Community", backref="record")
    files = relationship("File", backref="record")

    # Represents the last known metadata's state on Zenodo
    remote_metadata = Column(JSON, default=None)

    # State
    status = Column(Enum(RecordStatus), default=RecordStatus.TODO)
    response = Column(JSON, default=None)  # TODO response, errors

class FileStatus(str, enum.Enum):
    TODO = "TODO"
    UPLOADED = "UPLOADED"

class File(Model, Timestamp):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String, ForeignKey("record.id"))
    filename = Column(String)
    status = Column(Enum(FileStatus), default=FileStatus.TODO)

class CommunityStatus(str, enum.Enum):
    TODO = "TODO"
    REQUEST_CREATED = "REQUEST_CREATED"

class Community(Model, Timestamp):
    __tablename__ = "community"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String, ForeignKey("record.id"))
    slug = Column(String)
    status = Column(Enum(CommunityStatus), default=CommunityStatus.TODO)
