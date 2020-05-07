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

import plone
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.chart.analyses import EvolutionChart
from bika.lims.browser.resultsimport.autoimportlogs import AutoImportLogsView
from bika.lims.browser.viewlets import InstrumentQCFailuresViewlet  # noqa
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.content.instrumentmaintenancetask import \
    InstrumentMaintenanceTaskStatuses as mstatus
from bika.lims.utils import get_image, get_link, t
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import Forbidden
from ZODB.POSException import POSKeyError
from zope.interface import implements


class InstrumentMaintenanceView(BikaListingView):
    """Listing view for instrument maintenance tasks
    """

    def __init__(self, context, request):
        super(InstrumentMaintenanceView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            "portal_type": "InstrumentMaintenanceTask",
            "path": {
                "query": api.get_path(context),
                "depth": 1  # searching just inside the specified folder
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.form_id = "instrumentmaintenance"
        self.title = self.context.translate(_("Instrument Maintenance"))

        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/instrumentmaintenance_big.png"
        )
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=InstrumentMaintenanceTask",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        self.pagesize = 30

        self.columns = {
            'getCurrentState': {'title': ''},
            'Title': {'title': _('Task'),
                      'index': 'sortable_title'},
            'getType': {'title': _('Task type', 'Type'), 'sortable': True},
            'getDownFrom': {'title': _('Down from'), 'sortable': True},
            'getDownTo': {'title': _('Down to'), 'sortable': True},
            'getMaintainer': {'title': _('Maintainer'), 'sortable': True},
        }

        self.review_states = [
            {
                "id": "default",
                "title": _("Open"),
                "contentFilter": {"is_active": True},
                "columns": [
                    "getCurrentState",
                    "Title",
                    "getType",
                    "getDownFrom",
                    "getDownTo",
                    "getMaintainer",
                ]
            }, {
                "id": "cancelled",
                "title": _("Cancelled"),
                "contentFilter": {"is_active": False},
                "columns": [
                    "getCurrentState",
                    "Title",
                    "getType",
                    "getDownFrom",
                    "getDownTo",
                    "getMaintainer",
                ]
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": [
                    "getCurrentState",
                    "Title",
                    "getType",
                    "getDownFrom",
                    "getDownTo",
                    "getMaintainer"
                ]
            }
        ]

    def localize_date(self, date):
        """Return the localized date
        """
        return self.ulocalized_time(date, long_format=1)

    def folderitem(self, obj, item, index):
        """Augment folder listing item
        """
        obj = api.get_object(obj)
        url = item.get("url")
        title = item.get("Title")

        item["replace"]["Title"] = get_link(url, value=title)
        item["getType"] = _(obj.getType()[0])
        item["getDownFrom"] = self.localize_date(obj.getDownFrom())
        item["getDownTo"] = self.localize_date(obj.getDownTo())
        item["getMaintainer"] = obj.getMaintainer()

        status = obj.getCurrentState()
        statustext = obj.getCurrentStateI18n()
        statusimg = ""

        if status == mstatus.CLOSED:
            statusimg = "instrumentmaintenance_closed.png"
            item["state_class"] = "state-inactive"
        elif status == mstatus.CANCELLED:
            statusimg = "instrumentmaintenance_cancelled.png"
            item["state_class"] = "state-cancelled"
        elif status == mstatus.INQUEUE:
            statusimg = "instrumentmaintenance_inqueue.png"
            item["state_class"] = "state-open"
        elif status == mstatus.OVERDUE:
            statusimg = "instrumentmaintenance_overdue.png"
            item["state_class"] = "state-open"
        elif status == mstatus.PENDING:
            statusimg = "instrumentmaintenance_pending.png"
            item["state_class"] = "state-pending"

        item["replace"]["getCurrentState"] = get_image(
            statusimg, title=statustext)
        return item


