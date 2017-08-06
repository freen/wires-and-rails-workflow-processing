from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from panoptes_client import Project, Panoptes, Workflow, SubjectSet, Classification
from settings import *

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
    self._classificationsBySubject = {}
    for c in self._classifications:
      for subjectId in c.raw['links']['subjects']:
        if subjectId not in self._classificationsBySubject:
          self._classificationsBySubject[subjectId] = []
        self._classificationsBySubject[subjectId].append(c)
    import pdb; pdb.set_trace()

  def _validateClassAttributesImplemented(self):
    for attrName in self._requiredSubClassInstanceAttrs:
      if not hasattr(self, attrName):
        raise NotImplementedError()


class RailroadClassifyStationRowSubjectSet(AbstractProcessSubjectSet):

  TASKS = {
    'CONTAINS_STATION_NAME': {
      'id': 'T0',
      'answers': {
        0: 'Yes',
        1: 'No'
      }
    }
  }

  def __init__(self):
    self._workflowId = 4688
    self._subjectSetId = 8345
    super().__init__()

  def moveQualifyingSubjectsToNextWorkflows(self):
    pass

if __name__ == '__main__':
  subjectSet = RailroadClassifyStationRowSubjectSet()
  subjectSet.processCompletedSubjects()
