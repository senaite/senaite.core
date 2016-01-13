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
    return 0 values if the result is above 0.
    :param numeric_value: the value to get the precision from
    :return: the numeric_value's precision
            Examples:
            numeric_value     Returns
            0               0
            0.22            1
            1.34            0
            0.0021          3
            0.013           2
            2               0
            22              0
    """
    try:
        numeric_value = float(numeric_value)
    except ValueError:
        return None
    if numeric_value == 0:
        return 0
    significant_digit = int(math.floor(math.log10(abs(numeric_value))))
    return 0 if significant_digit > 0 else abs(significant_digit)


def format_uncertainty(analysis, result, decimalmark='.', sciformat=1):
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
    :param sciformat: 1. The sci notation has to be formatted as aE^+b
                  2. The sci notation has to be formatted as ax10^b
                  3. As 2, but with super html entity for exp
                  4. The sci notation has to be formatted as a·10^b
                  5. As 4, but with super html entity for exp
                  By default 1
    :return: the formatted uncertainty
    """
    try:
        result = float(result)
    except ValueError:
        return ""

    objres = None
    try:
        objres = float(analysis.getResult())
    except ValueError:
        pass

    service = analysis.getService()
    uncertainty = None
    if result == objres:
        # To avoid problems with DLs
        uncertainty = analysis.getUncertainty()
    else:
        uncertainty = analysis.getUncertainty(result)

    if uncertainty is None or uncertainty == 0:
        return ""

    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = service.getExponentialFormatPrecision()
    # Current result precision is above the threshold?
    sig_digits = get_significant_digits(result)
    negative = sig_digits < 0
    sign = '-' if negative else ''
    sig_digits = abs(sig_digits)
    sci = sig_digits >= threshold and sig_digits > 0

    formatted = ''
    if sci:
        # Scientific notation
        # 3.2014E+4
        if negative == True:
            res = float(uncertainty)*(10**sig_digits)
        else:
            res = float(uncertainty)/(10**sig_digits)
            res = float(str("%%.%sf" % (sig_digits-1)) % res)
        res = int(res) if res.is_integer() else res

        if sciformat in [2,3,4,5]:
            if sciformat == 2:
                # ax10^b or ax10^-b
                formatted = "%s%s%s%s" % (res,"x10^",sign,sig_digits)
            elif sciformat == 3:
                # ax10<super>b</super> or ax10<super>-b</super>
                formatted = "%s%s%s%s%s" % (res,"x10<sup>",sign,sig_digits,"</sup>")
            elif sciformat == 4:
                # ax10^b or ax10^-b
                formatted = "%s%s%s%s" % (res,"·10^",sign,sig_digits)
            elif sciformat == 5:
                # ax10<super>b</super> or ax10<super>-b</super>
                formatted = "%s%s%s%s%s" % (res,"·10<sup>",sign,sig_digits,"</sup>")
        else:
            # Default format: aE^+b
            sig_digits = "%02d" % sig_digits
            formatted = "%s%s%s%s" % (res,"e",sign,sig_digits)
            #formatted = str("%%.%se" % sig_digits) % uncertainty
    else:
        # Decimal notation
        prec = analysis.getPrecision(result)
        prec = prec if prec else ''
        formatted = str("%%.%sf" % prec) % uncertainty

    return formatDecimalMark(formatted, decimalmark)


def format_numeric_result(analysis, result, decimalmark='.', sciformat=1):
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
    :param sciformat: 1. The sci notation has to be formatted as aE^+b
                      2. The sci notation has to be formatted as ax10^b
                      3. As 2, but with super html entity for exp
                      4. The sci notation has to be formatted as a·10^b
                      5. As 4, but with super html entity for exp
                      By default 1
    :return: the formatted result
    """
    try:
        result = float(result)
    except ValueError:
        return result

    # continuing with 'nan' result will cause formatting to fail.
    if math.isnan(result):
        return result

    service = analysis.getService()
    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = service.getExponentialFormatPrecision()
    # Current result precision is above the threshold?
    sig_digits = get_significant_digits(result)
    negative = sig_digits < 0
    sign = '-' if negative else ''
    sig_digits = abs(sig_digits)
    sci = sig_digits >= threshold

    formatted = ''
    if sci:
        # Scientific notation
        if sciformat in [2,3,4,5]:
            if negative == True:
                res = float(result)*(10**sig_digits)
            else:
                res = float(result)/(10**sig_digits)
                res = float(str("%%.%sf" % (sig_digits-1)) % res)
            # We have to check if formatted is an integer using "'.' in formatted"
            # because ".is_integer" doesn't work with X.0
            res = int(res) if '.' not in res else res
            if sciformat == 2:
                # ax10^b or ax10^-b
                formatted = "%s%s%s%s" % (res,"x10^",sign,sig_digits)
            elif sciformat == 3:
                # ax10<super>b</super> or ax10<super>-b</super>
                formatted = "%s%s%s%s%s" % (res,"x10<sup>",sign,sig_digits,"</sup>")
            elif sciformat == 4:
                # ax10^b or ax10^-b
                formatted = "%s%s%s%s" % (res,"·10^",sign,sig_digits)
            elif sciformat == 5:
                # ax10<super>b</super> or ax10<super>-b</super>
                formatted = "%s%s%s%s%s" % (res,"·10<sup>",sign,sig_digits,"</sup>")
        else:
            # Default format: aE^+b
            formatted = str("%%.%se" % sig_digits) % result
    else:
        # Decimal notation
        prec = analysis.getPrecision(result)
        prec = prec if prec else ''
        formatted = str("%%.%sf" % prec) % result
        # We have to check if formatted is an integer using "'.' in formatted"
        # because ".is_integer" doesn't work with X.0
        formatted = str(int(float(formatted))) if '.' not in formatted else formatted
    return formatDecimalMark(formatted, decimalmark)
