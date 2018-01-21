import pytest
from lib.models.classifications import Classifications

class TestClassifications(object):

    @pytest.fixture
    def classifications_model(self, panoptes_classification_models, pages_raw_subject_ids):
        return Classifications(panoptes_classification_models, pages_raw_subject_ids)

    def test_all_task_ids_in_top_level_keys(self, classifications_model):
        assert list(classifications_model._annotations.keys()) == ['T0', 'T1']

    def test_tasks_contain_subject_ids(self, classifications_model, pages_raw_subject_ids):
        for task_id, annotations_by_subject in classifications_model._annotations.items():
            assert set(annotations_by_subject.keys()) - set(pages_raw_subject_ids) == set()
