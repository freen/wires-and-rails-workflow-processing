import csv
import os.path

from lib import settings

class SubjectSetCSV:

    def __init__(self):
        csv_filepath = settings.CACHE_FILE_SUBJECT_SET_CSV_FILEPATH
        if not os.path.isfile(csv_filepath):
            raise RuntimeError("Subject set CSV absent: %s" % csv_filepath)
        csv_file = open(csv_filepath, newline='')
        self.csv_reader = csv.DictReader(csv_file)

    def raw_pages_subject_ids(self):
        ids = [row['subject_id'] for row in self.csv_reader \
            if int(row['subject_set_id']) in settings.SUBJECT_SET_IDS_PAGES_RAW]
        return set(ids)
