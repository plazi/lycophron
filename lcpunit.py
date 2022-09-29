class Paper():

    def __init__(self, data):
        """
        Initializes an instance of the object Paper().

        Uses a data dictyonary filled by reading the provided database with a format-specific function in lcpdata.py module, setting all parameters including Zenodo parameters that might be empty in the spreadsheet (the latter will be set to "").

        Parameters
        ----------
        arg1 : data dictyonary

        Returns
        -------
        Instance of Paper()

        Example
        -------
        Paper(lcpunit.get_data())

        """

        # Internal attributes of a given publication;
        self.internal_id = data["internal_id"]            #string
        self.path_to_pdf = data["path_to_pdf"]           #string
        self.pdf_status = data["pdf_status"]            #string


        # Zenodo Resources attributes. On v1, it's not expected to have any of these until pushing, and some only after publishing, the article on Zenodo. Later, we might use these to verify the data on the client-side database versus the data on Zenodo for a given already published submission, to see if there was updates that the client is unaware of.
        self.zenodo_id = data["zenodo_id"]            #integer
        self.zenodo_doi = data["zenodo_doi"]            #string
        self.zenodo_doi_url = data["zenodo_doi_url"]            #url/string
        self.zenodo_published = data["zenodo_published"]            #bool
        self.zenodo_created = data["zenodo_created"]            #timestamp/string
        self.zenodo_modified = data["zenodo_modified"]            #timestamp/string
        self.zenodo_owner = data["zenodo_owner"]            #integer
        self.zenodo_record_id = data["zenodo_record_id"]            #integer
        self.zenodo_record_url = data["zenodo_record_url"]            #url/string
        self.zenodo_status = data["zenodo_status"]            #string

        # Metadata attributes. On v1 they are from the provided spreadsheet, but in the future I'll cross-check with the Zenodo stored attributs for submissions that already exists (possibly an implementation for creating new versions of a Zenodo submission).
        self.doi = data["metadata"]["doi"]      #string
        self.zenodo_prereserved = data["metadata"]["zenodo_prereserve"]         #string
        self.upload_type = data["metadata"]["upload_type"]          #string
        #self.image_type = data["metadata"]["image_type"]
        self.publication_type = data["metadata"]["publication_type"]    #string
        self.publication_date = data["metadata"]["publication_date"]    #string
        self.title = data["metadata"]["title"]          #string
        self.creators = data["metadata"]["creators"]       #array of objects (dict?)
        self.description = data["metadata"]["description"]      #string
        self.access_right = data["metadata"]["access_right"]        #string
        self.license = data["metadata"]["license"]      #string
        self.keywords = data["metadata"]["keywords"]        #array of strings
        self.contributors = data["metadata"]["contributors"] #array of objects (dict?)
        self.communities = data["metadata"]["communities"] #array of objects (dict?)
        self.journal_title = data["metadata"]["journal_title"]      #string
        self.journal_volume = data["metadata"]["journal_volume"]      #string
        self.journal_issue = data["metadata"]["journal_issue"]      #string
        self.journal_pages = data["metadata"]["journal_pages"]      #string
        #self.partof_title = data["metadata"]["partof_title"]
        #self.conference_title = data["metadata"]["conference_title"]
        #self.conference_dates = data["metadata"]["conference_dates"]
        #self.conference_place = data["metadata"]["conference_place"]
        #self.conference_url = data["metadata"]["conference_url"]
        #self.conference_session = data["metadata"]["conference_session"]
        #self.conference_session_part = data["metadata"]["conference_session_part"]
        self.language = data["metadata"]["language"]      #string
        #self.notes = data["metadata"]["notes"]

    def zenodo_metadata(self):

        #For regular articles
        metadata_fields = ["upload_type", "publication_type", "publication_date", "title", "doi", "creators", "description", "access_right", "license", "keywords", "contributors", "communities", "journal_title", "journal_volume", "journal_issue", "journal_pages", "language", "notes"]

        #For conference papers
        #metadata_fields = ["upload_type", "publication_type", "publication_date", "title", "creators", "description", "access_right", "license", "keywords", "contributors", "communities", "partof_title", "conference_title", "conference_dates", "conference_place", "conference_url", "conference_session", "conference_session_part", "language", "notes"]

        #For images
        #metadata_fields = ["upload_type", "image_type", "publication_date", "title", "creators", "description", "access_right", "license", "keywords", "contributors", "communities"]

        dict = {}
        metadata_dict = {}

        for info in self.__dict__:
            if info in metadata_fields:

                if info == "journal_volume" or info == "journal_issue":
                    metadata_dict[info] = str(self.__dict__[info])

                else:
                    metadata_dict[info] = self.__dict__[info]

        dict["metadata"] = metadata_dict

        return dict
