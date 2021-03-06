#!/usr/bin/env python3

import sys
sys.path.insert(0, "..")

import pdb
from panoptes_client import Panoptes, SubjectSet

from lib import settings

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

subject_set = SubjectSet.find(14804)

print(' '.join([s.id for s in subject_set.subjects]))
