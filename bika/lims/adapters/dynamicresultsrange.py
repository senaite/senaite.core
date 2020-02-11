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

from bika.lims import api
from bika.lims.interfaces import IDynamicResultsRange
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
        self.specification = self.analysisrequest.getSpecification()
        self.dynamicspec = None
        if self.specification:
            self.dynamicspec = self.specification.getDynamicAnalysisSpec()

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

        # Generate a match data object, which match both the column names and
        # the field names of the Analysis.
        match_data = self.get_match_data()

        rr = {}

        # Iterate over the rows and return the first where **all** values match
        # with the analysis' values
        for spec in specs:
            skip = False

            for k, v in match_data.items():
                # break if the values do not match
                if v != spec[k]:
                    skip = True
                    break

            # skip the whole specification row
            if skip:
                continue

            # at this point we have a match, update the results range dict
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

        return rr

    def __call__(self):
        return self.get_results_range()
