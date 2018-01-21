import pytest
from lib.models.vertex_classifications import VertexClassifications
from numpy import array

class TestVertexClassifications(object):

    @pytest.fixture
    def vertex_classifications_model(self, panoptes_classification_models, pages_raw_subject_ids):
        return VertexClassifications(panoptes_classification_models, pages_raw_subject_ids)

    def test_kmeans_centroids_calculation_is_correct(self, vertex_classifications_model):
        vertex_set_annotations = vertex_classifications_model.collect_vertex_set_annotations('T1')
        vertex_set_annotations = vertex_classifications_model.normalize_vertex_set_annotations(vertex_set_annotations)
        kmeans_centroids = vertex_classifications_model.kmeans_centroids_by_subject(vertex_set_annotations)

        expected_kmeans_centroids = {
            5823821: array([1663.09427897]),
            5823822: array([
                578.82873535,
                1114.28874207,
                1638.3444519,
                2168.9805603,
                2703.85162354
            ]),
            14813280: array([2010.61464844]),
            14813279: array([2052.32364909]),
            14813281: array([2051.82904053])
        }
        assert kmeans_centroids.keys() == expected_kmeans_centroids.keys()

        for key, centroid_set in expected_kmeans_centroids.items():
            expected_centroids = expected_kmeans_centroids[key]
            actual_centroids = kmeans_centroids[key]
            assert expected_centroids.all() == actual_centroids.all()
