#!/usr/bin/env python3

import sys
sys.path.insert(0, "..")

import csv
import json
import pdb
from collections import defaultdict
from panoptes_client import Panoptes, Subject
from tabulate import tabulate

from lib import settings
from lib.subject_set_csv import SubjectSetCSV

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

class SubjectSegmentationStatistics:

    def __init__(self, csv):
        self._subject_set_csv = csv
        self._stats = defaultdict(dict)


    def run(self):
        for row in self._subject_set_csv:
            row['metadata'] = json.loads(row['metadata'])
            self._process_row(row)

        tabular = []
        for subject_id, columns in self._stats.items():
            for column_index, quantity in columns.items():
                tabular.append([subject_id, column_index, quantity])

        print(tabulate(tabular))

    def _process_row(self, row):
        if not 'source_document_subject_id' in row['metadata']:
            return
        parent_subject_id = row['metadata']['source_document_subject_id']

        if not 'source_document_column_index' in row['metadata']:
            return
        column_index = row['metadata']['source_document_column_index']

        if not column_index in self._stats[parent_subject_id]:
            self._stats[parent_subject_id][column_index] = 0

        self._stats[parent_subject_id][column_index] += 1


if __name__ == '__main__':
    subject_set_csv = SubjectSetCSV()
    subject_segmentation_statistics = SubjectSegmentationStatistics(subject_set_csv.csv_reader)
    subject_segmentation_statistics.run()
