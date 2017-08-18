from distutils.core import setup

DESCRIPTION = 'Background service for workflow propagation and image processing for Wires and Rails'

setup(name='wires-and-rails-workflow-processing',
      version='0.0.1',
      description=DESCRIPTION,
      author='freen',
      url='https://github.com/freen/wires-and-rails-workflow-processing',
      install_requires=[
          'panoptes-client',
          'python-dotenv'
      ],
     )
