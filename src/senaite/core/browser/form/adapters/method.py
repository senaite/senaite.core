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

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.catalog import SETUP_CATALOG
from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Method
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        if name == "Instruments":
            # check if instruments can be removed
            self.add_error_field(
                "Instruments", self.validate_instruments(value))
        elif name == "Calculations":
            # check if calculations can be removed
            self.add_error_field(
                "Calculations", self.validate_calculations(value))

        return self.data

    @property
    def setup_catalog(self):
        return api.get_tool(SETUP_CATALOG)

    def validate_instruments(self, instruments):
        """Check if the new instruments are valid for the method
        """
        messages = []

        cur_instr = self.context.getRawInstruments()
        removed_instr = set(cur_instr).difference(instruments)

        # check methods using us
        query = {
            "portal_type": "AnalysisService",
            "method_available_uid": api.get_uid(self.context)
        }
        brains = self.setup_catalog(query)

        for brain in brains:
            service = api.get_object(brain)
            service_instr = service.getRawInstruments()
            used_instr = set(service_instr).intersection(removed_instr)
            for instr in used_instr:
                obj = api.get_object_by_uid(instr)
                message = _("Instrument '{}' is used by service '{}'"
                            .format(api.get_title(obj), api.get_title(brain)))
                messages.append(message)

        return "<br/>".join(messages)

    def validate_calculations(self, calculations):
        """Check if the new calculations are valid for the method
        """
        messages = []

        cur_calcs = self.context.getRawCalculations()
        removed_calcs = set(cur_calcs).difference(calculations)

        # check methods using us
        query = {
            "portal_type": "AnalysisService",
            "method_available_uid": api.get_uid(self.context)
        }
        brains = self.setup_catalog(query)

        for brain in brains:
            service = api.get_object(brain)
            service_calc = service.getRawCalculation()
            if service_calc in removed_calcs:
                obj = api.get_object_by_uid(service_calc)
                message = _("Calculation '{}' is used by service '{}'"
                            .format(api.get_title(obj), api.get_title(brain)))
                messages.append(message)

        return "<br/>".join(messages)
