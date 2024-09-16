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
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.catalog import SETUP_CATALOG

pos_regex = re.compile(r"(\d+)\.widgets\.pos$")
type_regex = re.compile(r"(\d+)\.widgets\.type$")
dup_proxy_regex = re.compile(r"(\d+)\.widgets\.dup_proxy$")
ref_proxy_regex = re.compile(r"(\d+)\.widgets\.reference_proxy$")

POS_PARENT_SELECTOR = "td:has(>[name='{}'])"
POS_DIV_BLOCK = "<div style='width: 85%; text-align: center;'>{}</div>"
FIELD_POS = "form.widgets.template_layout.{}.widgets.pos"
FIELD_TYPE = "form.widgets.template_layout.{}.widgets.type:list"
FIELD_BLANK  = "form.widgets.template_layout.{}.widgets.blank_ref"
FIELD_CONTROL  = "form.widgets.template_layout.{}.widgets.control_ref"
FIELD_DUP = "form.widgets.template_layout.{}.widgets.dup"
FIELD_DUP_PROXY = "form.widgets.template_layout.{}.widgets.dup_proxy:list"
FIELD_REF_PROXY = "form.widgets.template_layout.{}.widgets.reference_proxy:list"


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Worksheet Template
    """

    def initialized(self, data):
        self.modify_positions(data)
        self.init_toggle_fields(data)
        return self.data

    def init_toggle_fields(self, data):
        form = data.get("form")
        count_rows = self.get_count_rows(data)
        for index in range(count_rows):
            field = FIELD_TYPE.format(index)
            analysis_type = form.get(field, "a")
            self.toggle_fields(data, analysis_type, index)

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
            self.toggle_fields(data, val, idx)
        dup_match = dup_proxy_regex.search(name)
        if dup_match:
            idx = dup_match.group(1)
            val = value[0]
            self.add_update_field(FIELD_DUP.format(idx), val)
        ref_match = ref_proxy_regex.search(name)
        if ref_match:
            idx = ref_match.group(1)
            form = data.get("form")
            analysis_type = form.get(FIELD_TYPE.format(idx))
            if analysis_type == "b":
                self.add_update_field(FIELD_BLANK.format(idx), value)
                self.add_update_field(FIELD_CONTROL.format(idx), "")
            elif analysis_type == "c":
                self.add_update_field(FIELD_BLANK.format(idx), "")
                self.add_update_field(FIELD_CONTROL.format(idx), value)
            else:
                self.add_update_field(FIELD_BLANK.format(idx), "")
                self.add_update_field(FIELD_CONTROL.format(idx), "")

        return self.data

    def toggle_fields(self, data, field_type, index):
        self.toggle_reference_field(index, field_type)
        self.toggle_duplicate_field(data, index, field_type)

    def toggle_duplicate_field(self, data, index, field_type):
        field = FIELD_DUP_PROXY.format(index)
        toggle = field_type == "d"
        if toggle:
            self.update_duplicate_items(data, index)
        self.toggle_field(field, toggle)

    def toggle_reference_field(self, index, field_type):
        field = FIELD_REF_PROXY.format(index)
        toggle = field_type in ["b", "c"]
        self.toggle_field(field, toggle)
        if toggle:
            options = self.get_reference_definitions(field_type)
            self.add_update_field(field, {
                "options": options
            })

    def toggle_field(self, field, toggle=False):
        if toggle:
            self.add_show_field(field)
        else:
            self.add_hide_field(field)

    def update_duplicate_items(self, data, index):
        """Updating list of allowed duplicate values
        """
        form = data.get("form")
        include = set()
        exclude = set()
        count_rows = self.get_count_rows(data)
        for i in range(count_rows):
            select_type = form.get(FIELD_TYPE.format(i))
            if select_type == "a":
                include.add(form.get(FIELD_POS.format(i)))
            if select_type == "d":
                exclude.add(form.get(FIELD_DUP_PROXY.format(i)))

        options = [dict(value=pos, title=pos) for pos in include - exclude]
        self.add_update_field(FIELD_DUP_PROXY.format(index), {
            "options": options
        })

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

    def modify_positions(self, data):
        """Replacing input control to text for positions
        """
        count_rows = self.get_count_rows(data)
        for i in range(count_rows):
            field = FIELD_POS.format(i)
            pos = str(i + 1)
            self.add_update_field(field, pos)
            self.add_hide_field(field)
            selector = POS_PARENT_SELECTOR.format(field)
            html = POS_DIV_BLOCK.format(pos)
            self.add_inner_html(selector, html, append=True)

    def get_count_rows(self, data):
        form = data.get("form")
        positions = [k for k in form.keys() if pos_regex.search(k)]
        return len(positions)

    def get_reference_definitions(self, reference_type):
        reference_query = {
            "portal_type": "ReferenceDefinition",
            "is_active": True,
        }
        brains = api.search(reference_query, SETUP_CATALOG)
        definitions = map(api.get_object, brains)
        if  reference_type == "b":
            definitions = filter(lambda d: d.getBlank(), definitions)
        else:
            definitions = filter(lambda d: not d.getBlank(), definitions)
        return [dict(value=d.UID(), title=d.Title()) for d in definitions]
