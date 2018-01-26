#!/usr/bin/env python3

"""
Program point of entry, via cron.
"""

import logging

from lib import settings
from lib.logger import setup_logger
from lib.queue_operations import QueueOperations
from lib.models.vertex_classifications import Classifications, VertexClassifications
from lib.subject_set_csv import SubjectSetCSV

from panoptes_client import Classification, Panoptes, Subject, Workflow
from redis import Redis
from rq import Queue

LOGGER = setup_logger(settings.APP_NAME, 'log/kmeans_and_enqueue_completed_subjects.log',
                      logging.DEBUG)

SUBJECT_SET_CSV = SubjectSetCSV()
PAGES_RAW_SUBJECT_IDS = SUBJECT_SET_CSV.raw_pages_subject_ids()

class UnidentifiedRawSubjectSetException(Exception):
    """Raised to indicate that a subject is not in either "raw" page subject sets."""

def _target_railroad_subject_set_id(source_subject_id, classifications_records):
    classifications = Classifications(classifications_records, PAGES_RAW_SUBJECT_IDS)
    majority_element = classifications.majority_element(settings.TASK_ID_RAILROAD_LIST_TYPE,
                                                        source_subject_id)
    if majority_element == settings.VALUE_RAILROAD_PAGE_LIST_TYPE_STATION:
        target_subject_set_id = settings.SUBJECT_SET_ID_PAGES_ROWS_RAILROAD_STATION_LIST
        target_name = 'Station'
    elif majority_element == settings.VALUE_RAILROAD_PAGE_LIST_TYPE_COMPANY:
        target_subject_set_id = settings.SUBJECT_SET_ID_PAGES_ROWS_RAILROAD_COMPANY_LIST
        target_name = 'Company'
    else:
        raise RuntimeError('Unknown scenario, majority element for rail pg type: %s'
                           % majority_element)
    LOGGER.debug('With a majority element of %d for task %s, target subject set for subject ID' \
                 '%d is %s', majority_element, settings.TASK_ID_RAILROAD_LIST_TYPE,
                 source_subject_id, target_name)
    return target_subject_set_id

def _target_subject_set_id(source_subject_id, classifications_records):
    subject_set_id = SUBJECT_SET_CSV.get_subject_set_id(source_subject_id)
    if subject_set_id == settings.SUBJECT_SET_ID_PAGES_RAW_RAILROAD:
        return _target_railroad_subject_set_id(source_subject_id, classifications_records)
    elif subject_set_id == settings.SUBJECT_SET_ID_PAGES_RAW_TELEGRAPH:
        LOGGER.info('Identified source subject id %d as Telegraph subject.', source_subject_id)
        return settings.SUBJECT_SET_ID_PAGES_ROWS_UNCLASSIFIED_TELEGRAPH
    else:
        raise UnidentifiedRawSubjectSetException('Cannot identify as raw page, no target: %d'
                                                 % source_subject_id)

def run():
    """
    Query for completed subjects, calculate kmeans vertex centroids, fetch subject images, split
    columns by centroids, row segmentatino with Ocropy.
    """
    LOGGER.debug("Running Wires and Rails Workflow Processor")
    Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

    retired_subject_ids = []

    vertices_and_target_subject_sets = []

    for _subject_set_id, metadata in settings.COLUMNS_WORKFLOW_METADATA.items():

        LOGGER.debug("Loading vertices / subject retirement info for %(debug_name)s subject set " \
            "(subject set id: %(subject_set_id)d; workflow id: %(workflow_id)d; task id: " \
            " %(task_id)s", metadata)

        classification_kwargs = {
            'scope': 'project',
            'project_id': settings.PROJECT_ID,
            'workflow_id': metadata['workflow_id']
        }
        LOGGER.debug("Loading classifications by params %s", str(classification_kwargs))
        classifications_records = [c for c in Classification.where(**classification_kwargs)]

        classifications = VertexClassifications(classifications_records, PAGES_RAW_SUBJECT_IDS)

        # Aggregate vertex centroids
        centroids_by_subject = classifications.vertex_centroids(metadata['task_id'])
        for subject_id, centroids in centroids_by_subject.items():
            try:
                target_subject_set_id = _target_subject_set_id(subject_id, classifications_records)
            except UnidentifiedRawSubjectSetException as ex:
                LOGGER.warn(ex.args[0])
                continue
            vertices_and_target_subject_sets.append([subject_id, centroids, target_subject_set_id])

        # Aggregate retired subjects
        workflow = Workflow.find(metadata['workflow_id'])
        retirement_count = workflow.retirement['options']['count']
        retired_subject_ids += classifications.retired_subject_ids(metadata['task_id'],
                                                                   retirement_count)

    LOGGER.debug('Retrieved the following subject centroids for image segmentation: %s',
                 str(vertices_and_target_subject_sets))

    LOGGER.debug('For the following retired subject IDs: %s',
                 str(retired_subject_ids))

    queue = Queue(connection=Redis(host=settings.REDIS_HOST))

    for subject_id, centroids, target_subject_set_id in vertices_and_target_subject_sets:
        if subject_id not in retired_subject_ids:
            continue
        subject = Subject.find(subject_id)
        if settings.METADATA_KEY_ALREADY_PROCESSED in subject.metadata and \
           subject.metadata[settings.METADATA_KEY_ALREADY_PROCESSED]:
            LOGGER.debug('Skipping subject id %d; already processed.', subject_id)
            continue
        LOGGER.debug('Enqueuing subjects id: %d', subject_id)
        queue.enqueue(QueueOperations.queue_new_subject_creation, subject_id, centroids,
                      target_subject_set_id, timeout=2*60*60)
        QueueOperations.flag_subject_as_queued(subject)

if __name__ == '__main__':
    run()
