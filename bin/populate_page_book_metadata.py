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
from lib.subject_set_csv import SubjectSetCSV

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

class SubjectHydrator:

    BOOK_AND_PAGE_FIELDS = ['book', 'page']

    def __init__(self, csv):
        self._subject_set_csv = csv

    @classmethod
    def _hydrate_book_and_page(cls, row):
        subject = Subject.find(row['subject_id'])
        subject_model = SubjectModel(subject)
        subject.metadata['book'] = subject_model['book']
        subject.metadata['page'] = subject_model['page']
        for field in cls.BOOK_AND_PAGE_FIELDS:
            if subject.metadata[field] is None:
                raise ValueError("WARN: None '%s' for subject %d and filepath %s" % field,
                    subject.id, subject.metadata['filepath'])
        subject.save()

    @classmethod
    def _row_missing_book_and_page(cls, row):
        for field in cls.BOOK_AND_PAGE_FIELDS:
            if field in row['metadata'] and row['metadata'][field] is not None:
                return False
        return True

    @classmethod
    def _log_result(cls, skipped, filtered_subject_set_id, no_filename_ids):
        if len(skipped) > 0:
            msg = "INFO: Skipped %d subjects because one of target fields" % len(skipped)
            msg += " (%s) was already defined" % ", ".join(cls.BOOK_AND_PAGE_FIELDS)
            print(msg)
        print("INFO: Filtered %d rows w/ wrong subject set id; no-op" % filtered_subject_set_id)
        if len(no_filename_ids) > 0:
            print("INFO: Failed to identify file basname for %d rows: %s" % len(no_filename_ids),
                ", ".join(no_filename_ids))

    def run(self):
        filtered_subject_set_id = 0
        skipped = []
        rows_to_process = []
        no_filename_ids = []

        for row in self._subject_set_csv:
            if int(row['subject_set_id']) not in settings.SUBJECT_SET_IDS_PAGES_RAW:
                filtered_subject_set_id += 1
                continue
            row['metadata'] = json.loads(row['metadata'])
            if not SubjectHydrator._row_missing_book_and_page(row):
                skipped.append(row['subject_id'])
            else:
                rows_to_process.append(row)

        i = 0
        bar = progressbar.ProgressBar(max_value=len(rows_to_process))
        for row in rows_to_process:
            i += 1
            try:
                SubjectHydrator._hydrate_book_and_page(row)
            except ValueError:
                no_filename_ids.append(row['subject_id'])
            bar.update(i)

        SubjectHydrator._log_result(skipped, filtered_subject_set_id, no_filename_ids)

if __name__ == '__main__':
    subject_set_csv = SubjectSetCSV()
    subject_hydrater = SubjectHydrator(subject_set_csv.csv_reader)
    subject_hydrater.run()
