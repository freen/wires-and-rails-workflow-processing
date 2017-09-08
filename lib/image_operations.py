"""
Utility for splitting original subject images by vertex centroids derived from user annotations.
"""

import os
import urllib.request
from urllib.parse import urlparse

import settings
from lib.logger import setup_logger
from lib.ocropy import Ocropy
from PIL import Image
from panoptes_client import Subject

class ImageOperations:
    """
    Utility for splitting original subject images by vertex centroids derived from user
    annotations.
    """

    LOGGER_NAME = 'image_operations'

    def __init__(self, logger):
        self._logger = logger

    # TODO generalize naming and breakout function, this also pushes new subjects
    # TODO e.g. call this "QueueOperations" and add the function of pushing new subjects
    @classmethod
    def queue_new_subject_creation(cls, subject_id, vertex_centroids):
        """
        Given subject ID and vertex centroids, fetch subject image and perform segmentation.
        Static-w/-instance-of-self pattern to support enqueuing in RQ.
        """
        logger = setup_logger(cls.LOGGER_NAME, 'log/image_operations.log')
        image_ops = ImageOperations(logger)
        row_paths_by_column = image_ops.perform_image_segmentation(subject_id, vertex_centroids)
        # TODO w/ paths and old subject metadata, push new subjects to Panoptes API

    def perform_image_segmentation(self, subject_id, vertex_centroids):
        """Fetch subject image, split columns by centroids, row segmentation with Ocropy"""
        self._logger.debug('Received the following subject centroids for image segmentation: %s',
                           str(vertex_centroids))
        subject_image_path = self._fetch_subject_image_to_tmp(subject_id)

        # Split subject image by vertex centroids
        column_image_paths = self._split_by_vertical_centroids(
            subject_id,
            subject_image_path,
            vertex_centroids
        )

        ocropy = Ocropy(self._logger)

        row_paths_by_column = {}

        for index, image_path in enumerate(column_image_paths):
            row_paths_by_column[index] = ocropy.perform_row_segmentation(image_path)

        return row_paths_by_column


    def _fetch_subject_image_to_tmp(self, subject_id):
        """Given subject_id, fetch subject image files to tmp dir storage and return the paths"""
        subject = Subject.where(scope='project', project_id=settings.PROJECT_ID,
                                workflow_id=settings.DOCUMENT_VERTICES_WORKFLOW_ID,
                                subject_id=subject_id)
        # TODO some kind of `first` needed here?
        locations_urls = list(subject.raw['locations'][0].values())
        subject_image_url = locations_urls[0]
        self._logger.debug('Retrieving subject image for %s: %s', subject.id,
                           subject_image_url)
        local_filename, _headers = urllib.request.urlretrieve(subject_image_url)
        path = urlparse(subject_image_url).path
        ext = os.path.splitext(path)[1]
        subject_id_filepath = os.path.join(settings.TEMPDIR, subject.id + ext)
        os.rename(local_filename, subject_id_filepath)
        return subject_id_filepath

    def _split_by_vertical_centroids(self, subject_id, image_path, vertex_centroids):
        """Given each subject_id's image paths and centroids, chop the images into columns"""
        split_images = []
        self._logger.debug('Loading subject id %s image file %s', subject_id, image_path)
        offset, column_int = 0, 0
        image = Image.open(image_path)
        width, height = image.size
        for centroid in vertex_centroids:
            centroid = round(centroid)
            box = (offset, 0, centroid, height)
            split_images.append(self._slice_column(image, image_path, column_int, box))
            offset = centroid
            column_int += 1
        # Final column, from last centroid to max width
        box = (offset, 0, width, height)
        split_images.append(self._slice_column(image, image_path, column_int, box))
        return split_images

    def _slice_column(self, image, image_path, column_int, box):
        name, ext = os.path.splitext(image_path)
        out_path = "%s_%d%s" % (name, column_int, ext)
        self._logger.debug('Cutting with box %s and saving to %s', str(box), out_path)
        column = image.crop(box)
        column.save(out_path, image.format)
        return out_path
