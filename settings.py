"""
Loads settings from .env into an accessible package.
"""

import os
import platform
import tempfile
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

APP_NAME = 'WiresRailsWorkflowProcessor'

PANOPTES_USERNAME = os.environ.get("PANOPTES_USERNAME")
PANOPTES_PASSWORD = os.environ.get("PANOPTES_PASSWORD")
PROJECT_SLUG = os.environ.get("PROJECT_SLUG")
PROJECT_ID = os.environ.get("PROJECT_ID")

DOCUMENT_VERTICES_WORKFLOW_ID = 3548 # "Railroads_Mark_Image_Type"
DOCUMENT_VERTICES_SUBJECT_SET_ID = 8339 # "pages_raw"
DOCUMENT_VERTICES_WORKFLOW_TASK_ID = 'T1' # Only column demarcation task

TEMPDIR = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
