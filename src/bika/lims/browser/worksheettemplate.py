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

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import DisplayList
from bika.lims.browser import BrowserView
from bika.lims.browser.widgets.serviceswidget import ServicesView
import json


class AJAXGetWorksheetTemplateInstruments(BrowserView):
    """
    Returns a vocabulary with the instruments available for the selected method
    """
    def __call__(self):
        if 'method_uid' in self.request.keys():
            method_uid = str(json.loads(self.request.get('method_uid', '')))
            cfilter = {
                'portal_type': 'Instrument',
                'is_active': True,
                'getMethodUIDs': {"query": method_uid,
                                  "operator": "or"}}
            bsc = getToolByName(self, 'bika_setup_catalog')
            items = [{'uid': '', 'm_title': 'No instrument'}] + [
                {'uid': o.UID, 'm_title': o.Title} for o in
                bsc(cfilter)]
            items.sort(lambda x, y: cmp(x['m_title'], y['m_title']))
            return json.dumps(items)
