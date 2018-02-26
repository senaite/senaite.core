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
    """Checks if the result for the analysis passed in is out of range and out
    of shoulders range.

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

    # Note that routine analyses, duplicates and reference analyses all them
    # implement the function getResultRange. For routine analyses, the function
    # returns the valid range based on the specs assigned during the creation
    # process. For duplicates, the function returns the valid range assigned to
    # the analysis the duplicated was generated from. For reference analyses,
    # getResultRange returns the valid range as indicated in the Reference
    # Sample from which the analysis was created.
    result_range = api.safe_getattr(analysis, "getResultsRange", None)
    if not result_range or not isinstance(result_range, dict):
        # No result range defined or the passed in object does not suit
        return False, False

    # The assignment of result as default fallback for min and max guarantees
    # the result will be in range also if no min/max values are defined
    specs_min = api.to_float(result_range.get('min', result), result)
    specs_max = api.to_float(result_range.get('max', result), result)
    if specs_min is None and specs_max is None:
        # Neither min nor max defined
        return False, False

    result = api.to_float(result)
    if specs_min <= result <= specs_max:
        # In range, no need to check shoulders
        return False, False

    # Out of range, check shoulders
    error = api.to_float(result_range.get('error', 0.0), 0.0)
    # In results range, error comes in percentage
    error_ratio = error and error / 100.0 or 0.0
    error_amount = (specs_max - specs_min) * error_ratio
    error_min = specs_min - error_amount
    error_max = specs_max + error_amount
    in_shoulders = error_min <= result <= error_max
    return True, not in_shoulders
