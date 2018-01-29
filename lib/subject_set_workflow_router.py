"""
Determine the target subject set for segmented rows of a raw page, using source subject set ID and
aggregated classification records.
"""

from .models.classifications import Classifications

class SubjectSetWorkflowRouter:
    """
    Determine the target subject set for segmented rows of a raw page, using source subject set ID
    and aggregated classification records.
    """

    def __init__(self, subject_set_csv, settings, logger=None):
        self._subject_set_csv = subject_set_csv
        self._settings = settings
        self._pages_raw_subject_ids = subject_set_csv.raw_pages_subject_ids()
        self._logger = logger

    def _target_railroad_subject_set_id(self, source_subject_id, classifications_records):
        classifications = Classifications(classifications_records, self._pages_raw_subject_ids)
        majority_element = classifications \
            .majority_element(self._settings.TASK_ID_RAILROAD_LIST_TYPE, source_subject_id)
        if majority_element == self._settings.VALUE_RAILROAD_PAGE_LIST_TYPE_STATION:
            target_subject_set_id = self._settings.SUBJECT_SET_ID_PAGES_ROWS_RAILROAD_STATION_LIST
            target_name = 'Station'
        elif majority_element == self._settings.VALUE_RAILROAD_PAGE_LIST_TYPE_COMPANY:
            target_subject_set_id = self._settings.SUBJECT_SET_ID_PAGES_ROWS_RAILROAD_COMPANY_LIST
            target_name = 'Company'
        else:
            raise RuntimeError('Unknown scenario, majority element for rail pg type: %s'
                               % majority_element)
        if self._logger is not None:
            self._logger.debug('With a majority element of %d for task %s, target subject set ' \
                               'for subject ID %d is %s', majority_element,
                               self._settings.TASK_ID_RAILROAD_LIST_TYPE, source_subject_id,
                               target_name)
        return target_subject_set_id

    def target_subject_set_id(self, source_subject_id, classifications_records):
        """
        Identify the target subject set for a retired Railroad or Telegraph source subject, given
        its ID and its classification set.
        """
        subject_set_id = self._subject_set_csv.get_subject_set_id(source_subject_id)
        if subject_set_id == self._settings.SUBJECT_SET_ID_PAGES_RAW_RAILROAD:
            return self._target_railroad_subject_set_id(source_subject_id, classifications_records)
        elif subject_set_id == self._settings.SUBJECT_SET_ID_PAGES_RAW_TELEGRAPH:
            if self._logger is not None:
                self._logger.info('Identified source subject id %d as Telegraph subject.',
                                  source_subject_id)
            return self._settings.SUBJECT_SET_ID_PAGES_ROWS_UNCLASSIFIED_TELEGRAPH
        else:
            raise UnidentifiedRawSubjectSetException('Cannot identify as raw page, no target: %d'
                                                     % source_subject_id)

class UnidentifiedRawSubjectSetException(Exception):
    """Raised to indicate that a subject is not in either "raw" page subject sets."""
