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

import copy
import math

from bika.lims import api
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IBaseAnalysis
from bika.lims.interfaces import IReferenceSample
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.utils import formatDecimalMark
from bika.lims.utils import format_supsub


def create_analysis(context, source, **kwargs):
    """Create a new Analysis.  The source can be an Analysis Service or
    an existing Analysis, and all possible field values will be set to the
    values found in the source object.
    :param context: The analysis will be created inside this object.
    :param source: The schema of this object will be used to populate analysis.
    :param kwargs: The values of any keys which match schema fieldnames will
    be inserted into the corresponding fields in the new analysis.
    :returns: Analysis object that was created
    :rtype: Analysis
    """
    # Ensure we have an object as source
    source = api.get_object(source)
    if not IBaseAnalysis.providedBy(source):
        raise ValueError("Type not supported: {}".format(repr(type(source))))

    # compute the id of the new analysis if necessary
    analysis_id = kwargs.get("id")
    if not analysis_id:
        keyword = source.getKeyword()
        analysis_id = generate_analysis_id(context, keyword)

    # get the service to be assigned to the analysis
    service = source
    if not IAnalysisService.providedBy(source):
        service = source.getAnalysisService()

    # use "Analysis" as portal_type unless explicitly set
    portal_type = kwargs.pop("portal_type", "Analysis")

    # initialize interims with those from the service if not explicitly set
    interim_fields = kwargs.pop("InterimFields", service.getInterimFields())

    # do not copy these fields from source
    skip_fields = [
        "Attachment",
        "Result",
        "ResultCaptureDate",
        "Worksheet"
    ]

    kwargs.update({
        "container": context,
        "portal_type": portal_type,
        "skip": skip_fields,
        "id": analysis_id,
        "AnalysisService": service,
        "InterimFields": interim_fields,
    })
    return api.copy_object(source, **kwargs)


def get_significant_digits(numeric_value):
    """
    Returns the precision for a given floatable value.
    If value is None or not floatable, returns None.
    Will return positive values if the result is below 1 and will
    return 0 values if the result is above or equal to 1.
    :param numeric_value: the value to get the precision from
    :returns: the numeric_value's precision
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
    except (TypeError, ValueError):
        return None
    if numeric_value == 0:
        return 0
    significant_digit = int(math.floor(math.log10(abs(numeric_value))))
    return 0 if significant_digit > 0 else abs(significant_digit)


def _format_decimal_or_sci(result, precision, threshold, sciformat):
    # Current result's precision is above the threshold?
    sig_digits = get_significant_digits(result)

    # Note that if result < 1, sig_digits > 0. Otherwise, sig_digits = 0
    # Eg:
    #       result = 0.2   -> sig_digit = 1
    #                0.002 -> sig_digit = 3
    #                0     -> sig_digit = 0
    #                2     -> sig_digit = 0
    # See get_significant_digits signature for further details!
    #
    # Also note if threshold is negative, the result will always be expressed
    # in scientific notation:
    # Eg.
    #       result=12345, threshold=-3, sig_digit=0 -> 1.2345e4 = 1.2345·10⁴
    #
    # So, if sig_digits is > 0, the power must be expressed in negative
    # Eg.
    #      result=0.0012345, threshold=3, sig_digit=3 -> 1.2345e-3=1.2345·10-³
    sci = sig_digits >= threshold and abs(
        threshold) > 0 and sig_digits <= precision
    sign = '-' if sig_digits > 0 else ''
    if sig_digits == 0 and abs(threshold) > 0 and abs(int(float(result))) > 0:
        # Number >= 1, need to check if the number of non-decimal
        # positions is above the threshold
        sig_digits = int(math.log(abs(float(result)), 10)) if abs(
            float(result)) >= 10 else 0
        sci = sig_digits >= abs(threshold)

    formatted = ''
    if sci:
        # First, cut the extra decimals according to the precision
        prec = precision if precision and precision > 0 else 0
        nresult = str("%%.%sf" % prec) % api.to_float(result, 0)

        if sign:
            # 0.0012345 -> 1.2345
            res = float(nresult) * (10 ** sig_digits)
        else:
            # Non-decimal positions
            # 123.45 -> 1.2345
            res = float(nresult) / (10 ** sig_digits)
        res = int(res) if res.is_integer() else res

        # Scientific notation
        if sciformat == 2:
            # ax10^b or ax10^-b
            formatted = "%s%s%s%s" % (res, "x10^", sign, sig_digits)
        elif sciformat == 3:
            # ax10<super>b</super> or ax10<super>-b</super>
            formatted = "%s%s%s%s%s" % (
                res, "x10<sup>", sign, sig_digits, "</sup>")
        elif sciformat == 4:
            # ax10^b or ax10^-b
            formatted = "%s%s%s%s" % (res, "·10^", sign, sig_digits)
        elif sciformat == 5:
            # ax10<super>b</super> or ax10<super>-b</super>
            formatted = "%s%s%s%s%s" % (
                res, "·10<sup>", sign, sig_digits, "</sup>")
        else:
            # Default format: aE^+b
            sig_digits = "%02d" % sig_digits
            formatted = "%s%s%s%s" % (res, "e", sign, sig_digits)
    else:
        # Decimal notation
        prec = precision if precision and precision > 0 else 0
        formatted = str("%%.%sf" % prec) % api.to_float(result, 0)
        if float(formatted) == 0 and '-' in formatted:
            # We don't want things like '-0.00'
            formatted = formatted.replace('-', '')
    return formatted


def format_uncertainty(analysis, decimalmark=".", sciformat=1):
    """Return formatted uncertainty value

    If the "Calculate precision from uncertainties" is enabled in
    the Analysis service, and

    a) If the non-decimal number of digits of the result is above
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

    If the result is not floatable, the uncertainty is not defined or its value
    is not above 0, an empty string is returned.

    The default decimal mark '.' will be replaced by the decimalmark
    specified.

    :param analysis: the analysis from which the uncertainty, precision
                     and other additional info have to be retrieved
    :param decimalmark: decimal mark to use. By default '.'
    :param sciformat: 1. The sci notation has to be formatted as aE^+b
                  2. The sci notation has to be formatted as ax10^b
                  3. As 2, but with super html entity for exp
                  4. The sci notation has to be formatted as a·10^b
                  5. As 4, but with super html entity for exp
                  By default 1
    :returns: the formatted uncertainty
    """
    try:
        result = float(analysis.getResult())
    except (ValueError, TypeError):
        pass

    uncertainty = analysis.getUncertainty()
    if api.to_float(uncertainty, default=0) <= 0:
        # uncertainty is not defined or not above 0
        return ""

    # always convert exponential notation to decimal
    if "e" in uncertainty.lower():
        uncertainty = api.float_to_string(float(uncertainty))

    precision = -1
    # always get full precision of the uncertainty if user entered manually
    # => avoids rounding and cut-off
    allow_manual = analysis.getAllowManualUncertainty()
    manual_value = analysis.getField("Uncertainty").get(analysis)
    if allow_manual and manual_value:
        precision = uncertainty[::-1].find(".")

    if precision == -1:
        precision = analysis.getPrecision(result)

    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = analysis.getExponentialFormatPrecision()
    formatted = _format_decimal_or_sci(
        uncertainty, precision, threshold, sciformat)

    # strip off trailing zeros and the orphane dot,
    # e.g.: 1.000000 -> 1
    if "." in formatted:
        formatted = formatted.rstrip("0").rstrip(".")

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
    :result: should be a string to preserve the decimal precision.
    :returns: the formatted result as string
    """
    try:
        result = float(result)
    except ValueError:
        return result

    # continuing with 'nan' result will cause formatting to fail.
    if math.isnan(result):
        return result

    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = analysis.getExponentialFormatPrecision()
    precision = analysis.getPrecision(result)
    formatted = _format_decimal_or_sci(result, precision, threshold, sciformat)
    return formatDecimalMark(formatted, decimalmark)


