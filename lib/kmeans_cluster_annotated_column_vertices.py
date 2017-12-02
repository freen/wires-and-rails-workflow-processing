"""
Connects to Panoptes API, fetchs classifications from the Railroad_Mark_Image_Type workflow,
and finds the vertex centroids per subject using k-means clustering.
"""

import logging
from panoptes_client import Workflow, Classification
from numpy import array, median, std
from scipy.cluster.vq import kmeans, whiten

from . import settings
from .subject_set_csv import SubjectSetCSV

class KmeansClusterAnnotatedColumnVertices:
    """
    Connects to Panoptes API, fetchs classifications from the Railroad_Mark_Image_Type workflow,
    and finds the vertex centroids per subject using k-means clustering.
    """

    def __init__(self, project_metadata):
        self._project_metadata = project_metadata
        self._logger = logging.getLogger(settings.APP_NAME)
        self._hydrated = False

        # Populated by _load_data()
        self._annotations_by_task_and_subject = {}
        self._classifications = []
        self._workflow = None

        # Populated by processAndCropCompletedSubjects()
        self._column_annotations_by_subject = {}
        self._vertex_centroids_by_subject = {}

        subject_set_csv = SubjectSetCSV()
        self._pages_raw_subject_ids = subject_set_csv.raw_pages_subject_ids()

    def calculate_vertex_centroids(self):
        """
        Collect all column vertex classification annotations per subject and calculate vertex
        centroids using k-means clustering.
        """
        self._hydrate()
        self._normalize_column_set_annotations()
        self._calculate_kmeans_of_column_set_annotations()
        return self._vertex_centroids_by_subject

    def retired_subject_ids(self):
        """
        Derive this value (not available in the API) by comparing classification counts to the
        configured subject retirement classification count. Must call
        """
        self._hydrate()
        retirement_classification_count = self._workflow.retirement['options']['count']
        return [id for id in self._column_annotations_by_subject
                if len(self._column_annotations_by_subject[id]) >= retirement_classification_count]

    def _hydrate(self):
        if self._hydrated:
            return None
        self._fetch_classification_data()
        self._collect_column_set_annotations_by_subject()
        self._hydrated = True

    def _fetch_classification_data(self):
        """Fetches classification data from Panoptes API based on project_metadata criteria"""
        self._workflow = Workflow.find(self._project_metadata['workflow_id'])
        self._load_classification_data()
        self._structure_classification_data()

    # TODO pull retired subjects from the workflow which do not have the flag, and modify this query
    #      to pull classifications for those subjects
    def _load_classification_data(self):
        classification_kwargs = {
            'scope': 'project',
            'project_id': self._project_metadata['project_id'],
            'workflow_id': self._project_metadata['workflow_id']
        }
        self._logger.debug("Loading classifications by params %s", str(classification_kwargs))
        self._classifications = [c for c in Classification.where(**classification_kwargs)]

    def _structure_classification_data(self):
        """
        Resulting structure:

          self._annotations_by_task_and_subject[task_id][subject_id] = task_annotation

        """
        self._logger.debug("Structuring classifications")
        skipped_subject_ids = []
        for classification in self._classifications:
            for subject_id in classification.raw['links']['subjects']:
                if subject_id not in self._pages_raw_subject_ids:
                    skipped_subject_ids.append(subject_id)
                    continue
                for annotation in classification.raw['annotations']:
                    task_id = annotation['task']
                    if task_id not in self._annotations_by_task_and_subject:
                        self._annotations_by_task_and_subject[task_id] = {}
                    if subject_id not in self._annotations_by_task_and_subject[task_id]:
                        self._annotations_by_task_and_subject[task_id][subject_id] = []
                    self._annotations_by_task_and_subject[task_id][subject_id].append(annotation)
        unique_skipped_subject_ids = set(skipped_subject_ids)
        self._logger.debug("Skipped classifications recorded for %d subject IDs outside " \
            "pages_raw: %s", len(unique_skipped_subject_ids), ', '.join(unique_skipped_subject_ids))

    def _collect_column_set_annotations_by_subject(self):
        task_id = self._project_metadata['task_id']
        if not task_id in self._annotations_by_task_and_subject:
            return
        column_annotations = self._annotations_by_task_and_subject[task_id]
        for subject_id, annotations in column_annotations.items():
            if not subject_id in self._column_annotations_by_subject:
                self._column_annotations_by_subject[subject_id] = []
            for annotation in annotations:
                column_vertices = [line['x'] for line in annotation['value']]
                column_vertices.sort()
                self._column_annotations_by_subject[subject_id].append(column_vertices)

    def _normalize_column_set_annotations(self):
        """
        Strip out line sets which include column qties deviant from the average column qty for that
        subject. This works in our case because the quantity of columns on a subject is extremely
        clear and we simply want to exclude anomalous / erroneous entries, which should be very
        rare, so that they don't ruin our k means logic. e.g. for a set of classifications which
        include 5, 5, 5, 5, and 1 vertices respectively, prune the classification which includes
        only 1 vertex.
        """
        for subject_id, line_sets in self._column_annotations_by_subject.items():
            avg_column_qty = round(median([len(line_set) for line_set in line_sets]))
            normalized_set = [line_set for line_set in
                              self._column_annotations_by_subject[subject_id]
                              if len(line_set) == avg_column_qty]
            self._column_annotations_by_subject[subject_id] = normalized_set

    def _calculate_kmeans_of_column_set_annotations(self):
        for subject_id, line_sets in self._column_annotations_by_subject.items():
            features = array(line_sets)
            std_dev = std(features, axis=0)
            whitened = whiten(features)
            kmeans_codebook, _distortion = kmeans(whitened, 1)
            [dewhitened_kmeans] = kmeans_codebook * std_dev
            self._logger.debug('For subject %s, cluster centroids: %s', subject_id,
                               str(dewhitened_kmeans))
            self._vertex_centroids_by_subject[subject_id] = dewhitened_kmeans
