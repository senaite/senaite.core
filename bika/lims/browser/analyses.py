# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import api
from bika.lims import logger
from bika.lims.utils import t, dicts_to_dict, format_supsub, check_permission, \
    get_link
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.permissions import *
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.utils import getUsers
from bika.lims.utils import formatDecimalMark
from DateTime import DateTime
from operator import itemgetter
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ZCatalog.interfaces import ICatalogBrain
from bika.lims.workflow import wasTransitionPerformed, isActive
from zope.component import getAdapters
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from plone.api.user import has_permission
import json


class AnalysesView(BikaListingView):
    """ Displays a list of Analyses in a table.
        Visible InterimFields from all analyses are added to self.columns[].
        Keyword arguments are passed directly to bika_analysis_catalog.
    """

    def __init__(self, context, request, **kwargs):
        BikaListingView.__init__(
            self, context, request,
            show_categories=context.bika_setup.getCategoriseAnalysisServices(),
            expand_all_categories=True)
        self.catalog = CATALOG_ANALYSIS_LISTING
        self.contentFilter = dict(kwargs)
        self.contentFilter['portal_type'] = 'Analysis'
        self.contentFilter['sort_on'] = 'sortable_title'
        self.contentFilter['sort_order'] = 'ascending'
        self.sort_order = 'ascending'
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.pagesize = 999999
        self.form_id = 'analyses_form'
        # Initializing attributs for this view
        self.context_active = isActive(context)
        self.interim_fields = {}
        self.interim_columns = {}
        self.specs = {}
        self.bsc = getToolByName(context, 'bika_setup_catalog')
        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()
        self.rc = getToolByName(context, REFERENCE_CATALOG)
        # Initializing the deximal mark variable
        self.dmk = ''
        self.scinot = ''
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
            'ResultDM': {
                'title': _('Dry'),
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

        # This is used to cache the permissions for the current user, to avoid
        # the need of asking for the same permission now and then.
        # Is managed by `has_permission` function
        self._permissions_map = dict()

        # This is used to cache the instruments instead of retrieving them
        # individually each time we folder an analysis item
        # Is managed by `get_instrument`
        self._instruments_map = dict()

        # This is used to cache if the analyses are editable or not, cause
        # retrieving this information for same analysis multiple times is to
        # expensive in terms of performance.
        # Is managed by `is_analysis_edition_allowed` function
        self._analysis_edit_map = dict()

        # This is used to cache analysis keywords with Point of Capture to
        # reduce the number objects that need to be woken up
        # Is managed by `is_analysis_edition_allowed` function
        self._keywords_poc_map = dict()

        # This is used to cache the objects that have been woken up.
        # Is managed by `_get_object` function
        self._objects_map = dict()

        # This is used to display method and instrument columns if there is at
        # least one analysis to be rendered that allows the assignment of method
        # and/or instrument
        self.show_methodinstr_columns = False

    def has_permission(self, permission, obj=None):
        """Returns if the current user has rights for the permission passed in
        :param permission: permission identifier
        :param obj: object to check the permission against
        :return: True if the user has rights for the permission passed in
        """
        if permission is None:
            logger.warn("None permission is not allowed")
            return False

        if obj is None:
            obj = self.context

        obj_uid = api.get_uid(obj)
        if obj_uid not in self._permissions_map:
            self._permissions_map[obj_uid] = dict()

        obj_permissions = self._permissions_map[obj_uid]
        if permission not in obj_permissions:
            allowed = check_permission(permission, obj)
            self._permissions_map[obj_uid][permission] = allowed

        return self._permissions_map[obj_uid][permission]

    def is_analysis_edition_allowed(self, analysis_brain):
        """Returns if the analysis passed in can be edited by the current user
        :param analysis_brain: Brain that represents an analysis
        :return: True if the user can edit the analysis, otherwise False"""

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

        analysis_uid = analysis_brain.UID
        if analysis_uid in self._analysis_edit_map:
            # This analysis has been checked before, no need to go further
            return self._analysis_edit_map[analysis_uid]

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
                # Cache the value, so further checks for edition for this
                # specific analysis and user will be resolved rapidly
                self._analysis_edit_map[analysis_uid] = False
                return False

        elif not self.has_permission(EditResults):
            # The Point of Capture is 'lab' and the current user cannot edit
            # lab analyses. Cache the value, so further checks for edition for
            # this specific analysis and user will be resolved rapidly
            self._analysis_edit_map[analysis_uid] = False
            return False

        analysis_obj = analysis_obj or api.get_object(analysis_brain)
        if wasTransitionPerformed(analysis_obj, 'submit'):
            # Analysis has been already submitted. This analysis cannot be
            # edited anymore. Cache the value, so further checks for edition for
            # this specific analysis and user will be resolved rapidly
            self._analysis_edit_map[analysis_uid] = False
            return False

        # Is the instrument out of date?
        # The user can assign a result to the analysis if it does not have any
        # instrument assigned or the instrument assigned is valid.
        instrument_valid = self.is_analysis_instrument_valid(analysis_brain)
        self._analysis_edit_map[analysis_uid] = instrument_valid
        return instrument_valid

    def is_analysis_instrument_valid(self, analysis_brain):
        """Return if the analysis has a valid instrument. If the analysis passed
        in is from ReferenceAnalysis type or does not have an instrument
        assigned, returns True
        :param analysis_brain: Brain that represents an analysis
        :return: True if the instrument assigned is valid or is None"""

        # TODO: Workflow. All this logic will be considered in submit guard

        if analysis_brain.meta_type == 'ReferenceAnalysis':
            # If this is a ReferenceAnalysis, there is no need to check the
            # validity of the instrument, because this is a QC analysis and by
            # definition, it has the ability to promote an instrument to a
            # valid state if the result is correct.
            return True

        instrument = self.get_instrument(analysis_brain)
        if not instrument:
            return True

        return instrument.isValid()

    def get_instrument(self, analysis_brain):
        """Returns the instrument assigned to the analysis passed in, if any
        :param analysis_brain: Brain that represents an analysis
        :return: Instrument object or None"""
        instrument_uid = analysis_brain.getInstrumentUID
        if not instrument_uid:
            return None

        if instrument_uid not in self._instruments_map:
            instrument = api.get_object_by_uid(instrument_uid, None)
            if not instrument:
                return None
            self._instruments_map[instrument_uid] = instrument

        return self._instruments_map[instrument_uid]

    def get_analysis_spec(self, analysis):
        """
        Returns the dictionary with the result specifications (min, max,
        error, etc.) that apply to the passed in Analysis or ReferenceAnalysis.
        If no specifications are found, returns a basic specifications dict
        with the following structure:
            {'keyword': <analysis_service_keyword,
             'uid': <analysis_uid>,
             'min': ''
             'max': ''
             'error': ''}

        :param analysis: A single Analysis brain or Content object
        :type analysis: bika.lims.content.analysis.Analysis
                        bika.lims.content.referenceanalysis.ReferenceAnalysis
                        CatalogBrain
        :returns: The result specifications that apply to the Analysis.
        :rtype: dict
        """
        if api.is_brain(analysis):
            # This is a brain
            uid = analysis.UID
            keyword = analysis.getKeyword
            range = analysis.getResultsRange
        else:
            # This is an object
            uid = analysis.UID()
            keyword = analysis.getKeyword()
            range = analysis.getResultsRange()

        default = {'keyword': keyword, 'uid': uid,
                   'min': '', 'max': '', 'error': ''}
        range = range or default
        if isinstance(range, list):
            # Convert the list of dicts to a dictionary
            # TODO: Is this required? Why?
            range = dicts_to_dict(range, 'keyword')
            range = range.get(keyword, None) or default
        return range

    def ResultOutOfRange(self, analysis):
        """ Template wants to know, is this analysis out of range?
        We scan IResultOutOfRange adapters, and return True if any IAnalysis
        adapters trigger a result.
        """
        spec = self.get_analysis_spec(analysis)
        # The function get_analysis_spec ALWAYS return a dict. If no specs
        # are found for the analysis, returns a dict with empty values for
        # min and max keys.
        if not spec or (not spec.get('min') and not spec.get('max')):
            return False
        # The analysis has specs defined, evaluate if is out of range
        adapters = getAdapters((analysis,), IResultOutOfRange)
        for name, adapter in adapters:
            if adapter(specification=spec):
                return True
        # By default, not out of range
        return False

    def get_methods_vocabulary(self, analysis=None):
        """
        Returns a vocabulary with all the methods available for the passed in
        analysis, either those assigned to an instrument that are capable to
        perform the test (option "Allow Entry of Results") and those assigned
        manually in the associated Analysis Service. If the associated
        Analysis Service has a "None" method assigned by default (also if
        the Analysis Service has instruments with methods assigned), a "None"
        option is added in the vocabulary.
        If the analysis passed in is None, returns a vocabulary with all the
        methods available in the system.
        The vocabulary is a list of dictionaries. Each dictionary has the
        following structure:
            {'ResultValue': <method_UID>,
             'ResultText': <method_Title>}

        :param analysis: A single Analysis brain
        :type analysis: CatalogBrain
        :returns: A list of dicts
        """
        ret = []
        if analysis:
            # This function returns  a list of tuples as [(UID,Title),(),...]
            uids = analysis.getAllowedMethodUIDs
            # inactive_state is not specified below, because it is not relevant.
            # If the analysis was created with some method, that is the method
            # we want to permit the user select.
            brains = self.bsc(portal_type='Method', UID=uids)
        else:
            # All active methods
            brains = self.bsc(portal_type='Method', inactive_state='active')
        for brain in brains:
            ret.append({'ResultValue': brain.UID,
                        'ResultText': brain.Title})
        if not ret:
            ret = [{'ResultValue': '',
                    'ResultText': _('None')}]
        return ret

    def get_instruments_vocabulary(self, analysis_brain):
        """Returns a vocabulary with the valid and active instruments available
        for the analysis passed in.
        If the analysis is None, the function returns all the active and
        valid instruments registered in the system.
        If the option "Allow instrument entry of results" for the Analysis
        is disabled, the function returns an empty vocabulary.
        If the analysis passed in is a Reference Analysis (Blank or Control),
        the voculabury, the invalid instruments will be included in the
        vocabulary too.
        The vocabulary is a list of dictionaries. Each dictionary has the
        following structure:
            {'ResultValue': <instrument_UID>,
             'ResultText': <instrument_Title>}

        :param analysis_brain: A single Analysis or ReferenceAnalysis
        :type analysis_brain: Analysis or.ReferenceAnalysis
        :returns: A vocabulary with the instruments for the analysis
        :rtype: A list of dicts: [{'ResultValue':UID, 'ResultText':Title}]
        """
        ret = []
        if not analysis_brain or not analysis_brain.getInstrumentEntryOfResults:
            return []

        bsc = getToolByName(self.context, 'bika_setup_catalog')

        m_uid = analysis_brain.getMethodUID
        method = None
        if m_uid:
            # inactive_state is not specified below, because it is not relevant.
            # If the analysis was created with some method, that is the method
            # we want to permit the user select.
            brains = bsc(portal_type='Method', UID=m_uid)
            method = brains[0].getObject() if brains else None
        if method:
            instruments = method.getInstruments()
        else:
            i_uids = analysis_brain.getAllowedInstrumentUIDs
            brains = bsc(
                portal_type='Instrument', UID=i_uids, inactive_state='active')
            instruments = [b.getObject() for b in brains]

        for ins in instruments:
            if analysis_brain.meta_type in [
                'ReferenceAnalysis', 'DuplicateAnalysis'] \
                    and not ins.isOutOfDate():
                # Add the 'invalid', but in-date instrument
                ret.append({'ResultValue': ins.UID(),
                            'ResultText': ins.Title()})
            if ins.isValid():
                # Only add the 'valid' instruments: certificate
                # on-date and valid internal calibration tests
                ret.append({'ResultValue': ins.UID(),
                            'ResultText': ins.Title()})

        ret.insert(0, {'ResultValue': '',
                       'ResultText': _('None')})
        return ret

    def getAnalysts(self):
        analysts = getUsers(self.context, ['Manager', 'LabManager', 'Analyst'])
        analysts = analysts.sortedByKey()
        ret = []
        for a in analysts:
            ret.append({'ResultValue': a,
                        'ResultText': analysts.getValue(a)})
        return ret

    def isItemAllowed(self, obj):
        """
        Checks if the passed in Analysis must be displayed in the list. If the
        'filtering by department' option is enabled in Bika Setup, this
        function checks if the Analysis Service associated to the Analysis
        is assigned to any of the currently selected departments (information
        stored in a cookie).
        If department filtering is disabled in bika_setup, returns True.
        If the obj is None or empty, returns False.
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
                not has_permission(ViewRetractedAnalyses):
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

    def _folder_item_css_class(self, analysis_brain, item):
        """Sets the suitable css class name(s) to `table_row_class` from the
        item passed in, depending on the properties of the analysis object
        :analysis_brain: Brain that represents an analysis
        :item: analysis' dictionary counterpart to be represented as a row"""
        row_class = item.get('table_row_class', '')
        is_reference = analysis_brain.meta_type == 'ReferenceAnalysis'
        is_duplicate = analysis_brain.meta_type == 'DuplicateAnalysis'
        qc_class_name = 'qc-analysis'
        # If this is a Reference Analysis or a Duplicate from a Reference
        # Analysis, add the css class 'qc-analysis' accordingly.
        if is_reference:
            row_class = '{} {}'.format(row_class, qc_class_name)
            item['table_row_class'] = row_class
            return

        if is_duplicate:
            if analysis_brain.getAnalysisPortalType == 'ReferenceAnalysis':
                # This a duplicate from a ReferenceAnalysis
                row_class = '{} {}'.format(row_class, qc_class_name)
                item['table_row_class'] = row_class

    def _folder_item_duedate(self, obj, item):
        # Set the analysis' due date. Note that if a Reference Analysis, the
        # getDueDate returns the date when the ReferenceSample expires. If the
        # analysis is a duplicate, returns the due date of the source analysis.
        due_date = obj.getDueDate
        due_date_str = self.ulocalized_time(due_date, long_format=0)
        item['DueDate'] = due_date_str

        # If the Analysis is late/overdue, display an icon
        capture_date = obj.getResultCaptureDate
        capture_date = capture_date or DateTime()
        if capture_date > due_date:
            # The analysis is late or overdue
            img_src = '{}/++resource++bika.lims.images/late.png'
            img_src = img_src.format(self.portal_url)
            html = '{} <img width="16" height="16" src="{}" title="{}"/>'
            html = html.format(due_date_str, img_src, t(_("Late Analysis")))
            item['replace']['DueDate'] = html

    def _folder_item_result(self, obj, item):
        item['Result'] = ''
        if not self.has_permission(ViewResults, obj):
            img_src = "{}/++resource++bika.lims.images/to_follow.png"
            img_src = img_src.format(self.portal_url)
            img = '<img width="16" height="16" src="{}"/>'.format(img_src)
            item['before']['Result'] = img
            return

        result = obj.getResult
        capture_date = obj.getResultCaptureDate
        capture_date_str = self.ulocalized_time(capture_date, long_format=0)
        item['Result'] = result
        item['CaptureDate'] = capture_date_str
        item['result_captured'] = capture_date_str

        # If this analysis has a predefined set of options as result, tell the
        # template that selection list (choices) must be rendered instead of an
        # input field for the introduction of result.
        choices = obj.getResultOptions
        if choices:
            item['choices']['Result'] = choices

        if self.is_analysis_edition_allowed(obj):
            item['allow_edit'].extend(['Result', 'Remarks'])

        # Wake up the object only if necessary. If there is no result set, then
        # there is no need to go further with formatted result
        if result is None or result == '':
            return

        # TODO: Performance, we wake-up the full object here
        full_obj = self._get_object(obj)
        formatted_result = full_obj.getFormattedResult(
                            sciformat=int(self.scinot), decimalmark=self.dmk)
        item['formatted_result'] = formatted_result

    def _folder_item_calculation(self, obj, item):
        is_editable = self.is_analysis_edition_allowed(obj)
        # Set interim fields. Note we add the key 'formatted_value' to the list
        # of interims the analysis has assigned already.
        interim_fields = obj.getInterimFields or list()
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

        # Set calculation
        calculation_uid = obj.getCalculationUID
        has_calculation = calculation_uid and True or False
        item['calculation'] = has_calculation
        if is_editable and (not has_calculation or interim_fields):
            # If the analysis is editable and doesn't have a calculation or it
            # does, but has interim fields, it must be re-testable.
            item['allow_edit'].append('retested')

    def _folder_item_method(self, obj, item):
        is_editable = self.is_analysis_edition_allowed(obj)
        method_title = obj.getMethodTitle
        item['Method'] = method_title or ''
        if is_editable:
            method_vocabulary = self.get_methods_vocabulary(obj)
            if method_vocabulary:
                item['Method'] = obj.getMethodUID
                item['choices']['Method'] = method_vocabulary
                item['allow_edit'].append('Method')
                self.show_methodinstr_columns = True
        elif method_title:
            item['replace']['Method'] = get_link(obj.getMethodURL, method_title)
            self.show_methodinstr_columns = True

    def _folder_item_instrument(self, obj, item):
        item['Instrument'] = ''
        if not obj.getInstrumentEntryOfResults:
            # Manual entry of results, instrument is not allowed
            item['Instrument'] = _('Manual')
            msgtitle = t(_(
                "Instrument entry of results not allowed for ${service}",
                mapping={"service": obj.Title},
            ))
            item['replace']['Instrument'] = \
                '<a href="#" title="%s">%s</a>' % (msgtitle, t(_('Manual')))
            return

        # Instrument can be assigned to this analysis
        is_editable = self.is_analysis_edition_allowed(obj)
        self.show_methodinstr_columns = True
        instrument = self.get_instrument(obj)
        if is_editable:
            # Edition allowed
            voc = self.get_instruments_vocabulary(obj)
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
        item['choices']['Analyst'] = self.getAnalysts()
        item['allow_edit'].append('Analyst')

    def _folder_item_attachments(self, obj, item):
        item['Attachments'] = ''
        at_uids = obj.getAttachmentUIDs
        if not at_uids:
            return

        if not self.has_permission(ViewResults, obj):
            return

        attachments_html = []
        attachments = api.search({'UID': at_uids}, 'uid_catalog')
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
            url = url.format(attachment.absolute_url)
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
        if result is None or result == '':
            # Wake up the object only if necessary. If this analysis has no
            # result set yet, there is no need to go further with Uncertainty
            return

        # TODO: Performance, we wake-up the full object here
        full_obj = self._get_object(obj)
        formatted = format_uncertainty(full_obj, result, decimalmark=self.dmk,
                                       sciformat=int(self.scinot))
        if formatted:
            item['Uncertainty'] = formatted
            item['before']['Uncertainty'] = '&plusmn;&nbsp;'
            after = '<em class="discreet" style="white-space:nowrap;"> {}</em>'
            item['after']['Uncertainty'] = after.format(obj.getUnit)
            item['structure'] = True

        is_editable = self.is_analysis_edition_allowed(obj)
        if is_editable and full_obj.getAllowManualUncertainty():
            # User can set the value of uncertainty manually
            uncertainty = full_obj.getUncertainty(result)
            item['Uncertainty'] = uncertainty or ''
            item['allow_edit'].append('Uncertainty')
            item['structure'] = False

    def _folder_item_detection_limits(self, obj, item):
        is_editable = self.is_analysis_edition_allowed(obj)
        if not is_editable:
            return

        # TODO: Performance, we wake-up the full object here
        full_obj = self._get_object(obj)
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

        if full_obj.getDetectionLimitSelector():
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

    def _folder_item_specifications(self, obj, item):
        # Everyone can see valid-ranges
        item['Specification'] = ''
        spec = self.get_analysis_spec(obj)
        if not spec:
            return
        min_val = spec.get('min', '')
        min_str = ">{0}".format(min_val) if min_val else ''
        max_val = spec.get('max', '')
        max_str = "<{0}".format(max_val) if max_val else ''
        error_val = spec.get('error', '')
        error_str = "{0}%".format(error_val) if error_val else ''
        rngstr = ",".join([x for x in [min_str, max_str, error_str] if x])
        item['Specification'] = rngstr

    def _folder_item_verify_criteria(self, obj, item):
        submitter = obj.getSubmittedBy
        if not submitter:
            return

        after_key = 'state_title'
        if submitter in obj.getVerificators.split(','):
            # If analysis has been submitted and verified by the same person,
            # display a warning icon
            msg = t(_("Submitted and verified by the same user: {}"))
            msg = msg.format(submitter)
            icon = "<img src='{}/++resource++bika.lims.images/warning.png'" \
                   " title='{}'/>".format(self.portal_url, msg)
            self._append_after_element(item, after_key, icon)

        if obj.review_state != 'to_be_verified':
            return

        numverifications = obj.getNumberOfRequiredVerifications
        pending = numverifications
        if numverifications > 1:
            # More than one verification required, place an icon
            # Get the number of verifications already done:
            done = obj.getNumberOfVerifications
            pending = numverifications - done
            ratio = float(done) / float(numverifications) if done > 0 else 0
            ratio = int(ratio*100)
            scale = ratio == 0 and 0 or (ratio/25)*25
            anchor = "<a href='#' title='{} &#13;{} {}' " \
                     "class='multi-verification scale-{}'>{}/{}</a>"
            anchor = anchor.format(t(_("Multi-verification required")),
                                   str(pending),
                                   t(_("verification(s) pending")),
                                   str(scale),
                                   str(done),
                                   str(numverifications))
            self._append_after_element(item, after_key, anchor)

        # Check if the user has "Bika: Verify" privileges
        username = self.member.getUserName()
        verify_permission = has_permission(VerifyPermission, username=username)
        if not verify_permission:
            return

        self_submitted = submitter == username
        # The submitter and the user must be different unless the analysis
        # has the option SelfVerificationEnabled set to true
        selfverification = obj.isSelfVerificationEnabled
        isUserAllowedToVerify = not (self_submitted and not selfverification)
        if not isUserAllowedToVerify:
            img = '/++resource++bika.lims.images/submitted-by-current-user.png'
            title = t(_("Multi-verification by same user is not allowed"))
            html = '<img src="{}/{}" title="{}"/>'.format(self.portal_url, img,
                                                          title)
            self._append_after_element(item, after_key, html)
            return

        if isUserAllowedToVerify and  numverifications > 1:


        # Are they the same? TODO
        username = self.member.getUserName()
        user_id = self.member.getUser().getId()
        isUserAllowedToVerify = True
        # Check if the user who submited the result is the same as the
        # current one
        self_submitted = submitter == user_id
        # The submitter and the user must be different unless the analysis
        # has the option SelfVerificationEnabled set to true
        selfverification = obj.isSelfVerificationEnabled
        if verify_permission and self_submitted and not selfverification:
            isUserAllowedToVerify = False
        # Checking verifiability depending on multi-verification type
        # of bika_setup
        if isUserAllowedToVerify and numverifications > 1:
            # If user verified before and self_multi_disabled, then
            # return False
            if self.mv_type == 'self_multi_disabled' and \
                            username in obj.getVerificators.split(','):
                isUserAllowedToVerify = False
            # If user is the last verificator and consecutively
            # multi-verification is disabled, then return False
            # Comparing was added just to check if this method is called
            # before/after verification
            elif self.mv_type == 'self_multi_not_cons' and \
                            username == obj.getLastVerificator and \
                            pending > 0:
                isUserAllowedToVerify = False
        if verify_permission and not isUserAllowedToVerify:
            after_icons.append(
                "<img src='++resource++bika.lims.images/submitted"
                "-by-current-user.png' title='%s'/>" %
                (t(_(
                    "Cannot verify, submitted or"
                    " verified by current user before")))
            )
        elif verify_permission and isUserAllowedToVerify:
            if submitter == user_id:
                after_icons.append(
                    "<img src='++resource++bika.lims.images/warning.png'"
                    " title='%s'/>" %
                    (t(_("Can verify, but submitted by current user")))
                )

    def _append_after_element(self, item, element, html, glue="&nbsp;"):
        item['after'] = item.get('after', {})
        original = item['after'].get(element, '')
        if not original:
            item['after'][element] = html
            return
        item['after'][element] = glue.join([original, html])

    def _get_object(self, brain_object):
        uid = api.get_uid(brain_object)
        if uid not in self._objects_map:
            logger.warn('Waking up object {} ({}): {}'.format(brain_object.getId, brain_object.Title, brain_object.UID))
            obj = api.get_object(brain_object)
            self._objects_map[uid] = obj
            logger.warn("Cached objects: {}".format(len(self._objects_map)))
        return self._objects_map[uid]

    def folderitem(self, obj, item, index):
        """
        Obj should be a brain
        """
        # Additional info from AnalysisRequest to be added in the item
        # generated by default by bikalisting.

        # Getting the dictionary values
        unit = obj.getUnit
        if self.show_categories:
            cat = obj.getCategoryTitle
            cat_order = self.analysis_categories_order.get(cat)
            item['category'] = cat
            if (cat, cat_order) not in self.categories:
                self.categories.append((cat, cat_order))

        item['service_uid'] = obj.getServiceUID
        item['Keyword'] = obj.getKeyword
        item['Unit'] = format_supsub(unit) if unit else ''
        item['Remarks'] = obj.getRemarks
        item['Uncertainty'] = ''
        item['DetectionLimit'] = ''
        item['retested'] = obj.getRetested
        item['class']['retested'] = 'center'

        # Note that getSampleTypeUID returns the type of the Sample, no matter
        # if the sample associated to the analysis is a regular Sample (routine
        # analysis) or if is a Reference Sample (Reference Analysis). If the
        # analysis is a duplicate, it returns the Sample Type of the sample
        # associated to the source analysis.
        item['st_uid'] = obj.getSampleTypeUID

        # TODO: Is this necessary? If so, why?
        if self.has_permission(ManageBika):
            item['Service'] = obj.Title
            item['class']['Service'] = "service_title"

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
        self._folder_item_verify_criteria(obj, item)

        # add icon for assigned analyses in AR views
        full_obj = api.get_object(obj)
        if self.context.meta_type == 'AnalysisRequest':
            if obj.meta_type in ['ReferenceAnalysis',
                                   'DuplicateAnalysis'] or \
                            obj.worksheetanalysis_review_state == 'assigned':
                full_obj = full_obj if full_obj else obj.getObject()
                br = full_obj.getBackReferences('WorksheetAnalysis')
                if len(br) > 0:
                    ws = br[0]
                    after_icons.append(
                        "<a href='%s'><img "
                        "src='++resource++bika.lims.images/worksheet.png' "
                        "title='%s'/></a>" %
                        (ws.absolute_url(),
                         t(_("Assigned to: ${worksheet_id}",
                             mapping={'worksheet_id': safe_unicode(ws.id)}))))
        item['after']['state_title'] = '&nbsp;'.join(after_icons)
        after_icons = []
        if obj.getIsReflexAnalysis:
            after_icons.append("<img\
            src='%s/++resource++bika.lims.images/reflexrule.png'\
            title='%s'>" % (
                self.portal_url,
                t(_('It comes form a reflex rule'))
            ))
        item['after']['Service'] = '&nbsp;'.join(after_icons)


        # Users that can Add Analyses to an Analysis Request must be able to
        # set the visibility of the analysis in results report, also if the
        # current state of the Analysis Request (e.g. verified) does not allow
        # the edition of other fields. Note that an analyst has no privileges
        # by default to edit this value, cause this "visibility" field is
        # related with results reporting and/or visibility from the client side.
        # This behavior only applies to routine analyses, the visibility of QC
        # analyses is managed in publish and are not visible to clients.
        if 'Hidden' in self.columns:
            # TODO Performance. Use brain instead
            full_obj = full_obj if full_obj else obj.getObject()
            item['Hidden'] = full_obj.getHidden()
            if IRoutineAnalysis.providedBy(full_obj):
                    item['allow_edit'].append('Hidden')

        # Renders additional icons to be displayed for this item, if any
        self._folder_item_fieldicons(obj)

        return item

    def _folder_item_fieldicons(self, obj):
        """Resolves if field-specific icons must be displayed for the object
        passed in.
        """
        uid = api.get_uid(obj)
        full_obj = api.get_object(obj)
        for name, adapter in getAdapters((full_obj,), IFieldIcons):
            alerts = adapter()
            if not alerts or uid not in alerts:
                continue
            alerts = alerts[uid]
            if uid not in self.field_icons:
                self.field_icons[uid] = alerts
                continue
            self.field_icons[uid].extend(alerts)

    def folderitems(self):
        # Check if mtool has been initialized
        self.mtool = self.mtool if self.mtool \
            else getToolByName(self.context, 'portal_membership')
        # Getting the current user
        self.member = self.member if self.member \
            else self.mtool.getAuthenticatedMember()
        # Getting analysis categories
        analysis_categories = self.bsc(
            portal_type="AnalysisCategory",
            sort_on="sortable_title")
        # Sorting analysis categories
        self.analysis_categories_order = dict([
            (b.Title, "{:04}".format(a)) for a, b in
            enumerate(analysis_categories)])
        # Can the user edit?
        if not self.allow_edit:
            can_edit_analyses = False
        else:
            checkPermission = self.mtool.checkPermission
            if self.contentFilter.get('getPointOfCapture', '') == 'field':
                can_edit_analyses = checkPermission(
                    EditFieldResults, self.context)
            else:
                can_edit_analyses = checkPermission(EditResults, self.context)
            self.allow_edit = can_edit_analyses
        self.show_select_column = self.allow_edit

        # Users that can Add Analyses to an Analysis Request must be able to
        # set the visibility of the analysis in results report, also if the
        # current state of the Analysis Request (e.g. verified) does not allow
        # the edition of other fields. Note that an analyst has no privileges
        # by default to edit this value, cause this "visibility" field is
        # related with results reporting and/or visibility from the client side.
        # This behavior only applies to routine analyses, the visibility of QC
        # analyses is managed in publish and are not visible to clients.
        if not self.mtool.checkPermission(AddAnalysis, self.context):
            self.remove_column('Hidden')

        self.categories = []
        # Getting the multi-verification type of bika_setup
        self.mv_type = self.context.bika_setup.getTypeOfmultiVerification()
        self.show_methodinstr_columns = False
        self.dmk = self.context.bika_setup.getResultsDecimalMark()
        self.scinot = self.context.bika_setup.getScientificNotationResults()
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

        if can_edit_analyses:
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

        # Dry Matter.
        # The Dry Matter column is never enabled for reference sample contexts
        # and refers to getReportDryMatter in ARs.
        if items and \
                (hasattr(self.context, 'getReportDryMatter') and \
                         self.context.getReportDryMatter()):

            # look through all items
            # if the item's Service supports ReportDryMatter, add getResultDM().
            for item in items:
                full_object = item['obj'].getObject()
                if full_object.getReportDryMatter():
                    dry_matter = full_object.getResultDM()
                    item['ResultDM'] = dry_matter
                else:
                    item['ResultDM'] = ''
                if item['ResultDM']:
                    item['after']['ResultDM'] = "<em class='discreet'>%</em>"

            # modify the review_states list to include the ResultDM column
            new_states = []
            for state in self.review_states:
                pos = 'Result' in state['columns'] and \
                      state['columns'].index('Uncertainty') + 1 or len(
                    state['columns'])
                state['columns'].insert(pos, 'ResultDM')
                new_states.append(state)
            self.review_states = new_states

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


class QCAnalysesView(AnalysesView):
    """ Renders the table of QC Analyses performed related to an AR. Different
        AR analyses can be achieved inside different worksheets, and each one
        of these can have different QC Analyses. This table only lists the QC
        Analyses performed in those worksheets in which the current AR has, at
        least, one analysis assigned and if the QC analysis services match with
        those from the current AR.
    """

    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request, **kwargs)
        self.columns['getReferenceAnalysesGroupID'] = {
            'title': _('QC Sample ID'),
            'sortable': False}
        self.columns['Worksheet'] = {'title': _('Worksheet'),
                                     'sortable': False}
        self.review_states[0]['columns'] = ['Service',
                                            'Worksheet',
                                            'getReferenceAnalysesGroupID',
                                            'Partition',
                                            'Method',
                                            'Instrument',
                                            'Result',
                                            'Uncertainty',
                                            'CaptureDate',
                                            'DueDate',
                                            'state_title']

        qcanalyses = context.getQCAnalyses()
        asuids = [an.UID() for an in qcanalyses]
        self.contentFilter = {'UID': asuids,
                              'sort_on': 'getId'}
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/referencesample.png"

    # TODO-performance: Do not use object. Using brain, use meta_type in
    # order to get the object's type
    def folderitem(self, obj, item, index):
        """
        obj should be a brain
        """
        obj = obj.getObject()
        # Group items by RefSample - Worksheet - Position
        wss = obj.getBackReferences('WorksheetAnalysis')
        wsid = wss[0].id if wss and len(wss) > 0 else ''
        wshref = wss[0].absolute_url() if wss and len(wss) > 0 else None
        if wshref:
            item['replace']['Worksheet'] = "<a href='%s'>%s</a>" % (
                wshref, wsid)

        imgtype = ""
        if obj.portal_type == 'ReferenceAnalysis':
            antype = QCANALYSIS_TYPES.getValue(obj.getReferenceType())
            if obj.getReferenceType() == 'c':
                imgtype = "<img title='%s' " \
                          "src='%s/++resource++bika.lims.images/control.png" \
                          "'/>&nbsp;" % (
                              antype, self.context.absolute_url())
            if obj.getReferenceType() == 'b':
                imgtype = "<img title='%s' " \
                          "src='%s/++resource++bika.lims.images/blank.png" \
                          "'/>&nbsp;" % (
                              antype, self.context.absolute_url())
            item['replace']['Partition'] = "<a href='%s'>%s</a>" % (
                obj.aq_parent.absolute_url(), obj.aq_parent.id)
        elif obj.portal_type == 'DuplicateAnalysis':
            antype = QCANALYSIS_TYPES.getValue('d')
            imgtype = "<img title='%s' " \
                      "src='%s/++resource++bika.lims.images/duplicate.png" \
                      "'/>&nbsp;" % (
                          antype, self.context.absolute_url())
            item['sortcode'] = '%s_%s' % (obj.getSample().id, obj.getKeyword())

        item['before']['Service'] = imgtype
        item['sortcode'] = '%s_%s' % (obj.getReferenceAnalysesGroupID(),
                                      obj.getKeyword())
        return item

    def folderitems(self):
        items = AnalysesView.folderitems(self)
        # Sort items
        items = sorted(items, key=itemgetter('sortcode'))
        return items
