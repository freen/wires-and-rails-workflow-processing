#!/usr/bin/env python3

import sys
sys.path.insert(0, "..")

import pdb
import progressbar
from panoptes_client import Panoptes, SubjectSet

from lib import settings
from lib.models.subject_model import SubjectModel

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

class SubjectHydrator:

    PAGES_RAW_SUBJECT_SET_ID = 8339

    def __init__(self, subject_set_id = PAGES_RAW_SUBJECT_SET_ID):
        self._subject_set = SubjectSet.find(subject_set_id)

    def _book_and_page(self, subject):
        target_fields = ['book', 'page']

        for field in target_fields:
            if field in subject.metadata and subject.metadata[field] is not None:
                return False

        subject_model = SubjectModel(subject)
        subject.metadata['book'] = subject_model['book']
        subject.metadata['page'] = subject_model['page']
        for field in target_fields:
            if subject.metadata[field] is None:
                print("WARN: None '%s' for subject %d and filepath %s" % field, subject.id,
                    subject.metadata['filepath'])

        return True

    def run(self):
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
        i = 0
        skipped = []
        for subject in self._subject_set.subjects:
            i += 1
            bar.update(i)

            if not self._book_and_page(subject):
                skipped.append(subject.id)
                next

            subject.save()

        print("INFO: Skipped %d subjects because one of target fields (%s) was already defined: %s"
            % len(skipped), ", ".join(target_fields), ", ".join(skipped))

if __name__ == '__main__':
    subject_hydrater = SubjectHydrator()
    subject_hydrater.run()
