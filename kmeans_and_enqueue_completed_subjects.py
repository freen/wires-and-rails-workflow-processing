#!/usr/bin/env python3

"""
Runner script. Define .env variables per .env.example and run e.g.

   python3 main.py
"""

import logging
import settings
from lib.image_operations import ImageOperations
from lib.kmeans_cluster_annotated_column_vertices import KmeansClusterAnnotatedColumnVertices
from panoptes_client import Panoptes
from redis import Redis
from rq import Queue

class KmeansAndEnqueueCompletedSubjects:
    """
    Query for completed subjects, calculate kmeans vertex centroids, fetch subject images, split
    columns by centroids, row segmentatino with Ocropy.
    """

    def _setup_logger(self, log_level, file_name='log/kmeans_and_enqueue_completed_subjects.log'):
        """Configure file and console logger streams"""
        logger = logging.getLogger(settings.APP_NAME)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def run(self, log_level):
        """Run all processing tasks"""
        logger = self._setup_logger(log_level)
        logger.debug("Running Wires and Rails Workflow Processor")
        Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

        clusterer = KmeansClusterAnnotatedColumnVertices({
            'project_id': settings.PROJECT_ID,
            'workflow_id': settings.DOCUMENT_VERTICES_WORKFLOW_ID,
            'subject_set_id': settings.DOCUMENT_VERTICES_SUBJECT_SET_ID,
            'task_id': settings.DOCUMENT_VERTICES_WORKFLOW_TASK_ID
        })

        # Calculate vertex centroids
        vertex_centroids_by_subject = clusterer.calculate_vertex_centroids()

        logger.debug('Enqueueing the following subject centroids for image segmentation: %s',
                     str(vertex_centroids_by_subject))
        q = Queue(connection=Redis())
        q.enqueue(ImageOperations.perform_image_segmentation, vertex_centroids_by_subject)

# TODO SEQUENCE:
#
# [x] after kmeans clustering, shove the result into a queue (rq zB https://github.com/nvie/rq)
# [ ] write to Panoptes metadata saying we queued the subject for image processing
# [ ] add rq, redis daeman starters to dockerfile
#  =  inside the rq arch
#     [ ] move the vertical splitting logic in
#     [ ] add the ocropy row segmenter
#     [ ] create new subjects w/ new cropped images w/ retained metadata
# [ ] revise such that we only pull & process subjects which haven't been retired / completed

if __name__ == '__main__':
    kmeans_and_enqueue_completed_subjects = KmeansAndEnqueueCompletedSubjects()
    kmeans_and_enqueue_completed_subjects.run(logging.DEBUG)
