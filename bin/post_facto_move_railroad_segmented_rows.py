#!/usr/bin/env python3

"""
One-off script for adjusting position of previously routed segmented row subjects.

1) Collect all segmented row subjects w/ source_subject_id in pages_raw_railroads set
2) Identify majority element for T0 for the source subject
3) Add segmented row subjects to the new target railroad subject, remove them from the old one
"""

import sys
sys.path.insert(0, "..")

import logging
import csv
import json
from panoptes_client import Classification, Panoptes, Subject, SubjectSet
from collections import defaultdict
from lib import settings
from lib.logger import setup_logger
from lib.subject_set_csv import SubjectSetCSV
from lib.subject_set_workflow_router import SubjectSetWorkflowRouter
from lib.models.classifications import Classifications, SharedMajorityException
from lib.subject_set_workflow_router import SubjectSetWorkflowRouter, \
  UnidentifiedRawSubjectSetException

class MigrateRowsToAppropriateSubjectSet:

    def __init__(self, workflow_router, csv, logger, dry_run):
        self._workflow_router = workflow_router
        self._subject_set_csv = csv
        self._dry_run = dry_run
        self._logger = logger
        self._subject_sets = {}

    def _calculate_target_subject_sets_by_subject(self):
        subjects_and_their_target_sets = {}
        for _subject_set_id, metadata in settings.COLUMNS_WORKFLOW_METADATA.items():
            classification_kwargs = {
                'scope': 'project',
                'project_id': settings.PROJECT_ID,
                'workflow_id': metadata['workflow_id']
            }
            self._logger.debug("Loading classifications by params %s", str(classification_kwargs))
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
                    self._logger.error(ex.args[0])
                    continue
                except SharedMajorityException as ex:
                    # TODO need add'l monitoring for this, e.g. manual report exception
                    self._logger.error(ex.args[0])
                    continue
                subjects_and_their_target_sets[subject_id] = target_subject_set_id
        return subjects_and_their_target_sets

    def _get_subject_set(self, subject_set_id):
        if subject_set_id not in self._subject_sets:
            self._subject_sets[subject_set_id] = SubjectSet.find(subject_set_id)
        return self._subject_sets[subject_set_id]

    def _segmented_row_target_sets(self, subjects_and_their_target_sets):
        segmented_row_target_sets = {}
        self._subject_set_csv._reset_csv_reader()
        for row in self._subject_set_csv.csv_reader:
            subject_id = int(row['subject_id'])
            if subject_id in segmented_row_target_sets:
                continue
            row['metadata'] = json.loads(row['metadata'])
            if 'source_document_subject_id' not in row['metadata']:
                continue
            source_id = int(row['metadata']['source_document_subject_id'])
            # Expedient hack..one-off script
            if source_id == 14813279:
                continue
            target_subject_set_id = subjects_and_their_target_sets[source_id]
            segmented_row_target_sets[subject_id] = target_subject_set_id
            self._logger.debug('Moving segmented row %d to the parent\'s (%d) target: %d',
                               subject_id, source_id, target_subject_set_id)
        return segmented_row_target_sets

    def run(self):
        """
        Migrate segmented railroad rows.
        """
        subjects_and_their_target_sets = self._calculate_target_subject_sets_by_subject()
        segmented_rows_and_their_target_sets = self \
            ._segmented_row_target_sets(subjects_and_their_target_sets)
        additions_by_target_set = defaultdict(list)
        removals_by_target_set = defaultdict(list)

        for subject_id, target_subject_set_id in segmented_rows_and_their_target_sets.items():
            # target_subject_set = self._get_subject_set(target_subject_set_id)
            self._logger.debug('Saving segmented row %d to set: %s', subject_id,
                               target_subject_set_id)
            subject = Subject.find(subject_id)
            additions_by_target_set[target_subject_set_id].append(subject)

            for curr_subject_set in subject.links.subject_sets:
                removals_by_target_set[curr_subject_set.id].append(subject_id)

        # Remove to appropriate target sets
        for target_subject_set_id, new_subjects in additions_by_target_set.items():
            target_subject_set = self._get_subject_set(target_subject_set_id)
            target_subject_set.add(new_subjects)

if __name__ == '__main__':
    dry_run = True
    logger = setup_logger(settings.APP_NAME, 'log/row_migrations.log', logging.DEBUG)
    subject_set_csv = SubjectSetCSV()
    workflow_router = SubjectSetWorkflowRouter(subject_set_csv, settings, logger)
    pages_raw_subject_ids = subject_set_csv.raw_pages_subject_ids()
    MigrateRowsToAppropriateSubjectSet(workflow_router, subject_set_csv, logger, dry_run).run()
