from pprint import pprint

from frictionless import validate


class Data:
    def __init__(self, inputfile):
        self.file = inputfile

    def validate(self):
        """Generate a validation report on the inputted CSV file"""
        report = validate(self.file)
        pprint(report.flatten(["rowPosition", "fieldPosition", "code", "message"]))
