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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import cgi
from collections import Mapping

from bika.lims import api
from bika.lims.config import MAX_OPERATORS
from bika.lims.config import MIN_OPERATORS
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces import IRejected
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.interfaces import IRetracted
from bika.lims.interfaces.analysis import IRequestAnalysis
from zope.component._api import getAdapters

_marker = object()


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
        results = api.parse_json(result)
        if not results:
            # Single, non-duplicate, non-floatable result. There is no chance
            # to know if the result is out-of-range
            return False, False

        # Multiselect result, remove empty and non-floatable 'sub' results
        results = filter(api.is_floatable, results)
        if not results:
            # No values set yet, we cannot know if out-of-range yet
            return False, False

        # Out of range only when none of the 'sub' results are within range
        for sub_result in results:
            out_range, out_shoulders = is_out_of_range(analysis, sub_result)
            if not out_range:
                # sub result within range
                return False, False

        # None of the 'sub' results are within range
        return True, True

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


def get_formatted_interval(analysis_or_results_range, default=_marker):
    """Returns a string representation of the interval defined by the results
    range passed in

    :param analysis_or_results_range: analysis, dict or ResultsRangeDict
    """
    analysis = None
    if IAnalysis.providedBy(analysis_or_results_range) or IReferenceAnalysis.providedBy(analysis_or_results_range):
        analysis = analysis_or_results_range
        results_range = analysis.getResultsRange()
    else:
        results_range = analysis_or_results_range

    if not isinstance(results_range, Mapping):
        if default is not _marker:
            return default
        api.fail("Type not supported")

    results_range = ResultsRangeDict(results_range)
    min_str = results_range.min if api.is_floatable(results_range.min) else None
    max_str = results_range.max if api.is_floatable(results_range.max) else None

    if analysis:
        min_text = analysis.getResultOptionTextByValue(min_str)
        min_str = cgi.escape(min_text) if min_text else min_str
        max_text = analysis.getResultOptionTextByValue(max_str)
        max_str = cgi.escape(max_text) if max_text else max_str

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


def is_analysis(brain_or_object):
    """Checks if the object is an analysis

    :param brain_or_object: A single catalog brain or content object
    :returns: True if the object is an analysis, False otherwise
    """
    analysis = api.get_object(brain_or_object)
    return IAnalysis.providedBy(analysis)


def is_reference_analysis(brain_or_object):
    """Checks if the object is a reference analysis

    :param brain_or_object: A single catalog brain or content object
    :returns: True if the object is a reference analysis, False otherwise
    """
    analysis = api.get_object(brain_or_object)
    return IReferenceAnalysis.providedBy(analysis)


def is_duplicate_analysis(brain_or_object):
    """Checks if the object is a duplicate analysis

    :param brain_or_object: A single catalog brain or content object
    :returns: True if the object is a duplicate analysis, False otherwise
    """
    analysis = api.get_object(brain_or_object)
    return IDuplicateAnalysis.providedBy(analysis)


def is_retracted(brain_or_object):
    """Checks if an analysis is retracted

    :param brain_or_object: A single catalog brain or content object
    :returns: True if the analysis is retracted, False otherwise
    """
    analysis = api.get_object(brain_or_object)
    if not is_analysis(analysis) and not is_reference_analysis(analysis):
        api.fail("{} is not supported. Needs to be IAnalysis or "
                 "IReferenceAnalysis".format(repr(analysis)))
    return IRetracted.providedBy(analysis)


def is_rejected(brain_or_object):
    """Checks if the analysis is rejected

    :param brain_or_object: A single catalog brain or content object
    :returns: True if the analysis is rejected, False otherwise
    """
    analysis = api.get_object(brain_or_object)
    if not is_analysis(analysis) and not is_reference_analysis(analysis):
        api.fail("{} is not supported. Needs to be IAnalysis or "
                 "IReferenceAnalysis".format(repr(analysis)))
    return IRejected.providedBy(analysis)


def is_retested(brain_or_object):
    """Checks if the analysis is retested

    :param brain_or_object: A single catalog brain or content object
    :returns: True if the analysis is retested, False otherwise
    """
    analysis = api.get_object(brain_or_object)
    if not is_analysis(analysis) and not is_reference_analysis(analysis):
        api.fail("{} is not supported. Needs to be IAnalysis or "
                 "IReferenceAnalysis".format(repr(analysis)))
    return analysis.isRetested()


def get_dependencies(brain_or_object, with_retests=False, recursive=False):
    """Returns the list of dependent analysis UIDs for the analysis passed in

    :param brain_or_object: A single catalog brain or content object
    :returns: List analysis objects that this analysis depends on
    """
    if not is_analysis(brain_or_object):
        return []

    dependencies = set()
    analysis = api.get_object(brain_or_object)

    # no calculation, no dependencies
    calc = analysis.getCalculation()
    if not calc:
        return []

    # get the sample (might be a partition)
    sample = analysis.getRequest()
    # get calculation dependencies
    service_deps = calc.getDependentServices()
    # get the keywords of the dependent services
    keywords = [s.getKeyword() for s in service_deps]
    # no dependencies to other services, nothing to do
    if not keywords:
        return []
    # collect the analyses
    dependencies.update(sample.getAnalyses(getKeyword=keywords))

    # calculate all dependencies for our dependencies
    if recursive:
        # iterate over all dependencies and get their dependencies
        for dep in list(dependencies):
            dependencies.update(get_dependencies(
                dep, with_retests=with_retests, recursive=recursive))

    if not with_retests:
        # filter out retracted, rejected and retested analyses
        def is_retest(analysis):
            return is_retracted(analysis) or is_rejected(analysis) \
                or is_retested(analysis)
        dependencies = filter(lambda d: not is_retest(d), dependencies)

    return map(api.get_object, dependencies)


def get_dependents(brain_or_object, with_retests=False, recursive=False):
    """Returns the list of analysis UIDs that depend on the current

    :param brain_or_object: A single catalog brain or content object
    :returns: List of analysis object that depend on the current analysis
    """
    if not is_analysis(brain_or_object):
        return []

    dependents = set()
    analysis = api.get_object(brain_or_object)

    # get the service of the current analysis
    service = analysis.getAnalysisService()

    # get the sample (might be a partition)
    sample = analysis.getRequest()

    # get all analyses with calculations
    analyses_with_calcs = sample.getAnalyses(
        has_calculation=True, full_objects=True)

    # Now we check if we are part of any calculation
    for analysis in analyses_with_calcs:
        calc = analysis.getCalculation()
        if not calc:
            # in case the `has_calculation` index is not there yet
            continue
        dependencies = calc.getDependentServices()
        # check if our service is a dependency
        if service in dependencies:
            # remember the analysis that depends on us
            dependents.add(analysis)

    if recursive:
        for dep in list(dependents):
            dependents.update(get_dependents(
                dep, with_retests=with_retests, recursive=recursive))

    if not with_retests:
        # filter out retracted, rejected and retested analyses
        def is_retest(analysis):
            return is_retracted(analysis) or is_rejected(analysis) \
                or is_retested(analysis)
        dependents = filter(lambda d: not is_retest(d), dependents)

    return map(api.get_object, dependents)
