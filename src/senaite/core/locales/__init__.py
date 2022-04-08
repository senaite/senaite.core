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
import pycountry
from operator import itemgetter
from senaite.core.p3compat import cmp

from bika.lims.browser import BrowserView


_marker = object()


def get_countries():
    return pycountry.countries


def get_states(country, search_by='name', fallback_historic=True, default=_marker):
    kw = {search_by: country}
    country = pycountry.countries.get(**kw)
    if not country and fallback_historic:
        # Try with historical countries
        country = pycountry.historic_countries.get(**kw)

    if not country:
        if default is _marker:
            raise ValueError("Country not found: '{}'".format(country))
        return default

    # Extract the first-level subdivisions of the country
    states = pycountry.subdivisions.get(country_code=country.alpha_2)
    states = filter(lambda sub: sub.parent_code is None, states)

    # Sort by name
    return sorted(list(states), key=lambda s: s.name)


def get_districts(country_name, state_name):
    states = get_states(country_name, default=[])
    state = filter(lambda st: st.name == state_name, states)
    if not state:
        return []

    # Extracts the districts for this state
    state = state[0]
    districts = pycountry.subdivisions.get(country_code=state.country_code)
    districts = filter(lambda dis: dis.parent_code == state.code, districts)

    # Sort by name
    return sorted(list(districts), key=lambda s: s.name)


class ajaxGetCountries(BrowserView):

    def __call__(self):
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        rows = []

        # lookup objects from ISO code list
        for country in get_countries():
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
        items = get_states(country, default=[])
        items = map(lambda sub: [sub.country_code, sub.code, sub.name], items)
        return json.dumps(items)


class ajaxGetDistricts(BrowserView):

    def __call__(self):
        country = self.request.get('country', '')
        state = self.request.get('state', '')
        items = []
        if not all([country, state]):
            return json.dumps(items)

        items = get_districts(country, state)
        items = map(lambda sub: [sub.country_code, sub.code, sub.name],  items)
        return json.dumps(items)
