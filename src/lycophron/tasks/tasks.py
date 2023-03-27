# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron tasks implementation."""

from celery import group, Task
import os

from . import app
from ..db import db
from ..client import create_session

# TODO tasks are using 'db' directly. Breaks the basic flow Interface -> Business -> Data.
# TODO tasks do not have any logging implemented yet (e.g. success, errors).
# TODO tasks are not updating the record's local status (e.g. 'SUCCESS', 'FAILED', etc)


class SqlAlchemyTask(Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db.session.remove()

@app.task(base=SqlAlchemyTask)
def create_deposit(record, files, metadata, token, url):
    """Create a new deposit."""
    doi = record.get("doi")
    record_id = record["id"]

    # Create deposit
    session = create_session(token)
    r = session.post(url, json={})

    # TODO uncomment when MemoryError is fixed
    # db.update_record_status(record_id, "DEPOSIT_CREATED")

    data = r.json()

    if doi:
        metadata["doi"] = doi
    
    update_url = data["links"]["self"]
    html_url = data["links"]["html"]

    update_res = session.put(update_url, json={"metadata": metadata})

    bucket_url = data["links"]["bucket"]
    publish_url = data["links"]["publish"]

    all_res = group(
        upload_file.s(doi, file["filename"], bucket_url, file["filepath"], token)
        for file in files
    )

    all_res.link(publish.s(doi, publish_url, token))
    res = all_res()

    # TODO uncomment when MemoryError is fixed
    # db.update_record_remote_metadata(record_id=record_id, metadata=data["metadata"])

    print(f"Deposit created. Find it in : {html_url}")


@app.task(base=SqlAlchemyTask)
def publish(doi, publish_url, token):
    session = create_session(token)
    r = session.post(publish_url)
    data = r.json()
    html_url = data["links"]["record_html"]
    print(f"Record published. Find it in : {html_url}")

    # TODO uncomment when MemoryError is fixed
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
    
    # TODO uncomment when MemoryError is fixed
    # if failed:
    #     db.update_record_status(doi, "FILE_FAILED")
    # else:
    #     db.update_record_status(doi, "FILE_UPLOADED")

    fp.close()
