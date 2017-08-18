#!/usr/bin/env python3

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import logging
import settings
from panoptes_client import Panoptes
from lib.cluster_annotated_column_vertices import ClusterAnnotatedColumnVertices

class Runner:

  def __init__(self, log_level = logging.DEBUG):
    self._setupLogger(log_level)

  def _setupLogger(self, log_level):
    self._logger = logger = logging.getLogger('WiresRailsWorkflowProcessor')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    fileHandler = logging.FileHandler('run.log')
    fileHandler.setLevel(log_level)
    fileHandler.setFormatter(formatter)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(log_level)
    consoleHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

  def run(self):
    self._logger.debug("Running Wires and Rails Workflow Processor")
    Panoptes.connect(username=settings.PANOPTES_USERNAME, password=settings.PANOPTES_PASSWORD)

    processor = ClusterAnnotatedColumnVertices(settings.PROJECT_ID)
    vertex_centroids_by_subject = processor.calculateVertexCentroids()

    # TODO NEXT fetch subject image
    # TODO NEXT crop image on vertex centroids
    # TODO NEXT create new subjects w/ new cropped images w/ retained metadata

if __name__ == '__main__':
  runner = Runner()
  runner.run()
