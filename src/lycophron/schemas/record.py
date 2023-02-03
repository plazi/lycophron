from idutils import is_orcid
import logging
from marshmallow import (
    Schema,
    fields,
    EXCLUDE,
    ValidationError,
    post_load,
    validates,
)
import re

from ..errors import RecordValidationError

orcid_regex = re.compile("([0-9]{4}-{1}){3}[0-9]{4}")
dev_logger = logging.getLogger('lycophron_dev')

class DelimiterField(Schema):
    # TODO move the deserialization part here
    pass

    def load(self, obj):
        breakpoint()
        pass


class Creator(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(data_key="creators.name")
    affiliation = fields.Method(data_key="creators.affiliation")
    orcid = fields.String(data_key="creators.orcid")

    def load(self, value):
        return super().load(value)

    @validates("orcid")
    def validate_orcid(self, value):
        if value != "" and not is_orcid(value):
            raise ValidationError(f"Invalid orcid provided : {value}")

    @post_load()
    def clean(self, value, **kwargs):
        output = clean_empty(value)
        return output


# TODO naming, move to isolated Field
def extract_data_from_object(key_name, object):
    # from itertools import zip_longest
    # parsed = [zip_longest(k, v.splitlines()) for k, v in object.items() if k.startswith(key_name)]
    output = []
    for k, v in object.items():
        if not k.startswith(key_name):
            continue
        values = v.splitlines()
        idx = 0
        for val in values:
            curr = {k: val}
            if idx >= len(output):
                output.append(curr)
            else:
                output[idx].update(curr)
            idx += 1
    return output


def clean_empty(data):
    output = {}
    for key, value in data.items():
        if value:
            output[key] = value
    return output


class Metadata(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.String()
    description = fields.String()
    keywords = fields.Method(deserialize="load_keywords")
    access_right = fields.String()
    upload_type = fields.String()
    publication_type = fields.String()
    publication_date = fields.Date()
    journal_title = fields.String()
    journal_volume = fields.String()
    journal_issue = fields.String()
    journal_pages = fields.String()

    @post_load(pass_original=True)
    def load_creators(self, result, original, **kwargs):
        # creator_keys = [k for k in original.keys() if k.startswith("creators.")]
        # parsed = list([(k, v) for k, v in original.items() if k.startswith("creators.")])
        # TODO with zip of uneven lengths (Might happen when \n\n), use zip_longest  and fill
        # TODO rest with "None"
        output = extract_data_from_object("creators.", original)

        creators = Creator(many=True).load(output)
        result.update({"creators": creators})
        return result

    def load_keywords(self, value):
        split = value.splitlines()
        return [v.strip() for v in split]

    @post_load
    def clean(self, value, **kwargs):
        output = clean_empty(value)
        return output


class RecordRow(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=True)
    doi = fields.String()
    deposit_id = fields.String()
    files = fields.Method(deserialize="load_files")

    @post_load(pass_original=True)
    def load_metadata(self, result, original, **kwargs):
        metadata = Metadata().load(original)
        result.update(metadata)
        return result

    def load_files(self, value):
        return value.splitlines()

    def handle_error(self, error: ValidationError, data, **kwargs):
        dev_logger.error(error)
        record_id = data.get('doi', data.get('id'))
        raise RecordValidationError(f"'{record_id}' {error.messages}")


# load -> deserialize
# dump -> serialize
