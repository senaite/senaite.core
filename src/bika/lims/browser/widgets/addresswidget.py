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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from senaite.core.locales import get_countries
from senaite.core.locales import get_states
from senaite.core.locales import get_districts
from senaite.core.p3compat import cmp


class AddressWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/addresswidget",
        'helper_js': ("bika_widgets/addresswidget.js",),
        'helper_css': ("bika_widgets/addresswidget.css",),
        'showLegend': True,
        'showDistrict': True,
        'showCopyFrom': True,
        'showCity': True,
        'showPostalCode': True,
        'showAddress': True,
    })

    security = ClassSecurityInfo()

    # The values in the form/field are always
    # Country Name, State Name, District Name.

    def getCountries(self):
        countries = get_countries()
        items = map(lambda item: (item.alpha_2, item.name), countries)
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items

    def getDefaultCountry(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        bs = portal._getOb('bika_setup')
        return bs.getDefaultCountry()

    def getStates(self, country):
        items = []
        if not country:
            return items

        # Get the states
        items = get_states(country, default=[])
        return map(lambda sub: [sub.country_code, sub.code, sub.name], items)

    def getDistricts(self, country, state):
        items = []
        if not country or not state:
            return items
        items = get_districts(country, state)
        return map(lambda sub: [sub.country_code, sub.code, sub.name],  items)


registerWidget(AddressWidget,
               title = 'Address Widget',
               description = ('Simple address widget with country/state lookups'),
               )
