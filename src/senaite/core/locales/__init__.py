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

import json
from operator import itemgetter
from senaite.core.api import geo
from senaite.core.p3compat import cmp
from bika.lims.browser import BrowserView


class ajaxGetCountries(BrowserView):

    def __call__(self):
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ISO code list
        for country in geo.get_countries():
            iso = country.alpha_2
            name = country.name
            country_info = {"Code": iso, "Country": name}
            if iso.lower().find(searchTerm) > -1:
                rows.append(country_info)
            elif name.lower().find(searchTerm) > -1:
                rows.append(country_info)

        rows = sorted(rows, cmp=lambda x,y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'Country'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page) - 1) * int(nr_rows) : int(page) * int(nr_rows) ]}

        return json.dumps(ret)


class ajaxGetStates(BrowserView):

    def __call__(self):
        items = []
        country = self.request.get('country', '')
        if not country:
            return json.dumps(items)

        # Get the states
        items = geo.get_subdivisions(country, default=[])
        items = map(lambda sub: [sub.country_code, sub.code, sub.name], items)
        return json.dumps(items)


class ajaxGetDistricts(BrowserView):

    def __call__(self):
        country = self.request.get('country', '')
        state = self.request.get('state', '')
        items = []
        if not all([country, state]):
            return json.dumps(items)

        # first-level subdivisions (districts?) of this subdivision (state?)
        state = geo.get_subdivision(state, parent=country, default=None)
        items = geo.get_subdivisions(state, default=[])
        items = map(lambda sub: [sub.country_code, sub.code, sub.name],  items)
        return json.dumps(items)
