"""
Utility for splitting original subject images by vertex centroids derived from user annotations.
"""

import os
import urllib.request
from urllib.parse import urlparse
from PIL import Image
from panoptes_client import Project, Subject, SubjectSet

from . import settings
from .logger import setup_logger
from .ocropy import Ocropy

class QueueOperations:
    """
    Utility for splitting original subject images by vertex centroids derived from user
    annotations.
    """

    LOGGER_NAME = 'queue_operations'

    def __init__(self, logger):
        self._logger = logger

    @classmethod
    def queue_new_subject_creation(cls, subject_id, vertex_centroids):
        """
        Given subject ID and vertex centroids, fetch subject image and perform segmentation.
        Static-w/-instance-of-self pattern to support enqueuing in RQ.
        """
        logger = setup_logger(cls.LOGGER_NAME, 'log/queue_operations.log')
        queue_ops = QueueOperations(logger)
        subject = Subject.find(subject_id)
        subject_image_path = queue_ops.fetch_subject_image_to_tmp(subject)
        column_image_paths = queue_ops.perform_column_segmentation(
            subject_id,
            subject_image_path,
            vertex_centroids
        )
        for column_image_path in column_image_paths:
            queue_ops.upscale_small_images(column_image_path)
        row_paths_by_column = queue_ops.perform_row_segmentation(column_image_paths)
        queue_ops.push_new_row_subjects(subject, row_paths_by_column)

    @classmethod
    def flag_subject_as_queued(cls, subject):
        """Write to subject metadata that this subject has been been processed"""
        subject.metadata[settings.METADATA_KEY_ALREADY_PROCESSED] = True
        subject.save()

    def upscale_small_images(self, image_path):
        """
        Upscale images which are smaller than 600px by 600px, for ocropus-gpageseg compatibility
        """
        image = Image.open(image_path)
        width, height = image.size
        if width < 600:
            ratio = (600/width)
        elif height < 600:
            ratio = (600/height)
        else:
            self._logger.debug('Not upscaling image %s (%d by %d); already at threshold',
                               image_path, width, height)
            return True
        upscaled_size = (int(width * ratio), int(height * ratio))
        self._logger.info(
            'Upscaling image %s to %dx%d (originally %dx%d) to meet 600x600 pixel segmentation ' +
            'threshold',
            image_path, upscaled_size[0], upscaled_size[1], width, height
        )
        resized = image.resize(upscaled_size)
        resized.save(image_path)
        return True

    def push_new_row_subjects(self, source_subject, row_paths_by_column):
        """
        Given image paths for the new column-indexed rows (row_paths_by_column), push new
        unclassified row subjects to the appropriate subject set, with metadata references to the
        source subject and column.
        """
        project = Project.find(settings.PROJECT_ID)
        # subject = Subject.find(source_subject.id)
        subject_set_unclassified_rows = SubjectSet.find(
            settings.SUBJECT_SET_ID_PAGES_ROWS_UNCLASSIFIED
        )

        new_row_subjects = []

        for column_index, row_paths in row_paths_by_column.items():
            self._logger.info('Creating %d new row subjects for column index %d for subject %s',
                              len(row_paths), column_index, source_subject.id)
            for row_path in row_paths:
                new_subject = Subject()
                new_subject.links.project = project
                copy_source_metadata_fields = ['book', 'page']
                for copy_field in copy_source_metadata_fields:
                    new_subject.metadata[copy_field] = source_subject.metadata[copy_field]
                new_subject.metadata['source_document_subject_id'] = source_subject.id
                new_subject.metadata['source_document_column_index'] = column_index
                new_subject.add_location(row_path)
                new_subject.save()

                new_row_subjects.append(new_subject)

        subject_set_unclassified_rows.add(new_row_subjects)

    def perform_column_segmentation(self, subject_id, image_path, vertex_centroids):
        """Given each subject_id's image paths and centroids, chop the images into columns"""
        self._logger.debug('Called with the following vertex centroids: %s', str(vertex_centroids))
        split_images = []
        self._logger.info('Loading subject id %s image file %s', subject_id, image_path)
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

    def perform_row_segmentation(self, column_image_paths):
        """Split columns by centroids, row segmentation with Ocropy"""
        row_paths_by_column = {}
        ocropy = Ocropy(self._logger)
        for index, image_path in enumerate(column_image_paths):
            row_paths_by_column[index] = ocropy.perform_row_segmentation(image_path)
        return row_paths_by_column

    def fetch_subject_image_to_tmp(self, subject):
        """Given subject, fetch subject image files to tmp dir storage and return the paths"""
        locations_urls = list(subject.raw['locations'][0].values())
        subject_image_url = locations_urls[0]
        self._logger.info('Retrieving subject image for %s: %s', subject.id,
                          subject_image_url)
        local_filename, _headers = urllib.request.urlretrieve(subject_image_url)
        path = urlparse(subject_image_url).path
        ext = os.path.splitext(path)[1]
        subject_id_filepath = os.path.join(settings.TEMPDIR, subject.id + ext)
        os.rename(local_filename, subject_id_filepath)
        return subject_id_filepath

    def _slice_column(self, image, image_path, column_int, box):
        name, ext = os.path.splitext(image_path)
        out_path = "%s_%d%s" % (name, column_int, ext)
        self._logger.info('Cutting with box %s and saving to %s', str(box), out_path)
        column = image.crop(box)
        column.save(out_path, image.format)
        return out_path
