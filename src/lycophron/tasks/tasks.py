# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron tasks implementation."""

from requests.exceptions import HTTPError
from time import sleep

from inveniordm_py.records.metadata import DraftMetadata
from inveniordm_py.files.metadata import FilesListMetadata, OutgoingStream
from inveniordm_py import InvenioAPI

from . import app
from ..db import LycophronDB
from ..models import RecordStatus, FileStatus

db_uri = "sqlite:///lycophron.db"
db = LycophronDB(uri=db_uri)

# class SqlAlchemyTask(celery.Task):
#     """An abstract Celery Task that ensures that the connection the the
#     database is closed on task completion"""

#     abstract = True

#     def after_return(self, status, retval, task_id, args, kwargs, einfo):
#         db.session.remove()

def state_transition(frm="", to=""):
    def update_state(event):
        def wrapper(client, obj, *args, **kwargs):
            if obj.status != frm: return
            event(client, obj, *args, **kwargs)
            obj.status = to
            db.session.commit()
        return wrapper
    return update_state

@state_transition(frm=RecordStatus.QUEUED, to=RecordStatus.DRAFT_CREATED)
def create_draft_record(client, record):
    draft = client.records.create()
    record.upload_id = draft.data['id']
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
                if check_file_status(f.filename, draft) in ["pending"]: # TODO Add status of error
                    draft.files(f.filename).delete()
                    upload_file(client, f, draft) # TODO Configure number of retries

@state_transition(frm=FileStatus.TODO, to=FileStatus.UPLOADED)
def upload_file(client, file, draft):
    file_data = FilesListMetadata([{"key": file.filename}]) # TODO Cannot use FileMetadata for somereason
    draft.files.create(file_data)
    stream = open(f"files/{file.filename}", "rb") # TODO Hardcoded path, should be configurable?
    draft.files(file.filename).set_contents(OutgoingStream(data=stream))
    draft.files(file.filename).commit() # TODO Add retry on upload?

def check_file_status(filename, draft):
    # TODO Can be implemented as property in client
    f = draft.files(filename).get()
    return f.data['status']

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
    db_record = db.get_record(record_id)
    while True:
        try:
            # TODO Get from config
            base_url = "https://127.0.0.1:5000/api"
            token = "ZxRS6YdOcSabhcwOG3a3PRLzsRZPUcN14w1ReiTisvLAtCKqhTghdmzFthvq"

            client = InvenioAPI(base_url=base_url, access_token=token)
            client.session.verify = False
            draft = create_draft_record(client, db_record)
            update_draft_metadata(client, db_record, draft=draft)
            upload_record_files(client, db_record, draft=draft)
            publish_record(client, db_record, draft=draft)
            # add_to_community(client, db_record)
            break
        except HTTPError as e:
            print(e)
            if e.response.status_code == 429:
                sleep(10)
                continue
            break
            # continue


def record_dispatcher():
    records = db.get_unpublished_deposits(10)
    for record in records:
        record.status = RecordStatus.QUEUED
        db.session.commit()
        process_record.apply_async(args=[record.id])
