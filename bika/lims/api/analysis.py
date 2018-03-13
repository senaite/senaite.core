# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.api import _marker
from bika.lims.interfaces import IAnalysis, IReferenceAnalysis, \
    IResultOutOfRange
from zope.component._api import getAdapters


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
    if not api.is_floatable(result):
        # Result is empty/None or not a valid number
        return False, False

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

    # The assignment of result as default fallback for min and max guarantees
    # the result will be in range also if no min/max values are defined
    specs_min = api.to_float(result_range.get('min', result), result)
    specs_max = api.to_float(result_range.get('max', result), result)
    if specs_min <= result <= specs_max:
        # In range, no need to check shoulders
        return False, False

    # Out of range, check shoulders. If no explicit warn_min or warn_max have
    # been defined, no shoulders must be considered for this analysis. Thus, use
    # specs' min and max as default fallback values
    warn_min = api.to_float(result_range.get('warn_min', specs_min), specs_min)
    warn_max = api.to_float(result_range.get('warn_max', specs_max), specs_max)
    in_shoulder = warn_min <= result <= warn_max
    return True, not in_shoulder
