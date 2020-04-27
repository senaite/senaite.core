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
from Products.Archetypes.Widget import TypesWidget


class RejectionSetupWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/rejectionsetupwidget",
        'helper_js': ("bika_widgets/rejectionsetupwidget.js",),
        'helper_css': ("bika_widgets/rejectionsetupwidget.css",),
    })

    security = ClassSecurityInfo()

    def getSortKeys(self,keys):
        # return the option's keys in sorted in order to obtain a sorted set of
        # options.
        # checkbox object isn't an option
        if 'checkbox' in keys:
            keys.remove('checkbox')
        if len(keys) == 0:
            # Doing that in order to get one blank textfield
            keys = ['blank']
        return sorted(keys)


registerWidget(RejectionSetupWidget,
               title = "Setup's Rejection Widget",
               description = ('Widget to define the rejection reasons'),
               )
