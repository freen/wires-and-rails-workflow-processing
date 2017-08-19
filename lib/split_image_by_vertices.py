"""
Utility for splitting original subject images by vertex centroids derived from user annotations.
"""

import logging
import settings
from PIL import Image

class SplitImageByVertices:
    """
    Utility for splitting original subject images by vertex centroids derived from user
    annotations.
    """

    def __init__(self):
        self._logger = logging.getLogger(settings.APP_NAME)

    def split(self, image_path_by_subject, vertex_centroids_by_subject):
        """Given each subject_id's image paths and centroids, chop the images into columns"""
        for subject_id, image_path in image_path_by_subject.items():
            self._logger.debug('Loading subject id %s image file %s', subject_id, image_path)
            offset, column_int = 0, 0
            image = Image.open(image_path)
            width, height = image.size
            for centroid in vertex_centroids_by_subject[subject_id]:
                centroid = round(centroid)
                box = (offset, 0, centroid, height)
                self._slice_column(image, image_path, column_int, box)
                offset = centroid
                column_int += 1
            # Final column, from last centroid to max width
            box = (offset, 0, width, height)
            self._slice_column(image, image_path, column_int, box)

    def _slice_column(self, image, image_path, column_int, box):
        out_path = "%s_%d" % (image_path, column_int)
        self._logger.debug('Cutting with box %s and saving to %s', str(box), out_path)
        column = image.crop(box)
        column.save(out_path, image.format)
