"""Common operations for processing a set of classifications records."""

from collections import defaultdict, Counter

class Classifications:
    """Common operations for processing a set of classifications records."""

    def __init__(self, classifications, subject_id_whitelist):
        self._annotations = self._annotations_by_task_and_subject(classifications,
                                                                  subject_id_whitelist)

    def majority_element(self, task_id, subject_id):
        """
        Given a task ID and a subject ID, return the majority annotation value. Raises ValueError if
        the majority is shared by more than one value.
        """
        if not subject_id in self._annotations[task_id]:
            raise KeyError('Task ID %s has no annotations for subject ID %d' % task_id, subject_id)
        counter = Counter(self._annotations[task_id][subject_id])
        if len(counter.most_common(2)) > 1:
            raise ValueError('Multiple majority elements')
        most_common = counter.most_common(1)
        majority_element, _qty = most_common[0]
        return majority_element

    def retired_subject_ids(self, task_id, retirement_count):
        """
        Derive this value (not available in the API) by comparing classification counts to the
        configured subject retirement classification count.
        """
        return [int(id) for id in self._annotations[task_id]
                if len(self._annotations[task_id][id]) >= retirement_count]

    def _annotations_by_task_and_subject(self, classifications, subject_id_whitelist):
        """Result: self._annotations[task_id][subject_id] = annotation"""
        annotations = defaultdict(dict)
        for classification in classifications:
            for subject_id in classification.raw['links']['subjects']:
                subject_id = int(subject_id)
                if subject_id not in subject_id_whitelist:
                    continue
                annotations = self._add_annotations(annotations, classification, subject_id)
        return annotations

    def _add_annotations(self, annotations, classification, subject_id):
        for annotation in classification.raw['annotations']:
            task_id = annotation['task']
            if subject_id not in annotations[task_id]:
                annotations[task_id][subject_id] = []
            annotations[task_id][subject_id].append(annotation['value'])
        return annotations
