# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron tasks implementation."""

import traceback
from datetime import datetime
from time import sleep

from inveniordm_py.files.metadata import FilesListMetadata, OutgoingStream
from inveniordm_py.records.metadata import DraftMetadata
from requests.exceptions import HTTPError

from ..errors import ErrorHandler
from ..models import FileStatus, RecordStatus
from . import app


def state_transition(frm, to):
    def update_state(event):
        def wrapper(client, obj, *args, **kwargs):
            from lycophron.app import LycophronApp

            lapp = LycophronApp()
            if obj.status != frm:
                return
            event(client, obj, *args, **kwargs)
            obj.status = to
            lapp.project.db.session.commit()

        return wrapper

    return update_state


@state_transition(frm=RecordStatus.QUEUED, to=RecordStatus.DRAFT_CREATED)
def create_draft_record(client, record):
    draft = client.records.create()
    record.upload_id = draft.data["id"]
    return draft


@state_transition(frm=RecordStatus.DRAFT_CREATED, to=RecordStatus.METADATA_UPDATED)
def update_draft_metadata(client, record, draft=None):
    if not draft:
        draft = client.records(record.upload_id).draft.get()
    draft.update(data=DraftMetadata(**record.input_metadata))


@state_transition(frm=RecordStatus.METADATA_UPDATED, to=RecordStatus.FILE_UPLOADED)
def upload_record_files(client, record, draft=None):
    if not draft:
        draft = client.records(record.upload_id).draft.get()

    files = record.files
    for f in files:
        if f.status == FileStatus.UPLOADED:
            continue
        try:
            upload_file(client, f, draft)
        except HTTPError as e:
            if e.response.status_code == 400:
                if check_file_status(f.filename, draft) in [
                    "pending"
                ]:  # TODO Add status of error
                    draft.files(f.filename).delete()
                    upload_file(client, f, draft)  # TODO Configure number of retries
            else:
                raise e


@state_transition(frm=FileStatus.TODO, to=FileStatus.UPLOADED)
def upload_file(client, file, draft):
    file_data = FilesListMetadata(
        [{"key": file.filename}]
    )  # TODO Cannot use FileMetadata for somereason
    draft.files.create(file_data)
    stream = open(
        f"files/{file.filename}", "rb"
    )  # TODO Hardcoded path, should be configurable?
    draft.files(file.filename).set_contents(OutgoingStream(data=stream))
    draft.files(file.filename).commit()  # TODO Add retry on upload?


def check_file_status(filename, draft):
    # TODO Can be implemented as property in client
    f = draft.files(filename).get()
    return f.data["status"]


@state_transition(frm=RecordStatus.FILE_UPLOADED, to=RecordStatus.PUBLISHED)
def publish_record(client, record, draft=None):
    if not draft:
        client.records(record.upload_id).draft.publish()
        return
    draft.publish()


@state_transition(frm=RecordStatus.PUBLISHED, to=RecordStatus.COMMUNITIES_ADDED)
def add_to_community(client, record, published_record=None):
    # TODO Return if not to be added to Communities
    if not published_record:
        published_record = client.records(record.upload_id).get()
    # TODO implement add to community, and use Community Table


@app.task
def process_record(record_id):
    from lycophron.app import LycophronApp

    lapp = LycophronApp()
    db_record = lapp.project.db.get_record(record_id)
    client = lapp.client
    while True:
        try:
            draft = create_draft_record(client, db_record)
            update_draft_metadata(client, db_record, draft=draft)
            upload_record_files(client, db_record, draft=draft)
            publish_record(client, db_record, draft=draft)
            # add_to_community(client, db_record)
        except HTTPError as e:
            if e.response.status_code == 429:
                sleep(60)
                continue
            else:
                db_record.response = e.response.json()
                lapp.project.db.session.commit()
        except Exception as e:
            ErrorHandler.handle_error(e)
            db_record.error = "".join(traceback.format_tb(e.__traceback__))
            lapp.project.db.session.commit()
        break


@app.task
def record_dispatcher(num_records=10):
    from lycophron.app import LycophronApp

    lapp = LycophronApp()
    db = lapp.project.db
    records = db.get_unpublished_deposits(num_records)
    for record in records:
        if record.status == RecordStatus.TODO:
            record.status = RecordStatus.QUEUED
            db.session.commit()
        elif record.error:
            continue  # TODO Reporting error well (Awaiting fixes in client)
        elif record.response:
            continue  # TODO Manage 5xx/4xx
        elif (datetime.utcnow() - record.updated).seconds < 180:
            continue

        process_record.delay(record.id)
