# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Database manager for lycophron. Provides basic functionalities to create a database."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists, drop_database
from config import SQLALCHEMY_DATABASE_URI
from errors import DatabaseAlreadyExists

Model = declarative_base()


class LycophronDB(object):
    def __init__(self) -> None:
        self.engine = create_engine(SQLALCHEMY_DATABASE_URI)
        self.session = sessionmaker(bind=self.engine)

    def init_db(self) -> None:
        """Initializes the lycophron database."""
        if self.database_exists():
            raise DatabaseAlreadyExists("A database is already created with the given.")
        create_database(self.engine.url)
        Model.metadata.create_all(self.engine)

    def recreate_db(self) -> None:
        """Drop and recreate database."""
        drop_database(self.engine.url)
        create_database(self.engine.url)
        Model.metadata.create_all(self.engine)

    def database_exists(self) -> bool:
        return database_exists(self.engine.url)
