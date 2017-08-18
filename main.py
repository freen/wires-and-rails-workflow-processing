from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from panoptes_client import Project, Panoptes, Workflow, SubjectSet, Classification
from settings import *

from numpy import array, mean, std
from scipy.cluster.vq import kmeans, whiten

import logging

class Main:

  def __init__(self, log_level = logging.DEBUG):
    self._setupLogger(log_level)

  def _setupLogger(self, log_level):
    _logger = logging.getLogger('WiresRailsWorkflowProcessor')
    _logger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler('run.log')
    fileHandler.setLevel(log_level)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)

    _logger.addHandler(fileHandler)
    _logger.addHandler(consoleHandler)

  def run(self):
    Panoptes.connect(username=PANOPTES_USERNAME, password=PANOPTES_PASSWORD)
    processor = ClusterAndCropRawPagesByColumnAnnotations()
    processor.run()

class ClusterAndCropRawPagesByColumnAnnotations:

  def __init__(self):
    self._logger = logging.getLogger('WiresRailsWorkflowProcessor')
    self._workflowId = 3548 # Railroads_Mark_Image_Type
    self._subjectSetId = 8339 # pages_raw
    self._taskId = 'T1' # Only column demarcation task

    # Populated by _loadData
    self._classificationsByTaskAndSubject = {}
    self._classifications = []
    self._subjectSet = None
    self._subjects = []
    self._subjectIds = []

    self._loadData()
    self._structureClassificationData()
    import pdb; pdb.set_trace();

  def _loadData(self):
    self._loadWorkflowData()
    self._loadSubjectData()
    self._loadClassificationData()

  def _loadWorkflowData(self):
    self._logger.debug("Loading workflow " + str(self._workflowId))
    self._workflow = Workflow.find(self._workflowId)

  """
  self._classificationsByTaskAndSubject[taskId][subjectId] = taskAnnotation
  """
  def _structureClassificationData(self):
    self._logger.debug("Structuring classifications")
    for c in self._classifications:
      for subjectId in c.raw['links']['subjects']:
        for taskAnnotation in c.raw['annotations']:
          taskId = taskAnnotation['task']
          if taskId not in self._classificationsByTaskAndSubject:
            self._classificationsByTaskAndSubject[taskId] = {}
          if subjectId not in self._classificationsByTaskAndSubject[taskId]:
            self._classificationsByTaskAndSubject[taskId][subjectId] = []
          self._classificationsByTaskAndSubject[taskId][subjectId].append(taskAnnotation)

  # TODO only pull subjects which haven't been retired / completed
  def _loadClassificationData(self):
    classificationKwargs = {
      'scope': 'project',
      'project_id': PROJECT_ID,
      'workflow_id': self._workflowId
    }
    self._logger.debug("Loading classifications by params " + str(classificationKwargs))
    self._classifications = [c for c in Classification.where(**classificationKwargs)]

  def _loadSubjectData(self):
    self._logger.debug("Loading subjects data")
    self._subjectSet = SubjectSet.find(self._subjectSetId)
    self._subjects = [s for s in self._subjectSet.subjects]
    self._subjectIds = [s.id for s in self._subjects]

  def run(self):
    pass

  def processAndCropCompletedSubjects(self):
    # with open('mock_annotations.json', 'r') as json_file:
    #   mock_annotations = json.load(json_file)

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
        avg_column_qty = round(mean([len(line_set) for line_set in line_sets]))
        line_sets_by_subject[subject_id] = [line_set for line_set in line_sets_by_subject[subject_id] if len(line_set) == avg_column_qty]

    kmeans_by_subject = {}

    # Calculate k means
    for subject_id, line_sets in line_sets_by_subject.items():
      features = array(line_sets)
      std_dev = std(features, axis=0)
      whitened = whiten(features)
      kmeans_codebook, distortion = kmeans(whitened, 1)
      kmeans_by_subject[subject_id] = kmeans_codebook * std_dev
      # book = array((whitened[0],whitened[2]))
      # kmeans_codebook, distortion = kmeans(whitened, book)
      # kmeans_by_subject[subject_id] = (kmeans_codebook * std_dev)[-1]

    import pdb; pdb.set_trace();

if __name__ == '__main__':
  main = Main()
  main.run()
