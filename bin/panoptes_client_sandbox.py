#!/usr/bin/env python3

"""
Run for quick access to debug / run tests on the Panoptes API.
"""

import sys
sys.path.insert(0, "..")

import pdb
from lib import settings
from panoptes_client import Panoptes

Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

pdb.set_trace()
