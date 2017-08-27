"""
Utility for splitting original subject images by vertex centroids derived from user annotations.
"""

import logging
import os
import urllib.request
from urllib.parse import urlparse
import settings
from lib.ocropy import Ocropy
from PIL import Image
from panoptes_client import Subject

class ImageOperations:
    """
    Utility for splitting original subject images by vertex centroids derived from user
    annotations.
    """

    def _logger(self):
        return logging.getLogger(settings.APP_NAME)

    def fetch_subject_images_to_tmp(self, subject_ids):
        """Given subject_ids, fetch subject image files to tmp dir storage and return the paths"""
        file_paths_by_subject_id = {}
        subjects = Subject.where(scope='project', project_id=settings.PROJECT_ID,
                                 workflow_id=settings.DOCUMENT_VERTICES_WORKFLOW_ID,
                                 subject_ids=subject_ids)
        for subject in subjects:
            locations_urls = list(subject.raw['locations'][0].values())
            subject_image_url = locations_urls[0]
            self._logger().debug('Retrieving subject image for %s: %s', subject.id, subject_image_url)
            local_filename, _headers = urllib.request.urlretrieve(subject_image_url)
            path = urlparse(subject_image_url).path
            ext = os.path.splitext(path)[1]
            custom_filepath = os.path.join(settings.TEMPDIR, subject.id + ext)
            os.rename(local_filename, custom_filepath)
            file_paths_by_subject_id[subject.id] = custom_filepath

        return file_paths_by_subject_id

    def perform_image_segmentation(self, vertex_centroids_by_subject):
        """Fetch subject images, split columns by centroids, row segmentation with Ocropy"""
        self._logger().debug('Received the following subject centroids for image segmentation: %s',
                           str(vertex_centroids_by_subject))
        subject_ids = vertex_centroids_by_subject.keys()
        image_path_by_subject_ids = self.fetch_subject_images_to_tmp(subject_ids)

        # Split subject images by vertex centroids
        split_subject_images = self._split_by_vertical_centroids(
           image_path_by_subject_ids,
           vertex_centroids_by_subject
        )

        for subject_id, column_image_paths in split_subject_images.items():
            for image_file_path in column_image_paths:
                Ocropy.perform_row_segmentation(image_file_path)

    def _split_by_vertical_centroids(self, image_path_by_subject, vertex_centroids_by_subject):
        """Given each subject_id's image paths and centroids, chop the images into columns"""
        split_images = {}
        for subject_id, image_path in image_path_by_subject.items():
            split_images[subject_id] = []
            self._logger().debug('Loading subject id %s image file %s', subject_id, image_path)
            offset, column_int = 0, 0
            image = Image.open(image_path)
            width, height = image.size
            for centroid in vertex_centroids_by_subject[subject_id]:
                centroid = round(centroid)
                box = (offset, 0, centroid, height)
                new_path = self._slice_column(image, image_path, column_int, box)
                split_images[subject_id].append(new_path)
                offset = centroid
                column_int += 1
            # Final column, from last centroid to max width
            box = (offset, 0, width, height)
            self._slice_column(image, image_path, column_int, box)
        return split_images

    def _slice_column(self, image, image_path, column_int, box):
        name, ext = os.path.splitext(image_path)
        out_path = "%s_%d%s" % (name, column_int, ext)
        self._logger().debug('Cutting with box %s and saving to %s', str(box), out_path)
        column = image.crop(box)
        column.save(out_path, image.format)
        return out_path
