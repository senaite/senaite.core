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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import copy
import json

from bika.lims import api
from bika.lims.config import LDL
from bika.lims.config import UDL
from plone.autoform.form import AutoExtensibleForm
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from senaite.core.interfaces.datamanager import IDataManager
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE
from zope import event
from zope.component import queryAdapter

from .proxy import AnalysisSchemaProxy
from .schema import IEditAnalysisSchema


class EditAnalysisForm(AutoExtensibleForm, form.Form):
    """z3c.form-based modal for editing an analysis.
    """
    schema = IEditAnalysisSchema
    ignoreContext = False
    css_class = "edit-analysis-form"
    template = ViewPageTemplateFile(
        "templates/edit_analysis.pt"
    )

    _saved = False

    def __init__(self, context, request):
        super(EditAnalysisForm, self).__init__(
            context, request
        )
        uid = (
            request.get("uid")
            or request.form.get("uid")
        )
        self._analysis = api.get_object_by_uid(uid)
        self.context = self._analysis

    def __call__(self):
        """Handle form submission or render the form
        """
        self.update()
        if self.request.form.get("submitted"):
            self.handle_submit()
        if self._saved:
            return ""
        return self.render()

    def getContent(self):
        """Return the proxy that populates widgets
        """
        return AnalysisSchemaProxy(self._analysis)

    # -- Permission checks via z3c.form widgets --

    def is_field_visible(self, name):
        """Check if a field is visible (not hidden/omitted)
        """
        widget = self.widgets.get(name)
        if widget is None:
            return False
        return widget.mode != HIDDEN_MODE

    def updateWidgets(self):
        super(EditAnalysisForm, self).updateWidgets()
        analysis = self._analysis

        # Hide result for select-type results
        # (template renders a custom select)
        result_type = self.get_result_type()
        result_options = analysis.getResultOptions() or []
        if result_type == "select" and result_options:
            if "result" in self.widgets:
                self.widgets["result"].mode = HIDDEN_MODE

        # Hide DL operand if selector not enabled
        if not analysis.getDetectionLimitSelector():
            if "detection_limit_operand" in self.widgets:
                self.widgets[
                    "detection_limit_operand"
                ].mode = HIDDEN_MODE

        # Hide unit if no choices available
        if not analysis.getUnitChoices():
            if "unit" in self.widgets:
                self.widgets["unit"].mode = HIDDEN_MODE

        # Hide capture date if not allowed in setup
        setup = api.get_senaite_setup()
        if not setup.getAllowManualResultCaptureDate():
            if "result_capture_date" in self.widgets:
                self.widgets[
                    "result_capture_date"
                ].mode = HIDDEN_MODE

        # Hide remarks if not enabled in setup
        if not setup.getEnableAnalysisRemarks():
            if "remarks" in self.widgets:
                self.widgets["remarks"].mode = HIDDEN_MODE

        # Analyst is display-only (same as listing)
        if "analyst" in self.widgets:
            self.widgets["analyst"].mode = HIDDEN_MODE

        # Hide uncertainty if not manually editable
        if not self._is_uncertainty_editable():
            if "uncertainty" in self.widgets:
                self.widgets[
                    "uncertainty"
                ].mode = HIDDEN_MODE

    # -- Analysis property accessors --

    def get_analysis_title(self):
        """Returns the analysis title
        """
        return api.get_title(self._analysis)

    def get_analysis_uid(self):
        """Returns the analysis UID
        """
        return api.get_uid(self._analysis)

    def get_analysis_url(self):
        """Returns the analysis absolute URL
        """
        return self._analysis.absolute_url()

    def get_result(self):
        """Returns the current result value
        """
        return self._analysis.getResult() or ""

    def get_result_type(self):
        """Returns the result type
        """
        return self._analysis.getResultType() or "numeric"

    def get_result_options(self):
        """Returns result options for select-type results
        """
        options = copy.copy(
            self._analysis.getResultOptions()
        )
        if not options:
            return []
        sort_by = self._analysis.getResultOptionsSorting()
        if sort_by:
            sort_key, sort_order = sort_by.split("-")
            reverse = sort_order == "desc"
            options = sorted(
                options,
                key=lambda o: o.get(sort_key, ""),
                reverse=reverse,
            )
        return options

    def is_calculated(self):
        """Check if the analysis result is calculated
        """
        return bool(self._analysis.getCalculation())

    def get_uncertainty(self):
        """Returns the current uncertainty value
        """
        return self._analysis.getUncertainty() or ""

    def get_method_uid(self):
        """Returns the current method UID
        """
        method = self._analysis.getMethod()
        return api.get_uid(method) if method else ""

    def get_methods(self):
        """Returns allowed methods as list of dicts
        """
        methods = self._analysis.getAllowedMethods()
        result = []
        for method in methods:
            result.append({
                "uid": api.get_uid(method),
                "title": api.get_title(method),
            })
        return result

    def get_instrument_uid(self):
        """Returns the current instrument UID
        """
        instrument = self._analysis.getInstrument()
        return api.get_uid(instrument) if instrument else ""

    def get_instruments(self):
        """Returns valid instruments as list of dicts
        """
        instruments = self._get_valid_instruments()
        result = []
        for instrument in instruments:
            result.append({
                "uid": api.get_uid(instrument),
                "title": api.get_title(instrument),
            })
        return result

    def get_analyst(self):
        """Returns the current analyst username
        """
        return self._analysis.getAnalyst() or ""

    def get_analysts(self):
        """Returns available analysts as list of dicts
        """
        users = api.get_users_by_roles(
            ["Manager", "LabManager", "Analyst"]
        )
        result = []
        for user in users:
            username = user.getUserName()
            fullname = api.get_user_fullname(username)
            result.append({
                "username": username,
                "fullname": fullname or username,
            })
        result.sort(
            key=lambda x: (x["fullname"] or "").lower()
        )
        return result

    def get_unit(self):
        """Returns the current unit
        """
        return self._analysis.getUnit() or ""

    def get_unit_choices(self):
        """Returns unit choices as list of strings
        """
        choices = self._analysis.getUnitChoices() or []
        return [c.get("value", "") for c in choices]

    def get_dl_operand(self):
        """Returns the current detection limit operand
        """
        return (
            self._analysis.getDetectionLimitOperand() or ""
        )

    def is_hidden(self):
        """Returns whether analysis is hidden from report
        """
        return self._analysis.getHidden()

    def get_remarks(self):
        """Returns the current remarks
        """
        return self._analysis.getRemarks() or ""

    def get_result_capture_date(self):
        """Returns the result capture date in ISO format
        """
        from senaite.core.api import dtime
        capture_date = self._analysis.getResultCaptureDate()
        if not capture_date:
            return ""
        return dtime.to_iso_format(capture_date)

    def get_interims(self):
        """Returns interim fields from the analysis
        """
        raw_interims = (
            self._analysis.getInterimFields() or []
        )
        interims = copy.deepcopy(raw_interims)
        result = []
        for interim in interims:
            keyword = interim.get("keyword", "")
            if not keyword:
                continue
            interim["options"] = self._parse_choices(
                interim.get("choices", "")
            )
            interim["hidden"] = interim.get(
                "hidden", False
            )
            interim["result_type"] = interim.get(
                "result_type", ""
            )
            result.append(interim)
        return result

    def _parse_choices(self, choices):
        """Parse choices string into list of dicts
        """
        if not choices:
            return []
        options = []
        for item in choices.split("|"):
            parts = item.strip().split(":")
            if len(parts) == 2:
                options.append({
                    "value": parts[0],
                    "text": parts[1],
                })
        return options

    def parse_multi_value(self, value):
        """Parse a multi-value interim into a list

        Multi-select interims store values as JSON arrays.
        """
        if isinstance(value, (list, tuple)):
            return list(value)
        if not value:
            return []
        value = str(value).strip()
        if value.startswith("["):
            return json.loads(value)
        return [value]

    # -- Private helpers --

    def _get_valid_instruments(self):
        """Return valid instruments filtered by method
        """
        analysis = self._analysis
        instruments = analysis.getAllowedInstruments()
        method = analysis.getMethod()
        if method:
            method_instruments = method.getInstruments()
            instruments = list(
                set(instruments).intersection(
                    method_instruments
                )
            )
        return [i for i in instruments if i.isValid()]

    def _is_uncertainty_editable(self):
        """Check if uncertainty is manually editable
        """
        analysis = self._analysis
        if not analysis.getAllowManualUncertainty():
            return False
        if analysis.getDetectionLimitOperand() in [
            LDL, UDL
        ]:
            return False
        return True

    # -- Form submission --

    def handle_submit(self):
        """Save form data via IDataManager
        """
        analysis = self._analysis
        dm = queryAdapter(analysis, IDataManager)
        if dm is None:
            logger.error(
                "No IDataManager adapter for {}"
                .format(repr(analysis))
            )
            return

        form_data = self.request.form

        # Map form field names to AT field names
        field_map = {
            "Result": "Result",
            "Uncertainty": "Uncertainty",
            "Method": "Method",
            "Instrument": "Instrument",
            "Analyst": "Analyst",
            "Unit": "Unit",
            "DetectionLimitOperand": (
                "DetectionLimitOperand"
            ),
            "Remarks": "Remarks",
            "ResultCaptureDate": "ResultCaptureDate",
        }

        for form_name, at_name in field_map.items():
            if form_name not in form_data:
                continue
            value = form_data[form_name]
            if value is None:
                value = ""
            dm.set(at_name, value)

        # Handle Hidden checkbox (absent = unchecked)
        if self.is_field_visible("hidden"):
            hidden = "Hidden" in form_data
            dm.set("Hidden", hidden)

        # Save interims
        interims = analysis.getInterimFields() or []
        for interim in interims:
            keyword = interim.get("keyword", "")
            if keyword and keyword in form_data:
                dm.set(keyword, form_data[keyword])

        analysis.reindexObject()
        event.notify(ObjectEditedEvent(analysis))
        self._saved = True
