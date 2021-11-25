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

from senaite.core.p3compat import cmp
from bika.lims import api
from bika.lims.browser import BrowserView
import json


class AJAXGetWorksheetTemplateInstruments(BrowserView):
    """
    Returns a vocabulary with the instruments available for the selected method
    """
    def __call__(self):
        items = [{'uid': '', 'm_title': 'No instrument'}]
        if 'method_uid' not in self.request.keys():
            return json.dumps(items)

        method_uid = str(json.loads(self.request.get('method_uid', '')))
        if not method_uid:
            return json.dumps(items)

        try:
            instruments = api.get_object(method_uid).getInstruments()
        except api.APIError:
            return json.dumps(items)

        items.extend([
            {'uid': o.UID(), 'm_title': o.Title()} for o in instruments])
        items.sort(lambda x, y: cmp(x['m_title'], y['m_title']))
        return json.dumps(items)
