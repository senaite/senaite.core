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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from collections import OrderedDict
from copy import copy
from copy import deepcopy
from datetime import datetime
from datetime import timedelta
from operator import itemgetter

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.api.analysis import get_formatted_interval
from bika.lims.api.analysis import is_out_of_range
from bika.lims.api.analysis import is_result_range_compliant
from bika.lims.config import LDL
from bika.lims.config import UDL
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.interfaces import ISubmitted
from bika.lims.utils import check_permission
from bika.lims.utils import format_supsub
from bika.lims.utils import formatDecimalMark
from bika.lims.utils import get_fas_ico
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for
from bika.lims.utils.analysis import format_uncertainty
from DateTime import DateTime
from plone.memoize import view as viewcache
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFPlone.utils import safe_unicode
from senaite.app.listing import ListingView
from senaite.core.api import dtime
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate as t
from senaite.core.permissions import EditFieldResults
from senaite.core.permissions import EditResults
from senaite.core.permissions import FieldEditAnalysisConditions
from senaite.core.permissions import FieldEditAnalysisHidden
from senaite.core.permissions import FieldEditAnalysisResult
from senaite.core.permissions import TransitionVerify
from senaite.core.permissions import ViewResults
from senaite.core.permissions import ViewRetractedAnalyses
from senaite.core.registry import get_registry_record
from zope.component import getAdapters
from zope.component import getMultiAdapter


