#!/usr/bin/env python3

"""
Runner script. Define .env variables per .env.example and run e.g.

   python3 run.py
"""

import csv
import logging

from lib import settings
from lib.logger import setup_logger
from lib.queue_operations import QueueOperations
from lib.models.vertex_classifications import VertexClassifications
from lib.subject_set_csv import SubjectSetCSV

from panoptes_client import Classification, Panoptes, Subject, Workflow
from redis import Redis
from rq import Queue

def run(log_level):
    """
    Query for completed subjects, calculate kmeans vertex centroids, fetch subject images, split
    columns by centroids, row segmentatino with Ocropy.
    """
    logger = setup_logger(settings.APP_NAME, 'log/kmeans_and_enqueue_completed_subjects.log',
                          log_level)
    logger.debug("Running Wires and Rails Workflow Processor")
    Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

    retired_subject_ids = []
    vertex_centroids_by_subject = {}

    for subject_set_id, metadata in settings.COLUMNS_WORKFLOW_METADATA.items():

        logger.debug("Loading vertices / subject retirement info for %(debug_name)s subject set " \
            "(subject set id: %(subject_set_id)d; workflow id: %(workflow_id)d; task id: " \
            " %(task_id)s", metadata)

        classification_kwargs = {
            'scope': 'project',
            'project_id': settings.PROJECT_ID,
            'workflow_id': metadata['workflow_id']
        }
        logger.debug("Loading classifications by params %s", str(classification_kwargs))
        classifications_records = Classification.where(**classification_kwargs)

        subject_set_csv = SubjectSetCSV()
        pages_raw_subject_ids = subject_set_csv.raw_pages_subject_ids()
        classifications = VertexClassifications(classifications_records, pages_raw_subject_ids)

        # Aggregate vertex centroids
        centroids_by_subject = classifications.vertex_centroids(metadata['task_id'])
        vertex_centroids_by_subject.update(centroids_by_subject)

        # Aggregate retired subjects
        workflow = Workflow.find(metadata['workflow_id'])
        retirement_count = workflow.retirement['options']['count']
        retired_subject_ids += classifications.retired_subject_ids(metadata['task_id'],
                                                                   retirement_count)

    logger.debug('Retrieved the following subject centroids for image segmentation: %s',
                 str(vertex_centroids_by_subject))

    logger.debug('For the following retired subject IDs: %s',
                 str(retired_subject_ids))

    queue = Queue(connection=Redis(host=settings.REDIS_HOST))

    for subject_id in retired_subject_ids:
        subject = Subject.find(subject_id)
        if settings.METADATA_KEY_ALREADY_PROCESSED in subject.metadata and \
           subject.metadata[settings.METADATA_KEY_ALREADY_PROCESSED]:
            logger.debug('Skipping subject id %s; already processed.', subject_id)
            continue
        logger.debug('Enqueuing subjects id: %s', subject_id)
        queue.enqueue(QueueOperations.queue_new_subject_creation, subject_id,
                      vertex_centroids_by_subject[subject_id], timeout=2*60*60)
        QueueOperations.flag_subject_as_queued(subject)

if __name__ == '__main__':
    run(logging.DEBUG)
