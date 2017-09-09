"""
Interface to ocropus binaries for image row segmentation.
"""

import subprocess
import os
from lib.logger import setup_logger

class Ocropy:
    """
    Interface to ocropus scripts for image row segmentation.
    """

    ERROR_LOGGER_NAME = 'ocropy_error'

    def __init__(self, logger):
        self._logger = logger
        self._error_logger = setup_logger(self.ERROR_LOGGER_NAME, 'log/ocropy_error.log')

    def perform_row_segmentation(self, image_file_path):
        """Run row segmentation on the provided path and return the new row absolute filepaths"""
        if not self._execute_row_segmentation_command(image_file_path):
            # TODO throw exception so rq puts in failed queue / other recovery strategy
            return False
        name, _ext = os.path.splitext(image_file_path)
        # Conveniently, the name and the resulting ocropus directory have the exact same name
        return [os.path.join(name, file) for file in os.listdir(name)]

    def _try_subprocess_cmd(self, cmd):
        self._logger.debug('Running cmd in subprocess: %s', str(cmd))
        try:
            cmd_result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            self._logger.debug('Result of ocropus cmd: %s', cmd_result)
            return True
        except subprocess.CalledProcessError as exception:
            self._logger.debug('Command return code was greater than zero. See error log.')
            self._error_logger.error('Cmd: %s', str(cmd))
            self._error_logger.error('Return code: %s', exception.returncode)
            self._error_logger.error('Cmd output: %s', exception.output)
            return False

    def _execute_row_segmentation_command(self, image_file_path):
        # TODO issue with images less than 600px wide; need to upscale smaller images
        nlbin_cmd = ['ocropus-nlbin', image_file_path]
        if not self._try_subprocess_cmd(nlbin_cmd):
            return False
        gpageseg_cmd = ['ocropus-gpageseg', '-n', '-d', '--maxcolseps=0', '--maxseps=0',
                        '--hscale=100', image_file_path]
        return self._try_subprocess_cmd(gpageseg_cmd)
