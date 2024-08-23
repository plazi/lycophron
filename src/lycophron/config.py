# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Lycophron is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Lycophron config classes."""

import os
import types
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import urlparse

from .errors import ConfigNotFound, InvalidConfig
from .logger import logger


class Defaults:
    SQLALCHEMY_DATABASE_URI = "sqlite:///lycophron.db"
    ZENODO_URL = "https://127.0.0.1:5000/api"
    # API url for Zenodo, default is the local Zenodo instance

    TOKEN = "CHANGEME"
    # RECORD_BATCH_SIZE = 10

    LYCOPHRON_FIELDS = ["id", "filenames"]

    REQUIRED_FIELDS = [
        "title",
        "publication_date",
        "id",
        "filenames",
        "resource_type.id",
        "creators.type",
        "creators.given_name",
        "creators.family_name",
    ]

    # Base RDM fields
    RDM_FIELDS = [
        "resource_type.id",
        "creators.type",
        "creators.given_name",
        "creators.family_name",
        "creators.name",
        "creators.orcid",
        "creators.gnd",
        "creators.isni",
        "creators.ror",
        "creators.role.id",
        "creators.affiliations.id",
        "creators.affiliations.name",
        "title",
        "publication_date",
        # "additional_titles.title",
        # "additional_titles.type.id",
        # "additional_titles.lang.id",
        "description",
        "abstract.description",  # This is an additional_descriptions
        # "abstract.lang.id",
        "method.description",  # This is an additional_descriptions
        # "method.lang.id",
        "notes.description",  # This is an additional_descriptions
        # "notes.lang.id",
        # "other.description",  # This is an additional_descriptions
        # "other.lang.id",
        # "series-information.description",  # This is an additional_descriptions
        # "series-information.lang.id",
        # "table-of-contents.description",  # This is an additional_descriptions
        # "table-of-contents.lang.id",
        # "technical-info.description",  # This is an additional_descriptions
        # "technical-info.lang.id",
        "rights.id",
        "rights.title",
        # "rights.description",
        # "rights.link",
        "contributors.type",
        "contributors.given_name",
        "contributors.family_name",
        "contributors.name",
        "contributors.orcid",
        "contributors.gnd",
        "contributors.isni",
        "contributors.ror",
        "contributors.role.id",
        "contributors.affiliations.id",
        "contributors.affiliations.name",
        # "subjects.id",
        "subjects.subject",
        "languages.id",
        # "dates.date",
        # "dates.type.id",
        # "dates.description",
        "version",
        "publisher",
        "identifiers.identifier",
        # "identifiers.scheme",  # Auto guessed
        "related_identifiers.identifier",
        # "related_identifiers.scheme",  # Auto guessed
        "related_identifiers.relation_type.id",
        "related_identifiers.resource_type.id",
        # "funding.funder.id",
        # "funding.funder.name",
        # "funding.award.id",
        # "funding.award.title",
        # "funding.award.number",
        # "funding.award.identifiers.scheme",
        # "funding.award.identifiers.identifier",
        "references.reference",
        # "references.identifier",
        # "references.scheme",
        "default_community",
        "communities",
        "doi",
        "locations.lat",
        "locations.lon",
        "locations.place",
        "locations.description",
    ]

    ACCESS_FIELDS = [
        "access.files",
        "access.embargo.active",
        "access.embargo.until",
        "access.embargo.reason",
    ]

    # The base ones are the ones that will be formatted to field:field.value f.e. journal:journal.title
    BASE_CUSTOM_FIELD_PREFIXES = {
        "journal": "journal",
        "meeting": "meeting",
        "imprint": "imprint",
        "thesis": "university",
    }

    # This fields will be formatted to field.value f.e. dwc.class
    ADDITIONAL_CUSTOM_FIELD_PREFIXES = {
        "dwc": "dwc",
        "gbif-dwc": "gbif-dwc",
        "ac": "ac",
        "dc": "dc",
        "openbiodiv": "openbiodiv",
        "obo": "obo",
    }

    # Base field definitions
    BASE_CUSTOM_FIELD_DEFINITIONS = {
        "journal": ["title", "issue", "volume", "pages", "issn"],
        "meeting": [
            "acronym",
            "dates",
            "place",
            "session_part",
            "session",
            "title",
            "url",
        ],
        "imprint": ["title", "isbn", "pages", "place"],
        "thesis": ["thesis"],
    }

    # Additional field definitions
    ADDITIONAL_CUSTOM_FIELD_DEFINITIONS = {
        "dwc": [
            "basisOfRecord",
            "catalogNumber",
            "class",
            "collectionCode",
            "country",
            "county",
            "dateIdentified",
            "decimalLatitude",
            "decimalLongitude",
            "eventDate",
            "family",
            "genus",
            "identifiedBy",
            "individualCount",
            "institutionCode",
            "kingdom",
            "lifeStage",
            "locality",
            "materialSampleID",
            "namePublishedInID",
            "namePublishedInYear",
            "order",
            "otherCatalogNumbers",
            "phylum",
            "preparations",
            "recordedBy",
            "scientificName",
            "scientificNameAuthorship",
            "scientificNameID",
            "sex",
            "specificEpithet",
            "stateProvince",
            "taxonID",
            "taxonRank",
            "taxonomicStatus",
            "typeStatus",
            "verbatimElevation",
            "verbatimEventDate",
        ],
        "gbif-dwc": ["identifiedByID", "recordedByID"],
        "ac": [
            "associatedSpecimenReference",
            "captureDevice",
            "physicalSetting",
            "resourceCreationTechnique",
            "subjectOrientation",
            "subjectPart",
        ],
        "dc": ["creator", "rightsHolder"],
        "openbiodiv": ["TaxonomicConceptLabel"],
        "obo": ["RO_0002453"],
    }

    RETRY_IGNORE_TIME = 3600 * 24
    # Maximum time, in seconds, for a record to be processed before being ignored


