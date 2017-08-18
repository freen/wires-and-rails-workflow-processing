import logging
from panoptes_client import Workflow, SubjectSet, Classification
from numpy import array, median, std
from scipy.cluster.vq import kmeans, whiten

class ClusterAnnotatedColumnVertices:

  def __init__(self, project_id):
    self._project_id = project_id
    self._workflowId = 3548 # Railroads_Mark_Image_Type
    self._subjectSetId = 8339 # pages_raw
    self._taskId = 'T1' # Only column demarcation task
    self._logger = logging.getLogger('WiresRailsWorkflowProcessor')

    # Populated by _loadData()
    self._annotationsByTaskAndSubject = {}
    self._classifications = []
    self._subjectSet = None
    self._subjects = []
    self._subjectIds = []

    # Populated by processAndCropCompletedSubjects()
    self._column_annotations_by_subject = {}
    self._vertex_centroids_by_subject = {}

    self._loadData()
    self._structureClassificationData()

  def _loadData(self):
    self._loadWorkflowData()
    self._loadSubjectData()
    self._loadClassificationData()

  def _loadWorkflowData(self):
    self._logger.debug("Loading workflow " + str(self._workflowId))
    self._workflow = Workflow.find(self._workflowId)

  """
  self._annotationsByTaskAndSubject[taskId][subjectId] = taskAnnotation
  """
  def _structureClassificationData(self):
    self._logger.debug("Structuring classifications")
    for c in self._classifications:
      for subjectId in c.raw['links']['subjects']:
        for taskAnnotation in c.raw['annotations']:
          taskId = taskAnnotation['task']
          if taskId not in self._annotationsByTaskAndSubject:
            self._annotationsByTaskAndSubject[taskId] = {}
          if subjectId not in self._annotationsByTaskAndSubject[taskId]:
            self._annotationsByTaskAndSubject[taskId][subjectId] = []
          self._annotationsByTaskAndSubject[taskId][subjectId].append(taskAnnotation)

  # TODO only pull subjects which haven't been retired / completed
  def _loadClassificationData(self):
    classificationKwargs = {
      'scope': 'project',
      'project_id': self._project_id,
      'workflow_id': self._workflowId
    }
    self._logger.debug("Loading classifications by params " + str(classificationKwargs))
    self._classifications = [c for c in Classification.where(**classificationKwargs)]

  # NOTE note used anymore at the moment, remove unless retirement data is not denormalized onto classifications
  def _loadSubjectData(self):
    self._logger.debug("Loading subjects data")
    self._subjectSet = SubjectSet.find(self._subjectSetId)
    self._subjects = [s for s in self._subjectSet.subjects]
    self._subjectIds = [s.id for s in self._subjects]

  def calculateVertexCentroids(self):
    self._collectColumnSetAnnotationsBySubject()
    self._normalizeColumnSetAnnotations()
    return self._calculateKMeansOfColumnSetAnnotations()

  def _collectColumnSetAnnotationsBySubject(self):
    column_annotations = self._annotationsByTaskAndSubject[self._taskId]
    for subject_id, annotations in column_annotations.items():
      if not subject_id in self._column_annotations_by_subject:
        self._column_annotations_by_subject[subject_id] = []
      for annotation in annotations:
        column_vertices = [line['x'] for line in annotation['value']]
        self._column_annotations_by_subject[subject_id].append(column_vertices)

  """
  Strip out line sets which include column qties deviant from the average column qty for that subject. This works in
  our case because the quantity of columns on a subject is extremely clear and we simply want to exclude anomalous /
  erroneous entries, which should be very rare, so that they don't ruin our k means logic.
  e.g. for a set of classifications which include 5, 5, 5, 5, and 1 vertices respectively, prune the classification
  which includes only 1 vertex.
  """
  def _normalizeColumnSetAnnotations(self):
    for subject_id, line_sets in self._column_annotations_by_subject.items():
      avg_column_qty = round(median([len(line_set) for line_set in line_sets]))
      normalized_set = [line_set for line_set in self._column_annotations_by_subject[subject_id] if len(line_set) == avg_column_qty]
      self._column_annotations_by_subject[subject_id] = normalized_set

  def _calculateKMeansOfColumnSetAnnotations(self):
    for subject_id, line_sets in self._column_annotations_by_subject.items():
      features = array(line_sets)
      std_dev = std(features, axis=0)
      whitened = whiten(features)
      kmeans_codebook, distortion = kmeans(whitened, 1)
      self._vertex_centroids_by_subject[subject_id] = kmeans_codebook * std_dev
      # book = array((whitened[0],whitened[2]))
      # kmeans_codebook, distortion = kmeans(whitened, book)
      # self._vertex_centroids_by_subject[subject_id] = (kmeans_codebook * std_dev)[-1]
    return self._vertex_centroids_by_subject