class InstrumentCalibrationsView(BikaListingView):
    """Listing view for instrument calibrations
    """

    def __init__(self, context, request):
        super(InstrumentCalibrationsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            "portal_type": "InstrumentCalibration",
            "path": {
                "query": api.get_path(context),
                "depth": 1  # searching just inside the specified folder
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.form_id = "instrumentcalibrations"
        self.title = self.context.translate(_("Instrument Calibrations"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/instrumentcalibration_big.png"
        )
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=InstrumentCalibration",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        self.pagesize = 30

        # instrument calibrations
        calibrations = self.context.getCalibrations()
        # current running calibrations
        self.active_calibrations = filter(
            lambda c: c.isCalibrationInProgress(), calibrations)
        self.latest_calibration = self.context.getLatestValidCalibration()

        self.columns = {
            "Title": {"title": _("Task"),
                      "index": "sortable_title"},
            "getDownFrom": {"title": _("Down from")},
            "getDownTo": {"title": _("Down to")},
            "getCalibrator": {"title": _("Calibrator")},
        }
        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": [
                    "Title",
                    "getDownFrom",
                    "getDownTo",
                    "getCalibrator",
                ]
            }
        ]

    def localize_date(self, date):
        """Return the localized date
        """
        return self.ulocalized_time(date, long_format=1)

    def folderitem(self, obj, item, index):
        """Augment folder listing item
        """
        obj = api.get_object(obj)
        url = item.get("url")
        title = item.get("Title")
        calibrator = obj.getCalibrator()

        item["getDownFrom"] = self.localize_date(obj.getDownFrom())
        item["getDownTo"] = self.localize_date(obj.getDownTo())
        item["getCalibrator"] = ""
        if calibrator:
            props = api.get_user_properties(calibrator)
            name = props.get("fullname", calibrator)
            item["getCalibrator"] = name
        item["replace"]["Title"] = get_link(url, value=title)

        # calibration with the most remaining days
        if obj == self.latest_calibration:
            item["state_class"] = "state-published"
        # running calibrations
        elif obj in self.active_calibrations:
            item["state_class"] = "state-active"
        # inactive calibrations
        else:
            item["state_class"] = "state-inactive"

        return item


class InstrumentValidationsView(BikaListingView):
    """Listing view for instrument validations
    """

    def __init__(self, context, request):
        super(InstrumentValidationsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            "portal_type": "InstrumentValidation",
            "path": {
                "query": api.get_path(context),
                "depth": 1  # searching just inside the specified folder
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.form_id = "instrumentvalidations"
        self.title = self.context.translate(_("Instrument Validations"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/instrumentvalidation_big.png"
        )
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=InstrumentValidation",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        self.pagesize = 30

        # instrument validations
        validations = self.context.getValidations()
        # current running validations
        self.active_validations = filter(
            lambda v: v.isValidationInProgress(), validations)
        self.latest_validation = self.context.getLatestValidValidation()

        self.columns = {
            "Title": {"title": _("Task"),
                      "index": "sortable_title"},
            "getDownFrom": {"title": _("Down from")},
            "getDownTo": {"title": _("Down to")},
            "getValidator": {"title": _("Validator")},
        }
        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": [
                    "Title",
                    "getDownFrom",
                    "getDownTo",
                    "getValidator",
                ]
            }
        ]

    def localize_date(self, date):
        """Return the localized date
        """
        return self.ulocalized_time(date, long_format=1)

    def folderitem(self, obj, item, index):
        """Augment folder listing item
        """
        obj = api.get_object(obj)
        url = item.get("url")
        title = item.get("Title")

        item["getDownFrom"] = self.localize_date(obj.getDownFrom())
        item["getDownTo"] = self.localize_date(obj.getDownTo())
        item["getValidator"] = obj.getValidator()
        item["replace"]["Title"] = get_link(url, value=title)

        # validation with the most remaining days
        if obj == self.latest_validation:
            item["state_class"] = "state-published"
        # running validations
        elif obj in self.active_validations:
            item["state_class"] = "state-active"
        # inactive validations
        else:
            item["state_class"] = "state-inactive"

        return item


