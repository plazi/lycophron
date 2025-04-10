#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Defines lycophron errors and handler."""


class LycophronError(Exception):
    error_type: str
    hint: str
    message: str

    def __init__(self, *args, message=None, **kwargs):
        if message is None:
            message = self.message
        super().__init__(message, *args, **kwargs)


class ConfigError(LycophronError):
    error_type = "CONFIG"


class ConfigNotFound(ConfigError):
    hint = (
        "The configuration was deemed as required by the application. Try setting it "
        "in the configuration file."
    )

    def __init__(self, config_name, *args: object) -> None:
        super().__init__(*args)
        self.config_name = config_name

    def __repr__(self) -> str:
        return f"'{self.config_name}' was not found."


class InvalidConfig(ConfigError):
    def __init__(self, *, key, value):
        super().__init__(f"Invalid value '{value}' for config '{key}'")


class DatabaseError(LycophronError):
    error_type = "DATABASE"
    message = "Database error occurred."


class DatabaseAlreadyExists(DatabaseError):
    message = "A database is already created."


class DatabaseNotFound(DatabaseError):
    message = "Database not found. Aborting record add."


class DatabaseResourceNotModified(DatabaseError):
    message = "Datbase resource not modified."


class RecordError(LycophronError):
    error_type = "RECORD"
    message = "Record error occurred."


class InvalidDirectoryError(LycophronError):
    error_type = "DIRECTORY"
    hint = (
        "Create the appropriate directory structure. See documentation on how to do it."
    )

    def __init__(self, path):
        super().__init__(f"Directory {path} does not exist. Create it first.")


class RecordValidationError(RecordError):
    error_type = "DATA"
    message = "Record validation failed."
    hint = "Check the data structure. E.g. values have the correct format."


class InvalidRecordData(RecordError):
    error_type = "DATA"
    hint = "Check the data for, e.g. missing required fields like 'id', 'doi'."


class TemplateError(LycophronError):
    """Error raised when there is an issue with templates."""

    error_type = "TEMPLATE"
    hint = "Check the template syntax and structure."
