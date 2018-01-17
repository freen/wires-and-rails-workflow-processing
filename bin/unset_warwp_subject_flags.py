#!/usr/bin/env python3

"""
Un-flag arbitrary subjects as not processed, useful for debugging workflow processing.
"""

import sys
sys.path.insert(0, "..")

from panoptes_client import Panoptes, Subject

from lib import settings

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

# SUBJECT_IDS = ['5823821', '5823822']
# SUBJECT_IDS = ['14813279', '14813280', '14813281']
# SUBJECT_IDS = ['15327062','15327056','15327068','15327065']

# Telegraph tests -
SUBJECT_IDS = ['15327068', '15327065', '15327062', '15327059', '15327056'];

for subject_id in SUBJECT_IDS:
    subject = Subject.find(subject_id)
    subject.metadata[settings.METADATA_KEY_ALREADY_PROCESSED] = False
    subject.save()