class AnalysesView(ListingView):
    """Displays a list of Analyses in a table.

    Visible InterimFields from all analyses are added to self.columns[].
    Keyword arguments are passed directly to senaite_catalog_analysis.
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
        self.catalog = ANALYSIS_CATALOG
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
        self.bsc = api.get_tool(SETUP_CATALOG)
        self.portal = api.get_portal()
        self.portal_url = api.get_url(self.portal)
        self.rc = api.get_tool(REFERENCE_CATALOG)
        self.dmk = context.bika_setup.getResultsDecimalMark()
        self.scinot = context.bika_setup.getScientificNotationResults()
        self.categories = []
        self.expand_all_categories = True
        self.now = datetime.now()

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
            ("Uncertainty", {
                "title": _("+-"),
                "ajax": True,
                "sortable": False}),
            ("Unit", {
                "title": _("Unit"),
                "sortable": False,
                "ajax": True,
                "on_change": "_on_unit_change",
                "toggle": True}),
            ("Specification", {
                "title": _("Specification"),
                "sortable": False}),
            ("retested", {
                "title": _("Retested"),
                "type": "boolean",
                "sortable": False}),
            ("Method", {
                "title": _("Method"),
                "sortable": False,
                "ajax": True,
                "on_change": "_on_method_change",
                "toggle": True}),
            ("Instrument", {
                "title": _("Instrument"),
                "ajax": True,
                "sortable": False,
                "toggle": True}),
            ("Calculation", {
                "title": _("Calculation"),
                "sortable": False,
                "toggle": False}),
            ("Attachments", {
                "title": _("Attachments"),
                "sortable": False}),
            ("SubmittedBy", {
                "title": _("Submitter"),
                "sortable": False}),
            ("Analyst", {
                "title": _("Analyst"),
                "sortable": False,
                "ajax": True,
                "toggle": True}),
            ("ResultCaptureDate", {
                "title": _("Captured"),
                "index": "getResultCaptureDate",
                "type": "datetime",
                "max": self.now.strftime("%Y-%m-%d"),
                "ajax": True,
                "sortable": False}),
            ("DueDate", {
                "title": _("Due Date"),
                "index": "getDueDate",
                "sortable": False}),
            ("state_title", {
                "title": _("Status"),
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

    def update(self):
        """Update hook
        """
        super(AnalysesView, self).update()
        self.load_analysis_categories()
        self.append_partition_filters()
        if self.analysis_categories_enabled():
            self.show_categories = True

    def before_render(self):
        """Before render hook
        """
        super(AnalysesView, self).before_render()
        self.request.set("disable_plone.rightcolumn", 1)

    @viewcache.memoize
    def get_default_columns_order(self):
        """Return the default column order from the registry

        :returns: List of column keys
        """
        name = "sampleview_analysis_columns_order"
        columns_order = get_registry_record(name, default=[]) or []
        return columns_order

    def reorder_analysis_columns(self):
        """Reorder analysis columns based on registry configuration
        """
        columns_order = self.get_default_columns_order()
        if not columns_order:
            return
        # compute columns that are missing in the config
        missing_columns = filter(
            lambda col: col not in columns_order, self.columns.keys())
        # prepare the new sort order for the columns
        ordered_columns = columns_order + missing_columns

        # set the order in each review state
        for rs in self.review_states:
            # set a copy of the new ordered columns list
            rs["columns"] = ordered_columns[:]

    def calculate_interim_columns_position(self, review_state):
        """Calculate at which position the interim columns should be inserted
        """
        columns = review_state.get("columns", [])
        if "AdditionalValues" in columns:
            return columns.index("AdditionalValues")
        if "Result" in columns:
            return columns.index("Result")
        return len(columns)

    @property
    @viewcache.memoize
    def senaite_theme(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="senaite_theme")

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
    def analysis_categories_enabled(self):
        """Check if analyses should be grouped by category
        """
        # setting applies only for samples
        if not IAnalysisRequest.providedBy(self.context):
            return False
        setup = api.get_senaite_setup()
        return setup.getCategorizeSampleAnalyses()

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
        return check_permission(permission, self.get_object(obj))

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

        analysis_obj = self.get_object(analysis_brain)
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
        obj = self.get_object(analysis_brain)

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
        obj = self.get_object(analysis_brain)

        # Manual setting of uncertainty is not allowed
        if not obj.getAllowManualUncertainty():
            return False

        # Result is a detection limit -> uncertainty setting makes no sense!
        if obj.getDetectionLimitOperand() in [LDL, UDL]:
            return False

        return True

    @viewcache.memoize
    def is_analysis_conditions_edition_allowed(self, analysis_brain):
        """Returns whether the conditions of the analysis can be edited or not
        """
        # Check if permission is granted for the given analysis
        obj = self.get_object(analysis_brain)

        if IReferenceAnalysis.providedBy(obj):
            return False

        if not self.has_permission(FieldEditAnalysisConditions, obj):
            return False

        # Omit analysis does not have conditions set
        if not obj.getConditions(empties=True):
            return False

        return True

    @viewcache.memoize
    def is_manual_result_capture_date_allowed(self):
        """Returns whether it is allowed to set the result capture date manually
        """
        setup = api.get_senaite_setup()
        return setup.getAllowManualResultCaptureDate()

    def get_instrument(self, analysis_brain):
        """Returns the instrument assigned to the analysis passed in, if any

        :param analysis_brain: Brain that represents an analysis
        :return: Instrument object or None
        """
        obj = self.get_object(analysis_brain)
        return obj.getInstrument()

    def get_calculation(self, analysis_brain):
        """Returns the calculation assigned to the analysis passed in, if any

        :param analysis_brain: Brain that represents an analysis
        :return: Calculation object or None
        """
        obj = self.get_object(analysis_brain)
        return obj.getCalculation()

    @viewcache.memoize
    def get_object(self, brain_or_object_or_uid):
        """Get the full content object. Returns None if the param passed in is
        not a valid, not a valid object or not found

        :param brain_or_object_or_uid: UID/Catalog brain/content object
        :returns: content object
        """
        return api.get_object(brain_or_object_or_uid, default=None)

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
        vocab = []
        obj = self.get_object(analysis_brain)
        default_method = obj.getMethod()
        methods = obj.getAllowedMethods()
        empty_option = {"ResultValue": "", "ResultText": _("None")}
        for method in methods:
            vocab.append({
                "ResultValue": api.get_uid(method),
                "ResultText": api.get_title(method),
            })
        # allow empty option if we have no allowed methods
        if not methods:
            vocab = [empty_option]
        # allow empty option if the default method is set to "None"
        elif default_method is None:
            vocab.insert(0, empty_option)
        return vocab

    def get_unit_vocabulary(self, analysis_brain):
        """Returns a vocabulary with all the units available for the passed in
        analysis.

        The vocabulary is a list of dictionaries. Each dictionary has the
        following structure:

            {'ResultValue': <unit>,
             'ResultText': <unit>}

        :param analysis_brain: A single Analysis brain
        :type analysis_brain: CatalogBrain
        :returns: A list of dicts
        """
        obj = self.get_object(analysis_brain)
        # Get unit choices
        unit_choices = obj.getUnitChoices()
        vocab = []
        for unit in unit_choices:
            vocab.append({
                "ResultValue": unit['value'],
                "ResultText": unit['value'],
            })
        return vocab

    def get_instruments_vocabulary(self, analysis, method=None):
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

        :param analysis: A single Analysis or ReferenceAnalysis
        :type analysis_brain: Analysis or.ReferenceAnalysis
        :return: A vocabulary with the instruments for the analysis
        :rtype: A list of dicts: [{'ResultValue':UID, 'ResultText':Title}]
        """
        obj = self.get_object(analysis)
        # get the allowed interfaces from the analysis service
        instruments = obj.getAllowedInstruments()
        # if no method is passed, get the assigned method of the analyis
        if method is None:
            method = obj.getMethod()

        # check if the analysis has a method
        if method:
            # supported instrument from the method
            method_instruments = method.getInstruments()
            # allow only method instruments that are set in service
            instruments = list(
                set(instruments).intersection(method_instruments))

        # If the analysis is a QC analysis, display all instruments, including
        # those uncalibrated or for which the last QC test failed.
        is_qc = api.get_portal_type(obj) == "ReferenceAnalysis"

        vocab = []
        for instrument in instruments:
            uid = api.get_uid(instrument)
            title = api.safe_unicode(api.get_title(instrument))
            # append all valid instruments
            if instrument.isValid():
                vocab.append({
                    "ResultValue": uid,
                    "ResultText": title,
                })
            elif is_qc:
                # Is a QC analysis, include instrument also if is not valid
                if instrument.isOutOfDate():
                    title = _(u"{} (Out of date)".format(title))
                vocab.append({
                    "ResultValue": uid,
                    "ResultText": title,
                })
            elif instrument.isOutOfDate():
                # disable out of date instruments
                title = _(u"{} (Out of date)".format(title))
                vocab.append({
                    "disabled": True,
                    "ResultValue": None,
                    "ResultText": title,
                })

        # sort the vocabulary
        vocab = list(sorted(vocab, key=itemgetter("ResultText")))
        # prepend empty item
        vocab = [{"ResultValue": "", "ResultText": _("None")}] + vocab

        return vocab

    def load_analysis_categories(self):
        # Getting analysis categories
        bsc = api.get_tool('senaite_catalog_setup')
        analysis_categories = bsc(portal_type="AnalysisCategory",
                                  sort_on="sortable_title")
        # Sorting analysis categories
        self.analysis_categories_order = dict([
            (b.Title, "{:04}".format(a)) for a, b in
            enumerate(analysis_categories)])

    def append_partition_filters(self):
        """Append additional review state filters for partitions
        """

        # view is used for instrument QC view as well
        if not IAnalysisRequest.providedBy(self.context):
            return

        # check if the sample has partitions
        partitions = self.context.getDescendants()

        # root partition w/o partitions
        if not partitions:
            return

        new_states = []
        valid_states = [
            "registered",
            "unassigned",
            "assigned",
            "to_be_verified",
            "verified",
            "published",
        ]

        if self.context.isRootAncestor():
            root_id = api.get_id(self.context)
            new_states.append({
                "id": root_id,
                "title": root_id,
                "contentFilter": {
                    "getAncestorsUIDs": api.get_uid(self.context),
                    "review_state": valid_states,
                    "path": {
                        "query": api.get_path(self.context),
                        "level": 0,
                    },
                },
                "columns": self.columns.keys(),
            })

        for partition in partitions:
            part_id = api.get_id(partition)
            new_states.append({
                "id": part_id,
                "title": part_id,
                "contentFilter": {
                    "getAncestorsUIDs": api.get_uid(partition),
                    "review_state": valid_states,
                },
                "columns": self.columns.keys(),
            })

        for state in sorted(new_states, key=lambda s: s.get("id")):
            if state not in self.review_states:
                self.review_states.append(state)

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
        item['replace']['Service'] = '<strong>{}</strong>'.format(obj.Title)

        # Append info link before the service
        # see: bika.lims.site.coffee for the attached event handler
        item["before"]["Service"] = get_link(
            "analysisservice_info?service_uid={}&analysis_uid={}"
            .format(obj.getServiceUID, obj.UID),
            value="<i class='fas fa-info-circle'></i>",
            css_class="overlay_panel", tabindex="-1")

        # Append conditions link before the analysis
        # see: bika.lims.site.coffee for the attached event handler
        if self.is_analysis_conditions_edition_allowed(obj):
            url = api.get_url(self.context)
            url = "{}/set_analysis_conditions?uid={}".format(url, obj.UID)
            ico = "<i class='fas fa-list' style='padding-top: 5px;'/>"
            conditions = get_link(url, value=ico, css_class="overlay_panel",
                                  tabindex="-1")
            info = item["before"]["Service"]
            item["before"]["Service"] = "<br/>".join([info, conditions])

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
        # Fill unit field
        self._folder_item_unit(obj, item)
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
        # Fill hidden field (report visibility)
        self._folder_item_report_visibility(obj, item)
        # Renders additional icons to be displayed
        self._folder_item_fieldicons(obj)
        # Renders remarks toggle button
        self._folder_item_remarks(obj, item)
        # Renders the analysis conditions
        self._folder_item_conditions(obj, item)
        # Fill maximum holding time warnings
        self._folder_item_holding_time(obj, item)

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

            # Graceful handling of new item key introduced in
            # https://github.com/senaite/senaite.app.listing/pull/81
            item["help"] = item.get("help", {})

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
                pos = self.calculate_interim_columns_position(state)
                for col_id in interim_keys:
                    if col_id not in state["columns"]:
                        state["columns"].insert(pos, col_id)
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

        # Display method and instrument columns only if at least one of the
        # analyses requires them to be displayed for selection
        show_method_column = self.is_method_column_required(items)
        if "Method" in self.columns:
            self.columns["Method"]["toggle"] = show_method_column

        show_instrument_column = self.is_instrument_column_required(items)
        if "Instrument" in self.columns:
            self.columns["Instrument"]["toggle"] = show_instrument_column

        # show unit selection column only if required
        show_unit_column = self.is_unit_selection_column_required(items)
        if "Unit" in self.columns:
            self.columns["Unit"]["toggle"] = show_unit_column

        return items

    def render_unit(self, unit, css_class=None):
        """Render HTML element for unit
        """
        if css_class is None:
            css_class = "unit d-inline-block py-2 small text-secondary text-nowrap"
        return "<span class='{css_class}'>{unit}</span>".format(
            unit=unit, css_class=css_class)

    def get_category_title(self, analysis):
        """Returns the title of the category the analysis is assigned to
        """
        obj = api.get_object(analysis)
        cat_uid = obj.getRawCategory()
        if not cat_uid:
            return ""
        cat = self.get_object(cat_uid)
        return api.get_title(cat)

    def _folder_item_category(self, analysis_brain, item):
        """Sets the category to the item passed in

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        if not self.show_categories:
            return

        # get the category title
        cat = self.get_category_title(analysis_brain)

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

        # Get the analysis object
        obj = self.get_object(analysis_brain)

        result = obj.getResult()
        capture_date = obj.getResultCaptureDate()
        localized_capture_date = dtime.to_localized_time(
            capture_date, long_format=1)

        item["Result"] = result
        item["ResultCaptureDate"] = dtime.to_iso_format(capture_date)
        item["replace"]["ResultCaptureDate"] = localized_capture_date

        # Add the unit after the result
        unit = item.get("Unit")
        if unit:
            item["after"]["Result"] = self.render_unit(unit)

        # Edit mode enabled of this Analysis
        if self.is_analysis_edition_allowed(analysis_brain):
            # Allow to set Remarks
            item["allow_edit"].append("Remarks")

            if self.is_manual_result_capture_date_allowed():
                # Allow to edit the capture date, e.g. when the result was
                # captured manually after the instrument measurement.
                item["allow_edit"].append("ResultCaptureDate")

            # Set the results field editable
            if self.is_result_edition_allowed(analysis_brain):
                item["allow_edit"].append("Result")

            # Display the DL operand (< or >) in the results entry field if
            # the manual entry of DL is set, but DL selector is hidden
            allow_manual = obj.getAllowManualDetectionLimit()
            selector = obj.getDetectionLimitSelector()
            if allow_manual and not selector:
                operand = obj.getDetectionLimitOperand()
                item["Result"] = "{} {}".format(operand, result).strip()

            # Prepare result options
            result_type = obj.getResultType()
            item["result_type"] = result_type

            choices = self.get_result_options(obj)
            if choices:
                if result_type == "select":
                    # By default set empty as the default selected choice
                    choices.insert(0, dict(ResultValue="", ResultText=""))
                item["choices"]["Result"] = choices

            if result_type == "numeric":
                item["help"]["Result"] = _(
                    "Enter the result either in decimal or scientific "
                    "notation, e.g. 0.00005 or 1e-5, 10000 or 1e5")

        if not result:
            return

        formatted_result = obj.getFormattedResult(
            sciformat=int(self.scinot), decimalmark=self.dmk)
        item["formatted_result"] = formatted_result

    def get_result_options(self, analysis):
        """Returns the result options of the analysis to be rendered or empty
        """
        options = copy(analysis.getResultOptions())
        sort_by = analysis.getResultOptionsSorting()
        if not sort_by:
            return options

        sort_by, sort_order = sort_by.split("-")
        reverse = sort_order == "desc"
        return sorted(options, key=itemgetter(sort_by), reverse=reverse)

    def is_multi_interim(self, interim):
        """Returns whether the interim stores a list of values instead of a
        single value
        """
        result_type = interim.get("result_type", "")
        return result_type.startswith("multi")

    @deprecated("Use api.to_list instead")
    def to_list(self, value):
        """Converts the value to a list
        """
        return api.to_list(value)

    def get_interim_choices(self, interim):
        """Parse the interim choices field
        """
        choices = interim.get("choices")
        if not choices:
            return None
        items = choices.split("|")
        pairs = map(lambda item: item.strip().split(":"), items)
        return OrderedDict(pairs)

    def _folder_item_calculation(self, analysis_brain, item):
        """Set the analysis' calculation and interims to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """

        if not self.has_permission(ViewResults, analysis_brain):
            # Hide interims and calculation if user cannot view results
            return

        is_editable = self.is_analysis_edition_allowed(analysis_brain)

        # calculation
        calculation = self.get_calculation(analysis_brain)
        calculation_uid = api.get_uid(calculation) if calculation else ""
        calculation_title = api.get_title(calculation) if calculation else ""
        calculation_link = get_link_for(calculation) if calculation else ""
        item["calculation"] = calculation_uid
        item["Calculation"] = calculation_title
        item["replace"]["Calculation"] = calculation_link or _("Manual")

        if is_editable and calculation:
            url = analysis_brain.getURL()
            item["after"]["Result"] = item["after"].get("Result") or ""
            item["after"]["Result"] += get_link(
                "{}/action/recalculate".format(url),
                value="<i class='small text-secondary fas fa-sync'></i>",
                title=t(_("Recalculate")), css_class="listing-ajax-action")

        # Set interim fields. Note we add the key 'formatted_value' to the list
        # of interims the analysis has already assigned.
        analysis_obj = self.get_object(analysis_brain)
        interim_fields = analysis_obj.getInterimFields() or list()

        # Copy to prevent to avoid persistent changes
        interim_fields = deepcopy(interim_fields)
        for interim_field in interim_fields:
            interim_keyword = interim_field.get("keyword", "")
            if not interim_keyword:
                continue

            interim_value = interim_field.get("value", "")
            interim_allow_empty = interim_field.get("allow_empty") == "on"
            interim_unit = interim_field.get("unit", "")

            # Get the interim's formatted value
            interim_formatted = self.get_formatted_interim(interim_field)
            interim_field["formatted_value"] = interim_formatted

            # Update the item with the interim
            item[interim_keyword] = interim_field
            item["class"][interim_keyword] = "interim"

            # render the unit after the interim field
            if interim_unit:
                formatted_interim_unit = format_supsub(interim_unit)
                item["after"][interim_keyword] = self.render_unit(
                    formatted_interim_unit)

            # Note: As soon as we have a separate content type for field
            #       analysis, we can solely rely on the field permission
            #       "senaite.core: Field: Edit Analysis Result"
            if is_editable:
                if self.has_permission(
                        FieldEditAnalysisResult, analysis_brain):
                    item["allow_edit"].append(interim_keyword)

            # Add this analysis' interim fields to the interim_columns list
            interim_hidden = interim_field.get("hidden", False)
            if not interim_hidden:
                interim_title = interim_field.get("title")
                self.interim_columns[interim_keyword] = interim_title

            # Does interim's results list needs to be rendered?
            choices = self.get_interim_choices(interim_field)
            if choices:
                multi = self.is_multi_interim(interim_field)

                # Ensure empty option is available if no default value is set
                if not interim_value and not multi:
                    # allow empty selection and flush default value
                    interim_allow_empty = True

                # Generate the display list
                # [{"ResultValue": value, "ResultText": text},]
                headers = ["ResultValue", "ResultText"]
                dl = map(lambda it: dict(zip(headers, it)), choices.items())

                # Allow empty selection if allowed
                if interim_allow_empty:
                    empty = {"ResultValue": "", "ResultText": ""}
                    dl = [empty] + list(dl)

                item.setdefault("choices", {})[interim_keyword] = dl

            if not is_editable:
                # Display the text instead of the value
                interim_field["value"] = interim_formatted

            item[interim_keyword] = interim_field

        item["interimfields"] = interim_fields
        self.interim_fields[analysis_brain.UID] = interim_fields

    def get_formatted_interim(self, interim):
        """Returns the formatted value of the interim
        """
        # get the 'raw' value stored for this interim
        raw_value = interim.get("value")

        if self.is_multi_interim(interim):
            # value is a jsonified list of values
            values = api.to_list(raw_value)
        else:
            values = [raw_value]

        # remove empties
        values = filter(None, values)

        choices = self.get_interim_choices(interim)
        if choices:
            # values are predefined options for selection
            values = [choices.get(v) for v in values]
        else:
            # values are captured directly by the user
            values = [formatDecimalMark(value, self.dmk) for value in values]

        # return the values as a single string
        values = filter(None, values)
        return "<br/>".join(values)

    def _folder_item_unit(self, analysis_brain, item):
        """Fills the analysis' unit to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        if not self.is_analysis_edition_allowed(analysis_brain):
            return

        # Edition allowed
        voc = self.get_unit_vocabulary(analysis_brain)
        if voc:
            item["choices"]["Unit"] = voc
            item["allow_edit"].append("Unit")

    def _folder_item_method(self, analysis_brain, item):
        """Fills the analysis' method to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        obj = self.get_object(analysis_brain)
        is_editable = self.is_analysis_edition_allowed(analysis_brain)
        if is_editable:
            method_vocabulary = self.get_methods_vocabulary(analysis_brain)
            item["Method"] = obj.getRawMethod()
            item["choices"]["Method"] = method_vocabulary
            item["allow_edit"].append("Method")
        else:
            item["Method"] = _("Manual")
            method = obj.getMethod()
            if method:
                item["Method"] = api.get_title(method)
                item["replace"]["Method"] = get_link_for(method, tabindex="-1")

    def _on_method_change(self, uid=None, value=None, item=None, **kw):
        """Update instrument and calculation when the method changes

        :param uid: object UID
        :value: UID of the new method
        :item: old folderitem

        :returns: updated folderitem
        """
        obj = api.get_object_by_uid(uid, None)
        method = api.get_object_by_uid(value, None)

        if not all([obj, method, item]):
            return None

        # update the available instruments
        inst_vocab = self.get_instruments_vocabulary(obj, method=method)
        item["choices"]["Instrument"] = inst_vocab

        return item

    def _folder_item_instrument(self, analysis_brain, item):
        """Fills the analysis' instrument to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        item["Instrument"] = ""

        # Instrument can be assigned to this analysis
        is_editable = self.is_analysis_edition_allowed(analysis_brain)
        instrument = self.get_instrument(analysis_brain)

        if is_editable:
            # Edition allowed
            voc = self.get_instruments_vocabulary(analysis_brain)
            item["Instrument"] = instrument.UID() if instrument else ""
            item["choices"]["Instrument"] = voc
            item["allow_edit"].append("Instrument")

        elif instrument:
            # Edition not allowed
            item["Instrument"] = api.get_title(instrument)
            instrument_link = get_link_for(instrument, tabindex="-1")
            item["replace"]["Instrument"] = instrument_link

        else:
            item["Instrument"] = _("Manual")

    def _on_unit_change(self, uid=None, value=None, item=None, **kw):
        """ updates the rendered unit on selection of unit.
        """
        if not all([value, item]):
            return None
        item["after"]["Result"] = self.render_unit(value)
        uncertainty = item.get("Uncertainty")
        if uncertainty:
            item["after"]["Uncertainty"] = self.render_unit(value)
        elif "Uncertainty" in item["allow_edit"]:
            item["after"]["Uncertainty"] = self.render_unit(value)
        return item

    def _folder_item_analyst(self, obj, item):
        obj = self.get_object(obj)
        analyst = obj.getAnalyst()
        item["Analyst"] = self.get_user_name(analyst)

    def _folder_item_submitted_by(self, obj, item):
        obj = self.get_object(obj)
        submitted_by = obj.getSubmittedBy()
        item["SubmittedBy"] = self.get_user_name(submitted_by)

    @viewcache.memoize
    def get_user_name(self, user_id):
        if not user_id:
            return ""
        user = api.get_user_properties(user_id)
        return user and user.get("fullname") or user_id

    def _folder_item_attachments(self, obj, item):
        if not self.has_permission(ViewResults, obj):
            return

        attachments_names = []
        attachments_html = []
        analysis = self.get_object(obj)
        for attachment in analysis.getRawAttachment():
            attachment = self.get_object(attachment)
            link = self.get_attachment_link(attachment)
            attachments_html.append(link)
            filename = attachment.getFilename()
            attachments_names.append(filename)

        if attachments_html:
            item["replace"]["Attachments"] = "<br/>".join(attachments_html)
            item["Attachments"] = ", ".join(attachments_names)

        elif analysis.getAttachmentRequired():
            img = get_image("warning.png", title=_("Attachment required"))
            item["replace"]["Attachments"] = img

    def get_attachment_link(self, attachment):
        """Returns a well-formed link for the attachment passed in
        """
        filename = attachment.getFilename()
        att_url = api.get_url(attachment)
        url = "{}/at_download/AttachmentFile".format(att_url)
        return get_link(url, filename, tabindex="-1")

    def _folder_item_uncertainty(self, analysis_brain, item):
        """Fills the analysis' uncertainty to the item passed in.

        :param analysis_brain: Brain that represents an analysis
        :param item: analysis' dictionary counterpart that represents a row
        """
        item["Uncertainty"] = ""

        if not self.has_permission(ViewResults, analysis_brain):
            return

        # Wake up the Analysis object
        obj = self.get_object(analysis_brain)

        # NOTE: When we allow to edit the uncertainty, we want to have the raw
        #       uncertainty value and not the formatted (and possibly rounded)!
        #       This ensures that not the rounded value get stored
        allow_edit = self.is_uncertainty_edition_allowed(analysis_brain)
        if allow_edit:
            item["Uncertainty"] = obj.getUncertainty()
            item["before"]["Uncertainty"] = "± "
            item["allow_edit"].append("Uncertainty")
            unit = item.get("Unit")
            if unit:
                item["after"]["Uncertainty"] = self.render_unit(unit)
            return

        formatted = format_uncertainty(
            obj, decimalmark=self.dmk, sciformat=int(self.scinot))
        if formatted:
            item["replace"]["Uncertainty"] = formatted
            item["before"]["Uncertainty"] = "± "
            unit = item.get("Unit")
            if unit:
                item["after"]["Uncertainty"] = self.render_unit(unit)

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
            anchor = "<a href='#' tabindex='-1' title='{} &#13;{} {}' " \
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
        anchor = get_link(worksheet.absolute_url(), img, tabindex="-1")
        self._append_html_element(item, 'state_title', anchor)

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
            kwargs = {"class": "small", "tabindex": "-1"}
            url = get_link(part_url, value=sample_id, **kwargs)
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

        # Hidden checkbox is not reachable by tabbing
        item["tabindex"]["Hidden"] = "disabled"
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

    def _folder_item_conditions(self, analysis_brain, item):
        """Renders the analysis conditions
        """
        analysis = self.get_object(analysis_brain)

        if not IRoutineAnalysis.providedBy(analysis):
            return

        conditions = analysis.getConditions()
        if not conditions:
            return

        def to_str(condition):
            title = condition.get("title")
            value = condition.get("value", "")
            if condition.get("type") == "file" and api.is_uid(value):
                att = self.get_object(value)
                value = self.get_attachment_link(att)
            return ": ".join([title, str(value)])

        # Display the conditions properly formatted
        conditions = "<br/>".join([to_str(cond) for cond in conditions])
        service = item["replace"].get("Service") or item["Service"]
        item["replace"]["Service"] = "<br/>".join([service, conditions])

    def _folder_item_holding_time(self, analysis_brain, item):
        """Adds an icon to the item dictionary if no result has been submitted
        for the analysis and the holding time has passed or is about to expire.
        It also displays the icon if the result was recorded after the holding
        time limit.
        """
        analysis = self.get_object(analysis_brain)
        if not IRoutineAnalysis.providedBy(analysis):
            return

        # get the maximum holding time for this analysis
        max_holding_time = analysis.getMaxHoldingTime()
        if not max_holding_time:
            return

        # get the datetime from which the max holding time is computed
        start_date = analysis.getDateSampled()
        start_date = dtime.to_dt(start_date)
        if not start_date:
            return

        # get the timezone of the start date for correct comparisons
        timezone = dtime.get_timezone(start_date)

        # calculate the maximum holding date
        delta = timedelta(minutes=api.to_minutes(**max_holding_time))
        max_holding_date = dtime.to_ansi(start_date + delta)

        # maybe the result was captured past the holding time
        if ISubmitted.providedBy(analysis):
            captured = analysis.getResultCaptureDate()
            captured = dtime.to_ansi(captured, timezone=timezone)
            if captured > max_holding_date:
                msg = _("The result was captured past the holding time limit.")
                icon = get_fas_ico("exclamation-triangle",
                                   css_class="text-danger",
                                   title=t(msg))
                self._append_html_element(item, "ResultCaptureDate", icon)
            return

        # not yet submitted, maybe the holding time expired
        now = dtime.to_ansi(dtime.now(), timezone=timezone)
        if now > max_holding_date:
            msg = _("The holding time for this sample and analysis has "
                    "expired. Proceeding with the analysis may compromise the "
                    "reliability of the results.")
            icon = get_fas_ico("exclamation-triangle",
                               css_class="text-danger",
                               title=t(msg))
            self._append_html_element(item, "ResultCaptureDate", icon)
            return

        # or maybe is about to expire
        soon = dtime.to_ansi(dtime.now(), timezone=timezone)
        if soon > max_holding_date:
            msg = _("The holding time for this sample and analysis is about "
                    "to expire. Please complete the analysis as soon as "
                    "possible to ensure data accuracy and reliability.")
            icon = get_fas_ico("exclamation-triangle",
                               css_class="text-warning",
                               title=t(msg))
            self._append_html_element(item, "ResultCaptureDate", icon)
            return

    def is_method_required(self, analysis):
        """Returns whether the render of the selection list with methods is
        required for the method passed-in, even if only option "None" is
        displayed for selection
        """
        # Always return true if the analysis has a method assigned
        obj = self.get_object(analysis)
        method = obj.getRawMethod()
        if method:
            return True

        methods = obj.getRawAllowedMethods()
        return len(methods) > 0

    def is_instrument_required(self, analysis):
        """Returns whether the render of the selection list with instruments is
        required for the analysis passed-in, even if only option "None" is
        displayed for selection.
        :param analysis: Brain or object that represents an analysis
        """
        # If method selection list is required, the instrument selection too
        if self.is_method_required(analysis):
            return True

        # Always return true if the analysis has an instrument assigned
        analysis = self.get_object(analysis)
        if analysis.getRawInstrument():
            return True

        instruments = analysis.getRawAllowedInstruments()
        # There is no need to check for the instruments of the method assigned
        # to # the analysis (if any), because the instruments rendered in the
        # selection list are always a subset of the allowed instruments when
        # a method is selected
        return len(instruments) > 0

    def is_unit_choices_required(self, analysis):
        """Returns whether the render of the unit choice selection list is
        required for the analysis passed-in.
        :param analysis: Brain or object that represents an analysis
        """
        # Always return true if the analysis has unitchoices
        analysis = self.get_object(analysis)
        if analysis.getUnitChoices():
            return True
        return False

    def is_method_column_required(self, items):
        """Returns whether the method column has to be rendered or not.
        Returns True if at least one of the analyses from the listing requires
        the list for method selection to be rendered
        """
        for item in items:
            obj = item.get("obj")
            if self.is_method_required(obj):
                return True
        return False

    def is_instrument_column_required(self, items):
        """Returns whether the instrument column has to be rendered or not.
        Returns True if at least one of the analyses from the listing requires
        the list for instrument selection to be rendered
        """
        for item in items:
            obj = item.get("obj")
            if self.is_instrument_required(obj):
                return True
        return False

    def is_unit_selection_column_required(self, items):
        """Returns whether the unit column has to be rendered or not.
        Returns True if at least one of the analyses from the listing requires
        the list for unit selection to be rendered
        """
        for item in items:
            obj = item.get("obj")
            if self.is_unit_choices_required(obj):
                return True
        return False
