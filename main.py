#!/usr/bin/env python3

"""
Runner script. Define .env variables per .env.example and run e.g.

   python3 main.py
"""

import logging
import settings
from lib.cluster_annotated_column_vertices import ClusterAnnotatedColumnVertices
from lib.image_operations import ImageOperations
from panoptes_client import Panoptes

def _setup_logger(log_level, file_name='run.log'):
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


def main(log_level):
    """Run all processing tasks"""
    logger = _setup_logger(log_level)
    logger.debug("Running Wires and Rails Workflow Processor")
    Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

    clusterer = ClusterAnnotatedColumnVertices({
        'project_id': settings.PROJECT_ID,
        'workflow_id': settings.DOCUMENT_VERTICES_WORKFLOW_ID,
        'subject_set_id': settings.DOCUMENT_VERTICES_SUBJECT_SET_ID,
        'task_id': settings.DOCUMENT_VERTICES_WORKFLOW_TASK_ID
    })

    # Calculate vertext centroids
    vertex_centroids_by_subject = clusterer.calculate_vertex_centroids()

    # Fetch subject images of completed subjects
    subject_ids = vertex_centroids_by_subject.keys()
    image_path_by_subject_ids = ImageOperations.fetch_subject_images_to_tmp(subject_ids)

    # Split subject images by vertex centroids
    split_subject_images = ImageOperations.split(image_path_by_subject_ids,
                                                 vertex_centroids_by_subject)

# TODO row segmentation of new columns with ocropy
# TODO create new subjects w/ new cropped images w/ retained metadata
# TODO only pull & process subjects which haven't been retired / completed

if __name__ == '__main__':
    main(logging.DEBUG)
