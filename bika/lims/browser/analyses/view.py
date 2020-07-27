# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from collections import OrderedDict
from copy import copy

from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFPlone.utils import safe_unicode
from plone.memoize import view as viewcache
from zope.component import getAdapters

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api.analysis import get_formatted_interval
from bika.lims.api.analysis import is_out_of_range
from bika.lims.api.analysis import is_result_range_compliant
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import LDL
from bika.lims.config import UDL
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IFieldIcons
from bika.lims.permissions import EditFieldResults
from bika.lims.permissions import EditResults
from bika.lims.permissions import FieldEditAnalysisHidden
from bika.lims.permissions import FieldEditAnalysisResult
from bika.lims.permissions import TransitionVerify
from bika.lims.permissions import ViewResults
from bika.lims.permissions import ViewRetractedAnalyses
from bika.lims.utils import check_permission
from bika.lims.utils import formatDecimalMark
from bika.lims.utils import format_supsub
from bika.lims.utils import getUsers
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.utils import t
from bika.lims.utils.analysis import format_uncertainty


class AnalysesView(BikaListingView):
    """Displays a list of Analyses in a table.

    Visible InterimFields from all analyses are added to self.columns[].
    Keyword arguments are passed directly to bika_analysis_catalog.
    """

    def __init__(self, context, request, **kwargs):
        super(AnalysesView, self).__init__(context, request, **kwargs)

        # prepare the content filter of this listing
        self.contentFilter = dict(kwargs)
        self.contentFilter.update({
            "portal_type": "Analysis",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        })

        # set the listing view config
        self.catalog = CATALOG_ANALYSIS_LISTING
        self.sort_order = "ascending"
        self.context_actions = {}

        self.show_select_row = False
        self.show_select_column = False
        self.show_column_toggles = False
        self.pagesize = 9999999
        self.form_id = "analyses_form"
        self.context_active = api.is_active(context)
        self.interim_fields = {}
        self.interim_columns = OrderedDict()
        self.specs = {}
        self.bsc = api.get_tool("bika_setup_catalog")
        self.portal = api.get_portal()
        self.portal_url = api.get_url(self.portal)
        self.rc = api.get_tool(REFERENCE_CATALOG)
        self.dmk = context.bika_setup.getResultsDecimalMark()
        self.scinot = context.bika_setup.getScientificNotationResults()
        self.categories = []

        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = False

        self.columns = OrderedDict((
            # Although 'created' column is not displayed in the list (see
            # review_states to check the columns that will be rendered), this
            # column is needed to sort the list by create date
            ("created", {
                "title": _("Date Created"),
                "toggle": False}),
            ("Service", {
                "title": _("Analysis"),
                "attr": "Title",
                "index": "sortable_title",
                "sortable": False}),
            ("Method", {
                "title": _("Method"),
                "sortable": False,
                "ajax": True,
                "toggle": True}),
            ("Instrument", {
                "title": _("Instrument"),
                "ajax": True,
                "sortable": False,
                "toggle": True}),
            ("Analyst", {
                "title": _("Analyst"),
                "sortable": False,
                "ajax": True,
                "toggle": True}),
            ("state_title", {
                "title": _("Status"),
                "sortable": False}),
            ("DetectionLimitOperand", {
                "title": _("DL"),
                "sortable": False,
                "ajax": True,
                "autosave": True,
                "toggle": False}),
            ("Result", {
                "title": _("Result"),
                "input_width": "6",
                "input_class": "ajax_calculate numeric",
                "ajax": True,
                "sortable": False}),
            ("Specification", {
                "title": _("Specification"),
                "sortable": False}),
            ("Uncertainty", {
                "title": _("+-"),
                "ajax": True,
                "sortable": False}),
            ("retested", {
                "title": _("Retest"),
                "type": "boolean",
                "sortable": False}),
            ("Attachments", {
                "title": _("Attachments"),
                "sortable": False}),
            ("CaptureDate", {
                "title": _("Captured"),
                "index": "getResultCaptureDate",
                "sortable": False}),
            ("SubmittedBy", {
                "title": _("Submitter"),
                "sortable": False}),
            ("DueDate", {
                "title": _("Due Date"),
                "index": "getDueDate",
                "sortable": False}),
            ("Hidden", {
                "title": _("Hidden"),
                "toggle": True,
                "sortable": False,
                "ajax": True,
                "type": "boolean"}),
        ))

        # Inject Remarks column for listing
        if self.analysis_remarks_enabled():
            self.columns["Remarks"] = {
                "title": "Remarks",
                "toggle": False,
                "sortable": False,
                "type": "remarks",
                "ajax": True,
            }

        self.review_states = [
            {
                "id": "default",
                "title": _("Valid"),
                "contentFilter": {
                    "review_state": [
                        "registered",
                        "unassigned",
                        "assigned",
                        "to_be_verified",
                        "verified",
                        "published",
                    ]
                },
                "columns": self.columns.keys()
            },
            {
                "id": "invalid",
                "contentFilter": {
                    "review_state": [
                        "cancelled",
                        "retracted",
                        "rejected",
                    ]
                },
                "title": _("Invalid"),
                "columns": self.columns.keys(),
            },
            {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys()
             },
        ]

        # This is used to display method and instrument columns if there is at
        # least one analysis to be rendered that allows the assignment of
        # method and/or instrument
        self.show_methodinstr_columns = False

    def update(self):
        """Update hook
        """
        super(AnalysesView, self).update()
        self.load_analysis_categories()

    def before_render(self):
        """Before render hook
        """
        super(AnalysesView, self).before_render()
        self.request.set("disable_plone.rightcolumn", 1)

    @property
    @viewcache.memoize
    def show_partitions(self):
        """Returns whether the partitions must be displayed or not
        """
        if api.get_current_client():
            # Current user is a client contact
            return api.get_setup().getShowPartitions()
        return True

    @viewcache.memoize
    def analysis_remarks_enabled(self):
        """Check if analysis remarks are enabled
        """
        return self.context.bika_setup.getEnableAnalysisRemarks()

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
        return check_permission(permission, api.get_object(obj))

    @viewcache.memoize
    def is_analysis_edition_allowed(self, analysis_brain):
        """Returns if the analysis passed in can be edited by the current user

        :param analysis_brain: Brain that represents an analysis
        :return: True if the user can edit the analysis, otherwise False
        """
        if not self.context_active:
            # The current context must be active. We cannot edit analyses from
            # inside a deactivated Analysis Request, for instance
            return False

        analysis_obj = api.get_object(analysis_brain)
        if analysis_obj.getPointOfCapture() == 'field':
            # This analysis must be captured on field, during sampling.
            if not self.has_permission(EditFieldResults, analysis_obj):
                # Current user cannot edit field analyses.
                return False

        elif not self.has_permission(EditResults, analysis_obj):
            # The Point of Capture is 'lab' and the current user cannot edit
            # lab analyses.
            return False

        # Check if the user is allowed to enter a value to to Result field
        if not self.has_permission(FieldEditAnalysisResult, analysis_obj):
            return False

        # Is the instrument out of date?
        # The user can assign a result to the analysis if it does not have any
        # instrument assigned or the instrument assigned is valid.
        if not self.is_analysis_instrument_valid(analysis_brain):
            # return if it is allowed to enter a manual result
            return analysis_obj.getManualEntryOfResults()

        return True

    @viewcache.memoize
    def is_result_edition_allowed(self, analysis_brain):
        """Checks if the edition of the result field is allowed

        :param analysis_brain: Brain that represents an analysis
        :return: True if the user can edit the result field, otherwise False
        """

        # Always check general edition first
        if not self.is_analysis_edition_allowed(analysis_brain):
            return False

        # Get the ananylsis object
        obj = api.get_object(analysis_brain)

        if not obj.getDetectionLimitOperand():
            # This is a regular result (not a detection limit)
            return True

        # Detection limit selector is enabled in the Analysis Service
        if obj.getDetectionLimitSelector():
            # Manual detection limit entry is *not* allowed
            if not obj.getAllowManualDetectionLimit():
                return False

        return True

    @viewcache.memoize
    def is_uncertainty_edition_allowed(self, analysis_brain):
        """Checks if the edition of the uncertainty field is allowed

        :param analysis_brain: Brain that represents an analysis
        :return: True if the user can edit the result field, otherwise False
        """

        # Only allow to edit the uncertainty if result edition is allowed
        if not self.is_result_edition_allowed(analysis_brain):
            return False

        # Get the ananylsis object
        obj = api.get_object(analysis_brain)

        # Manual setting of uncertainty is not allowed
        if not obj.getAllowManualUncertainty():
            return False

        # Result is a detection limit -> uncertainty setting makes no sense!
        if obj.getDetectionLimitOperand() in [LDL, UDL]:
            return False

        return True

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
                 'is_active': True,
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
                 'is_active': True,
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

    def isItemAllowed(self, obj):
        """Checks if the passed in Analysis must be displayed in the list.
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
        return True

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
        item['retested'] = obj.getRetestOfUID and True or False
        item['class']['retested'] = 'center'

        # Append info link before the service
        # see: bika.lims.site.coffee for the attached event handler
        item["before"]["Service"] = get_link(
            "analysisservice_info?service_uid={}&analysis_uid={}"
            .format(obj.getServiceUID, obj.UID),
            value="<span class='glyphicon glyphicon-info-sign'></span>",
            css_class="service_info")

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
        # Fill submitted by
        self._folder_item_submitted_by(obj, item)
        # Fill attachments
        self._folder_item_attachments(obj, item)
        # Fill uncertainty
        self._folder_item_uncertainty(obj, item)
        # Fill Detection Limits
        self._folder_item_detection_limits(obj, item)
        # Fill Specifications
        self._folder_item_specifications(obj, item)
        self._folder_item_out_of_range(obj, item)
        self._folder_item_result_range_compliance(obj, item)
        # Fill Partition
        self._folder_item_partition(obj, item)
        # Fill Due Date and icon if late/overdue
        self._folder_item_duedate(obj, item)
        # Fill verification criteria
        self._folder_item_verify_icons(obj, item)
        # Fill worksheet anchor/icon
        self._folder_item_assigned_worksheet(obj, item)
        # Fill accredited icon
        self._folder_item_accredited_icon(obj, item)
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
        # This shouldn't be required here, but there are some views that calls
        # directly contents_table() instead of __call__, so before_render is
        # never called. :(
        self.before_render()

        # Gettin all the items
        items = super(AnalysesView, self).folderitems()

        # the TAL requires values for all interim fields on all
        # items, so we set blank values in unused cells
        for item in items:
            for field in self.interim_columns:
                if field not in item:
                    item[field] = ""

        # XXX order the list of interim columns
        interim_keys = self.interim_columns.keys()
        interim_keys.reverse()

        # add InterimFields keys to columns
        for col_id in interim_keys:
            if col_id not in self.columns:
                self.columns[col_id] = {
                    "title": self.interim_columns[col_id],
                    "input_width": "6",
                    "input_class": "ajax_calculate numeric",
                    "sortable": False,
                    "toggle": True,
                    "ajax": True,
                }


        if self.allow_edit:
            new_states = []
            for state in self.review_states:
                # InterimFields are displayed in review_state
                # They are anyway available through View.columns though.
                # In case of hidden fields, the calcs.py should check
                # calcs/services
                # for additional InterimFields!!
                pos = "Result" in state["columns"] and \
                      state["columns"].index("Result") or len(state["columns"])
                for col_id in interim_keys:
                    if col_id not in state["columns"]:
                        state["columns"].insert(pos, col_id)
                # retested column is added after Result.
                pos = "Result" in state["columns"] and \
                      state["columns"].index("Uncertainty") + 1 or len(
                    state["columns"])
                if "retested" in state["columns"]:
                    state["columns"].remove("retested")
                state["columns"].insert(pos, "retested")
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
        self.columns["Method"]["toggle"] = self.show_methodinstr_columns
        self.columns["Instrument"]["toggle"] = self.show_methodinstr_columns

        return items

    def _folder_item_category(self, analysis_brain, item):
        """Sets the category to the item passed in

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        if not self.show_categories:
            return

        cat = analysis_brain.getCategoryTitle
        item["category"] = cat
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
        if not due_date:
            return None
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

        item["Result"] = ""

        if not self.has_permission(ViewResults, analysis_brain):
            # If user has no permissions, don"t display the result but an icon
            img = get_image("to_follow.png", width="16px", height="16px")
            item["before"]["Result"] = img
            return

        result = analysis_brain.getResult
        capture_date = analysis_brain.getResultCaptureDate
        capture_date_str = self.ulocalized_time(capture_date, long_format=0)

        item["Result"] = result
        item["CaptureDate"] = capture_date_str
        item["result_captured"] = capture_date_str
        item["string_result"] = False

        # Edit mode enabled of this Analysis
        if self.is_analysis_edition_allowed(analysis_brain):
            # Allow to set Remarks
            item["allow_edit"].append("Remarks")

            # Set the results field editable
            if self.is_result_edition_allowed(analysis_brain):
                item["allow_edit"].append("Result")

            # Prepare result options
            choices = analysis_brain.getResultOptions
            if choices:
                # N.B.we copy here the list to avoid persistent changes
                choices = copy(choices)
                # By default set empty as the default selected choice
                choices.insert(0, dict(ResultValue="", ResultText=""))
                item["choices"]["Result"] = choices
            else:
                # If not choices, set whether the result must be floatable
                obj = self.get_object(analysis_brain)
                item["string_result"] = obj.getStringResult()

        if not result:
            return

        obj = self.get_object(analysis_brain)
        formatted_result = obj.getFormattedResult(
            sciformat=int(self.scinot), decimalmark=self.dmk)
        item["formatted_result"] = formatted_result

    def _folder_item_calculation(self, analysis_brain, item):
        """Set the analysis' calculation and interims to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """

        if not self.has_permission(ViewResults, analysis_brain):
            # Hide interims and calculation if user cannot view results
            return

        is_editable = self.is_analysis_edition_allowed(analysis_brain)

        # Set interim fields. Note we add the key 'formatted_value' to the list
        # of interims the analysis has already assigned.
        interim_fields = analysis_brain.getInterimFields or list()

        # Copy to prevent to avoid persistent changes
        interim_fields = copy(interim_fields)

        for interim_field in interim_fields:
            interim_keyword = interim_field.get('keyword', '')
            if not interim_keyword:
                continue

            interim_value = interim_field.get("value", "")
            interim_formatted = formatDecimalMark(interim_value, self.dmk)
            interim_field['formatted_value'] = interim_formatted
            item[interim_keyword] = interim_field
            item['class'][interim_keyword] = 'interim'

            # Note: As soon as we have a separate content type for field
            #       analysis, we can solely rely on the field permission
            #       "senaite.core: Field: Edit Analysis Result"
            if is_editable:
                if self.has_permission(FieldEditAnalysisResult, analysis_brain):
                    item['allow_edit'].append(interim_keyword)

            # Add this analysis' interim fields to the interim_columns list
            interim_hidden = interim_field.get('hidden', False)
            if not interim_hidden:
                interim_title = interim_field.get('title')
                self.interim_columns[interim_keyword] = interim_title

            # Does interim's results list needs to be rendered?
            choices = interim_field.get("choices")
            if choices:
                # Get the {value:text} dict
                choices = choices.split("|")
                choices = dict(map(lambda ch: ch.strip().split(":"), choices))

                # Generate the display list
                # [{"ResultValue": value, "ResultText": text},]
                headers = ["ResultValue", "ResultText"]
                d_list = map(lambda it: dict(zip(headers, it)), choices.items())
                item.setdefault("choices", {})[interim_keyword] = d_list

                # Display the text instead of the value
                val = choices.get(interim_value, "")
                interim_field["value"] = val
                item[interim_keyword] = interim_field

        item['interimfields'] = interim_fields
        self.interim_fields[analysis_brain.UID] = interim_fields

        # Set calculation
        calculation_uid = analysis_brain.getCalculationUID
        has_calculation = calculation_uid and True or False
        item['calculation'] = has_calculation

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

    def _folder_item_submitted_by(self, obj, item):
        submitted_by = obj.getSubmittedBy
        if submitted_by:
            user = self.get_user_by_id(submitted_by)
            user_name = user and user.getProperty("fullname") or submitted_by
            item['SubmittedBy'] = user_name

    @viewcache.memoize
    def get_user_by_id(self, user_id):
        return api.get_user(user_id)

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

    def _folder_item_uncertainty(self, analysis_brain, item):
        """Fills the analysis' uncertainty to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """

        item["Uncertainty"] = ""

        if not self.has_permission(ViewResults, analysis_brain):
            return

        result = analysis_brain.getResult

        obj = self.get_object(analysis_brain)
        formatted = format_uncertainty(obj, result, decimalmark=self.dmk,
                                       sciformat=int(self.scinot))
        if formatted:
            item["Uncertainty"] = formatted
            item["before"]["Uncertainty"] = "± "
            item["after"]["Uncertainty"] = obj.getUnit()

        if self.is_uncertainty_edition_allowed(analysis_brain):
            item["allow_edit"].append("Uncertainty")

    def _folder_item_detection_limits(self, analysis_brain, item):
        """Fills the analysis' detection limits to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        item["DetectionLimitOperand"] = ""

        if not self.is_analysis_edition_allowed(analysis_brain):
            # Return immediately if the we are not in edit mode
            return

        # TODO: Performance, we wake-up the full object here
        obj = self.get_object(analysis_brain)

        # No Detection Limit Selection
        if not obj.getDetectionLimitSelector():
            return None

        # Show Detection Limit Operand Selector
        item["DetectionLimitOperand"] = obj.getDetectionLimitOperand()
        item["allow_edit"].append("DetectionLimitOperand")
        self.columns["DetectionLimitOperand"]["toggle"] = True

        # Prepare selection list for LDL/UDL
        choices = [
            {"ResultValue": "", "ResultText": ""},
            {"ResultValue": LDL, "ResultText": LDL},
            {"ResultValue": UDL, "ResultText": UDL}
        ]
        # Set the choices to the item
        item["choices"]["DetectionLimitOperand"] = choices

    def _folder_item_specifications(self, analysis_brain, item):
        """Set the results range to the item passed in"""
        analysis = self.get_object(analysis_brain)
        results_range = analysis.getResultsRange()

        item["Specification"] = ""
        if results_range:
            item["Specification"] = get_formatted_interval(results_range, "")

    def _folder_item_out_of_range(self, analysis_brain, item):
        """Displays an icon if result is out of range
        """
        if not self.has_permission(ViewResults, analysis_brain):
            # Users without permissions to see the result should not be able
            # to see if the result is out of range naither
            return

        analysis = self.get_object(analysis_brain)
        out_range, out_shoulders = is_out_of_range(analysis)
        if out_range:
            msg = _("Result out of range")
            img = get_image("exclamation.png", title=msg)
            if not out_shoulders:
                msg = _("Result in shoulder range")
                img = get_image("warning.png", title=msg)
            self._append_html_element(item, "Result", img)

    def _folder_item_result_range_compliance(self, analysis_brain, item):
        """Displays an icon if the range is different from the results ranges
        defined in the Sample
        """
        if not IAnalysisRequest.providedBy(self.context):
            return

        analysis = self.get_object(analysis_brain)
        if is_result_range_compliant(analysis):
            return

        # Non-compliant range, display an icon
        service_uid = analysis_brain.getServiceUID
        original = self.context.getResultsRange(search_by=service_uid)
        original = get_formatted_interval(original, "")
        msg = _("Result range is different from Specification: {}"
                .format(original))
        img = get_image("warning.png", title=msg)
        self._append_html_element(item, "Specification", img)

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

        verifiers = analysis_brain.getVerificators
        in_verifiers = submitter in verifiers
        if in_verifiers:
            # If analysis has been submitted and verified by the same person,
            # display a warning icon
            msg = t(_("Submitted and verified by the same user: {}"))
            icon = get_image('warning.png', title=msg.format(submitter))
            self._append_html_element(item, 'state_title', icon)

        num_verifications = analysis_brain.getNumberOfRequiredVerifications
        if num_verifications > 1:
            # More than one verification required, place an icon and display
            # the number of verifications done vs. total required
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
        if not self.has_permission(TransitionVerify):
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
            title = t(
                _("Can verify, but was already verified by current user"))
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

        analysis_obj = self.get_object(analysis_brain)
        worksheet = analysis_obj.getWorksheet()
        if not worksheet:
            # No worksheet assigned. Do nothing
            return

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

    def _folder_item_accredited_icon(self, analysis_brain, item):
        """Adds an icon to the item dictionary if it is an accredited analysis
        """
        full_obj = self.get_object(analysis_brain)
        if full_obj.getAccredited():
            img = get_image("accredited.png", title=t(_("Accredited")))
            self._append_html_element(item, "Service", img)

    def _folder_item_partition(self, analysis_brain, item):
        """Adds an anchor to the partition if the current analysis is from a
        partition that does not match with the current context
        """
        if not IAnalysisRequest.providedBy(self.context):
            return

        sample_id = analysis_brain.getRequestID
        if sample_id != api.get_id(self.context):
            if not self.show_partitions:
                # Do not display the link
                return

            part_url = analysis_brain.getRequestURL
            url = get_link(part_url, value=sample_id, **{"class": "small"})
            title = item["replace"].get("Service") or item["Service"]
            item["replace"]["Service"] = "{}<br/>{}".format(title, url)

    def _folder_item_report_visibility(self, analysis_brain, item):
        """Set if the hidden field can be edited (enabled/disabled)

        :analysis_brain: Brain that represents an analysis
        :item: analysis' dictionary counterpart to be represented as a row"""
        # Users that can Add Analyses to an Analysis Request must be able to
        # set the visibility of the analysis in results report, also if the
        # current state of the Analysis Request (e.g. verified) does not allow
        # the edition of other fields. Note that an analyst has no privileges
        # by default to edit this value, cause this "visibility" field is
        # related with results reporting and/or visibility from the client
        # side. This behavior only applies to routine analyses, the visibility
        # of QC analyses is managed in publish and are not visible to clients.
        if 'Hidden' not in self.columns:
            return

        full_obj = self.get_object(analysis_brain)
        item['Hidden'] = full_obj.getHidden()
        if self.has_permission(FieldEditAnalysisHidden, obj=full_obj):
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
        """Renders the Remarks field for the passed in analysis

        If the edition of the analysis is permitted, adds the field into the
        list of editable fields.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """

        if self.analysis_remarks_enabled():
            item["Remarks"] = analysis_brain.getRemarks

        if self.is_analysis_edition_allowed(analysis_brain):
            item["allow_edit"].extend(["Remarks"])
        else:
            # render HTMLified text in readonly mode
            item["Remarks"] = api.text_to_html(
                analysis_brain.getRemarks, wrap=None)

    def _append_html_element(self, item, element, html, glue="&nbsp;",
                             after=True):
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
