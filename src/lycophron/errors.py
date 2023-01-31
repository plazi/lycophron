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

class DatabaseError(LycophronError):
    pass

class DatabaseAlreadyExists(DatabaseError):
    pass


class Logger(object):
    pass

class ErrorHandler(object):

    @classmethod
    def handle_error(error):
        logger = logging.getLogger(__name__)
        logger.error(error)