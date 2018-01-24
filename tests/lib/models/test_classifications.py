import pytest
from panoptes_client import Classification
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

    def test_majority_element(self):
        classifications_raw = [
            {
                'id': 1,
                'annotations': [{'task': 'T0', 'value': 0}],
                'links': {'subjects': ['5823821']}
            },
            {
                'id': 2,
                'annotations': [{'task': 'T0', 'value': 0}],
                'links': {'subjects': ['5823821']}
            },
            {
                'id': 3,
                'annotations': [{'task': 'T0', 'value': 1}],
                'links': {'subjects': ['5823821']}
            }
        ]
        classifications_models = [Classification(raw=c) for c in classifications_raw]
        classifications_model = Classifications(classifications_models, [5823821])
        element, qty = classifications_model.majority_element('T0', 5823821)
        assert element == 0
        assert qty == 2

    def test_majority_element(self):
        classifications_raw = [
            {
                'id': 1,
                'annotations': [{'task': 'T0', 'value': 0}],
                'links': {'subjects': ['5823821']}
            },
            {
                'id': 2,
                'annotations': [{'task': 'T0', 'value': 1}],
                'links': {'subjects': ['5823821']}
            }
        ]
        classifications_models = [Classification(raw=c) for c in classifications_raw]
        classifications_model = Classifications(classifications_models, [5823821])
        with pytest.raises(ValueError):
            element, qty = classifications_model.majority_element('T0', 5823821)
