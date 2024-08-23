# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron tasks implementation."""

from datetime import datetime, timedelta, timezone
from time import sleep

from inveniordm_py.files.metadata import FilesListMetadata, OutgoingStream
from inveniordm_py.records.metadata import DraftMetadata
from requests.exceptions import HTTPError

from ..logger import logger
from ..models import FileStatus, RecordStatus
from . import app


def state_transition(frm: FileStatus | list, to: FileStatus, err: FileStatus):
    """Update state of record based on event.

    If the event fails, the state is updated to `err`.

    Args:
    ----
        frm (RecordStatus | list): The current possible state(s) of the record.
        to (RecordStatus): The next state of the record.
        err (RecordStatus): The state to update to if the event fails.

    """

    def update_state(event):
        def wrapper(client, obj, *args, **kwargs):
            from lycophron.app import LycophronApp

            lapp = LycophronApp()
            if isinstance(frm, list):
                if obj.status not in frm:
                    return
            elif obj.status != frm:
                return
            raised = None
            try:
                event(client, obj, *args, **kwargs)
                obj.status = to
                obj.errors = None
            except Exception as e:
                obj.status = err
                raised = e
            lapp.project.db.session.commit()
            if raised:
                raise raised

        return wrapper

    return update_state


@state_transition(
    frm=RecordStatus.QUEUED,
    to=RecordStatus.DRAFT_CREATED,
    err=RecordStatus.DRAFT_FAILED,
)
def create_draft_record(client, record):
    draft = client.records.create()
    record.upload_id = draft.data["id"]
    record.response = draft.data
    return draft


@state_transition(
    frm=[
        RecordStatus.QUEUED,
        RecordStatus.DRAFT_CREATED,
        RecordStatus.METADATA_UPDATED,
        RecordStatus.FILE_UPLOADED,
    ],
    to=RecordStatus.METADATA_UPDATED,
    err=RecordStatus.METADATA_FAILED,
)
def update_draft_metadata(client, record, draft=None):
    if not draft:
        draft = client.records(record.upload_id).draft.get()
    res = draft.update(data=DraftMetadata(**record.input_metadata))
    record.response = res.data
    if getattr(res.data, "errors", None):
        raise Exception("Metadata update failed")


@state_transition(
    frm=RecordStatus.METADATA_UPDATED,
    to=RecordStatus.FILE_UPLOADED,
    err=RecordStatus.FILE_FAILED,
)
def upload_record_files(client, record, draft=None):
    def _sync_files(record, draft):
        for local_file in record.files:
            try:
                rem_file = draft.files(local_file.filename).get()
                rem_status = rem_file.data["status"]
                if rem_status == "completed":
                    local_file.status = FileStatus.UPLOADED
                elif rem_status == "pending":
                    local_file.status = FileStatus.TODO
                    rem_file.delete()
            except HTTPError as e:
                if e.response.status_code == 404:
                    local_file.status = FileStatus.TODO
            except Exception as e:
                logger.debug(f"Error getting remote file {local_file.filename}: {e}")
                raise e

    if not draft:
        draft = client.records(record.upload_id).draft.get()

    _sync_files(record, draft)
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


@state_transition(frm=FileStatus.TODO, to=FileStatus.UPLOADED, err=FileStatus.FAILED)
def upload_file(client, file, draft):
    logger.debug(f"Uploading file {file.filename}")
    file_data = FilesListMetadata(
        [{"key": file.filename}]
    )  # TODO Cannot use FileMetadata for somereason
    # TODO if the file already exists on remote, don't try to upload
    # TODO e.g. check checksum
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


@state_transition(
    frm=RecordStatus.FILE_UPLOADED,
    to=RecordStatus.PUBLISHED,
    err=RecordStatus.PUBLISH_FAILED,
)
def publish_record(client, record, draft=None):
    draft = draft or client.records(record.upload_id).draft
    res = draft.publish()
    record.response = res.data


@state_transition(
    frm=RecordStatus.PUBLISHED,
    to=RecordStatus.COMMUNITIES_ADDED,
    err=RecordStatus.COMMUNITIES_FAILED,
)
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
    logger.debug(f"Processing record {record_id}")
    while True:
        try:
            if db_record.upload_id:
                draft = client.records(db_record.upload_id).draft
            else:
                draft = create_draft_record(client, db_record)
            update_draft_metadata(client, db_record, draft=draft)
            upload_record_files(client, db_record, draft=draft)
            publish_record(client, db_record, draft=draft)
            # add_to_community(client, db_record)
        except HTTPError as e:
            logger.error(f"Error processing record {db_record.id}: {e}")
            if e.response.status_code == 429:
                sleep(60)
                continue
            else:
                db_record.response = e.response.json()
                lapp.project.db.session.commit()
        except Exception as e:
            logger.error(f"Error processing record {db_record.id}: {e}")
            db_record.error = str(e)
            lapp.project.db.session.commit()
            raise e
        break


@app.task
def record_dispatcher(num_records=10):
    from lycophron.app import LycophronApp

    lapp = LycophronApp()
    db = lapp.project.db
    records = db.get_unpublished_deposits(num_records)
    # TODO why we need this?
    retry_time = lapp.config.get("RETRY_IGNORE_TIME")
    # TODO For HTTP 500, maybe have max retries in a time frame
    # TODO METADATA_FAILED, FILES_FAILED, PUBLISH_FAILED
    for record in records:
        if record.status == RecordStatus.TODO:
            record.status = RecordStatus.QUEUED
            db.session.commit()
        elif record.failed:
            # When a record is failed, something has to be done first
            continue
        elif retry_time and (
            datetime.now(timezone.utc) - record.updated.replace(tzinfo=timezone.utc)
        ) > timedelta(seconds=retry_time):
            continue

        process_record.delay(record.id)
