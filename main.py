from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from panoptes_client import Project, Panoptes, Workflow, SubjectSet, Classification
from settings import *
import json

# Panoptes.connect(username=PANOPTES_USERNAME, password=PANOPTES_PASSWORD)

# project = Project.find(slug=PROJECT_SLUG)

with open('mock_annotations.json', 'r') as json_file:
  mock_annotations = json.load(json_file)
  guesses_by_subject = {}
  aggregate_vertical_lines_by_subject = {}
  for subject_annotation in mock_annotations:
    annotations, subject_id = subject_annotation
    if not subject_id in aggregate_vertical_lines_by_subject:
      aggregate_vertical_lines_by_subject[subject_id] = []
    column_annotations = [a for a in annotations if a['task'] == 'T1']
    for column_annotation in column_annotations:
      # Take length of first vertical line classification as k-means 'guess'
      if not subject_id in guesses_by_subject:
        guesses_by_subject[subject_id] = len(column_annotation['value'])
      for vertical_line in column_annotation['value']:
        aggregate_vertical_lines_by_subject[subject_id].append(vertical_line['x'])
  for subject_id in aggregate_vertical_lines_by_subject.keys():
    aggregate_vertical_lines_by_subject[subject_id].sort()
  import pdb; pdb.set_trace();