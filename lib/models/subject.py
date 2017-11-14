#!/usr/bin/env python3

import os.path
import re

"""
Model class for performing subject operations.
"""

class Subject(dict):
	"""
	Model class for performing subject operations.
	"""

	BOOK_AND_PAGE_PATTERN = r'^(?P<book>[\d\-]+)\s.+\s(?P<page>\d+)$'

	def __init__(self, subject):
		self._set_subject(subject)

	def _set_subject(self, subject):
		self._subject = subject
		self._metadata = subject.metadata
		self._hydrate_fields()

	def _get_basename(self):
		if 'filepath' in self._metadata:
			return os.path.basename(self._metadata['filepath'])
		elif 'Filename' in self._metadata:
			return self._metadata['Filename']
		raise RuntimeError('Cannot identify subject file basename')

	def _hydrate_fields(self):
		basename = self._get_basename()
		self['filename_no_ext'] = os.path.splitext(basename)[0]
		search = re.search(self.BOOK_AND_PAGE_PATTERN, self['filename_no_ext'])
		self['book'] = search['book']
		self['page'] = search['page']
