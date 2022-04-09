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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from six import string_types

import pycountry
from bika.lims.api import to_utf8

_marker = object()


def get_countries():
    """Return the list of countries sorted by name ascending
    :return: list of countries sorted by name ascending
    :rtype: list of Country objects
    """
    countries = pycountry.countries
    return sorted(list(countries), key=lambda s: s.name)


def get_country(thing, default=_marker):
    """Returns the country object
    :param thing: country, subdivision object or search term
    :type thing: Country/Subdivision/string
    :returns: the country that matches with the parameter passed in
    :rtype: pycountry.db.Country
    """
    if is_country(thing):
        return thing

    if is_subdivision(thing):
        return get_country(thing.country_code)

    if not isinstance(thing, string_types):
        if default is _marker:
            raise TypeError("{} is not supported".format(repr(thing)))
        return default

    try:
        return pycountry.countries.lookup(thing)
    except LookupError as e:
        if default is _marker:
            raise ValueError(str(e))
        return default


def get_country_code(thing, default=_marker):
    """Returns the 2-character code (alpha2) of the country
    :param thing: country, subdivision object or search term
    :return: the 2-character (alpha2) code of the country
    :rtype: string
    """
    thing = get_country_or_subdivision(thing, default=default)
    if is_country(thing):
        return thing.alpha_2
    if is_subdivision(thing):
        return thing.country_code
    return default


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

    # Search by parent
    if parent:

        def is_match(subdivision):
            terms = [subdivision.name, subdivision.code]
            needle = to_utf8(subdivision_or_term)
            return needle in map(to_utf8, terms)

        subdivisions = get_subdivisions(parent, default=[])
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


def is_country(thing):
    """Returns whether the value passed in is a country object
    """
    if not thing:
        return False
    # pycountry generates the classes dynamically, we cannot use isinstance
    return "Country" in repr(type(thing))


def is_subdivision(thing):
    """Returns whether the value passed in is a subdivision object
    """
    if not thing:
        return False
    # pycountry generates the classes dynamically, we cannot use isinstance
    return "Subdivision" in repr(type(thing))


def get_subdivisions(thing, default=_marker):
    """Returns the first-level subdivisions of the country or subdivision,
    sorted by code ascending
    :param thing: country, subdivision object or search term
    :return: the list of first-level subdivisions of the subdivision/country
    :rtype: list of pycountry.db.Subdivision
    """
    try:
        country_or_subdivision = get_country_or_subdivision(thing)
        country_code = get_country_code(country_or_subdivision)
    except (ValueError, TypeError) as e:
        if default is _marker:
            raise e
        return default

    # Extract the subdivisions
    subdivisions = pycountry.subdivisions.get(country_code=country_code)

    # Bail out those that are not first-level
    if is_subdivision(country_or_subdivision):
        code = country_or_subdivision.code
        subdivisions = filter(lambda sub: sub.parent_code == code, subdivisions)
    else:
        subdivisions = filter(lambda sub: sub.parent_code is None, subdivisions)

    # Sort by code
    return sorted(subdivisions, key=lambda s: s.code)


def get_country_or_subdivision(thing, default=_marker):
    """Returns the country or subdivision for the thing passed-in
    :param thing: the thing or search term to look for a country or subdivision
    :type thing: Country/Subdivision/string
    :return: the country or subdivision for the given thing
    """
    if is_country(thing):
        return thing
    if is_subdivision(thing):
        return thing

    if not isinstance(thing, string_types):
        if default is _marker:
            raise TypeError("{} is not supported".format(repr(thing)))
        return default

    # Maybe a country
    country = get_country(thing, default=None)
    if country:
        return country

    # Maybe a subdivision
    subdivision = get_subdivision(thing, default=None)
    if subdivision:
        return subdivision

    if default is _marker:
        raise ValueError("Could not find a record for '{}'".format(
            thing.lower()))
    return default
