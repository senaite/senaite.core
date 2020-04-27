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
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims.locales import COUNTRIES,STATES,DISTRICTS
import json
import plone

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
        items = []
        items = [(x['ISO'], x['Country']) for x in COUNTRIES]
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return items

    def getDefaultCountry(self):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        bs = portal._getOb('bika_setup')
        return bs.getDefaultCountry()

    def getStates(self, country):
        items = []
        if not country:
            return items
        # get ISO code for country
        iso = [c for c in COUNTRIES if c['Country'] == country or c['ISO'] == country]
        if not iso:
            return items
        iso = iso[0]['ISO']
        items = [x for x in STATES if x[0] == iso]
        items.sort(lambda x,y: cmp(x[2], y[2]))
        return items

    def getDistricts(self, country, state):
        items = []
        if not country or not state:
            return items
        # get ISO code for country
        iso = [c for c in COUNTRIES if c['Country'] == country or c['ISO'] == country]
        if not iso:
            return items
        iso = iso[0]['ISO']
        # get NUMBER of the state for lookup
        snr = [s for s in STATES if s[0] == iso and s[2] == state]
        if not snr:
            return items
        snr = snr[0][1]
        items = [x for x in DISTRICTS if x[0] == iso and x[1] == snr]
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return items

registerWidget(AddressWidget,
               title = 'Address Widget',
               description = ('Simple address widget with country/state lookups'),
               )