def create_retest(analysis, **kwargs):
    """Creates a retest of the given analysis
    """
    if not IRequestAnalysis.providedBy(analysis):
        raise ValueError("Type not supported: {}".format(repr(type(analysis))))

    # Create a copy of the original analysis
    parent = api.get_parent(analysis)
    kwargs.update({
        "portal_type": api.get_portal_type(analysis),
        "RetestOf": analysis,
    })
    retest = create_analysis(parent, analysis, **kwargs)

    # Add the retest to the same worksheet, if any
    worksheet = analysis.getWorksheet()
    if worksheet:
        worksheet.addAnalysis(retest)

    return retest


def create_duplicate(analysis, **kwargs):
    """Creates a duplicate of the given analysis
    """
    if not IRequestAnalysis.providedBy(analysis):
        raise ValueError("Type not supported: {}".format(repr(type(analysis))))

    worksheet = analysis.getWorksheet()
    if not worksheet:
        raise ValueError("Cannot create a duplicate without worksheet")

    sample_id = analysis.getRequestID()
    kwargs.update({
        "portal_type": "DuplicateAnalysis",
        "Analysis": analysis,
        "Worksheet": worksheet,
        "ReferenceAnalysesGroupID": "{}-D".format(sample_id),
    })

    return create_analysis(worksheet, analysis, **kwargs)


def create_reference_analysis(reference_sample, source, **kwargs):
    """Creates a reference analysis inside the referencesample
    """
    ref = api.get_object(reference_sample)
    if not IReferenceSample.providedBy(ref):
        raise ValueError("Type not supported: {}".format(repr(type(ref))))

    # Set the type of the reference analysis
    ref_type = "b" if ref.getBlank() else "c"
    kwargs.update({
        "portal_type": "ReferenceAnalysis",
        "ReferenceType": ref_type,
    })
    return create_analysis(ref, source, **kwargs)


def generate_analysis_id(instance, keyword):
    """Generates a new analysis ID
    """
    count = 1
    new_id = keyword
    while new_id in instance.objectIds():
        new_id = "{}-{}".format(keyword, count)
        count += 1
    return new_id


def format_interim(interim_field, html=True):
    """Returns a copy of the interim field plus additional attributes suitable
    for visualization, like formatted_result and formatted_unit
    """
    separator = "<br/>" if html else ", "

    # copy to prevent persistent changes
    item = copy.deepcopy(interim_field)

    # get the raw value
    value = item.get("value", "")
    values = filter(None, api.to_list(value))

    # if choices, display texts instead of values
    choices = item.get("choices")
    if choices:
        # generate a {value:text} dict
        choices = choices.split("|")
        choices = dict(map(lambda ch: ch.strip().split(":"), choices))

        # set the text as the formatted value
        texts = [choices.get(v, "") for v in values]
        values = filter(None, texts)

    else:
        # default formatting
        setup = api.get_setup()
        decimal_mark = setup.getResultsDecimalMark()
        values = [formatDecimalMark(val, decimal_mark) for val in values]

    item["formatted_value"] = separator.join(values)

    # unit formatting
    unit = item.get("unit", "")
    item["formatted_unit"] = format_supsub(unit) if html else unit

    return item
