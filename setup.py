"""
Package for performing post-classification workflow steps for the Wires and Rails Zooniverse
project.
"""

from distutils.core import setup

DESCRIPTION = ('Package for performing post-classification workflow steps for the Wires and ' +
               'Rails Zooniverse project.')

setup(name='wires-and-rails-workflow-processing',
      version='0.0.1',
      description=DESCRIPTION,
      author='freen',
      url='https://github.com/freen/wires-and-rails-workflow-processing',
      install_requires=[
          'panoptes-client',
          'python-dotenv',
          'scipy',
          'pylint'
          # easy_install Pillow
      ],
     )
