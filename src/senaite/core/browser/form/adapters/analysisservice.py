# -*- coding: utf-8 -*-

from six import string_types
from itertools import chain

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.validators import ServiceKeywordValidator
from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Analysis Service
    """

    def initialized(self, data):
        form = data.get("form")
        method = form.get("Method")
        if not method:
            self.set_status_message(
                _("No Method selected for this Service"),
                level="warning")
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # Handle Keyword change
        if name == "Keyword":
            self.set_field_error("Keyword", self.validate_keyword(value))

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
                self.update_field("Method", {"options": empty + m_opts})
                self.update_field("Instruments_options", {"options": i_opts})
                self.update_field("Instruments:list", {
                    "options": i_opts, "selected": i_sel})
                self.update_field("Instrument", {"options": empty + i_opts})
                self.update_field("Calculation", {"options": empty + c_opts})
            else:
                self.update_field("Method", {"options": empty})
                self.update_field("Instruments:list", {"options": []})
                self.update_field("Instruments_options", {"options": i_opts})
                self.update_field("Instrument", {"options": empty})

        # Handle Instruments Change
        elif name == "Instruments":
            instruments = map(api.get_object_by_uid, value)
            empty = [{"title": _("None"), "value": None}]
            i_opts = map(lambda o: dict(
                title=api.get_title(o), value=api.get_uid(o)), instruments)
            self.update_field("Instrument", {"options": empty + i_opts})

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
