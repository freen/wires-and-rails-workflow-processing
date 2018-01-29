#!/usr/bin/env python3

"""
1) Collect all segmented row subjects w/ source_subject_id in pages_raw_railroads set
2) Identify majority element for T0 for the source subject
3) Add segmented row subjects to the new target railroad subject, remove them from the old one
"""

import sys
sys.path.insert(0, "..")

import logging
import csv
import json
from panoptes_client import Classification, Panoptes, Subject

from lib import settings
from lib.logger import setup_logger
from lib.subject_set_csv import SubjectSetCSV
from lib.subject_set_workflow_router import SubjectSetWorkflowRouter
from lib.models.classifications import Classifications, SharedMajorityException
from lib.subject_set_workflow_router import SubjectSetWorkflowRouter, \
  UnidentifiedRawSubjectSetException

class MigrateRowsToAppropriateSubjectSet:

    def __init__(self, workflow_router, csv, dry_run):
        self._workflow_router = workflow_router
        self._subject_set_csv = csv
        self._dry_run = dry_run

    def _calculate_target_subject_sets_by_subject(self):
        subjects_and_their_target_sets = {}
        for _subject_set_id, metadata in settings.COLUMNS_WORKFLOW_METADATA.items():
            classification_kwargs = {
                'scope': 'project',
                'project_id': settings.PROJECT_ID,
                'workflow_id': metadata['workflow_id']
            }
            logger.debug("Loading classifications by params %s", str(classification_kwargs))
            classifications_records = [c for c in Classification.where(**classification_kwargs)]

            # Dirty, but this is a one-off fix
            subject_set_member_ids = self._subject_set_csv.subject_ids_by_subject_set_id() \
                [metadata['subject_set_id']]
            retirement_count = 3
            retired_subject_ids = Classifications(classifications_records, subject_set_member_ids) \
                .retired_subject_ids(metadata['task_id'], retirement_count)

            for subject_id in self._subject_set_csv.raw_pages_subject_ids():
                if subject_id not in retired_subject_ids:
                    continue
                try:
                    target_subject_set_id = workflow_router \
                        .target_subject_set_id(subject_id, classifications_records)
                except UnidentifiedRawSubjectSetException as ex:
                    logger.error(ex.args[0])
                    continue
                except SharedMajorityException as ex:
                    # TODO need add'l monitoring for this, e.g. manual report exception
                    logger.error(ex.args[0])
                    continue
                subjects_and_their_target_sets[subject_id] = target_subject_set_id
        return subjects_and_their_target_sets

    def run(self):
        """
        Migrate segmented railroad rows.
        """
        subjects_and_their_target_sets = self._calculate_target_subject_sets_by_subject()
        print(subjects_and_their_target_sets)

if __name__ == '__main__':
    dry_run = True
    logger = setup_logger(settings.APP_NAME, 'log/row_migrations.log', logging.DEBUG)
    subject_set_csv = SubjectSetCSV()
    workflow_router = SubjectSetWorkflowRouter(subject_set_csv, settings, logger)
    pages_raw_subject_ids = subject_set_csv.raw_pages_subject_ids()
    MigrateRowsToAppropriateSubjectSet(workflow_router, subject_set_csv, dry_run).run()
