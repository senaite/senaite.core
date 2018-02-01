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
from bika.lims import logger
from bika.lims.utils import t, dicts_to_dict, format_supsub
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.permissions import *
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.utils import isActive
from bika.lims.utils import getUsers
from bika.lims.utils import formatDecimalMark
from DateTime import DateTime
from operator import itemgetter
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ZCatalog.interfaces import ICatalogBrain
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
        if ICatalogBrain.providedBy(analysis):
            # It is a brain
            if not 'getResultsRange' in dir(analysis):
                pass
            if analysis.getResultsRange and not \
                    isinstance(analysis.getResultsRange, list):
                return analysis.getResultsRange
            if analysis.getResultsRange and \
                    isinstance(analysis.getResultsRange, list):
                rr = dicts_to_dict(
                    analysis.getResultsRange, 'keyword')
                return rr.get(analysis.getKeyword, None)
            if analysis.getReferenceResults:
                rr = dicts_to_dict(analysis.getReferenceResults, 'uid')
                return rr.get(analysis.UID, None)
            keyword = analysis.getKeyword
            uid = analysis.UID
            return {
                'keyword': keyword, 'uid': uid, 'min': '',
                'max': '', 'error': ''}

        # It is an object
        if hasattr(analysis, 'getResultsRange'):
            return analysis.getResultsRange()
        if hasattr(analysis.aq_parent, 'getResultsRange'):
            rr = dicts_to_dict(analysis.aq_parent.getResultsRange(), 'keyword')
            return rr.get(analysis.getKeyword(), None)
        if hasattr(analysis.aq_parent, 'getReferenceResults'):
            rr = dicts_to_dict(analysis.aq_parent.getReferenceResults(), 'uid')
            return rr.get(analysis.UID(), None)
        keyword = analysis.getKeyword()
        uid = analysis.UID()
        return {
            'keyword': keyword, 'uid': uid, 'min': '',
            'max': '', 'error': ''}

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

        :param analysis: A single Analysis or ReferenceAnalysis content object
        :type analysis: bika.lims.content.analysis.Analysis
                        bika.lims.content.referenceAnalysis.ReferenceAnalysis
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
                       'ResultText': _('None')});
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

        if not self.context.bika_setup.getAllowDepartmentFiltering():
            # Filtering by department is disabled. Return True
            return True

        # Department filtering is enabled. Check if the Analysis Service
        # associated to this Analysis is assigned to at least one of the
        # departments currently selected.
        depuid = ''
        if ICatalogBrain.providedBy(obj):
            depuid = obj.getDepartmentUID
        else:
            dep = obj.getDepartment()
            depuid = dep.UID() if dep else ''
        deps = self.request.get('filter_by_department_info', '')
        return not depuid or depuid in deps.split(',')

    def folderitem(self, obj, item, index):
        """
        Obj should be a brain
        """
        # Additional info from AnalysisRequest to be added in the item
        # generated by default by bikalisting.

        # Call the folderitem method from the base class
        item = BikaListingView.folderitem(self, obj, item, index)
        checkPermission = self.mtool.checkPermission
        if not item:
            return None
        if not ('obj' in item):
            return None
        if obj.review_state == 'retracted' \
                and not checkPermission(ViewRetractedAnalyses, self.context):
            return None
        # Getting the dictionary values
        result = obj.getResult
        unit = obj.getUnit
        if self.show_categories:
            cat = obj.getCategoryTitle
            cat_order = self.analysis_categories_order.get(cat)
            item['category'] = cat
            if (cat, cat_order) not in self.categories:
                self.categories.append((cat, cat_order))
        # Check for InterimFields attribute on our object,
        interim_fields = obj.getInterimFields
        # TODO: This should never happen, we must ensure that interim_fields
        # is always a list
        if not isinstance(interim_fields, list):
            logger.warn(
                "InterimFields from {} isn't a list " +
                "object. This should never happen".format(obj.getId))
            interim_fields = []
        full_obj = None
        # kick some pretty display values in.
        for x in range(len(interim_fields)):
            interim_fields[x]['formatted_value'] = \
                formatDecimalMark(interim_fields[x]['value'], self.dmk)
        self.interim_fields[obj.UID] = interim_fields
        item['service_uid'] = obj.getServiceUID
        item['Keyword'] = obj.getKeyword
        item['Unit'] = format_supsub(unit) if unit else ''
        item['Result'] = ''
        item['formatted_result'] = ''
        item['interim_fields'] = interim_fields
        item['Remarks'] = obj.getRemarks
        item['Uncertainty'] = ''
        item['DetectionLimit'] = ''
        item['retested'] = obj.getRetested
        item['class']['retested'] = 'center'
        item['result_captured'] = self.ulocalized_time(
            obj.getResultCaptureDate, long_format=0)
        item['calculation'] = obj.getCalculationUID and True or False
        if obj.meta_type == "ReferenceAnalysis":
            item['DueDate'] = self.ulocalized_time(
                obj.getExpiryDate, long_format=0)
        else:
            item['DueDate'] = self.ulocalized_time(
                obj.getDueDate, long_format=1)
        cd = obj.getResultCaptureDate
        item['CaptureDate'] = cd and self.ulocalized_time(
            cd, long_format=1) or ''
        tblrowclass = item.get('table_row_class', '')

        if obj.meta_type == 'ReferenceAnalysis':
            item['st_uid'] = obj.getParentUID
            item['table_row_class'] = ' '.join([tblrowclass, 'qc-analysis'])
        elif obj.meta_type == 'DuplicateAnalysis' and \
                        obj.getAnalysisPortalType == 'ReferenceAnalysis':
            item['st_uid'] = obj.getParentUID
            item['table_row_class'] = \
                ' '.join([tblrowclass, 'qc-analysis'])
        else:
            item['st_uid'] = obj.getSampleTypeUID

        if checkPermission(ManageBika, self.context):
            item['Service'] = obj.Title
            item['class']['Service'] = "service_title"

        # choices defined on Service apply to result fields.
        choices = obj.getResultOptions
        if choices:
            item['choices']['Result'] = choices
        # Editing Field Results is possible while in Sample Due.
        poc = self.contentFilter.get("getPointOfCapture", 'lab')
        # Getting the first edit_analysis permission
        can_edit_analysis = self.allow_edit and self.context_active
        # If the view has edit permissions, lets check if the user has them
        if can_edit_analysis and poc == 'field':
            can_edit_analysis = \
                self.security_manager.checkPermission(
                    EditFieldResults, full_obj)
        if can_edit_analysis and poc != 'field':
            can_edit_analysis = \
                self.security_manager.checkPermission(EditResults, obj)

        allowed_method_states = [
            'to_be_sampled',
            'to_be_preserved',
            'sample_received',
            'sample_registered',
            'sampled',
            'assigned']
        can_edit_analysis = can_edit_analysis and \
                            obj.review_state in allowed_method_states
        # TODO: Getting the instrument object until we define the correct
        # metacolumns for instrument brains.
        instrument_uid = obj.getInstrumentUID
        instrument = None
        if self.bsc is None:
            self.bsc = getToolByName(self.context, 'bika_setup_catalog')
        instrument_brain = self.bsc(UID=instrument_uid)
        isInstrumentValid = True
        if instrument_brain:
            instrument = instrument_brain[0].getObject()
            isInstrumentValid = instrument.isValid()
        # Prevent from being edited if the instrument assigned
        # is not valid (out-of-date or uncalibrated), except if
        # the analysis is a QC with assigned status
        can_edit_analysis =\
            can_edit_analysis and \
            (isInstrumentValid or obj.meta_type == 'ReferenceAnalysis')
        if can_edit_analysis:
            item['allow_edit'].extend([
                'Analyst',
                'Result',
                'Remarks'])
            # if the Result field is editable, our interim fields are too
            for f in self.interim_fields[obj.UID]:
                item['allow_edit'].append(f['keyword'])

            # if there isn't a calculation then result must be re-testable,
            # and if there are interim fields, they too must be re-testable.
            if not item.get('calculation') or \
                    (item['calculation'] and self.interim_fields[obj.UID]):
                item['allow_edit'].append('retested')

        # TODO: Only the labmanager should be able to change the method
        can_set_method = can_edit_analysis \
                         and item['review_state'] in allowed_method_states

        # Display the methods selector if the AS has at least one
        # method assigned
        item['Method'] = ''
        item['replace']['Method'] = ''
        if can_set_method:
            voc = self.get_methods_vocabulary(obj)
            if voc:
                # The service has at least one method available
                item['Method'] = obj.getMethodUID
                item['choices']['Method'] = voc
                item['allow_edit'].append('Method')
                self.show_methodinstr_columns = True
            else:
                method = obj.getMethodUID
                if method:
                    # This should never happen
                    # The analysis has set a method, but its parent
                    # service hasn't any method available O_o
                    item['Method'] = obj.getMethodTitle
                    item['replace']['Method'] = "<a href='%s'>%s</a>" % \
                                                (obj.getMethodURL,
                                                 obj.getMethodTitle)
                    self.show_methodinstr_columns = True
        elif obj.getMethodUID:
            # Edition not allowed, but method set
            item['Method'] = obj.getMethodTitle
            item['replace']['Method'] = "<a href='%s'>%s</a>" % \
                                        (obj.getMethodURL, obj.getMethodTitle)
            self.show_methodinstr_columns = True

        # TODO: Instrument selector dynamic behavior in worksheet Results
        # Only the labmanager must be able to change the instrument to be used.
        # Also, the instrument selection should be done in accordance with the
        # method selected
        # can_set_instrument = service.getInstrumentEntryOfResults() and
        # getSecurityManager().checkPermission(SetAnalysisInstrument, obj)
        can_set_instrument = obj.getInstrumentEntryOfResults \
                             and can_edit_analysis \
                             and item['review_state'] in allowed_method_states

        item['Instrument'] = ''
        item['replace']['Instrument'] = ''
        if obj.getInstrumentEntryOfResults:
            if can_set_instrument:
                # Edition allowed
                voc = self.get_instruments_vocabulary(obj)
                if voc:
                    # The service has at least one instrument available
                    item['Instrument'] = instrument.UID() if instrument else ''
                    item['choices']['Instrument'] = voc
                    item['allow_edit'].append('Instrument')
                    self.show_methodinstr_columns = True

                elif instrument:
                    # This should never happen
                    # The analysis has an instrument set, but the
                    # service hasn't any available instrument
                    item['Instrument'] = instrument.Title()
                    item['replace']['Instrument'] = \
                        "<a href='%s'>%s</a>" % (instrument.absolute_url(),
                                                 instrument.Title())
                    self.show_methodinstr_columns = True

            elif instrument:
                # Edition not allowed, but instrument set
                item['Instrument'] = instrument.Title()
                item['replace']['Instrument'] = \
                    "<a href='%s'>%s</a>" % (instrument.absolute_url(),
                                             instrument.Title())
                self.show_methodinstr_columns = True

        else:
            # Manual entry of results, instrument not allowed
            item['Instrument'] = _('Manual')
            msgtitle = t(_(
                "Instrument entry of results not allowed for ${service}",
                mapping={"service": obj.Title},
            ))
            item['replace']['Instrument'] = \
                '<a href="#" title="%s">%s</a>' % (msgtitle, t(_('Manual')))

        # Sets the analyst assigned to this analysis
        if can_edit_analysis:
            analyst = obj.getAnalyst
            # widget default: current user
            if not analyst:
                analyst = self.mtool.getAuthenticatedMember().getUserName()
            item['Analyst'] = analyst
            item['choices']['Analyst'] = self.getAnalysts()
        else:
            item['Analyst'] = obj.getAnalystName
        # permission to view this item's results and add attachment to it
        can_view_result = \
            self.security_manager.checkPermission(ViewResults, obj)
        can_add_attachment = \
            self.security_manager.checkPermission(AddAttachment, obj)
        # If the analysis service has the option 'attachment' enabled
        if can_add_attachment or can_view_result:
            attachments = ""
            at_uids = obj.getAttachmentUIDs
            if at_uids:
                uc = getToolByName(self.context, 'uid_catalog')
                attachments_objs = [x.getObject() for x in uc(UID=at_uids)]
                for attachment in attachments_objs:
                    af = attachment.getAttachmentFile()
                    icon = af.icon
                    if callable(icon):
                        icon = icon()
                    attachments += \
                        "<span class='attachment' attachment_uid='%s'>" % \
                        (attachment.UID())
                    if icon:
                        attachments += "<img src='%s/%s'/>" % \
                                       (self.portal_url, icon)
                    attachments += \
                        '<a href="%s/at_download/AttachmentFile"/>%s</a>' % \
                        (attachment.absolute_url(), af.filename)
                    if can_edit_analysis:
                        attachments += "<img class='deleteAttachmentButton' " \
                                       "attachment_uid='%s' src='%s'/>" % (
                                           attachment.UID(),
                                           "++resource++bika.lims.images/delete.png")
                    attachments += "</br></span>"
            item['replace']['Attachments'] = attachments[:-12] + "</span>"
        # TODO-performance: This part gets the full object...
        # Only display data bearing fields if we have ViewResults
        # permission, otherwise just put an icon in Result column.
        if can_view_result:
            full_obj = full_obj if full_obj else obj.getObject()
            item['Result'] = result
            item['formatted_result'] = \
                full_obj.getFormattedResult(
                    sciformat=int(self.scinot), decimalmark=self.dmk)

            # LIMS-1379 Allow manual uncertainty value input
            # https://jira.bikalabs.com/browse/LIMS-1379
            fu = format_uncertainty(
                full_obj, result, decimalmark=self.dmk, sciformat=int(
                    self.scinot))
            fu = fu if fu else ''
            if can_edit_analysis and full_obj.getAllowManualUncertainty():
                unc = full_obj.getUncertainty(result)
                item['allow_edit'].append('Uncertainty')
                item['Uncertainty'] = unc if unc else ''
                item['before']['Uncertainty'] = '&plusmn;&nbsp;'
                item['after'][
                    'Uncertainty'] = '<em class="discreet" ' \
                                     'style="white-space:nowrap;"> %s</em>' % \
                                     item['Unit']
                item['structure'] = False
            elif fu:
                item['Uncertainty'] = fu
                item['before']['Uncertainty'] = '&plusmn;&nbsp;'
                item['after'][
                    'Uncertainty'] = '<em class="discreet" ' \
                                     'style="white-space:nowrap;"> %s</em>' % \
                                     item['Unit']
                item['structure'] = True

            # LIMS-1700. Allow manual input of Detection Limits
            # LIMS-1775. Allow to select LDL or UDL defaults in results
            # with readonly mode
            # https://jira.bikalabs.com/browse/LIMS-1700
            # https://jira.bikalabs.com/browse/LIMS-1775
            if can_edit_analysis and \
                    hasattr(full_obj, 'getDetectionLimitOperand') and \
                    hasattr(full_obj, 'getDetectionLimitSelector') and \
                    full_obj.getDetectionLimitSelector():
                isldl = full_obj.isBelowLowerDetectionLimit()
                isudl = full_obj.isAboveUpperDetectionLimit()
                dlval = ''
                if isldl or isudl:
                    dlval = '<' if isldl else '>'
                item['allow_edit'].append('DetectionLimit')
                item['DetectionLimit'] = dlval
                choices = [
                    {'ResultValue': '<', 'ResultText': '<'},
                    {'ResultValue': '>', 'ResultText': '>'}]
                item['choices']['DetectionLimit'] = choices
                self.columns['DetectionLimit']['toggle'] = True
                defdls = {'min': full_obj.getLowerDetectionLimit(),
                          'max': full_obj.getUpperDetectionLimit(),
                          'manual': full_obj.getAllowManualDetectionLimit()}
                defin = \
                    '<input type="hidden" id="DefaultDLS.%s" value=\'%s\'/>'
                defin = defin % (full_obj.UID(), json.dumps(defdls))
                item['after']['DetectionLimit'] = defin

            # LIMS-1769. Allow to use LDL and UDL in calculations.
            # https://jira.bikalabs.com/browse/LIMS-1769
            # Since LDL, UDL, etc. are wildcards that can be used
            # in calculations, these fields must be loaded always
            # for 'live' calculations.
            if can_edit_analysis:
                dls = {'default_ldl': 'none',
                       'default_udl': 'none',
                       'below_ldl': False,
                       'above_udl': False,
                       'is_ldl': False,
                       'is_udl': False,
                       'manual_allowed': False,
                       'dlselect_allowed': False}
                if hasattr(full_obj, 'getDetectionLimits'):
                    dls['below_ldl'] = full_obj.isBelowLowerDetectionLimit()
                    dls['above_udl'] = full_obj.isBelowLowerDetectionLimit()
                    dls['is_ldl'] = full_obj.isLowerDetectionLimit()
                    dls['is_udl'] = full_obj.isUpperDetectionLimit()
                    dls['default_ldl'] = full_obj.getLowerDetectionLimit()
                    dls['default_udl'] = full_obj.getUpperDetectionLimit()
                    dls['manual_allowed'] = \
                        full_obj.getAllowManualDetectionLimit()
                    dls['dlselect_allowed'] = \
                        full_obj.getDetectionLimitSelector()
                dlsin = \
                    '<input type="hidden" id="AnalysisDLS.%s" value=\'%s\'/>'
                dlsin = dlsin % (full_obj.UID(), json.dumps(dls))
                item['after']['Result'] = dlsin

        else:
            item['Specification'] = ""
            if 'Result' in item['allow_edit']:
                item['allow_edit'].remove('Result')
            item['before']['Result'] = \
                '<img width="16" height="16" ' + \
                'src="%s/++resource++bika.lims.images/to_follow.png"/>' % \
                (self.portal_url)

        # Everyone can see valid-ranges
        spec = self.get_analysis_spec(obj)
        if spec:
            min_val = spec.get('min', '')
            min_str = ">{0}".format(min_val) if min_val else ''
            max_val = spec.get('max', '')
            max_str = "<{0}".format(max_val) if max_val else ''
            error_val = spec.get('error', '')
            error_str = "{0}%".format(error_val) if error_val else ''
            rngstr = ",".join([x for x in [min_str, max_str, error_str] if x])
        else:
            rngstr = ""

        item['Specification'] = rngstr
        # Add this analysis' interim fields to the interim_columns list
        for f in self.interim_fields[obj.UID]:
            if f['keyword'] not in self.interim_columns and not f.get('hidden',
                                                                      False):
                self.interim_columns[f['keyword']] = f['title']
            # and to the item itself
            item[f['keyword']] = f
            item['class'][f['keyword']] = 'interim'
        # check if this analysis is late/overdue
        resultdate = obj.getDateSampled \
            if obj.meta_type == 'ReferenceAnalysis' \
            else obj.getResultCaptureDate
        duedate = obj.getExpiryDate \
            if obj.meta_type == 'ReferenceAnalysis' \
            else obj.getDueDate
        item['replace']['DueDate'] = \
            self.ulocalized_time(duedate, long_format=1)

        if item['review_state'] not in ['to_be_sampled',
                                        'to_be_preserved',
                                        'sample_due',
                                        'published']:
            if (resultdate and resultdate > duedate) \
                    or (not resultdate and DateTime() > duedate):
                item['replace'][
                    'DueDate'] = '%s <img width="16" height="16" ' \
                                 'src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                                 (self.ulocalized_time(duedate, long_format=1),
                                  self.portal_url,
                                  t(_("Late Analysis")))

        after_icons = []
        submitter = obj.getSubmittedBy
        # Submitting user may not verify results unless the user is labman
        # or manager and the AS has isSelfVerificationEnabled set to True
        if item['review_state'] == 'to_be_verified':
            # If multi-verification required, place an informative icon
            numverifications = obj.getNumberOfRequiredVerifications
            if numverifications > 1:
                # More than one verification required, place an icon
                # Get the number of verifications already done:
                done = obj.getNumberOfVerifications
                pending = numverifications - done
                ratio = float(done) / float(numverifications) \
                    if done > 0 else 0
                scale = '' if ratio < 0.25 else '25' \
                    if ratio < 0.50 else '50' \
                    if ratio < 0.75 else '75'
                anchor = "<a href='#' title='%s &#13;%s %s' " \
                         "class='multi-verification scale-%s'>%s/%s</a>"
                anchor = anchor % (t(_("Multi-verification required")),
                                   str(pending),
                                   t(_("verification(s) pending")),
                                   scale, str(done), str(numverifications))
                after_icons.append(anchor)
            # Are they the same? TODO
            username = self.member.getUserName()
            user_id = self.member.getUser().getId()
            # Check if the user has "Bika: Verify" privileges
            verify_permission = has_permission(
                VerifyPermission,
                username=username)
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
        # If analysis Submitted and Verified by the same person, then warning
        # icon will appear.
        if submitter and submitter in obj.getVerificators.split(','):
            after_icons.append(
                "<img src='++resource++bika.lims.images/warning.png'"
                " title='%s'/>" %
                (t(_("Submited and verified by the same user- " + submitter)))
            )
        # add icon for assigned analyses in AR views
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
