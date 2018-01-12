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

SUBJECT_SET_ID_PAGES_ROWS_UNCLASSIFIED_RAILROAD = 16402
SUBJECT_SET_ID_PAGES_ROWS_UNCLASSIFIED_TELEGRAPH = 17845

# SUBJECT_SET_ID_PAGES_RAW_RAILROAD = 8339
SUBJECT_SET_ID_PAGES_RAW_RAILROAD = 16602 # pages_raw_beta_testing
SUBJECT_SET_ID_PAGES_RAW_TELEGRAPH = 17096 # pages_raw_telegraph
SUBJECT_SET_IDS_PAGES_RAW = [SUBJECT_SET_ID_PAGES_RAW_RAILROAD, SUBJECT_SET_ID_PAGES_RAW_TELEGRAPH]

WORKFLOW_ID_RAILROAD_MARK_IMAGE_TYPE = 3548 # "Railroads_Mark_Image_Type"
WORKFLOW_ID_TELEGRAPH_MARK_IMAGE_TYPE = 4413 # "Telegraph_Mark_Image_Type"

TASK_ID_RAILROAD_COLUMN_SEPARATORS = 'T1' # (Column demarcation task.)
TASK_ID_TELEGRAPH_COLUMN_SEPARATORS = 'T3' # (Column demarcation task.)

COLUMNS_WORKFLOW_METADATA = {
    SUBJECT_SET_ID_PAGES_RAW_RAILROAD: {
        'debug_name': 'Railroad Pages',
        'workflow_id': WORKFLOW_ID_RAILROAD_MARK_IMAGE_TYPE,
        'task_id': TASK_ID_RAILROAD_COLUMN_SEPARATORS,
        'subject_set_id': SUBJECT_SET_ID_PAGES_RAW_RAILROAD
    },
    SUBJECT_SET_ID_PAGES_RAW_TELEGRAPH: {
        'debug_name': 'Telegraph Pages',
        'workflow_id': WORKFLOW_ID_TELEGRAPH_MARK_IMAGE_TYPE,
        'task_id': TASK_ID_TELEGRAPH_COLUMN_SEPARATORS,
        'subject_set_id': SUBJECT_SET_ID_PAGES_RAW_TELEGRAPH
    },
}

METADATA_KEY_ALREADY_PROCESSED = 'WARWP_subject_processed'

CACHE_FILE_SUBJECT_SET_CSV_FILEPATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + \
    '/../etc/wires-and-rails-subjects.csv')

TEMPDIR = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
