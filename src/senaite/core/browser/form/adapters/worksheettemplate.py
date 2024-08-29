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

import re

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.interfaces import IWorksheetTemplates
from senaite.core.browser.form.adapters import EditFormAdapterBase

pos_regex = re.compile(r"(\d+)\.widgets\.pos$")
type_regex = re.compile(r"([\d|A]+)\.widgets\.type$")
layout_regex = re.compile(r"form\.widgets\.template_layout")

class EditForm(EditFormAdapterBase):
    """Edit form adapter for Worksheet Template
    """

    def initialized(self, data):
        # register callbacks
        self.add_callback("body",
                          "datagrid:row_removed",
                          "on_row_removed")
        # self.toggle_duplicate_field(0, False)
        return self.data

    def init_toggle_fields(self, data):
        form = data.get("form")
        count_rows = self.get_count_rows(data)
        for i in range(count_rows):
            field = "form.widgets.template_layout.%s.widgets.type:list" % i
            value = form.get(field, "a")
            self.toggle_fields(value, i)

    def added(self, data):
        return self.data

    def callback(self, data):
        name = data.get("name")
        if not name:
            return
        method = getattr(self, name, None)
        if not callable(method):
            return
        return method(data)

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # Handle Methods Change
        if name == "form.widgets.restrict_to_method" and value:
            method_uid = value[0]
            options = self.get_instruments_options(method_uid)
            self.add_update_field("form.widgets.instrument", {
                "options": options
            })

        type_match = type_regex.search(name)
        if type_match:
            idx = type_match.group(1)
            val = value[0]
            self.toggle_fields(val, idx)

        if name == "form.widgets.num_of_positions":
            if self.get_count_rows(data) == int(value):
                return self.data
            if IWorksheetTemplates.providedBy(self.context):
                object_url = api.get_url(self.context)
                redirect_url = "{}?num_positions={}".format(object_url,
                                              value)
                return self.request.response.redirect(redirect_url)
        return self.data

    def toggle_fields(self, field_type, index):
        if field_type == "a":
            self.toggle_duplicate_field(index, False)
            self.toggle_blank_field(index, False)
            self.toggle_control_field(index, False)
        else:
            self.toggle_duplicate_field(index, field_type == "d")
            self.toggle_blank_field(index, field_type == "b")
            self.toggle_control_field(index, field_type == "c")

    def toggle_duplicate_field(self, index, toggle=False):
        field = "form.widgets.template_layout.%s.widgets.dup:list" % index
        self.toggle_field(field, toggle)

    def toggle_blank_field(self, index, toggle=False):
        field = "form.widgets.template_layout.%s.widgets.blank_ref" % index
        self.toggle_field(field, toggle)

    def toggle_control_field(self, index, toggle=False):
        field = "form.widgets.template_layout.%s.widgets.control_ref" % index
        self.toggle_field(field, toggle)

    def toggle_field(self, field, toggle=False):
        if toggle:
            self.add_show_field(field)
        else:
            self.add_hide_field(field)

    def get_instruments_options(self, method):
        """Returns a list of dicts that represent instrument options suitable
        for a selection list, with an empty option as first item
        """
        options = [{
            "title": _(u"form_widget_instrument_title",
                       default=u"No Instrument"),
            "value": [""]
        }]
        method = api.get_object(method, default=None)
        instruments = method.getInstruments() if method else []
        for instrument in instruments:
            option = {
                "title": api.get_title(instrument),
                "value": api.get_uid(instrument)
            }
            options.append(option)

        return options

    def on_row_removed(self, data):
        """
        """
        self.recalculate_positions(data)
        return self.data

    def recalculate_positions(self, data):
        """
        """
        count_rows = self.get_count_rows(data)
        for i in range(count_rows):
            field = "form.widgets.template_layout.%s.widgets.pos" % i
            pos = str(i + 1)
            self.add_update_field(field, pos)
            self.add_hide_field(field)
            selector = "td:has(>[name='%s'])" % field
            html = "<span>%s</span>" % pos
            self.add_inner_html(selector, html, append=True)

    def get_count_rows(self, data):
        form = data.get("form")
        positions = [k for k in form.keys() if pos_regex.search(k)]
        return len(positions)
