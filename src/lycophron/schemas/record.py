# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Record schema."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, post_load

from ..logger import logger


def clean_empty(data):
    output = {}
    for key, value in data.items():
        if value:
            output[key] = value
    return output


class NewlineList(fields.Field):
    """Custom Marshmallow field to handle newline-separated lists."""

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return []
        return value.split("\n")


class Metadata(Schema):
    """Schema for handling metadata fields."""

    class Meta:
        unknown = EXCLUDE

    title = fields.String()
    publication_date = fields.String()
    description = fields.String()
    version = fields.String()
    publisher = fields.String()

    def load_related_identifiers(self, original):
        output = {"related_identifiers": []}

        # Split the values by '\n' and process each
        original_identifiers = original.get("related_identifiers.identifier", "")
        identifiers = original_identifiers.split("\n") if original_identifiers else []

        original_relation_types = original.get(
            "related_identifiers.relation_type.id", ""
        )
        relation_types = (
            original_relation_types.split("\n") if original_relation_types else []
        )

        original_resource_types = original.get(
            "related_identifiers.resource_type.id", ""
        )
        resource_types = (
            original_resource_types.split("\n") if original_resource_types else []
        )

        # Determine the number of related identifiers
        num_identifiers = max(
            len(identifiers), len(relation_types), len(resource_types)
        )

        for i in range(num_identifiers):
            related_identifier = {}

            identifier = identifiers[i].strip() if i < len(identifiers) else ""
            relation_type = relation_types[i].strip() if i < len(relation_types) else ""
            resource_type = resource_types[i].strip() if i < len(resource_types) else ""

            if not identifier:
                raise ValidationError("Missing 'identifier'.", "related_identifiers")
            if not relation_type:
                raise ValidationError("Missing 'relation_type'.", "related_identifiers")

            if identifier:
                related_identifier["identifier"] = identifier
            if relation_type:
                related_identifier["relation_type"] = {"id": relation_type}
            if resource_type:
                related_identifier["resource_type"] = {"id": resource_type}

            if related_identifier:
                output["related_identifiers"].append(related_identifier)

        return output

    def load_resource_type(self, original):
        resource_type_value = original.get("resource_type.id", "")
        if not resource_type_value:
            raise ValidationError("Missing 'resource_type' id.", "resource_type")
        return {"resource_type": {"id": resource_type_value}}

    def load_identifiers(self, original):
        output = {"identifiers": []}

        # Extract the identifiers from the original data
        identifiers_input = original.get("identifiers.identifier", "")

        # Split the identifiers by '\n' and process each
        for identifier in identifiers_input.split("\n"):
            if identifier.strip():  # Check if the identifier is not empty
                output["identifiers"].append({"identifier": identifier.strip()})

        return output

    def load_languages(self, original):
        output = {"languages": []}

        # Extract the languages from the original data
        languages_input = original.get("languages.id", "")

        # Split the languages by '\n' and process each
        for language in languages_input.split("\n"):
            if language.strip():  # Check if the language is not empty
                output["languages"].append({"id": language.strip()})

        return output

    def load_locations(self, original):
        output = {"locations": {"features": []}}

        # Split the values by '\n' and process each
        lats = original.get("locations.lat", "").split("\n")
        lons = original.get("locations.lon", "").split("\n")
        places = original.get("locations.place", "").split("\n")
        descriptions = original.get("locations.description", "").split("\n")

        # Determine the number of locations
        num_locations = max(len(lats), len(lons), len(places), len(descriptions))

        for i in range(num_locations):
            lat = lats[i].strip() if i < len(lats) else None
            lon = lons[i].strip() if i < len(lons) else None
            place = places[i].strip() if i < len(places) else None
            description = descriptions[i].strip() if i < len(descriptions) else None

            location = {}

            # Add "geometry" key only if both lat and lon are not None
            if lat and lon:
                location["geometry"] = {
                    "type": "Point",
                    "coordinates": [float(lon), float(lat)],
                }

            # Add "place" and "description" keys if they are not None
            if place:
                location["place"] = place
            if description:
                location["description"] = description
            if location:
                output["locations"]["features"].append(location)

        return output

    def load_references(self, original):
        output = {"references": []}

        # Extract the references from the original data
        references_input = original.get("references.reference", "")

        # Split the references by '\n' and process each
        for reference in references_input.split("\n"):
            if reference.strip():  # Check if the reference is not empty
                output["references"].append({"reference": reference.strip()})

        return output

    def load_subjects(self, original):
        output = {"subjects": []}

        # Extract the subjects from the original data
        subjects_input = original.get("subjects.subject", "")

        # Split the subjects by '\n' and process each
        for subject in subjects_input.split("\n"):
            if subject.strip():  # Check if the subject is not empty
                output["subjects"].append({"subject": subject.strip()})

        return output

    def load_rights(self, original):
        output = {"rights": []}
        rights_data = {k: v for k, v in original.items() if k.startswith("rights.")}

        # Initialize structures to hold rights data
        rights_ids = rights_data.get("rights.id", "").split("\n")
        rights_titles = rights_data.get("rights.title", "").split("\n")

        # Check the number of rights entries
        num_rights = max(len(rights_ids), len(rights_titles))
        for i in range(num_rights):
            right_entry = {}
            right_id = rights_ids[i] if i < len(rights_ids) else ""
            right_title = rights_titles[i] if i < len(rights_titles) else ""

            if right_id and right_title:
                raise ValidationError(
                    "Each right must have either an 'id' or a 'title', but not both",
                    "rights",
                )

            if right_id:
                right_entry["id"] = right_id
            elif right_title:
                right_entry["title"] = {"en": right_title}
            else:
                continue  # Skip empty entries

            output["rights"].append(right_entry)

        return output

    def load_additional_description(self, original):
        output = {"additional_descriptions": []}
        # Define a mapping for description types
        description_types = {
            "abstract.description": {"id": "abstract"},
            "method.description": {"id": "methods"},
            "notes.description": {"id": "notes"},
        }
        # Process only the relevant keys
        for key, full_value in original.items():
            if key in description_types.keys():
                # Split values by '\n' to handle multiple descriptions
                values = full_value.split("\n")
                for value in values:
                    if value.strip():  # Ensure the value is not empty
                        description_entry = {
                            "description": value,
                            "type": description_types[key],
                        }
                        output["additional_descriptions"].append(description_entry)

        return output

    def load_creatibutor(self, original, creatibutor_type):
        output = {creatibutor_type: []}
        people_input = {
            key: value
            for key, value in original.items()
            if key.startswith(f"{creatibutor_type}.")
        }
        # Determine the number of people
        num_people = max(len(value.split("\n")) for value in people_input.values())

        # Initialize a list of dictionaries for each person
        people = [{} for _ in range(num_people)]
        for key, value in people_input.items():
            parts = key.split(".")
            values = value.split("\n")

            for i in range(num_people):
                person = people[i]
                val = values[i] if i < len(values) else ""

                if not val:
                    continue
                if parts[1] in ["type", "given_name", "family_name", "name"]:
                    person[parts[1]] = val
                elif parts[1] in ["orcid", "gnd", "isni", "ror"]:
                    if "identifiers" not in person:
                        person["identifiers"] = []
                    person["identifiers"].append(
                        {"scheme": parts[1], "identifier": val}
                    )
                elif parts[1] == "affiliations":
                    if "affiliations" not in person:
                        person["affiliations"] = []
                    affiliation = {}
                    if parts[2] == "id":
                        affiliation["id"] = val
                    elif parts[2] == "name":
                        affiliation["name"] = val
                    person["affiliations"].append(affiliation)
                elif parts[1] == "role":
                    if parts[2] == "id":
                        person["role"] = dict(id=val)

        cleaned_people = [person for person in people if person]

        # Validate and add the processed people to the output
        for person in cleaned_people:
            affiliations = person.pop("affiliations", [])
            person_type = person.get("type")
            if person_type not in ["organizational", "personal"]:
                logger.debug(f"{original['id']} invalid type: {person_type}")
                raise ValidationError(
                    "Invalid type. Only 'organizational' and 'personal' are supported.",
                    creatibutor_type,
                )
            if person_type == "organizational" and "name" not in person:
                raise ValidationError(
                    "An organizational person must have 'name' filled in",
                    creatibutor_type,
                )
            elif person_type == "personal" and "family_name" not in person:
                raise ValidationError(
                    "A personal person must have 'family_name' filled in",
                    creatibutor_type,
                )

            output[creatibutor_type].append(
                {"person_or_org": person, "affiliations": affiliations}
            )
        return output

    @post_load(pass_original=True)
    def load_complex_fields(self, result, original, **kwargs):
        creators = self.load_creatibutor(original, "creators")
        contributors = self.load_creatibutor(original, "contributors")
        additional_descriptions = self.load_additional_description(original)
        rights = self.load_rights(original)
        subjects = self.load_subjects(original)
        languages = self.load_languages(original)
        identifiers = self.load_identifiers(original)
        resource_type = self.load_resource_type(original)
        related_identifiers = self.load_related_identifiers(original)
        references = self.load_references(original)
        locations = self.load_locations(original)

        result.update(creators)
        result.update(contributors)
        result.update(additional_descriptions)
        result.update(rights)
        result.update(subjects)
        result.update(languages)
        result.update(identifiers)
        result.update(resource_type)
        result.update(related_identifiers)
        result.update(references)
        result.update(locations)

        return result

    @post_load
    def clean(self, value, **kwargs):
        output = clean_empty(value)
        return output


