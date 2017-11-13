#!/usr/bin/env python3

import sys
sys.path.insert(0, "..")

import pdb
import progressbar
from panoptes_client import Panoptes, SubjectSet

from lib import settings
from lib.models.subject import Subject

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

subject_set = SubjectSet.find(8339)

bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
i = 0
skipped = []
target_fields = ['book', 'page']
for subject in subject_set.subjects:

    # Skip already populated
    for field in target_fields:
        if field in subject.metadata and subject.metadata[field] is not None:
            skipped.append(subject.id)
            next

    # Populate
    subject_model = Subject(subject)
    subject.metadata['book'] = subject_model['book']
    subject.metadata['page'] = subject_model['page']
    for field in target_fields:
        if subject.metadata[field] is None:
            print("WARN: None '%s' for subject %d and filepath %s" % field, subject.id,
                subject.metadata['filepath'])

    subject.save()
    i += 1
    bar.update(i)

print("INFO: Skipped %d subjects because one of target fields (%s) was already defined: %s"
    % len(skipped), ", ".join(target_fields), ", ".join(skipped))
