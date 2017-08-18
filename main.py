#!/usr/bin/env python3

"""
Runner script. Define .env variables per .env.example and run e.g.

   python3 main.py
"""

import logging
import platform
import settings
import urllib.request
from lib.cluster_annotated_column_vertices import ClusterAnnotatedColumnVertices
from panoptes_client import Panoptes, Subject

DOCUMENT_VERTICES_WORKFLOW_ID = 3548 # "Railroads_Mark_Image_Type"
DOCUMENT_VERTICES_SUBJECT_SET_ID = 8339 # "pages_raw"
DOCUMENT_VERTICES_WORKFLOW_TASK_ID = 'T1' # Only column demarcation task

def setup_logger(log_level, file_name='run.log'):
    """Configure file and console logger streams"""
    logger = logging.getLogger('WiresRailsWorkflowProcessor')
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

def fetch_images_to_tmp(subject_ids):
    file_paths_by_subject_id = {}
    subjects = Subject.where(scope='project', project_id=settings.PROJECT_ID,
                             workflow_id=DOCUMENT_VERTICES_WORKFLOW_ID, subject_id=subject_ids)
    for subject in subjects:
        import pdb; pdb.set_trace();
        locations_urls = list(subject.raw['locations'][0].values())
        subject_image_url = locations_urls[0]
        local_filename, headers = urllib.request.urlretrieve(subject_image_url)
        file_paths_by_subject_id[subject.id] = local_filename

    return file_paths_by_subject_id

def main(log_level):
    """Run all processing tasks"""
    logger = setup_logger(log_level)
    logger.debug("Running Wires and Rails Workflow Processor")
    Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

    processor = ClusterAnnotatedColumnVertices({
        'project_id': settings.PROJECT_ID,
        'workflow_id': DOCUMENT_VERTICES_WORKFLOW_ID,
        'subject_set_id': DOCUMENT_VERTICES_SUBJECT_SET_ID,
        'task_id': DOCUMENT_VERTICES_WORKFLOW_TASK_ID
    })

    # Calculate vertext centroids
    processor.fetch_classification_data()
    vertex_centroids_by_subject = processor.calculate_vertex_centroids()

    # Fetch subject images of completed subjects
    subject_ids = vertex_centroids_by_subject.keys()
    # TODO why is just one of two subjects coming through the next line
    subject_image_paths = fetch_images_to_tmp(subject_ids)

    # Split subject images by vertex centroids
    import pdb; pdb.set_trace();

# TODO only pull & process subjects which haven't been retired / completed
# TODO fetch subject image
# TODO crop image on vertex centroids
# TODO create new subjects w/ new cropped images w/ retained metadata

if __name__ == '__main__':
    main(logging.DEBUG)
