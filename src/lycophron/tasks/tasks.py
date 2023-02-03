# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron tasks implementation."""

from celery import group
import os

from . import app
from ..db import db
from ..client import create_session

# TODO tasks are using 'db' directly. Breaks the basic flow Interface -> Business -> Data.
# TODO tasks do not have any logging implemented yet (e.g. success, errors).
# TODO tasks are not updating the record's local status (e.g. 'SUCCESS', 'FAILED', etc)


@app.task
def process_all_files():
    pass


@app.task
def create_deposit(files, metadata, token, url):
    """Create a new deposit."""
    # Create deposit
    session = create_session(token)
    r = session.post(url, json={})
    # db.update_record_status(doi, "DEPOSIT_CREATED")

    data = r.json()
    doi = data["metadata"]["prereserve_doi"]["doi"]
    update_url = data["links"]["self"]

    update_res = session.put(update_url, json={"metadata": metadata})

    bucket_url = data["links"]["bucket"]
    publish_url = data["links"]["publish"]

    all_res = group(
        upload_file.s(doi, file["filename"], bucket_url, file["filepath"], token)
        for file in files
    )

    all_res.link(publish.s(doi, publish_url, token))
    res = all_res()


@app.task
def publish(doi, publish_url, token):
    session = create_session(token)
    r = session.post(publish_url)
    # if r.status_code == 200:
    #     db.update_record_status(doi, "DEPOSIT_CREATED")


@app.task
def store_response(doi, response):
    """Publish the deposit."""
    db.update_record_response(doi, response)


@app.task
def upload_file(doi, file_name, bucket_url, filepath, token):
    """Upload a file to a deposit."""
    session = create_session(token)
    full_path = os.path.join(os.getcwd(), filepath)

    failed = False
    with open(full_path, "rb") as fp:
        r = session.put(
            "%s/%s" % (bucket_url, file_name),
            data=fp,
            params={},
            headers={"Content-Type": "application/octet-stream"},
        )
        if r.status_code != 200:
            failed = True
    # if failed:
    #     db.update_record_status(doi, "FILE_FAILED")
    # else:
    #     db.update_record_status(doi, "FILE_UPLOADED")

    fp.close()
