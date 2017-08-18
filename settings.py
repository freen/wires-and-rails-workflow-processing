"""
Loads settings from .env into an accessible package.
"""

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

PANOPTES_USERNAME = os.environ.get("PANOPTES_USERNAME")
PANOPTES_PASSWORD = os.environ.get("PANOPTES_PASSWORD")
PROJECT_SLUG = os.environ.get("PROJECT_SLUG")
PROJECT_ID = os.environ.get("PROJECT_ID")