class RecordRow(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String()
    default_community = fields.String()
    communities = NewlineList()
    files = NewlineList(data_key="filenames")

    def load_doi(self, original):
        doi_value = original.get("doi")
        if doi_value:
            return {"pids": {"doi": {"identifier": doi_value, "provider": "external"}}}
        return {}

    def load_custom_fields(self, original):
        output = dict()
        for key, value in self.context.get("BASE_CUSTOM_FIELD_PREFIXES").items():
            output[f"{key}:{value}"] = {}

        # Iterate over all items in the original data
        for key, value in original.items():
            # Split the key to get the prefix and the actual field name
            split_key = key.split(".") if "." in key else key.split(":")
            if len(split_key) != 2:
                ValidationError("")
                continue  # Skip keys that do not match the expected format

            prefix, field = split_key
            field_prefixes = {
                **self.context.get("BASE_CUSTOM_FIELD_PREFIXES"),
                **self.context.get("ADDITIONAL_CUSTOM_FIELD_PREFIXES"),
            }
            # Find the key in field_prefixes corresponding to the prefix
            key_of_prefix = next(
                (key for key, value in field_prefixes.items() if value == prefix), None
            )

            basic_field_definitions = self.context.get("BASE_CUSTOM_FIELD_DEFINITIONS")
            if key_of_prefix and field in basic_field_definitions.get(
                key_of_prefix, []
            ):
                prefix = f"{key_of_prefix}:{prefix}"
                if key_of_prefix in ["thesis"]:
                    output[prefix] = value
                else:
                    output[prefix][field] = value

            additional_field_definitions = self.context.get(
                "ADDITIONAL_CUSTOM_FIELD_DEFINITIONS"
            )
            if key_of_prefix and field in additional_field_definitions.get(
                key_of_prefix, []
            ):
                prefix = f"{prefix}:{field}"
                output[prefix] = value.split("\n")

        # Remove empty dictionaries
        output = {k: v for k, v in output.items() if v}

        return dict(custom_fields=output)

    def load_access(self, original):
        output = {"access": {}}

        # Extract access fields
        access_files = original.get("access.files", None)
        embargo_active = original.get("access.embargo.active", None)
        embargo_until = original.get("access.embargo.until", None)
        embargo_reason = original.get("access.embargo.reason", None)
        output["access"]["record"] = "public"
        output["access"]["files"] = "public"

        # Process and add to the output
        if access_files:
            output["access"]["files"] = access_files

        if embargo_active or embargo_until or embargo_reason:
            output["access"]["embargo"] = {
                "active": embargo_active,
                "until": embargo_until,
                "reason": embargo_reason,
            }

        return output

    @post_load(pass_original=True)
    def load_metadata(self, result, original, **kwargs):
        access = self.load_access(original)
        custom_fields = self.load_custom_fields(
            original,
        )
        doi = self.load_doi(original)
        metadata = Metadata().load(original)
        result.update(
            {"input_metadata": {"metadata": metadata, **doi, **access, **custom_fields}}
        )
        return result