required_configs = ["TOKEN", "SQLALCHEMY_DATABASE_URI", "ZENODO_URL"]


class Config(dict):
    def __init__(self, root_path, defaults: None) -> None:
        self.defaults = defaults
        self.root_path = root_path

    def __setitem__(self, __key, __value) -> None:
        if not str(__key).isupper():
            logger.warn(f"Key {__key} is not upper cased. Ignoring it.")
            return
        return super().__setitem__(__key, __value)

    @property
    def is_initialized(self):
        return self.cfgLoader.exists()

    @property
    def defaultsLoader(self):
        return DefaultsLoader(self.defaults)

    @property
    def cfgLoader(self):
        return CFGLoader(root_path=self.root_path)

    def recreate(self):
        """Recreate the config file."""
        if self.cfgLoader.exists():
            os.remove(self.cfgLoader.cfg_path)
        self.create()

    def load(self):
        for loader in [self.defaultsLoader, self.cfgLoader]:
            configs = loader.load()
            self.update(**configs)

    def create(self):
        if not self.cfgLoader.exists():
            self.cfgLoader.create()

    def validate(self):
        """Validate the config."""
        self._all_configs_required_set()
        self._is_zendodo_url_valid()

    def _all_configs_required_set(self):
        """Check if all required configs are set."""
        for conf in required_configs:
            if not self.get(conf):
                raise ConfigNotFound(conf)

    def _is_zendodo_url_valid(self):
        """Check if the URL is valid."""
        parsed_url = urlparse(self["ZENODO_URL"])
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise InvalidConfig(f"Invalid URL provided: {self['ZENODO_URL']}.")

    def update_config(self, value, persist=False):
        if not isinstance(value, dict):
            raise TypeError("Config must be a dictionary with pair key/value")
        super().update(value)
        if persist:
            self.cfgLoader.update(value)

    def is_config_persisted(self, key):
        upper_key = key.upper()
        return self.cfgLoader.key_exists_in_file(upper_key)


class ConfigLoader(ABC):
    def load_from_object(self, obj) -> dict:
        otp = {}
        for key in dir(obj):
            if key.isupper():
                otp[key] = getattr(obj, key)
        return otp

    @abstractmethod
    def load() -> dict:
        pass


class DefaultsLoader(ConfigLoader):
    def __init__(self, defaults=None) -> None:
        _defaults = defaults or {}
        self.defaults = _defaults

    def load(self) -> dict:
        dfs = self.load_from_object(Defaults)
        if self.defaults:
            dfs.update(self.defaults)
        return dfs


class CFGLoader(ConfigLoader):
    def __init__(self, root_path) -> None:
        self.file_name = "lycophron.cfg"
        self.cfg_path = os.path.join(root_path, self.file_name)

    def exists(self) -> bool:
        return os.path.exists(self.cfg_path)

    def deserialize(self, key, val):
        return f"{key.upper()} = '{val}'\n"

    def dump(self, dump_data) -> None:
        if not isinstance(dump_data, dict):
            raise TypeError("Dump data must be a dictionary")
        with open(self.cfg_path, "w") as fp:
            for key, value in dump_data.items():
                fp.write(self.deserialize(key, value))
            fp.close()

    def key_exists_in_file(self, key):
        file_contents = self.load()
        return key in file_contents.keys()

    def update(self, input_dict) -> bool:
        if not isinstance(input_dict, dict):
            raise TypeError("Config must be a dictionary with pair key/value")

        if not self.exists():
            return False

        file_contents = self.load()

        for key, value in input_dict.items():
            upper_key = str(key).upper()
            if self.key_exists_in_file(upper_key):
                logger.warn(
                    f"Config '{upper_key}' already exists in {self.file_name} file. Overriding."
                )
            file_contents[upper_key] = value
        self.dump(file_contents)
        return True

    def create(self) -> bool:
        if self.exists():
            return False

        Path(self.cfg_path).touch(mode=0o600)
        return True

    def load(self) -> dict:
        if not self.exists():
            return {}

        d = types.ModuleType("config")
        d.__file__ = self.cfg_path
        try:
            with open(self.cfg_path, mode="rb") as config_file:
                exec(compile(config_file.read(), self.cfg_path, "exec"), d.__dict__)
        except OSError as e:
            e.strerror = f"Unable to load configuration file ({e.strerror})"
            raise
        loaded_configs = self.load_from_object(d)
        return loaded_configs
