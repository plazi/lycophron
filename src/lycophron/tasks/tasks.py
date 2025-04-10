#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron tasks implementation."""

from datetime import UTC, datetime, timedelta
from time import sleep

from inveniordm_py.files.metadata import FilesListMetadata, OutgoingStream
from inveniordm_py.records.metadata import DraftMetadata
from requests.exceptions import HTTPError

from ..logger import logger
from ..models import FileStatus, RecordStatus
from . import app

type Status = RecordStatus | FileStatus


def state_transition(frm: Status | list[Status], to: Status, err: Status):
    """Update state of record based on event."""

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
def update_draft_metadata(client, record: Record, draft: Draft | None = None):
    """Update draft metadata with resolved references."""
    from lycophron.app import LycophronApp

    lapp = LycophronApp()
    if not draft:
        draft = client.records(record.upload_id).draft.get()

    # Get the record with resolved references
    resolved_record = lapp.project.db.reference_manager.resolve_references(record)

    # Use the resolved metadata for the update
    res = draft.update(data=DraftMetadata(**resolved_record.input_metadata))
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
                logger.debug(f"Error getting remote file {local_file.filename=}: {e=}")
                raise

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
                raise


@state_transition(frm=FileStatus.TODO, to=FileStatus.UPLOADED, err=FileStatus.FAILED)
def upload_file(client, file: File, draft: Draft):
    logger.debug(f"Uploading file {file.filename=}")
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
    logger.debug(f"Processing record {record_id=}")
    if not db_record:
        logger.error(f"Record {record_id} not found in the database.")
        return

    # Process only draft creation in this phase
    # This allows all records to have pre-reserved DOIs before we update metadata
    # with cross-references
    if db_record.upload_id is None:
        while True:
            try:
                draft = create_draft_record(client, db_record)
                break
            except HTTPError as e:
                logger.error(f"Error creating draft for record {db_record.id=}: {e=}")
                if e.response.status_code == 429:
                    sleep(60)
                    continue
                else:
                    db_record.response = e.response.json()
                    lapp.project.db.session.commit()
                    return
            except Exception as e:
                logger.error(f"Error creating draft for record {db_record.id=}: {e=}")
                db_record.error = str(e)
                lapp.project.db.session.commit()
                raise

    # Continue with the rest of the processing
    while True:
        try:
            draft = client.records(db_record.upload_id).draft
            update_draft_metadata(client, db_record, draft=draft)
            upload_record_files(client, db_record, draft=draft)
            publish_record(client, db_record, draft=draft)
            # add_to_community(client, db_record)
        except HTTPError as e:
            logger.error(f"Error processing record {db_record.id=}: {e=}")
            if e.response.status_code == 429:
                sleep(60)
                continue
            else:
                db_record.response = e.response.json()
                lapp.project.db.session.commit()
        except Exception as e:
            logger.error(f"Error processing record {db_record.id=}: {e=}")
            db_record.error = str(e)
            lapp.project.db.session.commit()
            raise
        break


@app.task
def record_dispatcher(num_records=10):
    from lycophron.app import LycophronApp

    lapp = LycophronApp()
    db = lapp.project.db
    records = db.get_unpublished_deposits(num_records)
    # TODO why we need this?
    retry_time = lapp.config.get("RETRY_IGNORE_TIME")

    # Process records in two phases:
    # 1. First ensure all NEW records are queued for draft creation
    # 2. Then process all records that have drafts created for metadata updates
    todo_records = [r for r in records if r.status == RecordStatus.TODO]

    # Count records that need draft creation (new records)
    new_records = todo_records

    # Phase 1: Queue all new records for draft creation first
    for record in new_records:
        record.status = RecordStatus.QUEUED
        db.session.commit()
        process_record.delay(record.id)

    # If any new records are being processed, return and let them finish first
    # This ensures all records have DOIs before processing metadata with references
    if new_records:
        return

    # Phase 2: Process all records that already have drafts created
    for record in records:
        if record.failed:
            # When a record is failed, something has to be done first
            continue
        elif retry_time and (
            datetime.now(UTC) - record.updated.replace(tzinfo=UTC)
        ) > timedelta(seconds=retry_time):
            continue

        process_record.delay(record.id)
