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

from collections import Mapping
from bika.lims import api
from bika.lims.api import _marker
from bika.lims.config import MIN_OPERATORS, MAX_OPERATORS
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.interfaces import IAnalysis, IReferenceAnalysis, \
    IResultOutOfRange
from zope.component._api import getAdapters

from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.interfaces import ISubmitted
from bika.lims.interfaces.analysis import IRequestAnalysis


def is_out_of_range(brain_or_object, result=_marker):
    """Checks if the result for the analysis passed in is out of range and/or
    out of shoulders range.

            min                                                   max
            warn            min                   max             warn
    ·········|---------------|=====================|---------------|·········
    ----- out-of-range -----><----- in-range ------><----- out-of-range -----
             <-- shoulder --><----- in-range ------><-- shoulder -->

    :param brain_or_object: A single catalog brain or content object
    :param result: Tentative result. If None, use the analysis result
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Tuple of two elements. The first value is `True` if the result is
    out of range and `False` if it is in range. The second value is `True` if
    the result is out of shoulder range and `False` if it is in shoulder range
    :rtype: (bool, bool)
    """
    analysis = api.get_object(brain_or_object)
    if not IAnalysis.providedBy(analysis) and \
            not IReferenceAnalysis.providedBy(analysis):
        api.fail("{} is not supported. Needs to be IAnalysis or "
                 "IReferenceAnalysis".format(repr(analysis)))

    if result is _marker:
        result = api.safe_getattr(analysis, "getResult", None)

    if result in [None, '']:
        # Empty result
        return False, False

    if IDuplicateAnalysis.providedBy(analysis):
        # Result range for duplicate analyses is calculated from the original
        # result, applying a variation % in shoulders. If the analysis has
        # result options enabled or string results enabled, system returns an
        # empty result range for the duplicate: result must match %100 with the
        # original result
        original = analysis.getAnalysis()
        original_result = original.getResult()

        # Does original analysis have a valid result?
        if original_result in [None, '']:
            return False, False

        # Does original result type matches with duplicate result type?
        if api.is_floatable(result) != api.is_floatable(original_result):
            return True, True

        # Does analysis has result options enabled or non-floatable?
        if analysis.getResultOptions() or not api.is_floatable(original_result):
            # Let's always assume the result is 'out from shoulders', cause we
            # consider the shoulders are precisely the duplicate variation %
            out_of_range = original_result != result
            return out_of_range, out_of_range

    elif not api.is_floatable(result):
        # A non-duplicate with non-floatable result. There is no chance to know
        # if the result is out-of-range
        return False, False

    # Convert result to a float
    result = api.to_float(result)

    # Note that routine analyses, duplicates and reference analyses all them
    # implement the function getResultRange:
    # - For routine analyses, the function returns the valid range based on the
    #   specs assigned during the creation process.
    # - For duplicates, the valid range is the result of the analysis the
    #   the duplicate was generated from +/- the duplicate variation.
    # - For reference analyses, getResultRange returns the valid range as
    #   indicated in the Reference Sample from which the analysis was created.
    result_range = api.safe_getattr(analysis, "getResultsRange", None)
    if not result_range:
        # No result range defined or the passed in object does not suit
        return False, False

    # Maybe there is a custom adapter
    adapters = getAdapters((analysis,), IResultOutOfRange)
    for name, adapter in adapters:
        ret = adapter(result=result, specification=result_range)
        if not ret or not ret.get('out_of_range', False):
            continue
        if not ret.get('acceptable', True):
            # Out of range + out of shoulders
            return True, True
        # Out of range, but in shoulders
        return True, False

    result_range = ResultsRangeDict(result_range)

    # The assignment of result as default fallback for min and max guarantees
    # the result will be in range also if no min/max values are defined
    specs_min = api.to_float(result_range.min, result)
    specs_max = api.to_float(result_range.max, result)

    in_range = False
    min_operator = result_range.min_operator
    if min_operator == "geq":
        in_range = result >= specs_min
    else:
        in_range = result > specs_min

    max_operator = result_range.max_operator
    if in_range:
        if max_operator == "leq":
            in_range = result <= specs_max
        else:
            in_range = result < specs_max

    # If in range, no need to check shoulders
    if in_range:
        return False, False

    # Out of range, check shoulders. If no explicit warn_min or warn_max have
    # been defined, no shoulders must be considered for this analysis. Thus, use
    # specs' min and max as default fallback values
    warn_min = api.to_float(result_range.warn_min, specs_min)
    warn_max = api.to_float(result_range.warn_max, specs_max)
    in_shoulder = warn_min <= result <= warn_max
    return True, not in_shoulder


def get_formatted_interval(results_range, default=_marker):
    """Returns a string representation of the interval defined by the results
    range passed in
    :param results_range: a dict or a ResultsRangeDict
    """
    if not isinstance(results_range, Mapping):
        if default is not _marker:
            return default
        api.fail("Type not supported")
    results_range = ResultsRangeDict(results_range)
    min_str = results_range.min if api.is_floatable(results_range.min) else None
    max_str = results_range.max if api.is_floatable(results_range.max) else None
    if min_str is None and max_str is None:
        if default is not _marker:
            return default
        api.fail("Min and max values are not floatable or not defined")

    min_operator = results_range.min_operator
    max_operator = results_range.max_operator
    if max_str is None:
        return "{}{}".format(MIN_OPERATORS.getValue(min_operator), min_str)
    if min_str is None:
        return "{}{}".format(MAX_OPERATORS.getValue(max_operator), max_str)

    # Both values set. Return an interval
    min_bracket = min_operator == 'geq' and '[' or '('
    max_bracket = max_operator == 'leq' and ']' or ')'

    return "{}{};{}{}".format(min_bracket, min_str, max_str, max_bracket)


def is_result_range_compliant(analysis):
    """Returns whether the result range from the analysis matches with the
    result range for the service counterpart defined in the Sample
    """
    if not IRequestAnalysis.providedBy(analysis):
        return True

    if IDuplicateAnalysis.providedBy(analysis):
        # Does not make sense to apply compliance to a duplicate, cause its
        # valid range depends on the result of the original analysis
        return True

    rr = analysis.getResultsRange()
    service_uid = rr.get("uid", None)
    if not api.is_uid(service_uid):
        return True

    # Compare with Sample
    sample = analysis.getRequest()

    # If no Specification is set, assume is compliant
    specification = sample.getRawSpecification()
    if not specification:
        return True

    # Compare with the Specification that was initially set to the Sample
    sample_rr = sample.getResultsRange(search_by=service_uid)
    if not sample_rr:
        # This service is not defined in Sample's ResultsRange, we
        # assume this *does not* break the compliance
        return True

    return rr == sample_rr
