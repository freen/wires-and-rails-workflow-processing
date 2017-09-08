"""
Loads settings from .env into an accessible package.
"""

import os
import platform
import tempfile
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

APP_NAME = 'WiresRailsWorkflowProcessor'

REDIS_HOST = 'redis'

PANOPTES_USERNAME = os.environ.get("PANOPTES_USERNAME")
PANOPTES_PASSWORD = os.environ.get("PANOPTES_PASSWORD")
PROJECT_SLUG = os.environ.get("PROJECT_SLUG")
PROJECT_ID = os.environ.get("PROJECT_ID")

SUBJECT_SET_ID_DOCUMENT_VERTICES = 8339        # "pages_raw"
SUBJECT_SET_ID_PAGES_ROWS_UNCLASSIFIED = 14618 # "pages_rows_unclassified"

TASK_ID_DOCUMENT_VERTICES_WORKFLOW = 'T1'      # (Column demarcation task.)

WORKFLOW_ID_DOCUMENT_VERTICES = 3548           # "Railroads_Mark_Image_Type"

TEMPDIR = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
