# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron tasks entry point."""

from celery import Celery
from pathlib import Path


def init_celery_app():
    """Creates a celery app."""
    app = Celery("local")
    # paths for file backend, create folders
    _root = Path(__file__).parent / "worker"
    _folders = {
        "data_folder_in": _root / "messages",
        "data_folder_out": _root / "messages",
    }

    _backend_folder = _root / "results"
    _backend_folder.mkdir(exist_ok=True, parents=True)
    for fn in _folders.values():
        fn.mkdir(parents=True, exist_ok=True)

    app.conf.broker_url = "filesystem://"
    app.conf.broker_transport_options = _folders
    app.conf.task_serializer = "json"
    app.conf.accept_content = ["json"]
    app.conf.task_ignore_result = False
    app.conf.result_backend = f"file://{str(_backend_folder)}"

    return app


app = init_celery_app()

__all__ = ["app"]