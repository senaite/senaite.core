# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.
# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api


def is_out_of_range(brain_or_object):
    """Checks if the result for the analysis passed in is out of range and/or
    out of shoulders range.

            min                                                   max
            warn            min                   max             warn
    ·········|---------------|=====================|---------------|·········
    ----- out-of-range -----><----- in-range ------><----- out-of-range -----
             <-- shoulder --><----- in-range ------><-- shoulder -->

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: A tuple of a size of two where the first value is True or False
    whether if the passed in object is out of range and the second value is
    True or False if the passed in object is out of shoulders range.
    :rtype: (bool, bool)
    """
    analysis = api.get_object(brain_or_object)
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
    if not result_range or not isinstance(result_range, dict):
        # No result range defined or the passed in object does not suit
        return False, False

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
    return True, warn_min <= result <= warn_max
