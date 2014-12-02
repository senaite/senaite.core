# -*- coding: utf-8 -*-

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


def format_uncertainty(analysis, result, decimalmark='.'):
    """ Returns the precision formatted in accordance with the
        uncertainties and scientific notation.
    """
    try:
        result = float(result)
    except ValueError:
        return result

    service = analysis.getService()
    uncertainty = service.getUncertainty(result)

    if uncertainty is None:
        return ""

    # Scientific notation?
    # Get the default precision for scientific notation
    threshold = service.getExponentialFormatPrecision()
    # Current result precision is above the threshold?
    sig_digits = service.getExponentialFormatPrecision(result)
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
    Print the formatted number part of a results value.  This is responsible
    for deciding the precision, and notation of numeric values.  If a non-numeric
    result value is given, the value will be returned unchanged
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
    sig_digits = abs(service.getExponentialFormatPrecision(result))
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
