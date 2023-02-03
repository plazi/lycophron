# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron logger class."""

# TODO load  configs from a higher level file.
# TODO logging is currently implemented without using a class-based approach.

from logging import Logger, INFO, WARNING

DEFAULT_LEVEL = INFO


class LycophronLogger(Logger):
    """Represents a lycophron specific logger.
    Adds configuration to the built-in logger."""

    level = DEFAULT_LEVEL
    name = "lycophron"

    def __init__(self, name, level) -> None:
        super().__init__(name, level)
