#!/usr/bin/env python3

"""
Run for quick access to debug / run tests on the Panoptes API.
"""

import sys
sys.path.insert(0, "..")

import pdb
from panoptes_client import Panoptes, SubjectSet

from lib import settings

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

subject_set = SubjectSet.find(14804)

print(' '.join([s.id for s in subject_set.subjects]))
