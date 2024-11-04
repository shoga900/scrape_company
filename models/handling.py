"""Making table for company information"""

import csv
import os
import pathlib

OUTPUT_CSV_FILE_PATH = 'company_information.csv'

class CsvModel(object):
    """Base csv model."""
    def __init__(self, csv_file):
        self.csv_file = csv_file
        if not os.path.exists(csv_file):
            pathlib.Path(csv_file).touch()

class CoordinatingModel(CsvModel):
    """Write company informaiton to CSV"""
    def __init__(self, csv_file=None, *args, **kwargs):
        if not csv_file:
            csv_file = self.get_csv_file_path()
        super().__init__(csv_file, *args, **kwargs)