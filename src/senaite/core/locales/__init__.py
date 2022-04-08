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
from six import string_types
from bika.lims.utils import to_utf8

from bika.lims.browser import BrowserView

_marker = object()


def get_countries():
    """Return the list of countries sorted by name ascending
    :return: list of countries sorted by name ascending
    :rtype: list of Country objects
    """
    countries = pycountry.countries
    return sorted(list(countries), key=lambda s: s.name)


def get_country(country_subdivision_term, default=_marker):
    """Returns the country object
    :param country_subdivision_term: country, subdivision object or search term
    :type country_subdivision_term: Country/Subdivision/string
    :returns: the country that matches with the parameter passed in
    :rtype: pycountry.db.Country
    """
    if is_country(country_subdivision_term):
        return country_subdivision_term

    if is_subdivision(country_subdivision_term):
        return get_country(country_subdivision_term.country_code)

    if not isinstance(country_subdivision_term, string_types):
        if default is _marker:
            raise TypeError("{} is not supported".format(
                repr(country_subdivision_term)))
        return default

    try:
        return pycountry.countries.lookup(country_subdivision_term)
    except LookupError as e:
        if default is _marker:
            raise ValueError(str(e))
        return default


def get_country_code(country_subdivision_term, default=_marker):
    """Returns the 2-character code (alpha2) of the country
    :param country_subdivision_term: country, subdivision object or search term
    :return: the 2-character (alpha2) code of the country
    :rtype: string
    """
    if is_country(country_subdivision_term):
        return country_subdivision_term.alpha_2
    if is_subdivision(country_subdivision_term):
        return country_subdivision_term.country_code

    # Try to resolve the country by term
    country = get_country(country_subdivision_term, default=default)
    return country.alpha_2


def get_subdivision(subdivision_or_term, parent=None, default=_marker):
    """Returns the Subdivision object
    :param subdivision_or_term: subdivision or search term
    :param subdivision_or_term: Subdivision/string
    :param parent: filter by parent subdivision or country
    :returns: the subdivision that matches with the parameter passed in
    :rtype: pycountry.db.Subdivision
    """
    if is_subdivision(subdivision_or_term):
        return subdivision_or_term

    if not isinstance(subdivision_or_term, string_types):
        if default is _marker:
            raise TypeError("{} is not supported".format(
                repr(subdivision_or_term)))
        return default

    if parent:
        # Search by parent
        def is_match(subdivision):
            terms = [subdivision.name, subdivision.code]
            needle = to_utf8(subdivision_or_term)
            return needle in map(to_utf8, terms)

        subdivisions = get_subdivisions(parent, default=_marker)
        subdivisions = filter(lambda subdiv: is_match(subdiv), subdivisions)
        if len(subdivisions) == 1:
            return subdivisions[0]
        elif len(subdivisions) > 1:
            if default is _marker:
                raise ValueError("More than one subdivision found")
            return default
        else:
            if default is _marker:
                raise ValueError("No subdivisions found")
            return None

    # Search directly by term
    try:
        return pycountry.subdivisions.lookup(subdivision_or_term)
    except LookupError as e:
        if default is _marker:
            raise ValueError(str(e))
        return default


def is_country(something):
    """Returns whether the value passed in is a country object
    """
    if not something:
        return False
    # pycountry generates the classes dynamically, we cannot use isinstance
    return "Country" in repr(type(something))


def is_subdivision(something):
    """Returns whether the value passed in is a subdivision object
    """
    if not something:
        return False
    # pycountry generates the classes dynamically, we cannot use isinstance
    return "Subdivision" in repr(type(something))


def get_subdivisions(country_subdivision_term, default=_marker):
    """Returns the first-level subdivisions of the country or subdivision,
    sorted by code ascending
    :param country_subdivision_term: country, subdivision object or search term
    :return: the list of first-level subdivisions of the subdivision/country
    :rtype: list of pycountry.db.Subdivision
    """
    try:
        country_code = get_country_code(country_subdivision_term)
    except (ValueError, TypeError) as e:
        if default is _marker:
            raise e
        return default

    # Exract the subdivisions
    subdivisions = pycountry.subdivisions.get(country_code=country_code)

    # Bail out those that are not first-level
    if is_subdivision(country_subdivision_term):
        code = country_subdivision_term.code
        subdivisions = filter(lambda sub: sub.parent_code == code, subdivisions)
    else:
        subdivisions = filter(lambda sub: sub.parent_code is None, subdivisions)

    # Sort by code
    return sorted(subdivisions, key=lambda s: s.code)


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
        items = get_subdivisions(country, default=[])
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
        state = get_subdivision(state, parent=country, default=None)
        items = get_subdivisions(state, default=[])
        items = map(lambda sub: [sub.country_code, sub.code, sub.name],  items)
        return json.dumps(items)