class InstrumentScheduleView(BikaListingView):
    """Listing view for instrument scheduled tasks
    """

    def __init__(self, context, request):
        super(InstrumentScheduleView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            "portal_type": "InstrumentScheduledTask",
            "path": {
                "query": api.get_path(context),
                "depth": 1  # searching just inside the specified folder
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.form_id = "instrumentschedule"
        self.title = self.context.translate(_("Instrument Scheduled Tasks"))

        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/instrumentschedule_big.png"
        )
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=InstrumentScheduledTask",
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        self.pagesize = 30

        self.columns = {
            "Title": {"title": _("Scheduled task"),
                      "index": "sortable_title"},
            "getType": {"title": _("Task type", "Type")},
            "getCriteria": {"title": _("Criteria")},
            "creator": {"title": _("Created by")},
            "created": {"title": _("Created")},
        }

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "deactivate"}, ],
                "columns": [
                    "Title",
                    "getType",
                    "getCriteria",
                    "creator",
                    "created",
                ]
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "transitions": [{"id": "activate"}, ],
                "columns": [
                    "Title",
                    "getType",
                    "getCriteria",
                    "creator",
                    "created"
                ]
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": [
                    "Title",
                    "getType",
                    "getCriteria",
                    "creator",
                    "created",
                ]
            }
        ]

    def localize_date(self, date):
        """Return the localized date
        """
        return self.ulocalized_time(date, long_format=1)

    def folderitem(self, obj, item, index):
        """Augment folder listing item
        """
        obj = api.get_object(obj)
        url = item.get("url")
        title = item.get("Title")
        creator = obj.Creator()

        item["replace"]["Title"] = get_link(url, value=title)
        item["created"] = self.localize_date(obj.created())
        item["getType"] = _(obj.getType()[0])
        item["creator"] = ""
        if creator:
            props = api.get_user_properties(creator)
            name = props.get("fullname", creator)
            item["creator"] = name

        return item


class InstrumentReferenceAnalysesViewView(BrowserView):
    """View of Reference Analyses linked to the Instrument.

    Only shows the Reference Analyses (Control and Blanks), the rest of regular
    and duplicate analyses linked to this instrument are not displayed.

    The Reference Analyses from an Instrument can be from Worksheets (QC
    analysis performed regularly for any Analysis Request) or attached directly
    to the instrument, without being linked to any Worksheet).

    In this case, the Reference Analyses are created automatically by the
    instrument import tool.
    """

    implements(IViewView)
    template = ViewPageTemplateFile(
        "templates/instrument_referenceanalyses.pt")

    def __init__(self, context, request):
        super(InstrumentReferenceAnalysesViewView, self).__init__(
            context, request)

        self.title = self.context.translate(_("Internal Calibration Tests"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/referencesample_big.png"
        )
        self._analysesview = None

    def __call__(self):
        return self.template()

    def get_analyses_table_view(self):
        view_name = "table_instrument_referenceanalyses"
        view = api.get_view(
            view_name, context=self.context, request=self.request)
        # Call listing hooks
        view.update()
        view.before_render()

        # TODO Refactor QC Charts as React Components
        # The current QC Chart is rendered by looking at the value from a hidden
        # input with id "graphdata", that is rendered below the contents listing
        # (see instrument_referenceanalyses.pt).
        # The value is a json, is built by folderitem function and is returned
        # by self.chart.get_json(). This function is called directly by the
        # template on render, but the template itself does not directly render
        # the contents listing, but is done asyncronously.
        # Hence the function at this point returns an empty dictionary because
        # folderitems hasn't been called yet. As a result, the chart appears
        # empty. Here, we force folderitems function to be called in order to
        # ensure the graphdata is filled before the template is rendered.
        view.get_folderitems()
        return view


class InstrumentReferenceAnalysesView(AnalysesView):
    """View for the table of Reference Analyses linked to the Instrument.

    Only shows the Reference Analyses (Control and Blanks), the rest of regular
    and duplicate analyses linked to this instrument are not displayed.
    """

    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request, **kwargs)

        self.form_id = "{}_qcanalyses".format(api.get_uid(context))
        self.allow_edit = False
        self.show_select_column = False
        self.show_search = False
        self.omit_form = True

        self.catalog = CATALOG_ANALYSIS_LISTING

        self.contentFilter = {
            "portal_type": "ReferenceAnalysis",
            "getInstrumentUID": api.get_uid(self.context),
            "sort_on": "getResultCaptureDate",
            "sort_order": "reverse"
        }
        self.columns["getReferenceAnalysesGroupID"] = {
            "title": _("QC Sample ID"),
            "sortable": False
        }
        self.columns["Partition"] = {
            "title": _("Reference Sample"),
            "sortable": False
        }
        self.columns["Retractions"] = {
            "title": "",
            "sortable": False
        }

        self.review_states[0]["columns"] = [
            "Service",
            "getReferenceAnalysesGroupID",
            "Partition",
            "Result",
            "Uncertainty",
            "CaptureDate",
            "Retractions"
        ]
        self.review_states[0]["transitions"] = [{}]
        self.chart = EvolutionChart()

    def isItemAllowed(self, obj):
        allowed = super(InstrumentReferenceAnalysesView,
                        self).isItemAllowed(obj)
        return allowed or obj.getResult != ""

    def folderitem(self, obj, item, index):
        item = super(InstrumentReferenceAnalysesView,
                     self).folderitem(obj, item, index)
        analysis = api.get_object(obj)

        # Partition is used to group/toggle QC Analyses
        sample = analysis.getSample()
        item["replace"]["Partition"] = get_link(api.get_url(sample),
                                                api.get_id(sample))

        # Get retractions field
        item["Retractions"] = ""
        report = analysis.getRetractedAnalysesPdfReport()
        if report:
            url = api.get_url(analysis)
            href = "{}/at_download/RetractedAnalysesPdfReport".format(url)
            attrs = {"class": "pdf", "target": "_blank"}
            title = _("Retractions")
            link = get_link(href, title, **attrs)
            item["Retractions"] = title
            item["replace"]["Retractions"] = link

        # Add the analysis to the QC Chart
        self.chart.add_analysis(analysis)

        return item


