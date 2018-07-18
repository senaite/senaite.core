# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import api, logger
from bika.lims import bikaMessageFactory as _
from bika.lims.api.analysis import is_out_of_range
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.interfaces import (IAnalysisRequest, IFieldIcons,
                                  IRoutineAnalysis)
from bika.lims.permissions import (EditFieldResults, EditResults,
                                   ViewResults, ViewRetractedAnalyses)
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.utils import (check_permission, format_supsub,
                             formatDecimalMark, get_image, get_link, getUsers,
                             t)
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.workflow import isActive, wasTransitionPerformed
from plone.memoize import view as viewcache
from zope.component import getAdapters


class AnalysesView(BikaListingView):
    """Displays a list of Analyses in a table.

    Visible InterimFields from all analyses are added to self.columns[].
    Keyword arguments are passed directly to bika_analysis_catalog.
    """

    def __init__(self, context, request, **kwargs):
        BikaListingView.__init__(
            self, context, request,
            show_categories=context.bika_setup.getCategoriseAnalysisServices(),
            expand_all_categories=True)

        # prepare the content filter of this listing
        self.contentFilter = dict(kwargs)
        self.contentFilter.update({
            "portal_type": "Analysis",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        })

        # set the listing view config
        self.catalog = CATALOG_ANALYSIS_LISTING
        self.sort_order = 'ascending'
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.pagesize = 999999
        self.form_id = 'analyses_form'
        self.context_active = isActive(context)
        self.interim_fields = {}
        self.interim_columns = {}
        self.specs = {}
        self.bsc = getToolByName(context, 'bika_setup_catalog')
        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()
        self.rc = getToolByName(context, REFERENCE_CATALOG)
        self.dmk = context.bika_setup.getResultsDecimalMark()
        self.scinot = context.bika_setup.getScientificNotationResults()
        self.categories = []
        request.set('disable_plone.rightcolumn', 1)

        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = False

        self.columns = {
            # Although 'created' column is not displayed in the list (see
            # review_states to check the columns that will be rendered), this
            # column is needed to sort the list by create date
            'created': {
                'title': _('Date Created'),
                'toggle': False},
            'Service': {
                'title': _('Analysis'),
                'attr': 'Title',
                'index': 'sortable_title',
                'sortable': False},
            'Partition': {
                'title': _("Partition"),
                'attr': 'getSamplePartitionID',
                'sortable': False},
            'Method': {
                'title': _('Method'),
                'sortable': False,
                'toggle': True},
            'Instrument': {
                'title': _('Instrument'),
                'sortable': False,
                'toggle': True},
            'Analyst': {
                'title': _('Analyst'),
                'sortable': False,
                'toggle': True},
            'state_title': {
                'title': _('Status'),
                'sortable': False},
            'DetectionLimit': {
                'title': _('DL'),
                'sortable': False,
                'toggle': False},
            'Result': {
                'title': _('Result'),
                'input_width': '6',
                'input_class': 'ajax_calculate numeric',
                'sortable': False},
            'Specification': {
                'title': _('Specification'),
                'sortable': False},
            'Uncertainty': {
                'title': _('+-'),
                'sortable': False},
            'retested': {
                'title': "<img title='%s' "
                         "src='%s/++resource++bika.lims.images/retested.png"
                         "'/>" % \
                         (t(_('Retested')), self.portal_url),
                'type': 'boolean',
                'sortable': False},
            'Attachments': {
                'title': _('Attachments'),
                'sortable': False},
            'CaptureDate': {
                'title': _('Captured'),
                'index': 'getResultCaptureDate',
                'sortable': False},
            'DueDate': {
                'title': _('Due Date'),
                'index': 'getDueDate',
                'sortable': False},
            'Hidden': {
                'title': _('Hidden'),
                'toggle': True,
                'sortable': False,
                'input_class': 'autosave',
                'type': 'boolean'},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Service',
                         'Partition',
                         'DetectionLimit',
                         'Result',
                         'Specification',
                         'Method',
                         'Instrument',
                         'Analyst',
                         'Uncertainty',
                         'CaptureDate',
                         'DueDate',
                         'state_title',
                         'Hidden']
             },
        ]
        if not context.bika_setup.getShowPartitions():
            self.review_states[0]['columns'].remove('Partition')

        # This is used to cache analysis keywords with Point of Capture to
        # reduce the number objects that need to be woken up
        # Is managed by `is_analysis_edition_allowed` function
        self._keywords_poc_map = dict()

        # This is used to display method and instrument columns if there is at
        # least one analysis to be rendered that allows the assignment of method
        # and/or instrument
        self.show_methodinstr_columns = False

    @viewcache.memoize
    def has_permission(self, permission, obj=None):
        """Returns if the current user has rights for the permission passed in

        :param permission: permission identifier
        :param obj: object to check the permission against
        :return: True if the user has rights for the permission passed in
        """
        if not permission:
            logger.warn("None permission is not allowed")
            return False
        if obj is None:
            return check_permission(permission, self.context)
        return check_permission(permission, obj)

    @viewcache.memoize
    def is_analysis_edition_allowed(self, analysis_brain):
        """Returns if the analysis passed in can be edited by the current user

        :param analysis_brain: Brain that represents an analysis
        :return: True if the user can edit the analysis, otherwise False
        """

        # TODO: Workflow. This function will be replaced by
        # `isTransitionAllowed(submit)` as soon as all this logic gets moved
        # into analysis' submit guard.... Very soon
        if not self.context_active:
            # The current context must be active. We cannot edit analyses from
            # inside a deactivated Analysis Request, for instance
            return False

        if analysis_brain.review_state == 'retracted':
            # Retracted analyses cannot be edited
            return False

        analysis_obj = None
        analysis_keyword = analysis_brain.getKeyword
        if analysis_keyword not in self._keywords_poc_map:
            # Store the point of capture for this analysis keyword in cache, so
            # waking up analyses with same keyword will not be longer required
            analysis_obj = api.get_object(analysis_brain)
            analysis_poc = analysis_obj.getPointOfCapture()
            self._keywords_poc_map[analysis_keyword] = analysis_poc

        poc = self._keywords_poc_map[analysis_keyword]
        if poc == 'field':
            # This analysis must be captured on field, during sampling.
            if not self.has_permission(EditFieldResults):
                # Current user cannot edit field analyses.
                return False

        elif not self.has_permission(EditResults):
            # The Point of Capture is 'lab' and the current user cannot edit
            # lab analyses.
            return False

        analysis_obj = analysis_obj or api.get_object(analysis_brain)
        if wasTransitionPerformed(analysis_obj, 'submit'):
            # Analysis has been already submitted. This analysis cannot be
            # edited anymore.
            return False

        # Is the instrument out of date?
        # The user can assign a result to the analysis if it does not have any
        # instrument assigned or the instrument assigned is valid.
        return self.is_analysis_instrument_valid(analysis_brain)

    @viewcache.memoize
    def is_analysis_instrument_valid(self, analysis_brain):
        """Return if the analysis has a valid instrument.

        If the analysis passed in is from ReferenceAnalysis type or does not
        have an instrument assigned, returns True

        :param analysis_brain: Brain that represents an analysis
        :return: True if the instrument assigned is valid or is None"""
        if analysis_brain.meta_type == 'ReferenceAnalysis':
            # If this is a ReferenceAnalysis, there is no need to check the
            # validity of the instrument, because this is a QC analysis and by
            # definition, it has the ability to promote an instrument to a
            # valid state if the result is correct.
            return True
        instrument = self.get_instrument(analysis_brain)
        return not instrument or instrument.isValid()

    def get_instrument(self, analysis_brain):
        """Returns the instrument assigned to the analysis passed in, if any

        :param analysis_brain: Brain that represents an analysis
        :return: Instrument object or None"""
        instrument_uid = analysis_brain.getInstrumentUID
        # Note we look for the instrument by using its UID, case we want the
        # instrument to be cached by UID so if same instrument is assigned to
        # several analyses, a single search for instrument will be required
        return self.get_object(instrument_uid)

    @viewcache.memoize
    def get_object(self, brain_or_object_or_uid):
        """Get the full content object. Returns None if the param passed in is
        not a valid, not a valid object or not found

        :param brain_or_object_or_uid: UID/Catalog brain/content object
        :returns: content object
        """
        if api.is_uid(brain_or_object_or_uid):
            return api.get_object_by_uid(brain_or_object_or_uid, default=None)
        if api.is_object(brain_or_object_or_uid):
            return api.get_object(brain_or_object_or_uid)
        return None

    @viewcache.memoize
    def get_methods_vocabulary(self, analysis_brain):
        """Returns a vocabulary with all the methods available for the passed in
        analysis, either those assigned to an instrument that are capable to
        perform the test (option "Allow Entry of Results") and those assigned
        manually in the associated Analysis Service.

        The vocabulary is a list of dictionaries. Each dictionary has the
        following structure:

            {'ResultValue': <method_UID>,
             'ResultText': <method_Title>}

        :param analysis_brain: A single Analysis brain
        :type analysis_brain: CatalogBrain
        :returns: A list of dicts
        """
        uids = analysis_brain.getAllowedMethodUIDs
        query = {'portal_type': 'Method',
                 'inactive_state': 'active',
                 'UID': uids}
        brains = api.search(query, 'bika_setup_catalog')
        if not brains:
            return [{'ResultValue': '', 'ResultText': _('None')}]
        return map(lambda brain: {'ResultValue': brain.UID,
                                  'ResultText': brain.Title}, brains)

    @viewcache.memoize
    def get_instruments_vocabulary(self, analysis_brain):
        """Returns a vocabulary with the valid and active instruments available
        for the analysis passed in.

        If the option "Allow instrument entry of results" for the Analysis
        is disabled, the function returns an empty vocabulary.

        If the analysis passed in is a Reference Analysis (Blank or Control),
        the vocabulary, the invalid instruments will be included in the
        vocabulary too.

        The vocabulary is a list of dictionaries. Each dictionary has the
        following structure:

            {'ResultValue': <instrument_UID>,
             'ResultText': <instrument_Title>}

        :param analysis_brain: A single Analysis or ReferenceAnalysis
        :type analysis_brain: Analysis or.ReferenceAnalysis
        :return: A vocabulary with the instruments for the analysis
        :rtype: A list of dicts: [{'ResultValue':UID, 'ResultText':Title}]
        """
        if not analysis_brain.getInstrumentEntryOfResults:
            # Instrument entry of results for this analysis is not allowed
            return list()

        # If the analysis is a QC analysis, display all instruments, including
        # those uncalibrated or for which the last QC test failed.
        meta_type = analysis_brain.meta_type
        uncalibrated = meta_type == 'ReferenceAnalysis'
        if meta_type == 'DuplicateAnalysis':
            base_analysis_type = analysis_brain.getAnalysisPortalType
            uncalibrated = base_analysis_type == 'ReferenceAnalysis'

        uids = analysis_brain.getAllowedInstrumentUIDs
        query = {'portal_type': 'Instrument',
                 'inactive_state': 'active',
                 'UID': uids}
        brains = api.search(query, 'bika_setup_catalog')
        vocab = [{'ResultValue': '', 'ResultText': _('None')}]
        for brain in brains:
            instrument = self.get_object(brain)
            if uncalibrated and not instrument.isOutOfDate():
                # Is a QC analysis, include instrument also if is not valid
                vocab.append({'ResultValue': instrument.UID(),
                              'ResultText': instrument.Title()})
            if instrument.isValid():
                # Only add the 'valid' instruments: certificate
                # on-date and valid internal calibration tests
                vocab.append({'ResultValue': instrument.UID(),
                              'ResultText': instrument.Title()})
        return vocab

    @viewcache.memoize
    def get_analysts(self):
        analysts = getUsers(self.context, ['Manager', 'LabManager', 'Analyst'])
        analysts = analysts.sortedByKey()
        results = list()
        for analyst_id, analyst_name in analysts.items():
            results.append({'ResultValue': analyst_id,
                            'ResultText': analyst_name})
        return results

    def load_analysis_categories(self):
        # Getting analysis categories
        bsc = api.get_tool('bika_setup_catalog')
        analysis_categories = bsc(portal_type="AnalysisCategory",
                                  sort_on="sortable_title")
        # Sorting analysis categories
        self.analysis_categories_order = dict([
            (b.Title, "{:04}".format(a)) for a, b in
            enumerate(analysis_categories)])

    def before_render(self):
        """Called before the template is rendered
        """
        # Load analysis categories available in the system
        self.load_analysis_categories()

    def isItemAllowed(self, obj):
        """Checks if the passed in Analysis must be displayed in the list.

        If the 'filtering by department' option is enabled in Bika Setup, this
        function checks if the Analysis Service associated to the Analysis is
        assigned to any of the currently selected departments (information
        stored in a cookie).

        If department filtering is disabled in bika_setup, returns True. If the
        obj is None or empty, returns False.

        If the obj has no department assigned, returns True

        :param obj: A single Analysis brain or content object
        :type obj: ATContentType/CatalogBrain
        :returns: True if the item can be added to the list.
        :rtype: bool
        """
        if not obj:
            return False

        # Does the user has enough privileges to see retracted analyses?
        if obj.review_state == 'retracted' and \
                not self.has_permission(ViewRetractedAnalyses):
            return False

        if not self.context.bika_setup.getAllowDepartmentFiltering():
            # Filtering by department is disabled. Return True
            return True

        # Department filtering is enabled. Check if the Analysis Service
        # associated to this Analysis is assigned to at least one of the
        # departments currently selected.
        dep_uid = obj.getDepartmentUID
        departments = self.request.get('filter_by_department_info', '')
        return not dep_uid or dep_uid in departments.split(',')

    def folderitem(self, obj, item, index):
        """Prepare a data item for the listing.

        :param obj: The catalog brain or content object
        :param item: Listing item (dictionary)
        :param index: Index of the listing item
        :returns: Augmented listing data item
        """

        item['Service'] = obj.Title
        item['class']['service'] = 'service_title'
        item['service_uid'] = obj.getServiceUID
        item['Keyword'] = obj.getKeyword
        item['Unit'] = format_supsub(obj.getUnit) if obj.getUnit else ''
        item['retested'] = obj.getRetested
        item['class']['retested'] = 'center'

        # Note that getSampleTypeUID returns the type of the Sample, no matter
        # if the sample associated to the analysis is a regular Sample (routine
        # analysis) or if is a Reference Sample (Reference Analysis). If the
        # analysis is a duplicate, it returns the Sample Type of the sample
        # associated to the source analysis.
        item['st_uid'] = obj.getSampleTypeUID

        # Fill item's category
        self._folder_item_category(obj, item)
        # Fill item's row class
        self._folder_item_css_class(obj, item)
        # Fill result and/or result options
        self._folder_item_result(obj, item)
        # Fill calculation and interim fields
        self._folder_item_calculation(obj, item)
        # Fill method
        self._folder_item_method(obj, item)
        # Fill instrument
        self._folder_item_instrument(obj, item)
        # Fill analyst
        self._folder_item_analyst(obj, item)
        # Fill attachments
        self._folder_item_attachments(obj, item)
        # Fill uncertainty
        self._folder_item_uncertainty(obj, item)
        # Fill Detection Limits
        self._folder_item_detection_limits(obj, item)
        # Fill Specifications
        self._folder_item_specifications(obj, item)
        # Fill Due Date and icon if late/overdue
        self._folder_item_duedate(obj, item)
        # Fill verification criteria
        self._folder_item_verify_icons(obj, item)
        # Fill worksheet anchor/icon
        self._folder_item_assigned_worksheet(obj, item)
        # Fill reflex analysis icons
        self._folder_item_reflex_icons(obj, item)
        # Fill hidden field (report visibility)
        self._folder_item_report_visibility(obj, item)
        # Renders additional icons to be displayed
        self._folder_item_fieldicons(obj)
        # Renders remarks toggle button
        self._folder_item_remarks(obj, item)

        return item

    def folderitems(self):
        # This shouldn't be required here, but there are some views that
        # calls directly contents_table() instead of __call__, so  before_render
        # is never called. :(
        self.before_render()

        # Gettin all the items
        items = super(AnalysesView, self).folderitems(classic=False)

        # the TAL requires values for all interim fields on all
        # items, so we set blank values in unused cells
        for item in items:
            for field in self.interim_columns:
                if field not in item:
                    item[field] = ''

        # XXX order the list of interim columns
        interim_keys = self.interim_columns.keys()
        interim_keys.reverse()

        # add InterimFields keys to columns
        for col_id in interim_keys:
            if col_id not in self.columns:
                self.columns[col_id] = {'title': self.interim_columns[col_id],
                                        'input_width': '6',
                                        'input_class': 'ajax_calculate numeric',
                                        'sortable': False}

        if self.allow_edit:
            new_states = []
            for state in self.review_states:
                # InterimFields are displayed in review_state
                # They are anyway available through View.columns though.
                # In case of hidden fields, the calcs.py should check
                # calcs/services
                # for additional InterimFields!!
                pos = 'Result' in state['columns'] and \
                      state['columns'].index('Result') or len(state['columns'])
                for col_id in interim_keys:
                    if col_id not in state['columns']:
                        state['columns'].insert(pos, col_id)
                # retested column is added after Result.
                pos = 'Result' in state['columns'] and \
                      state['columns'].index('Uncertainty') + 1 or len(
                    state['columns'])
                state['columns'].insert(pos, 'retested')
                new_states.append(state)
            self.review_states = new_states
            # Allow selecting individual analyses
            self.show_select_column = True

        if self.show_categories:
            self.categories = map(lambda x: x[0],
                                  sorted(self.categories, key=lambda x: x[1]))
        else:
            self.categories.sort()

        # self.json_specs = json.dumps(self.specs)
        self.json_interim_fields = json.dumps(self.interim_fields)
        self.items = items

        # Method and Instrument columns must be shown or hidden at the
        # same time, because the value assigned to one causes
        # a value reassignment to the other (one method can be performed
        # by different instruments)
        self.columns['Method']['toggle'] = self.show_methodinstr_columns
        self.columns['Instrument']['toggle'] = self.show_methodinstr_columns

        return items

    def _folder_item_category(self, analysis_brain, item):
        """Sets the category to the item passed in

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        if not self.show_categories:
            return

        cat = analysis_brain.getCategoryTitle
        item['category'] = cat
        cat_order = self.analysis_categories_order.get(cat)
        if (cat, cat_order) not in self.categories:
            self.categories.append((cat, cat_order))

    def _folder_item_css_class(self, analysis_brain, item):
        """Sets the suitable css class name(s) to `table_row_class` from the
        item passed in, depending on the properties of the analysis object

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        meta_type = analysis_brain.meta_type

        # Default css names for table_row_class
        css_names = item.get('table_row_class', '').split()
        css_names.extend(['state-{}'.format(analysis_brain.review_state),
                          'type-{}'.format(meta_type.lower())])

        if meta_type == 'ReferenceAnalysis':
            css_names.append('qc-analysis')

        elif meta_type == 'DuplicateAnalysis':
            if analysis_brain.getAnalysisPortalType == 'ReferenceAnalysis':
                css_names.append('qc-analysis')

        item['table_row_class'] = ' '.join(css_names)

    def _folder_item_duedate(self, analysis_brain, item):
        """Set the analysis' due date to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """

        # Note that if the analysis is a Reference Analysis, `getDueDate`
        # returns the date when the ReferenceSample expires. If the analysis is
        # a duplicate, `getDueDate` returns the due date of the source analysis
        due_date = analysis_brain.getDueDate
        due_date_str = self.ulocalized_time(due_date, long_format=0)
        item['DueDate'] = due_date_str

        # If the Analysis is late/overdue, display an icon
        capture_date = analysis_brain.getResultCaptureDate
        capture_date = capture_date or DateTime()
        if capture_date > due_date:
            # The analysis is late or overdue
            img = get_image('late.png', title=t(_("Late Analysis")),
                            width='16px', height='16px')
            item['replace']['DueDate'] = '{} {}'.format(due_date_str, img)

    def _folder_item_result(self, analysis_brain, item):
        """Set the analysis' result to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """

        item['Result'] = ''
        if not self.has_permission(ViewResults, analysis_brain):
            # If user has no permissions, don't display the result but an icon
            img = get_image('to_follow.png', width='16px', height='16px')
            item['before']['Result'] = img
            return

        result = analysis_brain.getResult
        capture_date = analysis_brain.getResultCaptureDate
        capture_date_str = self.ulocalized_time(capture_date, long_format=0)
        item['Result'] = result
        item['CaptureDate'] = capture_date_str
        item['result_captured'] = capture_date_str

        # If this analysis has a predefined set of options as result, tell the
        # template that selection list (choices) must be rendered instead of an
        # input field for the introduction of result.
        choices = analysis_brain.getResultOptions
        if choices:
            item['choices']['Result'] = choices

        if self.is_analysis_edition_allowed(analysis_brain):
            item['allow_edit'].extend(['Result', 'Remarks'])

        # Wake up the object only if necessary. If there is no result set, then
        # there is no need to go further with formatted result
        if not result:
            return

        # TODO: Performance, we wake-up the full object here
        full_obj = self.get_object(analysis_brain)
        formatted_result = full_obj.getFormattedResult(
            sciformat=int(self.scinot), decimalmark=self.dmk)
        item['formatted_result'] = formatted_result

    def _folder_item_calculation(self, analysis_brain, item):
        """Set the analysis' calculation and interims to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """

        is_editable = self.is_analysis_edition_allowed(analysis_brain)
        # Set interim fields. Note we add the key 'formatted_value' to the list
        # of interims the analysis has already assigned.
        interim_fields = analysis_brain.getInterimFields or list()
        for interim_field in interim_fields:
            interim_keyword = interim_field.get('keyword', '')
            if not interim_keyword:
                continue
            interim_value = interim_field.get('value', '')
            interim_formatted = formatDecimalMark(interim_value, self.dmk)
            interim_field['formatted_value'] = interim_formatted
            item[interim_keyword] = interim_field
            item['class'][interim_keyword] = 'interim'
            if is_editable:
                item['allow_edit'].append(interim_keyword)

            # Add this analysis' interim fields to the interim_columns list
            interim_hidden = interim_field.get('hidden', False)
            if not interim_hidden:
                interim_title = interim_field.get('title')
                self.interim_columns[interim_keyword] = interim_title

        item['interimfields'] = interim_fields
        self.interim_fields[analysis_brain.UID] = interim_fields

        # Set calculation
        calculation_uid = analysis_brain.getCalculationUID
        has_calculation = calculation_uid and True or False
        item['calculation'] = has_calculation
        if is_editable and (not has_calculation or interim_fields):
            # If the analysis is editable and doesn't have a calculation or it
            # does, but has interim fields, it must be re-testable.
            item['allow_edit'].append('retested')

    def _folder_item_method(self, analysis_brain, item):
        """Fills the analysis' method to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """

        is_editable = self.is_analysis_edition_allowed(analysis_brain)
        method_title = analysis_brain.getMethodTitle
        item['Method'] = method_title or ''
        if is_editable:
            method_vocabulary = self.get_methods_vocabulary(analysis_brain)
            if method_vocabulary:
                item['Method'] = analysis_brain.getMethodUID
                item['choices']['Method'] = method_vocabulary
                item['allow_edit'].append('Method')
                self.show_methodinstr_columns = True
        elif method_title:
            item['replace']['Method'] = get_link(analysis_brain.getMethodURL,
                                                 method_title)
            self.show_methodinstr_columns = True

    def _folder_item_instrument(self, analysis_brain, item):
        """Fills the analysis' instrument to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        item['Instrument'] = ''
        if not analysis_brain.getInstrumentEntryOfResults:
            # Manual entry of results, instrument is not allowed
            item['Instrument'] = _('Manual')
            item['replace']['Instrument'] = \
                '<a href="#">{}</a>'.format(t(_('Manual')))
            return

        # Instrument can be assigned to this analysis
        is_editable = self.is_analysis_edition_allowed(analysis_brain)
        self.show_methodinstr_columns = True
        instrument = self.get_instrument(analysis_brain)
        if is_editable:
            # Edition allowed
            voc = self.get_instruments_vocabulary(analysis_brain)
            if voc:
                # The service has at least one instrument available
                item['Instrument'] = instrument.UID() if instrument else ''
                item['choices']['Instrument'] = voc
                item['allow_edit'].append('Instrument')
                return

        if instrument:
            # Edition not allowed
            instrument_title = instrument and instrument.Title() or ''
            instrument_link = get_link(instrument.absolute_url(),
                                       instrument_title)
            item['Instrument'] = instrument_title
            item['replace']['Instrument'] = instrument_link
            return

    def _folder_item_analyst(self, obj, item):
        is_editable = self.is_analysis_edition_allowed(obj)
        if not is_editable:
            item['Analyst'] = obj.getAnalystName
            return

        # Analyst is editable
        item['Analyst'] = obj.getAnalyst or api.get_current_user().id
        item['choices']['Analyst'] = self.get_analysts()
        item['allow_edit'].append('Analyst')

    def _folder_item_attachments(self, obj, item):
        item['Attachments'] = ''
        attachment_uids = obj.getAttachmentUIDs
        if not attachment_uids:
            return

        if not self.has_permission(ViewResults, obj):
            return

        attachments_html = []
        attachments = api.search({'UID': attachment_uids}, 'uid_catalog')
        for attachment in attachments:
            attachment = api.get_object(attachment)
            uid = api.get_uid(attachment)
            html = '<span class="attachment" attachment_uid="{}">'.format(uid)
            attachments_html.append(html)

            at_file = attachment.getAttachmentFile()
            icon = at_file.icon
            if callable(icon):
                icon = icon()
            if icon:
                html = '<img src="{}/{}">'.format(self.portal_url, icon)
                attachments_html.append(html)

            url = '{}/at_download/AttachmentFile'
            url = url.format(attachment.absolute_url())
            link = get_link(url, at_file.filename)
            attachments_html.append(link)

            if not self.is_analysis_edition_allowed(obj):
                attachments_html.append('<br/></span>')
                continue

            img = '<img class="deleteAttachmentButton"' \
                  ' attachment_uid="{}" src="{}"/>'
            img = img.format(uid, '++resource++bika.lims.images/delete.png')
            attachments_html.append(img)
            attachments_html.append('<br/></span>')

        if attachments_html:
            # Remove the last <br/></span> and add only </span>
            attachments_html = attachments_html[:-1]
            attachments_html.append('</span>')
            item['replace']['Attachments'] = ''.join(attachments_html)

    def _folder_item_uncertainty(self, obj, item):
        item['Uncertainty'] = ''
        if not self.has_permission(ViewResults, obj):
            return

        result = obj.getResult

        # TODO: Performance, we wake-up the full object here
        full_obj = self.get_object(obj)
        formatted = format_uncertainty(full_obj, result, decimalmark=self.dmk,
                                       sciformat=int(self.scinot))
        if formatted:
            item['Uncertainty'] = formatted
            item['structure'] = True
            # Add before and after snippets
            after = '<em class="discreet" style="white-space:nowrap;"> {}</em>'
            item['before']['Uncertainty'] = '&plusmn;&nbsp;'
            item['after']['Uncertainty'] = after.format(obj.getUnit)

        is_editable = self.is_analysis_edition_allowed(obj)
        if is_editable and full_obj.getAllowManualUncertainty():
            # User can set the value of uncertainty manually
            uncertainty = full_obj.getUncertainty(result)
            item['Uncertainty'] = uncertainty or ''
            item['allow_edit'].append('Uncertainty')
            item['structure'] = False
            # Add before and after snippets
            after = '<em class="discreet" style="white-space:nowrap;"> {}</em>'
            item['before']['Uncertainty'] = '&plusmn;&nbsp;'
            item['after']['Uncertainty'] = after.format(obj.getUnit)

    def _folder_item_detection_limits(self, obj, item):
        item['DetectionLimit'] = ''
        is_editable = self.is_analysis_edition_allowed(obj)
        if not is_editable:
            return

        # TODO: Performance, we wake-up the full object here
        full_obj = self.get_object(obj)
        uid = api.get_uid(obj)

        is_below_ldl = full_obj.isBelowLowerDetectionLimit()
        is_above_udl = full_obj.isAboveUpperDetectionLimit()

        # Allow to use LDL and UDL in calculations.
        # Since LDL, UDL, etc. are wildcards that can be used in calculations,
        # these fields must be loaded always for 'live' calculations.
        dls = {
            'above_udl': is_above_udl,
            'below_ldl': is_below_ldl,
            'is_ldl': full_obj.isLowerDetectionLimit(),
            'is_udl': full_obj.isUpperDetectionLimit(),
            'default_ldl': full_obj.getLowerDetectionLimit(),
            'default_udl': full_obj.getUpperDetectionLimit(),
            'manual_allowed': full_obj.getAllowManualDetectionLimit(),
            'dlselect_allowed': full_obj.getDetectionLimitSelector()
        }
        dlsin = \
            '<input type="hidden" id="AnalysisDLS.%s" value=\'%s\'/>'
        dlsin = dlsin % (uid, json.dumps(dls))
        item['after']['Result'] = dlsin

        if not full_obj.getDetectionLimitSelector():
            # The user cannot manually set the Detection Limit
            return

        # User can manually set the Detection Limit for this analysis.
        # A selector with options '', '<' and '>' must be displayed.
        dl_operator = ''
        if is_below_ldl or is_above_udl:
            dl_operator = '<' if is_below_ldl else '>'

        item['allow_edit'].append('DetectionLimit')
        item['DetectionLimit'] = dl_operator
        item['choices']['DetectionLimit'] = [
            {'ResultValue': '<', 'ResultText': '<'},
            {'ResultValue': '>', 'ResultText': '>'}
        ]
        self.columns['DetectionLimit']['toggle'] = True
        defaults = {'min': full_obj.getLowerDetectionLimit(),
                    'max': full_obj.getUpperDetectionLimit(),
                    'manual': full_obj.getAllowManualDetectionLimit()}
        defin = \
            '<input type="hidden" id="DefaultDLS.%s" value=\'%s\'/>'
        defin = defin % (uid, json.dumps(defaults))
        item['after']['DetectionLimit'] = defin

    def _folder_item_specifications(self, analysis_brain, item):
        """Set the results range to the item passed in"""
        # Everyone can see valid-ranges
        item['Specification'] = ''
        results_range = analysis_brain.getResultsRange
        if not results_range:
            return
        min_str = results_range.get('min', '')
        max_str = results_range.get('max', '')
        min_str = api.is_floatable(min_str) and "{0}".format(min_str) or ""
        max_str = api.is_floatable(max_str) and "{0}".format(max_str) or ""
        specs = ", ".join([val for val in [min_str, max_str] if val])
        if not specs:
            return
        item["Specification"] = "[{}]".format(specs)

        # Show an icon if out of range
        out_range, out_shoulders = is_out_of_range(analysis_brain)
        if not out_range:
            return
        # At least is out of range
        img = get_image("exclamation.png", title=_("Result out of range"))
        if not out_shoulders:
            img = get_image("warning.png", title=_("Result in shoulder range"))
        self._append_html_element(item, "Result", img)

    def _folder_item_verify_icons(self, analysis_brain, item):
        """Set the analysis' verification icons to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        submitter = analysis_brain.getSubmittedBy
        if not submitter:
            # This analysis hasn't yet been submitted, no verification yet
            return

        if analysis_brain.review_state == 'retracted':
            # Don't display icons and additional info about verification
            return

        verifiers = analysis_brain.getVerificators.split(',')
        in_verifiers = submitter in verifiers
        if in_verifiers:
            # If analysis has been submitted and verified by the same person,
            # display a warning icon
            msg = t(_("Submitted and verified by the same user: {}"))
            icon = get_image('warning.png', title=msg.format(submitter))
            self._append_html_element(item, 'state_title', icon)

        num_verifications = analysis_brain.getNumberOfRequiredVerifications
        if num_verifications > 1:
            # More than one verification required, place an icon and display the
            # number of verifications done vs. total required
            done = analysis_brain.getNumberOfVerifications
            pending = num_verifications - done
            ratio = float(done) / float(num_verifications) if done > 0 else 0
            ratio = int(ratio * 100)
            scale = ratio == 0 and 0 or (ratio / 25) * 25
            anchor = "<a href='#' title='{} &#13;{} {}' " \
                     "class='multi-verification scale-{}'>{}/{}</a>"
            anchor = anchor.format(t(_("Multi-verification required")),
                                   str(pending),
                                   t(_("verification(s) pending")),
                                   str(scale),
                                   str(done),
                                   str(num_verifications))
            self._append_html_element(item, 'state_title', anchor)

        if analysis_brain.review_state != 'to_be_verified':
            # The verification of analysis has already been done or first
            # verification has not been done yet. Nothing to do
            return

        # Check if the user has "Bika: Verify" privileges
        if not self.has_permission(VerifyPermission):
            # User cannot verify, do nothing
            return

        username = api.get_current_user().id
        if username not in verifiers:
            # Current user has not verified this analysis
            if submitter != username:
                # Current user is neither a submitter nor a verifier
                return

            # Current user is the same who submitted the result
            if analysis_brain.isSelfVerificationEnabled:
                # Same user who submitted can verify
                title = t(_("Can verify, but submitted by current user"))
                html = get_image('warning.png', title=title)
                self._append_html_element(item, 'state_title', html)
                return

            # User who submitted cannot verify
            title = t(_("Cannot verify, submitted by current user"))
            html = get_image('submitted-by-current-user.png', title=title)
            self._append_html_element(item, 'state_title', html)
            return

        # This user verified this analysis before
        multi_verif = self.context.bika_setup.getTypeOfmultiVerification()
        if multi_verif != 'self_multi_not_cons':
            # Multi verification by same user is not allowed
            title = t(_("Cannot verify, was verified by current user"))
            html = get_image('submitted-by-current-user.png', title=title)
            self._append_html_element(item, 'state_title', html)
            return

        # Multi-verification by same user, but non-consecutively, is allowed
        if analysis_brain.getLastVerificator != username:
            # Current user was not the last user to verify
            title = t(_("Can verify, but was already verified by current user"))
            html = get_image('warning.png', title=title)
            self._append_html_element(item, 'state_title', html)
            return

        # Last user who verified is the same as current user
        title = t(_("Cannot verify, last verified by current user"))
        html = get_image('submitted-by-current-user.png', title=title)
        self._append_html_element(item, 'state_title', html)
        return

    def _folder_item_assigned_worksheet(self, analysis_brain, item):
        """Adds an icon to the item dict if the analysis is assigned to a
        worksheet and if the icon is suitable for the current context

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        if not IAnalysisRequest.providedBy(self.context):
            # We want this icon to only appear if the context is an AR
            return

        if analysis_brain.worksheetanalysis_review_state != 'assigned':
            # No need to go further. This analysis is not assigned to any WS
            return

        analysis_obj = self.get_object(analysis_brain)
        worksheet = analysis_obj.getBackReferences('WorksheetAnalysis')
        if not worksheet:
            # No worksheet assigned. Do nothing
            return

        worksheet = worksheet[0]
        title = t(_("Assigned to: ${worksheet_id}",
                    mapping={'worksheet_id': safe_unicode(worksheet.id)}))
        img = get_image('worksheet.png', title=title)
        anchor = get_link(worksheet.absolute_url(), img)
        self._append_html_element(item, 'state_title', anchor)

    def _folder_item_reflex_icons(self, analysis_brain, item):
        """Adds an icon to the item dictionary if the analysis has been
        automatically generated due to a reflex rule

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        if not analysis_brain.getIsReflexAnalysis:
            # Do nothing
            return
        img = get_image('reflexrule.png',
                        title=t(_('It comes form a reflex rule')))
        self._append_html_element(item, 'Service', img)

    def _folder_item_report_visibility(self, analysis_brain, item):
        """Set if the hidden field can be edited (enabled/disabled)

        :analysis_brain: Brain that represents an analysis
        :item: analysis' dictionary counterpart to be represented as a row"""
        # Users that can Add Analyses to an Analysis Request must be able to
        # set the visibility of the analysis in results report, also if the
        # current state of the Analysis Request (e.g. verified) does not allow
        # the edition of other fields. Note that an analyst has no privileges
        # by default to edit this value, cause this "visibility" field is
        # related with results reporting and/or visibility from the client side.
        # This behavior only applies to routine analyses, the visibility of QC
        # analyses is managed in publish and are not visible to clients.
        if 'Hidden' not in self.columns:
            return

        full_obj = self.get_object(analysis_brain)
        item['Hidden'] = full_obj.getHidden()
        if IRoutineAnalysis.providedBy(full_obj):
            item['allow_edit'].append('Hidden')

    def _folder_item_fieldicons(self, analysis_brain):
        """Resolves if field-specific icons must be displayed for the object
        passed in.

        :param analysis_brain: Brain that represents an analysis
        """
        full_obj = self.get_object(analysis_brain)
        uid = api.get_uid(full_obj)
        for name, adapter in getAdapters((full_obj,), IFieldIcons):
            alerts = adapter()
            if not alerts or uid not in alerts:
                continue
            alerts = alerts[uid]
            if uid not in self.field_icons:
                self.field_icons[uid] = alerts
                continue
            self.field_icons[uid].extend(alerts)

    def _folder_item_remarks(self, analysis_brain, item):
        """Renders the Remarks field for the passed in analysis and if the
        edition of the analysis is permitted, adds a button to toggle the
        visibility of remarks field

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row"""
        item['Remarks'] = analysis_brain.getRemarks

        if not self.is_analysis_edition_allowed(analysis_brain):
            # Edition not allowed, do not add the remarks toggle button, the
            # remarks field will be displayed without the option to hide it
            return

        if not self.context.bika_setup.getEnableAnalysisRemarks():
            # Remarks not enabled in Setup, so don't display the balloon button
            return

        # Analysis can be edited. Add the remarks toggle button
        title = t(_("Add Remark"))
        img = get_image('comment_ico.png', title=title)
        kwargs = {'class': "add-remark"}
        anchor = get_link('#', img, **kwargs)
        self._append_html_element(item, 'Service', anchor, after=False)

    def _append_html_element(self, item, element, html, glue="&nbsp;", after=True):
        """Appends an html value after or before the element in the item dict

        :param item: dictionary that represents an analysis row
        :param element: id of the element the html must be added thereafter
        :param html: element to append
        :param glue: glue to use for appending
        :param after: if the html content must be added after or before"""
        position = after and 'after' or 'before'
        item[position] = item.get(position, {})
        original = item[position].get(element, '')
        if not original:
            item[position][element] = html
            return
        item[position][element] = glue.join([original, html])
