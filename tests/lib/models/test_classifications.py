import json
import pytest
from lib.models.classifications import Classifications
from panoptes_client import Workflow, Classification

class TestClassifications(object):

    @pytest.fixture
    def pages_raw_subject_ids(self):
        return [14813280, 14813281, 12992773, 12993513, 12993899, 5823821, 5823822, 12992657,
            12992851, 12993844, 12996372, 14813279]

    @pytest.fixture
    def panoptes_classification_models(self):
        fixtures_fpath = 'tests/fixtures/classifications/railroad_workflow_classifications_raw.json'
        with open(fixtures_fpath, 'r') as content_file:
            classifications_json = content_file.read()
        classifications_raw = json.JSONDecoder().decode(classifications_json)
        classifications_objects = []
        for c_raw in classifications_raw:
            classifications_objects.append(Classification(raw=c_raw))
        return classifications_objects

    @pytest.fixture
    def classifications_model(self, panoptes_classification_models, pages_raw_subject_ids):
        return Classifications(panoptes_classification_models, pages_raw_subject_ids)

    def test_all_task_ids_in_top_level_keys(self, classifications_model):
        assert list(classifications_model._annotations.keys()) == ['T0', 'T1']

    def test_tasks_contain_subject_ids(self, classifications_model, pages_raw_subject_ids):
        for task_id, annotations_by_subject in classifications_model._annotations.items():
            assert set(annotations_by_subject.keys()) - set(pages_raw_subject_ids) == set()