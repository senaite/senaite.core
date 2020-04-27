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

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
import json

class RecordsWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/recordswidget",
        'helper_js': ("bika_widgets/recordswidget.js",),
        'helper_css': ("bika_widgets/recordswidget.css",),
        'allowDelete': True,
        'readOnly': False,
        'combogrid_options': '',
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        Basic impl for form processing in a widget plus allowing empty
        values to be saved
        """

        # a poor workaround for Plone repeating itself.
        # XXX this is important XXX
        key = field.getName() + '_value'
        if key in instance.REQUEST:
            return instance.REQUEST[key], {}
        value = form.get(field.getName(), empty_marker)
        # When a recordswidget's visibility is defined as hidden
        # '...visible={'view': 'hidden', 'edit': 'hidden'},...' the template
        # displays it as an input field with the attribute 'value' as a string
        # 'value="[{:},{:}]"'. This makes the system save the content of the
        # widget as the string instead of a dictionary inside a list, so we
        # need to check if the variable contains a python object as a string.
        if value and value is not empty_marker and isinstance(value, str):
            import ast
            try:
                value = ast.literal_eval(form.get(field.getName()))
            except:
                # cannot resolve string as a list!
                return empty_marker

        if not value:
            return value, {}
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker

        # we make sure that empty "value" inputs are saved as "" empty string.
        for i in range(len(value)):
            value[i] = dict(value[i])
            if 'value' not in value[i]:
                value[i]['value'] = ''

        instance.REQUEST[key] = value
        return value, {}

    def jsondumps(self, val):
        return json.dumps(val)

registerWidget(RecordsWidget,
               title = 'RecordsWidget',
               description = '',
               )
