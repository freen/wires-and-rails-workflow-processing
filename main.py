#!/usr/bin/env python3

import logging
import settings
from panoptes_client import Panoptes
from lib.cluster_annotated_column_vertices import ClusterAnnotatedColumnVertices

def setup_logger(log_level):
    logger = logging.getLogger('WiresRailsWorkflowProcessor')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler('run.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def main(log_level):
    logger = setup_logger(log_level)
    logger.debug("Running Wires and Rails Workflow Processor")
    Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

    processor = ClusterAnnotatedColumnVertices({
        'project_id': settings.PROJECT_ID,
        'workflow_id': 3548, # Railroads_Mark_Image_Type
        'subject_set_id': 8339, # pages_raw
        'task_id': 'T1' # Only column demarcation task
    })

    vertex_centroids_by_subject = processor.calculate_vertex_centroids()

# TODO fetch subject image
# TODO crop image on vertex centroids
# TODO create new subjects w/ new cropped images w/ retained metadata

if __name__ == '__main__':
    main(logging.DEBUG)
