import click

from lycophron.data import Data
from lycophron.project import Project


@click.group()
@click.version_option("1.0.0")
def main():
    """Lycophron tool"""
    pass


@main.command()
@click.argument("keyword")
def init(keyword):
    """Command to intialize the project"""

    project = Project(keyword)
    project.initialize()


@main.command()
@click.option("--inputfile", required=True)
def validate(inputfile):
    """Command to validate data"""

    data = Data(inputfile)
    data.validate()


@main.command()
@click.option("--inputfile", required=True)
@click.option("--update", required=False)
def load(inputfile):
    """Loads/Updates CSV into the local DB"""
    pass


@main.command()
def create():
    """Creates for each record in the DB a new deposit on Zenodo"""
    pass


@main.command()
@click.option("--outputfile", required=True)
def export(outputfile):
    """Exports all records from the DB to a CSV format"""
    pass


@main.command()
def upload_files():
    """Uploads created records files to their deposits"""
    pass


@main.command()
def publish():
    """Publishes all records to Zenodo"""
    pass


@main.command()
def update():
    """Edits and updates records on Zenodo"""
    pass
