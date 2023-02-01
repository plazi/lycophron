# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Defines lycophron errors and handler."""

import logging


class LycophronError(Exception):
    pass


class ConfigError(LycophronError):
    pass


class ConfigNotFound(ConfigError):
    def __init__(self, config_name, *args: object) -> None:
        super().__init__(*args)
        self.config_name = config_name


class DatabaseError(LycophronError):
    pass


class DatabaseAlreadyExists(DatabaseError):
    pass


class Logger(object):
    pass


class ErrorHandler(object):
    @staticmethod
    def handle_error(error):
        logger = logging.getLogger(__name__)
        if type(error) == list:
            for er in error:
                logger.error(er)

        if isinstance(error, Exception):
            logger.error(error)
