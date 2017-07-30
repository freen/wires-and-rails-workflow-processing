from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from panoptes_client import Project, Panoptes
from settings import *

Panoptes.connect(username=PANOPTES_USERNAME, password=PANOPTES_PASSWORD)

project = Project.find(slug='dbickett/untitled-project-30-dot-7-2017-10-14-26')
print vars(project)

for workflow in project.links.workflows:
    print workflow.display_name