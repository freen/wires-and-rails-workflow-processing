"""
Connects to Panoptes API, fetchs classifications from the Railroad_Mark_Image_Type workflow,
and finds the vertex centroids per subject using k-means clustering.
"""

import logging
import settings
from panoptes_client import Workflow, Classification
from numpy import array, median, std
from scipy.cluster.vq import kmeans, whiten

class ClusterAnnotatedColumnVertices:
    """
    Connects to Panoptes API, fetchs classifications from the Railroad_Mark_Image_Type workflow,
    and finds the vertex centroids per subject using k-means clustering.
    """

    def __init__(self, project_metadata):
        self._project_metadata = project_metadata
        self._logger = logging.getLogger(settings.LOGGER_NAME)

        # Populated by _load_data()
        self._annotations_by_task_and_subject = {}
        self._classifications = []
        self._workflow = None

        # Populated by processAndCropCompletedSubjects()
        self._column_annotations_by_subject = {}
        self._vertex_centroids_by_subject = {}

    def _fetch_classification_data(self):
        """Fetches classification data from Panoptes API based on project_metadata criteria"""
        self._load_data()
        self._structure_classification_data()

    def _load_data(self):
        self._logger.debug("Loading workflow %s", str(self._project_metadata['workflow_id']))
        self._workflow = Workflow.find(self._project_metadata['workflow_id'])
        self._load_classification_data()

    # TODO only pull subjects which haven't been retired / completed
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
        for classification in self._classifications:
            for subject_id in classification.raw['links']['subjects']:
                for annotation in classification.raw['annotations']:
                    task_id = annotation['task']
                    if task_id not in self._annotations_by_task_and_subject:
                        self._annotations_by_task_and_subject[task_id] = {}
                    if subject_id not in self._annotations_by_task_and_subject[task_id]:
                        self._annotations_by_task_and_subject[task_id][subject_id] = []
                    self._annotations_by_task_and_subject[task_id][subject_id].append(annotation)

    def calculate_vertex_centroids(self):
        """
        Collect all column vertex classification annotations per subject and calculate vertex
        centroids using k-means clustering.
        """
        self._fetch_classification_data()
        self._collect_column_set_annotations_by_subject()
        self._normalize_column_set_annotations()
        return self._calculate_kmeans_of_column_set_annotations()

    def _collect_column_set_annotations_by_subject(self):
        task_id = self._project_metadata['task_id']
        column_annotations = self._annotations_by_task_and_subject[task_id]
        for subject_id, annotations in column_annotations.items():
            if not subject_id in self._column_annotations_by_subject:
                self._column_annotations_by_subject[subject_id] = []
            for annotation in annotations:
                column_vertices = [line['x'] for line in annotation['value']]
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
            self._vertex_centroids_by_subject[subject_id] = kmeans_codebook * std_dev
            # book = array((whitened[0],whitened[2]))
            # kmeans_codebook, distortion = kmeans(whitened, book)
            # self._vertex_centroids_by_subject[subject_id] = (kmeans_codebook * std_dev)[-1]
        return self._vertex_centroids_by_subject
