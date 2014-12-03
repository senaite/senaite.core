# -*- coding: utf-8 -*-

import math
import zope.event
from bika.lims.utils import formatDecimalMark
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import _createObjectByType


def create_analysis(context, service, keyword, interim_fields):
    # Determine if the sampling workflow is enabled
    workflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()
    # Create the analysis
    analysis = _createObjectByType("Analysis", context, keyword)
    analysis.setService(service)
    analysis.setInterimFields(interim_fields)
    analysis.setMaxTimeAllowed(service.getMaxTimeAllowed())
    analysis.unmarkCreationFlag()
    analysis.reindexObject()
    # Trigger the intitialization event of the new object
    zope.event.notify(ObjectInitializedEvent(analysis))
    # Perform the appropriate workflow action
    try:
        workflow_action =  'sampling_workflow' if workflow_enabled \
            else 'no_sampling_workflow'
        context.portal_workflow.doActionFor(analysis, workflow_action)
    except WorkflowException:
        # The analysis may have been transitioned already!
        # I am leaving this code here though, to prevent regression.
        pass
    # Return the newly created analysis
    return analysis


def get_significant_digits(numeric_value):
    """
    Returns the precision for a given floatable value.
    If value is None or not floatable, returns None.
    Will return positive values if the result is below 0 and will
    return 0 or positive values if the result is above 0.
    :param numeric_value: the value to get the precision from
    :return: the numeric_value's precision
    """
    try:
        numeric_value = float(numeric_value)
    except ValueError:
        return None
    return int(math.floor(math.log10(abs(numeric_value))))


def format_uncertainty(analysis, result, decimalmark='.'):
    """
    Returns the formatted uncertainty according to the analysis, result
    and decimal mark specified following these rules:

    If the "Calculate precision from uncertainties" is enabled in
    the Analysis service, and
    
    a) If the the non-decimal number of digits of the result is above
       the service's ExponentialFormatPrecision, the uncertainty will
       be formatted in scientific notation. The uncertainty exponential
       value used will be the same as the one used for the result. The
       uncertainty will be rounded according to the same precision as
       the result.

       Example:
       Given an Analysis with an uncertainty of 37 for a range of
       results between 30000 and 40000, with an
       ExponentialFormatPrecision equal to 4 and a result of 32092,
       this method will return 0.004E+04

    b) If the number of digits of the integer part of the result is
       below the ExponentialFormatPrecision, the uncertainty will be
       formatted as decimal notation and the uncertainty will be
       rounded one position after reaching the last 0 (precision
       calculated according to the uncertainty value).
       
       Example:
       Given an Analysis with an uncertainty of 0.22 for a range of
       results between 1 and 10 with an ExponentialFormatPrecision
       equal to 4 and a result of 5.234, this method will return 0.2

    If the "Calculate precision from Uncertainties" is disabled in the
    analysis service, the same rules described above applies, but the
    precision used for rounding the uncertainty is not calculated from
    the uncertainty neither the result. The fixed length precision is
    used instead.

    For further details, visit
    https://jira.bikalabs.com/browse/LIMS-1334

    If the result is not floatable or no uncertainty defined, returns
    an empty string.

    The default decimal mark '.' will be replaced by the decimalmark
    specified.

    :param analysis: the analysis from which the uncertainty, precision
                     and other additional info have to be retrieved
    :param result: result of the analysis. Used to retrieve and/or
                   calculate the precision and/or uncertainty
    :param decimalmark: decimal mark to use. By default '.'
    :return: the formatted uncertainty
    """
    try:
        result = float(result)
    except ValueError:
        return ""

    service = analysis.getService()
    uncertainty = service.getUncertainty(result)

    if uncertainty is None:
        return ""

    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = service.getExponentialFormatPrecision()
    # Current result precision is above the threshold?
    sig_digits = get_significant_digits(result)
    negative = sig_digits < 0
    sig_digits = abs(sig_digits)
    sci = sig_digits >= threshold and sig_digits > 0

    formatted = ''
    if sci:
        # Scientific notation
        # 3.2014E+4
        sign = '-' if negative else '+'
        if negative == True:
            res = float(uncertainty)*(10**sig_digits)
        else:
            res = float(uncertainty)/(10**sig_digits)
            res = str("%%.%sf" % (sig_digits-1)) % res
        sig_digits = "%02d" % sig_digits
        formatted = "%s%s%s%s" % (res,"e",sign,sig_digits)
    else:
        # Decimal notation
        prec = service.getPrecision(result)
        prec = prec if prec else ''
        formatted = str("%%.%sf" % prec) % uncertainty

    return formatDecimalMark(formatted, decimalmark)


def format_numeric_result(analysis, result, decimalmark='.'):
    """
    Returns the formatted number part of a results value.  This is
    responsible for deciding the precision, and notation of numeric
    values in accordance to the uncertainty. If a non-numeric
    result value is given, the value will be returned unchanged.

    The following rules apply:

    If the "Calculate precision from uncertainties" is enabled in
    the Analysis service, and
    
    a) If the non-decimal number of digits of the result is above
       the service's ExponentialFormatPrecision, the result will
       be formatted in scientific notation.

       Example:
       Given an Analysis with an uncertainty of 37 for a range of
       results between 30000 and 40000, with an
       ExponentialFormatPrecision equal to 4 and a result of 32092,
       this method will return 3.2092E+04

    b) If the number of digits of the integer part of the result is
       below the ExponentialFormatPrecision, the result will be
       formatted as decimal notation and the resulta will be rounded
       in accordance to the precision (calculated from the uncertainty)
       
       Example:
       Given an Analysis with an uncertainty of 0.22 for a range of
       results between 1 and 10 with an ExponentialFormatPrecision
       equal to 4 and a result of 5.234, this method will return 5.2

    If the "Calculate precision from Uncertainties" is disabled in the
    analysis service, the same rules described above applies, but the
    precision used for rounding the result is not calculated from
    the uncertainty. The fixed length precision is used instead.

    For further details, visit
    https://jira.bikalabs.com/browse/LIMS-1334

    The default decimal mark '.' will be replaced by the decimalmark
    specified.

    :param analysis: the analysis from which the uncertainty, precision
                     and other additional info have to be retrieved
    :param result: result to be formatted.
    :param decimalmark: decimal mark to use. By default '.'
    :return: the formatted result
    """
    try:
        result = float(result)
    except ValueError:
        return result

    service = analysis.getService()
    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = service.getExponentialFormatPrecision()
    # Current result precision is above the threshold?
    sig_digits = abs(get_significant_digits(result))
    sci = sig_digits >= threshold

    formatted = ''
    if sci:
        # Scientific notation
        # 3.2014E+4
        formatted = str("%%.%se" % sig_digits) % result
    else:
        # Decimal notation
        prec = service.getPrecision(result)
        prec = prec if prec else ''
        formatted = str("%%.%sf" % prec) % result

    return formatDecimalMark(formatted, decimalmark)
