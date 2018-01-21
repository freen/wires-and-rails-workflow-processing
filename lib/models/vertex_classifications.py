"""
Answers questions about a set of vertex classifications.
"""

from .classifications import Classifications
from collections import defaultdict
from numpy import array, median, std
from scipy.cluster.vq import kmeans, whiten

class VertexClassifications(Classifications):

    def vertex_centroids(self, task_id):
        vertex_set_annotations = self._collect_vertex_set_annotations(task_id)
        vertex_set_annotations = self._normalize_vertex_set_annotations(vertex_set_annotations)
        return self._kmeans_centroids_by_subject(vertex_set_annotations)

    def _collect_vertex_set_annotations(self, task_id):
        vertex_set_annotations = defaultdict(list)
        if task_id not in self._annotations:
            return vertex_set_annotations
        for subject_id, vertex_annotations in self._annotations[task_id].items():
            for vertex_annotation in vertex_annotations:
                vertex_set = [vertex['x'] for vertex in vertex_annotation['value']]
                vertex_set.sort()
                vertex_set_annotations[subject_id].append(vertex_set)

        # import pdb; pdb.set_trace();
        return vertex_set_annotations

    def _normalize_vertex_set_annotations(self, vertex_set_annotations):
        """
        Strip out line sets which include vertex qties deviant from the median vertex qty for that
        subject. This works in our case because the quantity of vertexs on a subject is extremely
        clear and we simply want to exclude anomalous / erroneous entries, so that they don't ruin
        k-means logic. e.g. for a set of classifications which include 5, 5, 5, 5, and 1 vertices
        respectively, prune the classification which includes only 1 vertex.
        """
        for subject_id, vertex_sets in vertex_set_annotations.items():
            median_vertex_qty = round(median([len(vertex_set) for vertex_set in vertex_sets]))
            normalized_sets = [vertex_set for vertex_set in vertex_set_annotations[subject_id]
                              if len(vertex_set) == median_vertex_qty]
            vertex_set_annotations[subject_id] = normalized_sets
        return vertex_set_annotations

    def _kmeans_centroids_by_subject(self, vertex_set_annotations):
        centroids = {}
        for subject_id, vertex_sets in vertex_set_annotations.items():
            if len(vertex_sets) < 2:
                continue
            features = array(vertex_sets)
            std_dev = std(features, axis=0)
            whitened = whiten(features)
            kmeans_codebook, _distortion = kmeans(whitened, 1)
            [dewhitened_kmeans] = kmeans_codebook * std_dev
            centroids[subject_id] = dewhitened_kmeans
        return centroids
