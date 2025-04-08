#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron logger class."""

import logging
import os
import sys

import colorlog

logger = logging.getLogger("lycophron")
logger.setLevel(logging.DEBUG)  # Set the logger to handle all levels of logging

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s : %(message)s",
    log_colors={
        "DEBUG": "white",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
    datefmt="%Y-%m-%d %H:%M:%S",
)
stdout_handler.setFormatter(stdout_formatter)

file_handler = logging.FileHandler(f"{os.getcwd()}/dev_logs.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s : %(message)s\n", "%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_formatter)

logger.addHandler(stdout_handler)
logger.addHandler(file_handler)
