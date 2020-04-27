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
from bika.lims.browser.widgets.recordswidget import RecordsWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName

class PartitionSetupWidget(RecordsWidget):
    security = ClassSecurityInfo()
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/recordswidget",
        'helper_js': ("bika_widgets/recordswidget.js",),
        'helper_css': ("bika_widgets/recordswidget.css",),
        'allowDelete': True,
    })

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
                     emptyReturnsMarker = False):
        """ Some special field handling for disabled fields, which don't
        get submitted by the browser but still need to be written away.
        """
        bsc = getToolByName(instance, 'bika_setup_catalog')
        default = super(PartitionSetupWidget,self).process_form(
            instance, field, form, empty_marker, emptyReturnsMarker)
        if not default:
            return [], {}
        value = default[0]
        kwargs = len(default) > 1 and default[1] or {}
        newvalue = []
        for v in value:
            v = dict(v)
            if v.get('separate', '') == 'on' and not 'preservation' in v:
                container_uid = v.get('container', [''])[0];
                if container_uid:
                    container = bsc(UID=container_uid)[0].getObject();
                    if container.getPrePreserved():
                        pres = container.getPreservation()
                        if pres:
                            v['preservation'] = [pres.UID()]
            newvalue.append(v)
        return newvalue, kwargs

registerWidget(PartitionSetupWidget,
               title = 'PartitionSetupWidget',
               description = (''),
               )
