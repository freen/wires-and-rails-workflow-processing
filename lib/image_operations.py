"""
Utility for splitting original subject images by vertex centroids derived from user annotations.
"""

import os
import logging
import urllib.request
from urllib.parse import urlparse
import settings
from PIL import Image
from panoptes_client import Subject

class ImageOperations:
    """
    Utility for splitting original subject images by vertex centroids derived from user
    annotations.
    """

    @classmethod
    def fetch_subject_images_to_tmp(cls, subject_ids):
        """Given subject_ids, fetch subject image files to tmp dir storage and return the paths"""
        file_paths_by_subject_id = {}
        subjects = Subject.where(scope='project', project_id=settings.PROJECT_ID,
                                 workflow_id=settings.DOCUMENT_VERTICES_WORKFLOW_ID,
                                 subject_ids=subject_ids)
        for subject in subjects:
            locations_urls = list(subject.raw['locations'][0].values())
            subject_image_url = locations_urls[0]
            local_filename, _headers = urllib.request.urlretrieve(subject_image_url)
            path = urlparse(subject_image_url).path
            ext = os.path.splitext(path)[1]
            custom_filepath = os.path.join(settings.TEMPDIR, subject.id + ext)
            os.rename(local_filename, custom_filepath)
            file_paths_by_subject_id[subject.id] = custom_filepath

        return file_paths_by_subject_id

    @classmethod
    def split(cls, image_path_by_subject, vertex_centroids_by_subject):
        """Given each subject_id's image paths and centroids, chop the images into columns"""
        logger = logging.getLogger(settings.APP_NAME)
        for subject_id, image_path in image_path_by_subject.items():
            logger.debug('Loading subject id %s image file %s', subject_id, image_path)
            offset, column_int = 0, 0
            image = Image.open(image_path)
            width, height = image.size
            for centroid in vertex_centroids_by_subject[subject_id]:
                centroid = round(centroid)
                box = (offset, 0, centroid, height)
                cls._slice_column(image, image_path, column_int, box)
                offset = centroid
                column_int += 1
            # Final column, from last centroid to max width
            box = (offset, 0, width, height)
            cls._slice_column(image, image_path, column_int, box)

    @classmethod
    def _slice_column(cls, image, image_path, column_int, box):
        logger = logging.getLogger(settings.APP_NAME)
        name, ext = os.path.splitext(image_path)
        out_path = "%s_%d%s" % (name, column_int, ext)
        logger.debug('Cutting with box %s and saving to %s', str(box), out_path)
        column = image.crop(box)
        column.save(out_path, image.format)
