# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.interfaces import IDynamicResultsRange
from zope.interface import implementer

marker = object()


@implementer(IDynamicResultsRange)
class DynamicResultsRange(object):
    """Default Dynamic Results Range Adapter

    Matches all columns against the Analysis field values with the same names.
    """

    def __init__(self, analysis):
        self.analysis = analysis
        self.analysisrequest = analysis.getRequest()
        self.specification = self.analysisrequest.getSpecification()
        self.dynamicspec = None
        if self.specification:
            self.dynamicspec = self.specification.getDynamicAnalysisSpec()

    def convert(self, value):
        if api.is_uid(value):
            obj = api.get_object_by_uid(value)
            return api.get_title(obj)
        return value

    def get_match_data(self):
        data = {}
        for column in self.dynamicspec.get_header():
            an_value = getattr(self.analysis, column, marker)
            ar_value = getattr(self.analysisrequest, column, marker)
            if an_value is not marker:
                data[column] = self.convert(an_value)
            elif ar_value is not marker:
                data[column] = self.convert(ar_value)
        return data

    def get_results_range(self):
        if self.dynamicspec is None:
            return {}
        keyword = self.analysis.getKeyword()
        by_keyword = self.dynamicspec.get_by_keyword()
        specs = by_keyword.get(keyword)
        if not specs:
            return {}

        match_data = self.get_match_data()

        # Iterate over the rows and return the first where all values match
        # with the analysis' values
        for spec in specs:
            match = True
            for k, v in match_data.items():
                if v != spec[k]:
                    match = False
                    break
            if match:
                return spec
        return {}

    def __call__(self):
        return self.get_results_range()
