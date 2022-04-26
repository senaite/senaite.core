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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from six import string_types
from itertools import chain

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.validators import ServiceKeywordValidator
from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Analysis Service
    """

    def initialized(self, data):
        form = data.get("form")
        # Check if method is set
        method = form.get("Method")
        methods = form.get("Methods:list")
        if not (method or methods):
            self.add_status_message(
                _("No Method selected for this Service"),
                level="warning")
        # Protect keyword field
        keyword = form.get("Keyword")
        if keyword:
            writable = self.can_change_keyword(keyword)
            if not writable:
                self.add_readonly_field(
                    "Keyword", _("Keyword is used in active analyses "
                                 "and can not be changed anymore"))

        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # Handle Keyword change
        if name == "Keyword":
            self.add_error_field("Keyword", self.validate_keyword(value))

        # Handle Methods Change
        elif name == "Methods":
            # Available Methods
            empty = [{"title": _("None"), "value": None}]
            # Get selected methods
            methods = map(api.get_object_by_uid, value)
            # Available instruments for the selected methods
            instruments = self.get_available_instruments_for(methods)
            # Available calculations for the selected methods
            calculations = self.get_available_calculations_for(methods)
            # Build select options
            m_opts = map(lambda o: dict(
                title=api.get_title(o), value=api.get_uid(o)), methods)
            i_opts = map(lambda o: dict(
                title=api.get_title(o), value=api.get_uid(o)), instruments)
            c_opts = map(lambda o: dict(
                title=api.get_title(o), value=api.get_uid(o)), calculations)

            # When methods are selected, we filter other fields accordingly
            if methods:
                # selected instruments
                i_sel = map(api.get_uid, instruments)
                # set update fields
                self.add_update_field("Method", {
                    "options": empty + m_opts})
                self.add_update_field("Instruments_options", {
                    "options": i_opts})
                self.add_update_field("Instruments:list", {
                    "options": i_opts, "selected": i_sel})
                self.add_update_field("Instrument", {
                    "options": empty + i_opts})
                self.add_update_field("Calculation", {
                    "options": empty + c_opts})
            else:
                self.add_update_field("Method", {
                    "options": empty})
                self.add_update_field("Instruments:list", {
                    "options": []})
                self.add_update_field("Instruments_options", {
                    "options": i_opts})
                self.add_update_field("Instrument", {
                    "options": empty})
                self.add_update_field("Calculation", {
                    "options": empty + c_opts})

        # Handle Instruments Change
        elif name == "Instruments":
            instruments = map(api.get_object_by_uid, value)
            empty = [{"title": _("None"), "value": None}]
            i_opts = map(lambda o: dict(
                title=api.get_title(o), value=api.get_uid(o)), instruments)
            self.add_update_field("Instrument", {
                "options": empty + i_opts})

        return self.data

    def get_available_instruments_for(self, methods):
        """Return all available instruments for the given methods

        If no methods are given, all active instruments are returned
        """
        if methods:
            return list(chain(*map(lambda m: m.getInstruments(), methods)))
        query = {
            "portal_type": "Instrument",
            "is_active": True,
            "sort_on": "sortable_title"
        }
        brains = self.setup_catalog(query)
        return map(api.get_object, brains)

    def get_available_calculations_for(self, methods):
        """Return all available instruments for the given methods

        If no methods are given, all active instruments are returned
        """
        if methods:
            return list(chain(*map(lambda m: m.getCalculations(), methods)))
        query = {
            "portal_type": "Calculation",
            "is_active": True,
            "sort_on": "sortable_title"
        }
        brains = self.setup_catalog(query)
        return map(api.get_object, brains)

    @property
    def setup_catalog(self):
        return api.get_tool(SETUP_CATALOG)

    @property
    def analysis_catalog(self):
        return api.get_tool(CATALOG_ANALYSIS_LISTING)

    def can_change_keyword(self, keyword):
        """Check if the keyword can be changed

        Writable if no active analyses exist with the given keyword
        """
        query = {
            "portal_type": "Analysis",
            "is_active": True,
            "getKeyword": keyword}
        brains = self.analysis_catalog(query)
        return len(brains) == 0

    def validate_keyword(self, value):
        """Validate the service keyword
        """
        current_value = self.context.getKeyword()
        # Check if the values changed
        if current_value == value:
            # nothing changed
            return
        # Check if the new value is empty
        if not value:
            return _("Keyword required")
        # Check if the current value is used in a calculation
        ref = "[{}]".format(current_value)
        query = {"portal_type": "Calculation"}
        for brain in self.setup_catalog(query):
            calc = api.get_object(brain)
            if ref in calc.getFormula():
                return _("Current keyword '{}' used in calculation '{}'"
                         .format(current_value, api.get_title(calc)))
        # Check the current value with the validator
        validator = ServiceKeywordValidator()
        check = validator(value, instance=self.context)
        if isinstance(check, string_types):
            return _(check)
        return None
