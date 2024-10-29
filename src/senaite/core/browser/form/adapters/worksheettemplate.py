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
from string import Template

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate

pos_regex = re.compile(r"(\d+)\.widgets\.pos$")
type_regex = re.compile(r"(\d+)\.widgets\.type$")
dup_proxy_regex = re.compile(r"(\d+)\.widgets\.dup_proxy$")
ref_proxy_regex = re.compile(r"(\d+)\.widgets\.reference_proxy$")

POS_PARENT_SELECTOR = "td:has(>[name='{}'])"
NUM_POS_SELECTOR = "#formfield-form-widgets-num_of_positions > .input-group"
POS_DIV_BLOCK = "<div style='width: 85%; text-align: center;'>{}</div>"
FIELD_NUM_POSITIONS = "form.widgets.num_of_positions"
FIELD_LAYOUT = "form.widgets.template_layout"
FIELD_POS = "form.widgets.template_layout.{}.widgets.pos"
FIELD_TYPE = "form.widgets.template_layout.{}.widgets.type:list"
FIELD_BLANK  = "form.widgets.template_layout.{}.widgets.blank_ref"
FIELD_CONTROL  = "form.widgets.template_layout.{}.widgets.control_ref"
FIELD_DUP = "form.widgets.template_layout.{}.widgets.dup"
FIELD_DUP_PROXY = "form.widgets.template_layout.{}.widgets.dup_proxy:list"
FIELD_REF_PROXY = "form.widgets.template_layout.{}.widgets.reference_proxy:list"

NUM_POS_HTML = Template("""
<input
    type="submit"
    class="button-num-positions btn-primary"
    formaction="$absolute_url/@@update_num_positions"
    value="$title"
/>
""")


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Worksheet Template
    """

    def initialized(self, data):
        self.add_change_num_positions(data)
        self.init_toggle_fields(data)
        return self.data

    def init_toggle_fields(self, data):
        form = data.get("form")
        if int(form.get(FIELD_NUM_POSITIONS, "0")) == 0:
            self.toggle_field(FIELD_LAYOUT, False)
        else:
            self.modify_positions(data)
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

        type_match = type_regex.search(name)
        dup_match = dup_proxy_regex.search(name)
        ref_match = ref_proxy_regex.search(name)

        if name == "form.widgets.restrict_to_method" and value:
            method_uid = value[0]
            options = self.get_instruments_options(method_uid)
            self.add_update_field("form.widgets.instrument", {
                "options": options
            })
        elif type_match:
            idx = type_match.group(1)
            val = value[0]
            self.toggle_fields(data, val, idx)
        elif dup_match:
            idx = dup_match.group(1)
            if value:
                val = value[0]
                self.add_update_field(FIELD_DUP.format(idx), val)
            else:
                msg = translate(_(
                    u"duplicate_reference_not_found",
                    default=u"Not found Analysis position for duplicate."))
                self.add_error_field(FIELD_DUP_PROXY.format(idx), msg)
        elif ref_match:
            idx = ref_match.group(1)
            form = data.get("form")
            analysis_type = form.get(FIELD_TYPE.format(idx))
            if analysis_type == "b":
                self.add_update_field(FIELD_BLANK.format(idx), value)
                self.add_update_field(FIELD_CONTROL.format(idx), "")
            elif analysis_type == "c":
                self.add_update_field(FIELD_BLANK.format(idx), "")
                self.add_update_field(FIELD_CONTROL.format(idx), value)

        return self.data

    def toggle_fields(self, data, field_type, index):
        self.add_error_field(FIELD_TYPE.format(index), "")
        if field_type == "a":
            self.add_update_field(FIELD_BLANK.format(index), "")
            self.add_update_field(FIELD_CONTROL.format(index), "")
            self.add_update_field(FIELD_REF_PROXY.format(index), "")
            self.add_update_field(FIELD_DUP_PROXY.format(index), "")
            self.add_update_field(FIELD_DUP.format(index), "")

        self.toggle_reference_field(data, index, field_type)
        self.toggle_duplicate_field(data, index, field_type)

    def toggle_duplicate_field(self, data, index, field_type):
        field = FIELD_DUP_PROXY.format(index)
        toggle = field_type == "d"
        if toggle and self.validate_duplicate(data, index):
            self.update_duplicate_items(data, index)
        self.toggle_field(field, toggle)

    def validate_duplicate(self, data, index):
        form = data.get("form")
        current_pos = int(form.get(FIELD_POS.format(index)))
        count_rows = self.get_count_rows(data)
        dup_pos = 0
        for i in range(count_rows):
            dup_value = form.get(FIELD_DUP.format(i))
            if not dup_value:
                continue
            if int(dup_value) == current_pos:
                dup_pos = int(form.get(FIELD_POS.format(i)))
                break

        if dup_pos:
            msg = translate(_(
                u"duplicate_reference_this_position",
                default=u"Duplicate in position ${dup} references this, "
                        u"so it must be a routine analysis.",
                mapping={"dup": dup_pos})
            )
            self.add_error_field(FIELD_TYPE.format(index), msg)
            return False
        return True

    def toggle_reference_field(self, data, index, field_type):
        field = FIELD_REF_PROXY.format(index)
        toggle = field_type in ["b", "c"]
        field_ref = FIELD_BLANK if field_type == "b" else FIELD_CONTROL
        field_ref = field_ref.format(index)
        self.toggle_field(field, toggle)
        if toggle and self.validate_duplicate(data, index):
            form = data.get("form")
            options = self.get_reference_definitions(field_type)
            selected = form.get(field_ref)
            if len(options) and not selected:
                selected = options[0].get("value")
                self.add_update_field(field_ref, selected)

            self.add_update_field(field, {
                "options": options,
                "selected": selected,
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
        includes = set()
        count_rows = self.get_count_rows(data)
        for i in range(count_rows):
            select_type = form.get(FIELD_TYPE.format(i))
            if select_type == "a":
                includes.add(form.get(FIELD_POS.format(i)))

        field_dup = FIELD_DUP.format(index)
        options = [dict(value=pos, title=pos) for pos in includes]
        selected = form.get(field_dup)
        if len(includes) and not selected:
            selected = next(iter(includes))
            self.add_update_field(field_dup, selected)

        self.add_update_field(FIELD_DUP_PROXY.format(index), {
            "options": options,
            "selected": selected,
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

    def add_change_num_positions(self, data):
        url = self.context.absolute_url()
        title = translate(_(u"num_of_positions_button_title", default=u"Set"))
        html = NUM_POS_HTML.safe_substitute(absolute_url=url, title=title)
        self.add_inner_html(NUM_POS_SELECTOR, html, append=True)

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
