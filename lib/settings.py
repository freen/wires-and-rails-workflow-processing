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

# SUBJECT_SET_ID_PAGES_RAW = 8339
SUBJECT_SET_ID_PAGES_RAW = 16602 # pages_raw_beta_testing
SUBJECT_SET_ID_PAGES_ROWS_UNCLASSIFIED = 16402

TASK_ID_DOCUMENT_VERTICES_WORKFLOW = 'T1'      # (Column demarcation task.)

WORKFLOW_ID_DOCUMENT_VERTICES = 3548           # "Railroads_Mark_Image_Type"

METADATA_KEY_ALREADY_PROCESSED = 'WARWP_subject_processed'

CACHE_FILE_SUBJECT_SET_CSV_FILEPATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + \
    '/../etc/wires-and-rails-subjects.csv')

TEMPDIR = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
