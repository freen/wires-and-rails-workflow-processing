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

    def test_annotations_sorted_structure(self, classifications_model):
        assert classifications_model._annotations['T0'] == {
            5823821: [0, 0, 0, 0, 0, 0],
            5823822: [0, 0, 0, 0, 0, 0, 0, 0, 0],
            12992657: [0],
            12992773: [0],
            12992851: [0],
            12993513: [0],
            12993844: [0],
            12993899: [0],
            12996372: [0],
            14813279: [1, 1, 1, 1, 1, 0],
            14813280: [1, 1, 1, 1, 1],
            14813281: [1, 1, 1, 1]
        }
        assert classifications_model._annotations['T1'][14813281] == [
            [{'details': [], 'frame': 0, 'tool': 0, 'x': 2053.390625}],
            [{'details': [], 'frame': 0, 'tool': 0, 'x': 2047.852294921875}],
            [{'details': [], 'frame': 0, 'tool': 0, 'x': 2057.1474609375}],
            [{'details': [], 'frame': 0, 'tool': 0, 'x': 2048.92578125}]
        ]

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
