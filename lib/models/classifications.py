"""
Answers questions about a set of classifications.
"""

from collections import defaultdict

class Classifications:

    def __init__(self, classifications, subject_id_whitelist):
        self._annotations = self._annotations_by_task_and_subject(classifications,
                                                                  subject_id_whitelist)

    def retired_subject_ids(self, task_id, retirement_count):
        """
        Derive this value (not available in the API) by comparing classification counts to the
        configured subject retirement classification count.
        """
        return [id for id in self._annotations[task_id]
                if len(self._annotations[task_id][id]) >= retirement_count]

    def _annotations_by_task_and_subject(self, classifications, subject_id_whitelist):
        """
        Result: self._annotations[task_id][subject_id] = annotation
        """
        annotations = defaultdict(dict)
        skipped_subject_ids = []
        for classification in classifications:
            for subject_id in classification.raw['links']['subjects']:
                subject_id = int(subject_id)
                if subject_id not in subject_id_whitelist:
                    skipped_subject_ids.append(subject_id)
                    continue
                annotations = self._add_annotations(annotations, classification, subject_id)
        unique_skipped_subject_ids = set(skipped_subject_ids)
        return annotations

    def _add_annotations(self, annotations, classification, subject_id):
        for annotation in classification.raw['annotations']:
            task_id = annotation['task']
            if subject_id not in annotations[task_id]:
                annotations[task_id][subject_id] = []
            annotations[task_id][subject_id].append(annotation)
        return annotations
