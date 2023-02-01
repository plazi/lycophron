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
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import logging

from .errors import DatabaseAlreadyExists
from .app import app

Model = declarative_base()
logger = logging.getLogger(__name__)


class LycophronDB(object):
    """Manages a lycophron DB."""

    def __init__(self, uri) -> None:
        self.engine = create_engine(uri)
        _session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(_session_factory)

    def init_db(self) -> None:
        """Initializes the lycophron database."""
        if self.database_exists():
            raise DatabaseAlreadyExists(
                "A database is already created."
            )
        create_database(self.engine.url)
        Model.metadata.create_all(self.engine)
        logger.info("Database created!")

    def recreate_db(self) -> None:
        """Drop and recreate database."""
        logger.warn("Recreating database. THIS WILL DESTROY THE CURRENT DATABASE, PROCEED WITH CAUTION.")
        drop_database(self.engine.url)
        create_database(self.engine.url)
        Model.metadata.create_all(self.engine)

    def database_exists(self) -> bool:
        """Check if database exists

        :return: True if exists, False otherwise
        :rtype: bool
        """
        return database_exists(self.engine.url)


db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
db = LycophronDB(uri=db_uri)
