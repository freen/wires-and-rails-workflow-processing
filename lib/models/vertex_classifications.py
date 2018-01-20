"""
Answers questions about a set of vertex classifications.
"""

from collections import defaultdict
from .classifications import Classifications

class VertexClassifications(Classifications):

    def collect_vertex_set_annotations(self, task_id):
        vertex_set_annotations = defaultdict(list)
        if task_id not in self._annotations:
            return vertex_set_annotations
        for subject_id, vertex_annotations in self._annotations[task_id].items():
            for vertex_annotation in vertex_annotations:
                vertex_set = [vertex['x'] for vertex in vertex_annotation['value']]
                vertex_set.sort()
                vertex_set_annotations[subject_id].append(vertex_set)
        return vertex_set_annotations

    def normalize_vertex_set_annotations(self, vertex_set_annotations):
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

    def kmeans_centroids_by_subject(self):
        pass