class InstrumentCertificationsView(BikaListingView):
    """Listing view for instrument certifications
    """

    def __init__(self, context, request, **kwargs):
        BikaListingView.__init__(self, context, request, **kwargs)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            "portal_type": "InstrumentCertification",
            "path": {
                "query": api.get_path(context),
                "depth": 1  # searching just inside the specified folder
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.form_id = "instrumentcertifications"
        self.title = self.context.translate(_("Calibration Certificates"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/instrumentcertification_big.png"
        )
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=InstrumentCertification",
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        self.pagesize = 30

        # latest valid certificate UIDs
        self.valid_certificates = self.context.getValidCertifications()
        self.latest_certificate = self.context.getLatestValidCertification()

        self.columns = {
            "Title": {"title": _("Cert. Num"), "index": "sortable_title"},
            "getAgency": {"title": _("Agency"), "sortable": False},
            "getDate": {"title": _("Date"), "sortable": False},
            "getValidFrom": {"title": _("Valid from"), "sortable": False},
            "getValidTo": {"title": _("Valid to"), "sortable": False},
            "getDocument": {"title": _("Document"), "sortable": False},
        }

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": [
                    "Title",
                    "getAgency",
                    "getDate",
                    "getValidFrom",
                    "getValidTo",
                    "getDocument",
                ],
                "transitions": []
            }
        ]

    def get_document(self, certificate):
        """Return the document of the given document
        """
        try:
            return certificate.getDocument()
        except POSKeyError:  # POSKeyError: "No blob file"
            # XXX When does this happen?
            return None

    def localize_date(self, date):
        """Return the localized date
        """
        return self.ulocalized_time(date, long_format=0)

    def folderitem(self, obj, item, index):
        """Augment folder listing item with additional data
        """
        obj = api.get_object(obj)
        url = item.get("url")
        title = item.get("Title")

        item["replace"]["Title"] = get_link(url, value=title)
        item["getDate"] = self.localize_date(obj.getDate())
        item["getValidFrom"] = self.localize_date(obj.getValidFrom())
        item["getValidTo"] = self.localize_date(obj.getValidTo())

        if obj.getInternal() is True:
            item["replace"]["getAgency"] = ""
            item["state_class"] = "%s %s" % \
                (item["state_class"], "internalcertificate")

        item["getDocument"] = ""
        item["replace"]["getDocument"] = ""
        doc = self.get_document(obj)
        if doc and doc.get_size() > 0:
            filename = doc.filename
            download_url = "{}/at_download/Document".format(url)
            anchor = get_link(download_url, filename)
            item["getDocument"] = filename
            item["replace"]["getDocument"] = anchor

        # Latest valid certificate
        if obj == self.latest_certificate:
            item["state_class"] = "state-published"
        # Valid certificate
        elif obj in self.valid_certificates:
            item["state_class"] = "state-valid state-published"
        # Invalid certificates
        else:
            img = get_image("exclamation.png", title=t(_("Out of date")))
            item["replace"]["getValidTo"] = "%s %s" % (item["getValidTo"], img)
            item["state_class"] = "state-invalid"

        return item


