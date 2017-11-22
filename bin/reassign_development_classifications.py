#!/usr/bin/env python3

"""
Run for quick access to debug / run tests on the Panoptes API.
"""

import sys
sys.path.insert(0, "..")

import pdb
from lib import settings
from panoptes_client import Panoptes, Classification

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

subject_ids = ['5823821', '5823822']

for subject_id in subject_ids:
    classifications = Classification.where(subject_id=subject_id)
    for classification in classifications:
        pdb.set_trace()
