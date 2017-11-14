#!/usr/bin/env python3

import sys
sys.path.insert(0, "..")

import csv
import json
import os.path
import pdb
import progressbar
from panoptes_client import Panoptes, Subject

from lib import settings
from lib.models.subject import Subject as SubjectModel

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

CACHE_FILE_SUBJECT_SET_CSV = os.path.abspath('../etc/wires-and-rails-subjects.csv')

class SubjectHydrator:

    PAGES_RAW_SUBJECT_SET_ID = 8339
    BOOK_AND_PAGE_FIELDS = ['book', 'page']

    def __init__(self, csv):
        self._subject_set_csv = csv

    @classmethod
    def _hydrate_book_and_page(cls, row):
        subject = Subject.find(row['subject_id'])
        # import pdb; pdb.set_trace()
        subject_model = SubjectModel(subject)
        subject.metadata['book'] = subject_model['book']
        subject.metadata['page'] = subject_model['page']
        for field in cls.BOOK_AND_PAGE_FIELDS:
            if subject.metadata[field] is None:
                print("WARN: None '%s' for subject %d and filepath %s" % field, subject.id,
                    subject.metadata['filepath'])
        subject.save()

    @classmethod
    def _row_missing_book_and_page(cls, row):
        for field in cls.BOOK_AND_PAGE_FIELDS:
            if field in row['metadata'] and row['metadata'][field] is not None:
                return False
        return True

    @classmethod
    def _log_result(cls, skipped, filtered_subject_set_id):
        print("INFO: Skipped %d subjects because one of target fields (%s) was already defined: %s"
            % len(skipped), ", ".join(cls.BOOK_AND_PAGE_FIELDS), ", ".join(skipped))
        print("INFO: Filtered %d rows w/ wrong subject set id; no-op" % filtered_subject_set_id)

    def run(self):
        filtered_subject_set_id = 0
        skipped = []
        rows_to_process = []

        for row in self._subject_set_csv:
            if self.PAGES_RAW_SUBJECT_SET_ID != int(row['subject_set_id']):
                filtered_subject_set_id += 1
                next
            row['metadata'] = json.loads(row['metadata'])
            if not SubjectHydrator._row_missing_book_and_page(row):
                skipped.append(row['subject_id'])
            else:
                rows_to_process.append(row)

        i = 0
        bar = progressbar.ProgressBar(max_value=len(rows_to_process))
        for row in rows_to_process:
            i += 1
            SubjectHydrator._hydrate_book_and_page(row)
            bar.update(i)

        SubjectHydrator._log_result(skipped, filtered_subject_set_id)

if __name__ == '__main__':
    if not os.path.isfile(CACHE_FILE_SUBJECT_SET_CSV):
        raise RuntimeError("Subject set CSV absent: %s" % CACHE_FILE_SUBJECT_SET_CSV)

    csv_file = open(CACHE_FILE_SUBJECT_SET_CSV, newline='')
    csv_reader = csv.DictReader(csv_file)

    subject_hydrater = SubjectHydrator(csv_reader)
    subject_hydrater.run()
