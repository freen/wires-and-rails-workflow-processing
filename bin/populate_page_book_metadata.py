#!/usr/bin/env python3

import sys
sys.path.insert(0, "..")

import pdb
from panoptes_client import Panoptes, SubjectSet

from lib import settings
from lib.models.subject import Subject

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

subject_set = SubjectSet.find(8339)

for subject in subject_set.subjects:
	subject_model = Subject(subject)
