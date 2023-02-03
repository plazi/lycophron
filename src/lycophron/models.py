# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron data models."""

from sqlalchemy import Column, Integer, String, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.models import Timestamp

engine = create_engine("sqlite:///" + "data.db", echo=True)

session = sessionmaker()
session.configure(bind=engine)

Model = declarative_base()


class Record(Model, Timestamp):
    """Local representation of a record."""

    __tablename__ = "record"
    id = Column(String, primary_key=True)
    doi = Column(String)
    deposit_id = Column(String)
    # Represents the last known metadata's state on Zenodo
    remote_metadata = Column(JSON)
    response = Column(JSON)  # TODO response, errors
    # Already validated by marshmallow
    original = Column(JSON)
    files = Column(JSON)
    status = Column(String)

    def __repr__(self) -> str:
        return f"Record {self.doi}"