class InstrumentAutoImportLogsView(AutoImportLogsView):
    """Logs of Auto-Imports of this instrument.
    """

    def __init__(self, context, request, **kwargs):
        AutoImportLogsView.__init__(self, context, request, **kwargs)
        del self.columns["Instrument"]
        self.review_states[0]["columns"].remove("Instrument")
        self.contentFilter = {
            "portal_type": "AutoImportLog",
            "path": {
                "query": api.get_path(context),
                "depth": 1  # searching just inside the specified folder
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.title = self.context.translate(
            _("Auto Import Logs of %s" % self.context.Title()))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/instrumentcertification_big.png"
        )
        self.context_actions = {}

        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        self.pagesize = 30


class InstrumentMultifileView(BikaListingView):
    """Listing view for instrument multi files
    """

    def __init__(self, context, request):
        super(InstrumentMultifileView, self).__init__(context, request)

        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            "portal_type": "Multifile",
            "path": {
                "query": api.get_path(context),
                "depth": 1  # searching just inside the specified folder
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.form_id = "instrumentfiles"
        self.title = self.context.translate(_("Instrument Files"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/instrumentcertification_big.png"
        )
        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=Multifile",
                "icon": "++resource++bika.lims.images/add.png"
            }
        }

        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = True
        self.pagesize = 30

        self.columns = {
            "DocumentID": {"title": _("Document ID"),
                           "index": "sortable_title"},
            "DocumentVersion": {"title": _("Document Version"),
                                "index": "sortable_title"},
            "DocumentLocation": {"title": _("Document Location"),
                                 "index": "sortable_title"},
            "DocumentType": {"title": _("Document Type"),
                             "index": "sortable_title"},
            "FileDownload": {"title": _("File")}
        }

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": [
                    "DocumentID",
                    "DocumentVersion",
                    "DocumentLocation",
                    "DocumentType",
                    "FileDownload"
                ]
            },
        ]

    def get_file(self, obj):
        """Return the file of the given object
        """
        try:
            return obj.getFile()
        except POSKeyError:  # POSKeyError: "No blob file"
            # XXX When does this happen?
            return None

    def folderitem(self, obj, item, index):
        """Augment folder listing item with additional data
        """
        obj = api.get_object(obj)
        url = item.get("url")
        title = item.get("DocumentID")

        item["replace"]["DocumentID"] = get_link(url, title)

        item["FileDownload"] = ""
        item["replace"]["FileDownload"] = ""
        file = self.get_file(obj)
        if file and file.get_size() > 0:
            filename = file.filename
            download_url = "{}/at_download/File".format(url)
            anchor = get_link(download_url, filename)
            item["FileDownload"] = filename
            item["replace"]["FileDownload"] = anchor

        item["DocumentVersion"] = obj.getDocumentVersion()
        item["DocumentLocation"] = obj.getDocumentLocation()
        item["DocumentType"] = obj.getDocumentType()

        return item


class ajaxGetInstrumentMethods(BrowserView):
    """ Returns the method assigned to the defined instrument.
        uid: unique identifier of the instrument
    """
    # Modified to return multiple methods after enabling multiple method
    # for intruments.
    def __call__(self):
        out = {
            "title": None,
            "instrument": None,
            "methods": [],
        }
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(out)
        bsc = getToolByName(self, "bika_setup_catalog")
        results = bsc(portal_type="Instrument",
                      UID=self.request.get("uid", "0"))
        instrument = results[0] if results and len(results) == 1 else None
        if instrument:
            instrument_obj = instrument.getObject()
            out["title"] = instrument_obj.Title()
            out["instrument"] = instrument.UID
            # Handle multiple Methods per instrument
            methods = instrument_obj.getMethods()
            for method in methods:
                out["methods"].append({
                    "uid": method.UID(),
                    "title": method.Title(),
                })
        return json.dumps(out)
