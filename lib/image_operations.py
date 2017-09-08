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
from panoptes_client import Project, Subject, SubjectSet

# TODO generalize naming, this also pushes new subjects
# TODO e.g. call this "QueueOperations"
class ImageOperations:
    """
    Utility for splitting original subject images by vertex centroids derived from user
    annotations.
    """

    LOGGER_NAME = 'image_operations'

    def __init__(self, logger):
        self._logger = logger

    @classmethod
    def queue_new_subject_creation(cls, subject_id, vertex_centroids):
        """
        Given subject ID and vertex centroids, fetch subject image and perform segmentation.
        Static-w/-instance-of-self pattern to support enqueuing in RQ.
        """
        logger = setup_logger(cls.LOGGER_NAME, 'log/image_operations.log')
        image_ops = ImageOperations(logger)
        row_paths_by_column = image_ops.perform_image_segmentation(subject_id, vertex_centroids)
        image_ops.push_new_row_subjects(subject_id, row_paths_by_column)

    def push_new_row_subjects(self, source_subject_id, row_paths_by_column):
        """
        Given image paths for the new column-indexed rows (row_paths_by_column), push new
        unclassified row subjects to the appropriate subject set, with metadata references to the
        source subject (source_subject_id) and column.
        """
        project = Project.find(settings.PROJECT_ID)
        # subject = Subject.find(source_subject_id)
        subject_set_unclassified_rows = SubjectSet.find(
            settings.SUBJECT_SET_ID_PAGES_ROWS_UNCLASSIFIED
        )

        new_row_subjects = []

        # TODO w/ paths and old subject metadata, push new subjects to Panoptes API
        for column_index, row_paths in row_paths_by_column.items():
            self._logger.debug('Creating %d new row subjects for column index %d for subject %s',
                               len(row_paths), column_index, source_subject_id)
            for row_path in row_paths:
                new_subject = Subject()
                new_subject.links.project = project
                new_subject.metadata['source_document_subject_id'] = source_subject_id
                new_subject.metadata['source_document_column_index'] = column_index
                new_subject.add_location(row_path)
                new_subject.save()

                new_row_subjects.append(new_subject)

        subject_set_unclassified_rows.add(new_row_subjects)

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
        subject = Subject.find(subject_id)
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
