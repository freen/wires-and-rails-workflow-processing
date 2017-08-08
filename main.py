from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from panoptes_client import Project, Panoptes, Workflow, SubjectSet, Classification
from settings import *

# from itertools import groupby
# from operator import attrgetter, itemgetter

from collections import Counter

Panoptes.connect(username=PANOPTES_USERNAME, password=PANOPTES_PASSWORD)

project = Project.find(slug=PROJECT_SLUG)

## Workflow sequence

# <Workflow 3548> Railroads_Mark_Image_Type
# <Workflow 3552> Railroad_Transcribe_Companies
# <Workflow 4688> Railroad_Classify_Station_Row
#   - subject_set pages_row_stations (#8345)
# <Workflow 4409> Railroad_Transcribe_Station_Company
# <Workflow 4410> Railroad_Transcribe_Station_ExplanatoryText
# <Workflow 4406> Railroad_Transcribe_Station_Name

# <Workflow 4413> Telegraph_Mark_Image_Type
# <Workflow 4417> Telegraph_Transcribe_Price
# <Workflow 4416> Telegraph_Transcribe_Second_Place
# <Workflow 4414> Telegraph_Transcribe_Office
# <Workflow 4415> Telegraph_Transcribe_Rate

# N/A
# <Workflow 4408> Railroad_Transcribe_Station_State

# TODO: use abc library
class AbstractProcessSubjectSet:

  # TODO: _workflowVersionId
  _requiredSubClassInstanceAttrs = ['_workflowId', '_subjectSetId']

  def __init__(self):
    self._validateClassAttributesImplemented()

  def processCompletedSubjects(self):
    self._preloadWorkflowData()
    self._preloadSubjectData()
    self._preloadClassificationData()
    self._structureClassificationData()
    self._moveQualifyingSubjectsToNextWorkflows()

  def _preloadWorkflowData(self):
    self._workflow = Workflow.find(self._workflowId)

  def _preloadSubjectData(self):
    self._subjectSet = SubjectSet.find(self._subjectSetId)
    self._subjects = [s for s in self._subjectSet.subjects]
    self._subjectIds = [s.id for s in self._subjects]

  def _preloadClassificationData(self):
    classificationKwargs = {
      'scope': 'project',
      'project_id': PROJECT_ID,
      'workflow_id': self._workflowId
    }
    # TODO confirm we're only pulling subjects which haven't been retired / completed
    self._classifications = [c for c in Classification.where(**classificationKwargs)]

  """
  self._classificationsByTaskAndSubject[taskId][subjectId] = taskAnnotation
  """
  def _structureClassificationData(self):
    self._classificationsByTaskAndSubject = {}
    for c in self._classifications:
      for subjectId in c.raw['links']['subjects']:
        for taskAnnotation in self._classifications[0].raw['annotations']:
          taskId = taskAnnotation['task']
          if taskId not in self._classificationsByTaskAndSubject:
            self._classificationsByTaskAndSubject[taskId] = {}
          if subjectId not in self._classificationsByTaskAndSubject[taskId]:
            self._classificationsByTaskAndSubject[taskId][subjectId] = []
          self._classificationsByTaskAndSubject[taskId][subjectId].append(taskAnnotation)

  def _validateClassAttributesImplemented(self):
    for attrName in self._requiredSubClassInstanceAttrs:
      if not hasattr(self, attrName):
        raise NotImplementedError()

  def _moveQualifyingSubjectsToNextWorkflows(self):
    for taskId, subjectClassifications in self._classificationsByTaskAndSubject.items():
      for subjectId, classifications in subjectClassifications.items():
        # MAYBETODO classification threshold might be stored in task / workflow configuration
        # if len(classifications) < 15:
        #   continue
        self._processCompletedTaskAnnotations(taskId, subjectId, classifications)

  def _processCompletedTaskAnnotations(self, taskId, subjectId, classifications):
    raise NotImplementedError()


class RailroadClassifyStationRowSubjectSet(AbstractProcessSubjectSet):

  TASKS = {
    'CONTAINS_STATION_NAME': {
      'id': 'T0',
      'answers': {
        'Yes': 0,
        'No': 1
      }
    }
  }

  def __init__(self):
    self._workflowId = 4688
    self._subjectSetId = 8345
    super().__init__()

  def _processCompletedTaskAnnotations(self, taskId, subjectId, classifications):
    # classifications = [{'task': 'T0', 'value': 1}, {'task': 'T0', 'value': 1}, {'task': 'T0', 'value': 0}, {'task': 'T0', 'value': 0}, {'task': 'T0', 'value': 1}]
    groupedByValue = Counter(c['value'] for c in classifications)
    if self.TASKS['CONTAINS_STATION_NAME']['id'] == taskId:
      pass # TODO add subject to station name transcription workflow

if __name__ == '__main__':
  subjectSet = RailroadClassifyStationRowSubjectSet()
  subjectSet.processCompletedSubjects()
