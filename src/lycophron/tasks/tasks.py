# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron tasks implementation."""

from celery import group, Task
from celery.contrib import rdb
import json
import time
import os

from . import app
from ..db import LycophronDB
from ..client import create_session
from ..models import RecordStatus

# TODO tasks are using 'db' directly. Breaks the basic flow Interface -> Business -> Data.
# TODO tasks do not have any logging implemented yet (e.g. success, errors).
# TODO record serialization to zenodo is done in place, should have its own module (e.g. marshmallow serializers)

# TODO db instantiation needed here to avoid a MemoryError
db_uri = "sqlite:///lycophron.db"
db = LycophronDB(uri=db_uri)

# TODO can be moved to configs
RATE_LIMIT = 10
SLEEP_TIME_SECONDS = 5


class SqlAlchemyTask(Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db.session.remove()


@app.task(base=SqlAlchemyTask)
def publish_records(url, token, num_records=None):
    records = db.get_unpublished_deposits(num_records)
    print(f"Found {len(records)} records to be published.")

    count = 0
    for record in records:
        process_record(record, token, url)
        upload_files(record, token)
        publish(record, token)
        count += 1
        if count % RATE_LIMIT == 0:
            print(f"Processed {count} records so far.")
            print(f"Sleeping {SLEEP_TIME_SECONDS} seconds.")
            time.sleep(SLEEP_TIME_SECONDS)


def process_record(record, token, url):
    """Create a new deposit."""
    print("----- processing one record")

    def _serialize_to_zenodo(record):
        # TODO implement a serializer to Zenodo
        data = record.original

        if record.doi:
            data["doi"] = record.doi

        serialized_communities = []
        if communities:
            for c in communities:
                serialized_communities.append({"identifier": c})
        data["communities"] = serialized_communities
        return data

    communities = record.communities

    if record.status not in (RecordStatus.DEPOSIT_FAIL, RecordStatus.NEW):
        print(
            f"Record {record.doi or record.id} status {record.status}: deposit not created."
        )
        return

    # Create deposit if needed, otherwise check files or publish
    session = create_session(token)
    r = session.post(url, json={})

    if r.status_code != 201:
        print(
            f"Request for record {record.doi or record.id} failed with status {r.status_code} and text: {r.text}"
        )
        record.status = RecordStatus.DEPOSIT_FAIL
        record.response = r.text
        db.update_record(record)
        return

    data = r.json()
    links = data["links"]
    update_url = links["self"]
    html_url = links["html"]

    # Add metadata to record
    serialized_record = _serialize_to_zenodo(record)

    update_res = session.put(update_url, json={"metadata": serialized_record})

    if update_res.status_code != 200:
        print(
            f"Update for record {record.doi or record.id} failed with text {update_res.text}"
        )
        record.status = RecordStatus.DEPOSIT_FAIL
        record.response = update_res.text
        db.update_record(record)
        return
    record.status = RecordStatus.DEPOSIT_SUCCESS
    record.deposit_id = data["id"]
    record.response = data
    record.links = links
    record.remote_metadata = update_res.json()["metadata"]
    db.update_record(record)

    print(f"Deposit created. Find it in : {html_url}")


def publish(record, token):
    def _publish_failed(record, text=None):
        record.status = RecordStatus.PUBLISH_FAIL
        if text:
            record.response = text
        db.update_record(record)
        return record

    def _publish_succeeded(record, new_data):
        record.remote_metadata = new_data
        record.status = RecordStatus.PUBLISH_SUCCESS
        db.update_record(record)
        return record

    publish_url = record.links.get("publish")

    if not publish_url:
        print(f"No publish url provided for record {record.doi or record.id}")
        return

    if record.status not in (
        RecordStatus.PUBLISH_FAIL,
        RecordStatus.FILE_SUCCESS,
        RecordStatus.DEPOSIT_SUCCESS,
    ):
        print(
            f"Record {record.doi or record.id} status {record.status}: record not published."
        )
        return

    session = create_session(token)
    r = session.post(publish_url)
    if r.status_code != 202:
        print(
            f"Publish for record {record.doi or record.id} failed with code {r.status_code} text {r.text}"
        )
        _publish_failed(record, r.text)
    else:
        data = r.json()
        html_url = data["links"]["record_html"]
        _publish_succeeded(record, data["metadata"])
        print(f"Record published. Find it in : {html_url}")


def upload_files(record, token):
    """Upload a file to a deposit."""

    def _upload_success(record):
        record.status = RecordStatus.FILE_SUCCESS
        db.update_record(record)
        return record

    def _upload_failed(record, text=None):
        record.status = RecordStatus.FILE_FAIL
        if text:
            record.response = text
        db.update_record(record)
        return record

    session = create_session(token)
    bucket_url = record.links.get("bucket")
    if not bucket_url:
        print(
            f"Record {record.doi or record.id} failed to upload files. No bucket url found."
        )
        return

    if record.status not in (
        RecordStatus.FILE_FAIL,
        RecordStatus.DEPOSIT_SUCCESS,
    ):
        print(
            f"Record {record.doi or record.id} status {record.status}: files can't be uploaded."
        )
        return

    for file in record.files:
        file_name = file["filename"]
        filepath = file["filepath"]
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

        if failed:
            _upload_failed(record)
        else:
            _upload_success(record)

        fp.close()
