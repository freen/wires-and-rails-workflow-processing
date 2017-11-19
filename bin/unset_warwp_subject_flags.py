#!/usr/bin/env python3

"""
Run for quick access to debug / run tests on the Panoptes API.
"""

import sys
sys.path.insert(0, "..")

from panoptes_client import Panoptes, Subject

from lib import settings

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

SUBJECT_IDS = ['5823821', '5823822']

for subject_id in SUBJECT_IDS:
    subject = Subject.find(subject_id)
    subject.metadata[settings.METADATA_KEY_ALREADY_PROCESSED] = False
    subject.save()