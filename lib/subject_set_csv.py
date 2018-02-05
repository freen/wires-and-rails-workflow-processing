"""
We reduce unnecessary calls to the Panoptes API by using the project's base subject export CSV
to answer as many questions as possible, namely where the stable "pages_raw" subjects are
concerned. This CSV is exported from the project backend [1] and must be located in the
application's docker container at the path: settings.CACHE_FILE_SUBJECT_SET_CSV_FILEPATH

For more info, see discussion here: https://github.com/zooniverse/panoptes-python-client/issues/124

[1] https://www.zooniverse.org/lab/3370/data-exports
"""

import csv
import os.path
from collections import defaultdict
from lib import settings

class SubjectSetCSV:
    """
    Reduce unnecessary calls to the Panoptes API by using the project's base subject export
    CSV to answer as many questions as possible, namely where the stable "pages_raw" subjects
    are concerned.

    TODO singleton
    """

    def __init__(self):
        csv_filepath = settings.CACHE_FILE_SUBJECT_SET_CSV_FILEPATH
        if not os.path.isfile(csv_filepath):
            raise RuntimeError("Subject set CSV absent: %s" % csv_filepath)
        self._csv_file = open(csv_filepath, newline='')
        self.csv_reader = csv.DictReader(self._csv_file)

        self._raw_pages_subject_ids = None
        self._subject_ids_by_subject_set_id = None
        self._subject_set_ids_by_subject_id = None

    def _reset_csv_reader(self):
        self._csv_file.seek(0)
        next(self.csv_reader)

    def raw_pages_subject_ids(self):
        """
        Returns a set of subject ids of all raw pages, both Telegraph and Railroad.
        """
        if self._raw_pages_subject_ids is None:
            self._reset_csv_reader()
            ids = [int(row['subject_id']) for row in self.csv_reader \
                if int(row['subject_set_id']) in settings.SUBJECT_SET_IDS_PAGES_RAW]
            self._raw_pages_subject_ids = set(ids)
        return self._raw_pages_subject_ids

    def get_subject_set_id(self, subject_id):
        """
        Returns the subject set ID which corresponds to a subject which is only in one subject
        set, namely any raw page subject.
        """
        for subject_set_id, subject_set_children in self.subject_ids_by_subject_set_id().items():
            if int(subject_id) in subject_set_children:
                return subject_set_id
        return False

    def subject_ids_by_subject_set_id(self):
        """
        2D array grouping subject IDs into their respective subject set IDs.
        """
        if self._subject_ids_by_subject_set_id is None:
            self._reset_csv_reader()
            self._subject_ids_by_subject_set_id = defaultdict(set)
            for row in self.csv_reader:
                set_id = int(row['subject_set_id'])
                self._subject_ids_by_subject_set_id[set_id].add(int(row['subject_id']))
        return self._subject_ids_by_subject_set_id

    def subject_set_ids_by_subject_id(self):
        """
        2D array grouping subject set IDs into by the keys of their member subject IDs.
        """
        if self._subject_set_ids_by_subject_id is None:
            self._reset_csv_reader()
            self._subject_set_ids_by_subject_id = defaultdict(set)
            for row in self.csv_reader:
                subject_id = int(row['subject_id'])
                self._subject_set_ids_by_subject_id[subject_id].add(int(row['subject_set_id']))
        return self._subject_set_ids_by_subject_id
