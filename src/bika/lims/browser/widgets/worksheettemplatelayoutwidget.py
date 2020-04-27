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
from Products.Archetypes.Registry import registerWidget
from Products.ATExtensions.widget.records import RecordsWidget


class WorksheetTemplateLayoutWidget(RecordsWidget):
    security = ClassSecurityInfo()
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/worksheettemplatelayoutwidget",
        'helper_js': ("bika_widgets/worksheettemplatelayoutwidget.js",),
        'helper_css': ("bika_widgets/worksheettemplatelayoutwidget.css",),
    })

    security.declarePublic('get_template_rows')
    def get_template_rows(self, num_positions, current_field_value):
        try:
            num_pos = int(num_positions)
        except ValueError:
            num_pos = 10

        rows = []
        i = 1
        if current_field_value:
            for row in current_field_value:
                if num_pos > 0:
                    if i > num_pos:
                        break
                rows.append(row)
                i = i + 1
        for i in range(i, (num_pos + 1)):
            row = {
                'pos': i,
                'type': 'a',
                'sub': 1}
            rows.append(row)
        return rows


registerWidget(
    WorksheetTemplateLayoutWidget,
    title='WS Template Analyses Layout',
    description=('Worksheet analyses layout.'),
)
