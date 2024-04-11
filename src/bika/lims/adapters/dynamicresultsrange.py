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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IDynamicResultsRange
from plone.memoize.instance import memoize
from senaite.core.p3compat import cmp
from zope.interface import implementer

marker = object()

DEFAULT_RANGE_KEYS = [
    "min",
    "warn_min",
    "min_operator",
    "minpanic",
    "max",
    "warn_max",
    "max",
    "maxpanic",
    "error",
]


@implementer(IDynamicResultsRange)
class DynamicResultsRange(object):
    """Default Dynamic Results Range Adapter
    """

    def __init__(self, analysis):
        self.analysis = analysis
        self.analysisrequest = analysis.getRequest()

    @property
    def specification(self):
        spec = None
        try:
            spec = self.analysisrequest.getSpecification()
        except AttributeError:
            # specification is only possible for AnalysisRequest's
            pass
        return spec

    @property
    def dynamicspec(self):
        dspec = None
        if self.specification:
            dspec = self.specification.getDynamicAnalysisSpec()
        return dspec

    @property
    def keyword(self):
        """Analysis Keyword
        """
        return self.analysis.getKeyword()

    @property
    def range_keys(self):
        """The keys of the result range dict
        """
        if not self.specification:
            return DEFAULT_RANGE_KEYS
        # return the subfields of the specification
        return self.specification.getField("ResultsRange").subfields

    def convert(self, value):
        # convert referenced UIDs to the Title
        if api.is_uid(value):
            obj = api.get_object_by_uid(value)
            return api.get_title(obj)
        return value

    @memoize
    def get_match_data(self):
        """Returns a fieldname -> value mapping of context data

        The fieldnames are selected from the column names of the dynamic
        specifications file. E.g. the column "Method" of teh specifications
        file will lookup the value (title) of the Analysis and added to the
        mapping like this: `{"Method": "Method-1"}`.

        :returns: fieldname -> value mapping
        :rtype: dict
        """
        data = {}

        # Lookup the column names on the Analysis and the Analysis Request
        for column in self.dynamicspec.get_header():
            an_value = getattr(self.analysis, column, marker)
            ar_value = getattr(self.analysisrequest, column, marker)
            if an_value is not marker:
                data[column] = self.convert(an_value)
            elif ar_value is not marker:
                data[column] = self.convert(ar_value)

        return data

    def match(self, dynamic_range):
        """Returns whether the values of all fields declared in the dynamic
        specification for the current sample match with the values set in the
        given results range
        """
        data = self.get_match_data()
        if not data:
            return False

        for k, v in data.items():
            # a missing value in excel is considered a match
            value = dynamic_range.get(k)
            if not value and value != 0:
                continue

            # break if the values do not match
            if v != value:
                return False

        # all key values matched
        return True

    def cmp_specs(self, a, b):
        """Compares two specification records
        """
        def is_empty(value):
            return not value and value != 0

        # specs with less empty values have priority
        keys = set(a.keys() + b.keys())
        empties_a = len(filter(lambda key: is_empty(a.get(key)), keys))
        empties_b = len(filter(lambda key: is_empty(b.get(key)), keys))
        if empties_a != empties_b:
            return cmp(empties_a, empties_b)

        # spec with highest min value has priority
        min_a = api.to_float(a.get("min"), 0)
        min_b = api.to_float(b.get("min"), 0)
        if min_a != min_b:
            return cmp(min_b, min_a)

        # spec with lowest max value has priority
        max_a = api.to_float(a.get("max"), 0)
        max_b = api.to_float(b.get("max"), 0)
        return cmp(max_a, max_b)

    def get_results_range(self):
        """Return the dynamic results range

        The returning dicitionary should containe at least the `min` and `max`
        values to override the ResultsRangeDict data.

        :returns: An `IResultsRangeDict` compatible dict
        :rtype: dict
        """
        if self.dynamicspec is None:
            return {}

        # A matching Analysis Keyword is mandatory for any further matches
        keyword = self.analysis.getKeyword()
        by_keyword = self.dynamicspec.get_by_keyword()

        # Get all specs (rows) from the Excel with the same Keyword
        specs = by_keyword.get(keyword)
        if not specs:
            return {}

        # Filter those with a match
        specs = filter(self.match, specs)
        if not specs:
            return {}

        # Sort them and pick the first match, that is less generic
        spec = sorted(specs, cmp=self.cmp_specs)[0]

        # at this point we have a match, update the results range dict
        rr = {}
        for key in self.range_keys:
            value = spec.get(key, marker)
            # skip if the range key is not set in the Excel
            if value is marker:
                continue
            # skip if the value is not floatable
            if not api.is_floatable(value):
                continue
            # set the range value
            rr[key] = value
        # return the updated result range
        return rr

    def __call__(self):
        return self.get_results_range()
