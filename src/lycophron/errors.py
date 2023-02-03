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
    def __init__(self, config_name, *args: object) -> None:
        super().__init__(*args)
        self.config_name = config_name


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

class RecordValidationError(RecordError, ValidationError):
    error_type = "DATA"
    hint = "Check the data structure. E.g. values have the correct format."

class InvalidRecordData(RecordError):
    error_type = "DATA"
    hint = "Check the data for, e.g. missing required fields like 'id', 'doi'."

class ErrorHandler(object):
    @staticmethod
    def handle_error(error):
        if type(error) == list:
            for er in error:
                ErrorHandler.log_error(er)
        if isinstance(error, Exception):
            ErrorHandler.log_error(error)

    def log_error(error):
        if isinstance(error, LycophronError):
            logger = logging.getLogger('lycophron')
        else:
            logger = logging.getLogger('lycophron_dev')
        logger.error(serialize(error))

def serialize(error: Exception) -> str:
    if hasattr(error, 'error_type'):
        return f"{getattr(error, 'error_type')}: {error}"
    return str(error)
