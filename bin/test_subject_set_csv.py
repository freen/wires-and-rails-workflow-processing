#!/usr/bin/env python3

"""
Useful for synchronously debugging queue operations.
"""

from numpy import array

import sys
sys.path.insert(0, "..")

from lib.queue_operations import QueueOperations
from lib.subject_set_csv import SubjectSetCSV

subject_set_csv = SubjectSetCSV()
subject_set_csv.subject_ids_by_subject_set_id()
