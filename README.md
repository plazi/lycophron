# Lycophron

Lycophron is a CLI tool to support batch uploads of records to Zenodo.

The tool supports the upload through CSV files that describe each record to be uploaded.

## "The" Quickstart Guide

1. Install

    ```bash
    # (Optionally, create a virtual environment first)
    mkvirtualenv lycophron # with pyenv 
    python -m pip install -r requirements.txt
    ```

2. Create a folder for the project

    ```bash
    mkdir $HOME/monkeys
    cd $HOME/monkeys
    ```

3. Initalize a local project

    ```bash
    python -m lycophron init --force
    
    tree
    #|____lycophron.cfg
    #|____lycophron.db
    #|____files
    #| |____Adam_Hubert_1976.pdf
    #|____dev_logs.log
    ```

    > You will be prompted to input the authentication token. You can leave it empty as this can be done afterward by directly editing the configuration file.

4. Configure the project (add or edit `TOKEN` and `ZENODO_URL`)

    ```bash
    cat lycophron.cfg
    # TOKEN = 'CHANGE_ME'
    # ZENODO_URL = 'https://zenodo.org/api/deposit/depositions'
    ```

5. Create a CSV file and load it

    ```bash
    python -m lycophron load --inputfile data.csv
    ```

6. Publish to Zenodo

    ```bash
    python -m lycophron publish
    ```

## Getting started

- [Installation](#installation)
- [Commands](#commands)
- [Configuration](#configuration)
- [Metadata](#supported-metadata)
- [How to create a CSV](#how-to-create-a-csv)
- [Examples](#examples)
- [Development](#development)
- [Known issues](#known-issues)

## Installation

**Requirements**

- Python v3.9+

### Linux/macOS

> It is recommended to use a virtual environment to install and run the application.
>
> To create a virtual environment named `lycophron`, run the following command in your terminal:
>
> ```shell
> python3 -m venv lycophron
> source lycophron/bin/activate
> ```

To install the CLI tool just run:

```shell
# For using the tool
python -m pip install -r requirements.txt

# For local development
python -m pip install requirements-dev.txt
```

## Commands

**init**

This command initializes the project, creates necessary configuration files, and sets up a local database.

`init --token` : initialize the app with a token
`init --force` : initialize the app and wipe the local database

>:warning: Adjust configurations in the generated files to meet specific upload requirements.

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

- Get the template from [here](https://docs.google.com/spreadsheets/d/1JAxI4uBLS9lhhtP9iyhOQPOHsSMqywjCYfIcqUIMCKU/edit#gid=0) and fill in the metadata.
- File names must match the files under the directory `/files/`

> :warning:
When working with fields defined as a list in the CSV file, it is essential to separate each item with a new line ("\n"). This ensures proper formatting and accurate representation of the list structure in the CSV file, thus allowing lycophron to parse the values correctly.
  
Example:

|title                                                                                                                        |description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |access_right|upload_type|communities |publication_type|publication_date|journal_title       |journal_volume|journal_issue|journal_pages|doi                       |creators.name                                                 |creators.affiliation                                                                                                |creators.orcid|keywords|files                |id         |dwc:eventID|related_identifiers.identifier                 |related_identifiers.relation |
|-----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|-----------|------------|----------------|----------------|--------------------|--------------|-------------|-------------|--------------------------|--------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|--------------|--------|---------------------|-----------|-----------|-----------------------------------------------|-----------------------------|
|LES NYCTERIDAE (CHIROPTERA) DU SÉNÉGAL: DISTRIBUTION, BIOMETRIE ET DIMORPHISME SEXUEL                                        |Cinq especes de Nycteridae sont preserves au Sénegal|open        |publication|bats_project|article         |1976-12-31      |Mammalia            |40            |4            |597-613      |10.1515/mamm.1976.40.4.597|Adam, F. Hubert, B.                                           |                                                                                                                    |              |        |Adam_Hubert_1976.pdf |specimen001|           |{doi:figure001} {doi:figure002} {doi:figure003}|Documents Documents Documents|
|New ecological data on the noctule bat (Nyctalus noctula Schreber, 1774) (Chiroptera, Vespertilionidae) in two towns of Spain|The  Iberian  Peninsula represents the South-western limit of distribution of thenoctule  bat  (<i>Nyctalus noctula</i>) in Europe. |open        |publication|bats_project|article         |1999-01-31      |Mammalia            |63            |3            |273-280      |10.1515/mamm.1999.63.3.273|Alcalde, J. T.                                                |Departamento de Zoología, Faculdad de Ciencias, Universidad de Navarra. Avda Irunlarrea s/n. 31080, Pamplona. Spain |              |        |Alcade_1999.pdf      |figure001  |           |{doi:speciment001}                             |isDocumentedBy               |
|ROOSTING, VOCALIZATIONS, AND FORAGING BY THE AFRICAN BAT, NYCTERIS THEBAICA                                                  |There is no abstract                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |open        |publication|bats_project|article         |1990-05-21      |Journal of Mammalogy|71            |2            |242-246      |10.2307/1382175           |Aldridge, H. D. J. N. Obrist, M. Merriam, H. G. Fenton, M. B. |                                                                                                                    |              |        |                     |           |           |                                               |                             |

## Known issues

- Missing commands
  - `validate`
  - `gen-template`
- Rate limiting applied manually, could be using celery
- DOIs are generated on demand, existing or external DOIs are not accepted. [issue](https://github.com/plazi/lycophron/issues/19)
- Metadata is compliant with legacy Zenodo, not RDM
- Output is not clear for the user. E.g. user does not know what to run next, how to fix issues with the data, etc.
- `init` does not create the needed file structure, still requires manual intervention (e.g. creation of `./files/`)
- Linking between rows is not supported. E.g. row 1 references a record from row 2
- Does not use `invenio-client` yet
- To parse the original "excel" files, a small script was implemented to parse the file (under `./lycophron/src/transform_excel.py`)

## Development

### Dependency management

To manage Python dependencies, lycophron uses [`pip-tools`](https://github.com/jazzband/pip-tools).

#### Generate dependency files

> You should not need to do this. More often, you will want to just bump all dependencies to their latest versions. See [upgrading dependencies](#upgrade-a-dependency)

Two major files are used by `pip-tools`:

- `requirements.in`, used for production
- `requirements-dev.in`, used for development

The files are generated from scratch like so:

```shell
# Generate requirements.txt
pip-compile requirements.in

# Generate requirements-dev.txt
pip-compile requirements-dev.in
```

#### Add a new dependency

To add a new dependency, add it in the `dependencies` section of the `pyproject.toml` file. Add testing/development dependencies under `[project.optional-dependencies]` section's `tests` extra.

```shell
# Update the requirements.txt file
pip-compile requirements.in --upgrade-package <new-package>

# Update the requirements.dev.txt file
pip-compile requirements-dev.in --upgrade-package <new-package>
```

#### Upgrade all dependencies

To upgrade all dependencies in development, run the following command in your terminal:

```shell
pip-compile requirements-dev.in --upgrade
```

and for production:

```shell
pip-compile --upgrade
pip-compile requirements.in --upgrade
```
