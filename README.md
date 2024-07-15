# Lycophron

Lycophron is a CLI tool to support batch uploads of records to Zenodo.

The tool supports the upload through CSV files that describe each record to be uploaded.

## "The" Quickstart Guide

1. Installation

    Install from GitHub using `pip`:

    ```bash
    pip install --user "lycophron @ git+https://github.com/plazi/lycophron@main"
    ```

    Alternatively, use [pipx](https://pipx.pypa.io/):

    ```bash
    pipx install "lycophron @ git+https://github.com/plazi/lycophron@main"
    ```

2. Initalize a local project named "monkeys"

    ```bash
    lycophron init monkeys
    ```

    List the project contents:

    ```bash
    cd monkeys/

    tree
    .
    ├── lycophron.cfg
    ├── lycophron.db
    ├── files
    │   └── Adam_Hubert_1976.pdf
    └── dev_logs.log
    ```

    > You will be prompted to input the authentication token. You can leave it empty as this can be done afterward by directly editing the configuration file.

3. Configure the project (add or edit `TOKEN` and `ZENODO_URL`)

    ```bash
    cat lycophron.cfg

    # TOKEN = 'CHANGE_ME'
    # ZENODO_URL = 'https://zenodo.org/api'
    ```

4. Create a CSV file from a template

    Generate a template with all the fields:

    ```bash
    lycophron gen-template --filename output.csv --all
    ```

    Add custom fields (e.g. `dwc` and `ac`) to the template:

    ```bash
    lycophron gen-template --filename output.csv --custom "dwc,ac"
    ```

5. Fill in the metadata and load the file

    ```bash
    lycophron load --inputfile output.csv
    ```

6. Publish to Zenodo

    ```bash
    lycophron publish
    ```

## Getting started

- [Installation](#installation)
- [Commands](#commands)
- [Configuration](#configuration)
- [Metadata](#supported-metadata)
- [How to create a CSV](#how-to-create-a-csv)
- [Development](#development)
- [Known issues](#known-issues)

## Installation

**Requirements**

- Python v3.11+

Install from GitHub using `pip` or [`pipx`](https://pipx.pypa.io/):

```bash
pipx install "lycophron @ git+https://github.com/plazi/lycophron.git@v1.0.0
```

> [!NOTE]
> In the future Lycophron will be published on PyPI and just require `pip install lycophron`.

### Linux/macOS

> It is recommended to use a virtual environment to install and run the application.
>
> To create a virtual environment named `lycophron`, run the following command in your terminal:
>
> ```shell
> python3 -m venv lycophron
> source lycophron/bin/activate
> ```

To install the CLI tool for development, clone this repository and run:

```shell
# For local development
uv pip sync requirements-dev.txt
uv pip install -e .[dev]
```

## Commands

**init**

This command initializes the project, creates necessary configuration files, and sets up a local database.

`init [name]` : initialize the app with the given name
`init --token` : initialize the app with a token

>:warning: Adjust configurations in the generated files to meet specific upload requirements.

**validate**

This command validates the current project. I.e. it checks whether the application is properly configured, the directory structure is correct and the metadata is valid and ready to be loaded locally.

`validate --filename` : validate the project and the given file.

**gen-template**

This command generates a CSV file from the default template, containing all the required headers. The template can either be generated with all the fields or by explicitely adding custom fields on top of the required ones.

`gen-template --filename`       : creates the output file in the given path and name.
`gen-template --all`            : creates a template using all fields (required and custom fields).
`gen-template --custom "x,y,z"` : creates a template using the required fields plus the given custom fields.

**load**

This command loads records from a local file into the local Database, ensuring they are ready to upload to Zenodo.

`load --inputfile`: load records from a given file to a local DB

**publish**

Publishes the previously loaded records to Zenodo.

This command specifically targets records that are currently unpublished. Importantly, this operation is designed to be executed multiple times, allowing for a phased or incremental approach to publishing records as needed.

`publish`: publish records to Zenodo

## Configuration

| name       | description                                            |
| ---------- | ------------------------------------------------------ |
| TOKEN      | Token to authenticate with Zenodo                      |
| ZENODO_URL | URL where to publish records (e.g. https://zenodo.org/api/deposit/depositions) |

## Supported metadata

| name      |  cardinality     | data type               | description                                                           |
|-----------|-----------|-------------------------|-----------------------------------------------------------------------|
| description  |  1 | string   | record's description  |
| creators | 1-N | list of strings | - |
| title | 1 | string | - |
| keywords | 0-N | list of strings | - |
| access_right | 0-1 | string | - |
| upload_type | 0-1 | string | - |
| publication_type | 0-1 | string | - |
| publication_date | 0-1 | ISO8601-formatted date string | - |
| journal_title | 0-1 | string | - |
| journal_volume | 0-1 | string | - |
| journal_issue | 0-1 | string | - |
| journal_pages | 0-1 | string | - |
| communities | 0-N | list of strings | - |
| doi | 0-1 | string | - |
| files | 0-N | list of strings | name of the files to upload for the record |

## How to create a .csv

- Generate the template by running `lycophron gen-template` and fill in the metadata.
- File names must match the files under the directory `/files/`

> [!TIP]
> We also provide [a sample generated sheet import template](https://docs.google.com/spreadsheets/d/1TUyDT6yOypX2DBuM_PNUZucFTC93uFlEa7PoAMYvnDI/edit?gid=54078251#gid=54078251) with some pre-filled values.

> [!WARNING]
> When working with fields defined as a list in the CSV file, it is essential to separate each item with a new line ("\n"). This ensures proper formatting and accurate representation of the list structure in the CSV file, thus allowing Lycophron to parse the values correctly.

Example:

|title                                                                                                                        |description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |access_right|upload_type|communities |publication_type|publication_date|journal_title       |journal_volume|journal_issue|journal_pages|doi                       |creators.name                                                 |creators.affiliation                                                                                                |creators.orcid|keywords|files                |id         |dwc:eventID|related_identifiers.identifier                 |related_identifiers.relation |
|-----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|-----------|------------|----------------|----------------|--------------------|--------------|-------------|-------------|--------------------------|--------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|--------------|--------|---------------------|-----------|-----------|-----------------------------------------------|-----------------------------|
|LES NYCTERIDAE (CHIROPTERA) DU SÉNÉGAL: DISTRIBUTION, BIOMETRIE ET DIMORPHISME SEXUEL                                        |Cinq especes de Nycteridae sont preserves au Sénegal|open        |publication|bats_project|article         |1976-12-31      |Mammalia            |40            |4            |597-613      |10.1515/mamm.1976.40.4.597|Adam, F. Hubert, B.                                           |                                                                                                                    |              |        |Adam_Hubert_1976.pdf |specimen001|           |{doi:figure001} {doi:figure002} {doi:figure003}|Documents Documents Documents|
|New ecological data on the noctule bat (Nyctalus noctula Schreber, 1774) (Chiroptera, Vespertilionidae) in two towns of Spain|The  Iberian  Peninsula represents the South-western limit of distribution of thenoctule  bat  (<i>Nyctalus noctula</i>) in Europe. |open        |publication|bats_project|article         |1999-01-31      |Mammalia            |63            |3            |273-280      |10.1515/mamm.1999.63.3.273|Alcalde, J. T.                                                |Departamento de Zoología, Faculdad de Ciencias, Universidad de Navarra. Avda Irunlarrea s/n. 31080, Pamplona. Spain |              |        |Alcade_1999.pdf      |figure001  |           |{doi:speciment001}                             |isDocumentedBy               |
|ROOSTING, VOCALIZATIONS, AND FORAGING BY THE AFRICAN BAT, NYCTERIS THEBAICA                                                  |There is no abstract                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |open        |publication|bats_project|article         |1990-05-21      |Journal of Mammalogy|71            |2            |242-246      |10.2307/1382175           |Aldridge, H. D. J. N. Obrist, M. Merriam, H. G. Fenton, M. B. |                                                                                                                    |              |        |                     |           |           |                                               |                             |

## Known issues

- DOIs are generated on demand, existing or external DOIs are not accepted. [issue](https://github.com/plazi/lycophron/issues/19)
- Metadata is compliant with legacy Zenodo, not RDM
- Output is not clear for the user. E.g. user does not know what to run next, how to fix issues with the data, etc.
- `init` does not create the needed file structure, still requires manual intervention (e.g. creation of `./files/`)
- Linking between rows is not supported. E.g. row 1 references a record from row 2

## Development

### Dependency management

To manage Python dependencies, Lycophron uses [`uv`](https://github.com/astral-sh/uv).

#### Generate dependency files

> You should not need to do this. More often, you will want to just bump all dependencies to their latest versions. See [upgrading dependencies](#upgrade-all-dependencies)

```shell
# Generate requirements.txt
uv pip compile pyproject.toml > requirements.txt

# Generate requirements-dev.txt
uv pip compile pyproject.toml --extra tests > requirements-dev.txt
```

#### Add a new dependency

To add a new dependency, add it in the `dependencies` section of the `pyproject.toml` file. Add testing/development dependencies under `[project.optional-dependencies]` section's `tests` extra.

```shell
# Update the requirements.txt file
uv pip compile pyproject.toml --upgrade-package <new-package>

# Update the requirements-dev.txt file
uv pip compile pyproject.toml --extra tests --upgrade-package <new-package>
```

#### Upgrade all dependencies

To upgrade all dependencies in development, run the following command in your terminal:

```shell
uv pip compile pyproject.toml --extra tests --upgrade
```

and for production:

```shell
uv pip compile pyproject.toml --upgrade
```
