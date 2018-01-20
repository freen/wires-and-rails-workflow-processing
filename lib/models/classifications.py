"""
Answers questions about a set of classifications.
"""

import logging
from panoptes_client import Workflow, Classification
from lib import settings

class Classifications:

    def __init__(self, classifications, subject_id_whitelist, logger=None):
        self._logger = logger
        # self._logger = logging.getLogger(settings.APP_NAME)
        self._annotations = self._annotations_by_task_and_subject(classifications,
                                                                  subject_id_whitelist)

    def _annotations_by_task_and_subject(self, classifications, subject_id_whitelist):
        """
        Result: self._annotations[task_id][subject_id] = annotation
        """
        annotations = {}
        skipped_subject_ids = []
        for classification in classifications:
            for subject_id in classification.raw['links']['subjects']:
                subject_id = int(subject_id)
                if subject_id not in subject_id_whitelist:
                    skipped_subject_ids.append(subject_id)
                    continue
                annotations = self._add_annotations(annotations, classification, subject_id)
        unique_skipped_subject_ids = set(skipped_subject_ids)
        if self._logger is not None:
            self._logger.debug("Skipped classifications recorded for %d subject IDs outside " \
                "pages_raw: %s", len(unique_skipped_subject_ids),
                ', '.join(unique_skipped_subject_ids))
        return annotations

    def _add_annotations(self, annotations, classification, subject_id):
        for annotation in classification.raw['annotations']:
            task_id = annotation['task']
            if task_id not in annotations:
                annotations[task_id] = {}
            if subject_id not in annotations[task_id]:
                annotations[task_id][subject_id] = []
            annotations[task_id][subject_id].append(annotation)
        return annotations
