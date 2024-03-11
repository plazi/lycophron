# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Defines lycophron errors and handler."""

import logging

from marshmallow import ValidationError


class LycophronError(Exception):
    pass


class ConfigError(LycophronError):
    error_type = "CONFIG"


class ConfigNotFound(ConfigError):
    hint = "The configuration was deemed as required by the application. Try setting it in the configuration file."

    def __init__(self, config_name, *args: object) -> None:
        super().__init__(*args)
        self.config_name = config_name

    def __repr__(self) -> str:
        return f"'{self.config_name}' was not found."


class InvalidConfig(ConfigError):
    pass


class DatabaseError(LycophronError):
    pass


class DatabaseAlreadyExists(DatabaseError):
    pass


class DatabaseNotFound(DatabaseError):
    pass


class DatabaseResourceNotModified(DatabaseError):
    error_type = "DATABASE"


class Logger(object):
    pass


class RecordError(LycophronError):
    error_type = "RECORD"


class InvalidDirectoryError(LycophronError):
    error_type = "DIRECTORY"
    hint = (
        "Create the appropriate directory structure. See documentation on how to do it."
    )


class RecordValidationError(RecordError, ValidationError):
    error_type = "DATA"
    hint = "Check the data structure. E.g. values have the correct format."


class InvalidRecordData(RecordError):
    error_type = "DATA"
    hint = "Check the data for, e.g. missing required fields like 'id', 'doi'."


class ErrorHandler(object):
    @staticmethod
    def handle_error(error):
        if not error:
            return
        if isinstance(error, list):
            for er in error:
                ErrorHandler.log_error(er)
            raise error[0]
        if isinstance(error, Exception):
            ErrorHandler.log_error(error)
            raise error

    @staticmethod
    def log_error(error):
        if isinstance(error, LycophronError):
            logger = logging.getLogger("lycophron")
        else:
            logger = logging.getLogger("lycophron_dev")
        logger.error(serialize(error))


def serialize(error: Exception) -> str:
    msg = error.__repr__()
    er_type = getattr(error, "error_type", "")
    msg = f"[{er_type}] {msg}"
    if hasattr(error, "hint"):
        msg = f"{msg}\nHint: {getattr(error, 'hint')}"
    return msg
