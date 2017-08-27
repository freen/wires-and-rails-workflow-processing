"""
Interface to ocropus binaries for image row segmentation.
"""

from subprocess import Popen, PIPE
from lib.logger import setup_logger

class Ocropy:
    """
    Interface to ocropus binaries for image row segmentation.
    """

    @classmethod
    def perform_row_segmentation(cls, image_file_path):
        """Given subject_ids, fetch subject image files to tmp dir storage and return the paths"""
        # ocropus-gpageseg -d --maxcolseps=0
        #                  --maxseps=0 --hscale=100 5823821_0.png
        pass