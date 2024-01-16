import csv
import json


def read_file():
    path = ""
    with open(path) as csvfile:
        yield from csv.DictReader(csvfile, delimiter=",", quotechar='"')


def serialize_record(record):
    def _serialize_keywords(keywords_list):
        output = ""

        for kw in keywords_list:
            if not kw:
                continue
            output += f"{kw}\n"
        return output

    def _get_keywords_list(data):
        keywords_list = []
        keyword_1 = row.get("Keyword 1", "")
        keyword_2 = row.get("Keyword 2", "")
        keyword_3 = row.get("Keyword 3", "")
        keyword_4 = row.get("Keyword 4", "")
        keyword_5 = row.get("Keyword 5", "")
        keyword_6 = row.get("Keyword 6", "")
        keyword_7 = row.get("Keyword 7", "")
        keyword_8 = row.get("Keyword 8", "")
        keyword_9 = row.get("Keyword 9", "")
        keyword_10 = row.get("Keyword 10", "")
        keyword_11 = row.get("Keyword 11", "")
        keyword_12 = row.get("Keyword 12", "")
        keyword_13 = row.get("Keyword 13", "")
        keyword_14 = row.get("Keyword 14", "")
        keyword_15 = row.get("Keyword 15", "")
        keyword_16 = row.get("Keyword 16", "")

        keywords_list = [
            keyword_1,
            keyword_2,
            keyword_3,
            keyword_4,
            keyword_5,
            keyword_6,
            keyword_7,
            keyword_8,
            keyword_9,
            keyword_10,
            keyword_11,
            keyword_12,
            keyword_13,
            keyword_14,
            keyword_15,
            keyword_16,
        ]

        return keywords_list

    def _serialize_creators(creators_list):
        names = ""
        affiliations = ""
        orcids = ""
        for creator in creators_list:
            name = creator[0].replace("\n", ", ")
            if "\n" in creator[0]:
                breakpoint()
            if not name:
                continue
            affiliation = creator[1].replace("\n", ", ")
            orcid = ""
            if len(creator) == 3:
                orcid = creator[2].replace("\n", ", ")
            names += f"{name}\n"
            affiliations += f"{affiliation}\n"
            orcids += f"{orcid}\n"
        breakpoint()
        return names, affiliations, orcids

    def _get_creators_list(data):
        creator1_name = row.get("creator1_name", "")
        creator1_affiliation = row.get("creator1_affiliation", "")
        creator1_orcid = row.get("creator1_orcid", "")
        creator2_name = row.get("creator2_name", "")
        creator2_affiliation = row.get("creator2_affiliation", "")
        creator2_orcid = row.get("creator2_orcid", "")
        creator3_name = row.get("creator3_name", "")
        creator3_affiliation = row.get("creator3_affiliation", "")
        creator3_orcid = row.get("creator3_orcid", "")
        creator4_name = row.get("creator4_name", "")
        creator4_affiliation = row.get("creator4_affiliation", "")
        creator4_orcid = row.get("creator4_orcid", "")
        creator5_name = row.get("creator5_name", "")
        creator5_affiliation = row.get("creator5_affiliation", "")
        creator5_orcid = row.get("creator5_orcid", "")
        creator6_name = row.get("creator6_name", "")
        creator6_affiliation = row.get("creator6_affiliation", "")
        creator6_orcid = row.get("creator6_orcid", "")
        creator7_name = row.get("creator7_name", "")
        creator7_affiliation = row.get("creator7_affiliation", "")
        creator7_orcid = row.get("creator7_orcid", "")
        creator8_name = row.get("creator8_name", "")
        creator8_affiliation = row.get("creator8_affiliation", "")
        creator8_orcid = row.get("creator8_orcid", "")
        creator9_name = row.get("creator9_name", "")
        creator9_affiliation = row.get("creator9_affiliation", "")
        creator9_orcid = row.get("creator9_orcid", "")
        creator10_name = row.get("creator10_name", "")
        creator10_affiliation = row.get("creator10_affiliation", "")
        creator10_orcid = row.get("creator10_orcid", "")
        creator11_name = row.get("creator11_name", "")
        creator11_affiliation = row.get("creator11_affiliation", "")
        creator11_orcid = row.get("creator11_orcid", "")
        creators_list = [
            (creator1_name, creator1_affiliation, creator1_orcid),
            (creator2_name, creator2_affiliation, creator2_orcid),
            (creator3_name, creator3_affiliation, creator3_orcid),
            (creator4_name, creator4_affiliation, creator4_orcid),
            (creator5_name, creator5_affiliation, creator5_orcid),
            (creator6_name, creator6_affiliation, creator6_orcid),
            (creator7_name, creator7_affiliation, creator7_orcid),
            (creator8_name, creator8_affiliation, creator8_orcid),
            (creator9_name, creator9_affiliation, creator9_orcid),
            (creator10_name, creator10_affiliation, creator10_orcid),
            (creator11_name, creator11_affiliation, creator11_orcid),
        ]
        return creators_list

    def _serialize_files(files):
        output = ""
        for file in files:
            output += f"{file}\n"
        return output

    _files = row["files"]  # TODO only reads one
    files = _serialize_files([_files])
    doi = row.get("doi", "")
    upload_type = row["upload_type"]
    title = row["title"]

    creators_list = _get_creators_list(row)
    creators_names, creators_affiliation, creators_orcid = _serialize_creators(
        creators_list
    )

    keywords_list = _get_keywords_list(row)
    keywords = _serialize_keywords(keywords_list)

    description = row.get("description")
    if not description:
        description = row.get("Abstract", "")
    access_right = row.get("access_right", "")
    communities = row.get("communities", [])
    if not communities:
        communities = communities.append(
            "coviho", "biosyslit", "globalbioticinteractions"
        )
    publication_type = row.get("publication_type", "")
    publication_date = row.get("publication_date", "")
    journal_title = row.get("journal_title", "")
    journal_volume = row.get("journal_volume", "")
    journal_issue = row.get("journal_issue", "")
    journal_pages = row.get("journal_pages", "")

    return {
        "title": title,
        "description": description,
        "access_right": access_right,
        "upload_type": upload_type,
        "communities": communities,
        "publication_type": publication_type,
        "publication_date": publication_date,
        "journal_title": journal_title,
        "journal_volume": journal_volume,
        "journal_issue": journal_issue,
        "journal_pages": journal_pages,
        "doi": doi,
        "creators.name": creators_names,
        "creators.affiliation": creators_affiliation,
        "creators.orcid": creators_orcid,
        "keywords": keywords,
        "files": files,
    }


def export_data(data):
    headers = [
        "title",
        "description",
        "access_right",
        "upload_type",
        "communities",
        "publication_type",
        "publication_date",
        "journal_title",
        "journal_volume",
        "journal_issue",
        "journal_pages",
        "doi",
        "creators.name",
        "creators.affiliation",
        "creators.orcid",
        "keywords",
        "files",
        "id",
    ]
    with open("transformed_data.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


def test_data(data, expected):
    pass


data = read_file()
records_list = []
for row in data:
    record = serialize_record(row)
    records_list.append(record)
export_data(records_list)
