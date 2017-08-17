# from dotenv import load_dotenv, find_dotenv
# load_dotenv(find_dotenv())

# from panoptes_client import Project, Panoptes, Workflow, SubjectSet, Classification
# from settings import *

# Panoptes.connect(username=PANOPTES_USERNAME, password=PANOPTES_PASSWORD)

# project = Project.find(slug=PROJECT_SLUG)

import json
from numpy import array, mean, std
from scipy.cluster.vq import vq, kmeans, whiten

with open('mock_annotations.json', 'r') as json_file:
  mock_annotations = json.load(json_file)

line_sets_by_subject = {}

for subject_annotation in mock_annotations:
  annotations, subject_id = subject_annotation
  if not subject_id in line_sets_by_subject:
    line_sets_by_subject[subject_id] = []
  column_annotations = [a for a in annotations if a['task'] == 'T1']

  # Aggregate line sets by subject
  for column_annotation in column_annotations:
    # Append classification line set to subject's sets
    classification_line_set = [line['x'] for line in column_annotation['value']]
    line_sets_by_subject[subject_id].append(classification_line_set)

  # Strip out line sets which include column qties deviant from the average column qty for that subject
  # This works in our case because the quantity of columns on a subject is extremely clear and we simply want to
  #   exclude anomalous / erroneous entries, which should be very rare, so that they don't ruin our k means logic.
  for subject_id, line_sets in line_sets_by_subject.items():
    avg_column_qty =  mean([len(line_set) for line_set in line_sets])
    line_sets_by_subject[subject_id] = [line_set for line_set in line_sets_by_subject[subject_id] if len(line_set) == avg_column_qty]

k_means_by_subject = {}

# Calculate k means
for subject_id, line_sets in line_sets_by_subject.items():
  features = array(line_sets)
  std_dev = std(features, axis=0)
  whitened = whiten(features)
  book = array((whitened[0],whitened[2]))
  k_means_by_subject[subject_id] = kmeans(whitened,book) * std_dev
