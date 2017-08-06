from distutils.core import setup

setup(name='wires-and-rails-workflow-processing',
      version='0.0.1',
      description='Background service for workflow propagation and image processing for Wires and Rails',
      author='freen',
      url='https://github.com/freen/wires-and-rails-workflow-processing',
      install_requires=[
        'panoptes-client',
        'python-dotenv'
      ],
     )