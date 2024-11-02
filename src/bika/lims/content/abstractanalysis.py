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

import cgi
import copy
import json
import math
from decimal import Decimal
from six import string_types

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import ResultRangeField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.config import LDL
from bika.lims.config import UDL
from bika.lims.content.abstractbaseanalysis import AbstractBaseAnalysis
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.interfaces import IDuplicateAnalysis
from senaite.core.permissions import FieldEditAnalysisResult
from senaite.core.permissions import ViewResults
from bika.lims.utils import formatDecimalMark
from bika.lims.utils.analysis import format_numeric_result
from bika.lims.utils.analysis import get_significant_digits
from bika.lims.workflow import getTransitionActor
from bika.lims.workflow import getTransitionDate
from DateTime import DateTime
from senaite.core.browser.fields.datetime import DateTimeField
from Products.Archetypes.Field import IntegerField
from Products.Archetypes.Field import StringField
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.Schema import Schema
from Products.CMFCore.permissions import View

# A link directly to the AnalysisService object used to create the analysis
AnalysisService = UIDReferenceField(
    'AnalysisService'
)

# Attachments which are added manually in the UI, or automatically when
# results are imported from a file supplied by an instrument.
Attachment = UIDReferenceField(
    'Attachment',
    multiValued=1,
    allowed_types=('Attachment',),
    relationship='AnalysisAttachment'
)

# The final result of the analysis is stored here
Result = StringField(
    'Result',
    read_permission=ViewResults,
    write_permission=FieldEditAnalysisResult,
)

# When the result is changed, this value is updated to the current time.
# Only the most recent result capture date is recorded here and used to
# populate catalog values, however the workflow review_history can be
# used to get all dates of result capture
ResultCaptureDate = DateTimeField(
    'ResultCaptureDate',
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
    max="current",
)

# Returns the retracted analysis this analysis is a retest of
RetestOf = UIDReferenceField(
    'RetestOf',
    relationship="AnalysisRetestOf",
)

# If the result is outside of the detection limits of the method or instrument,
# the operand (< or >) is stored here.  For routine analyses this is taken
# from the Result, if the result entered explicitly startswith "<" or ">"
DetectionLimitOperand = StringField(
    'DetectionLimitOperand',
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
)

# The ID of the logged in user who submitted the result for this Analysis.
Analyst = StringField(
    'Analyst'
)

# The actual uncertainty for this analysis' result, populated from the ranges
# specified in the analysis service when the result is submitted.
Uncertainty = StringField(
    'Uncertainty',
    read_permission=View,
    write_permission="Field: Edit Result",
    precision=10,
)

# transitioned to a 'verified' state. This value is set automatically
# when the analysis is created, based on the value set for the property
# NumberOfRequiredVerifications from the Analysis Service
NumberOfRequiredVerifications = IntegerField(
    'NumberOfRequiredVerifications',
    default=1
)

# Routine Analyses and Reference Analysis have a versioned link to
# the calculation at creation time.
Calculation = HistoryAwareReferenceField(
    'Calculation',
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
    allowed_types=('Calculation',),
    relationship='AnalysisCalculation',
    referenceClass=HoldingReference
)

# InterimFields are defined in Calculations, Services, and Analyses.
# In Analysis Services, the default values are taken from Calculation.
# In Analyses, the default values are taken from the Analysis Service.
# When instrument results are imported, the values in analysis are overridden
# before the calculation is performed.
InterimFields = InterimFieldsField(
    'InterimFields',
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
    schemata='Method',
    widget=RecordsWidget(
        label=_("Calculation Interim Fields"),
        description=_(
            "Values can be entered here which will override the defaults "
            "specified in the Calculation Interim Fields."),
    )
)

# Results Range that applies to this analysis
ResultsRange = ResultRangeField(
    "ResultsRange",
    required=0
)

schema = schema.copy() + Schema((
    AnalysisService,
    Analyst,
    Attachment,
    DetectionLimitOperand,
    # NumberOfRequiredVerifications overrides AbstractBaseClass
    NumberOfRequiredVerifications,
    Result,
    ResultCaptureDate,
    RetestOf,
    Uncertainty,
    Calculation,
    InterimFields,
    ResultsRange,
))


class AbstractAnalysis(AbstractBaseAnalysis):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @deprecated('[1705] Currently returns the Analysis object itself.  If you '
                'need to get the service, use getAnalysisService instead')
    @security.public
    def getService(self):
        return self

    def getServiceUID(self):
        """Return the UID of the associated service.
        """
        return self.getRawAnalysisService()

    @security.public
    def getNumberOfVerifications(self):
        return len(self.getVerificators())

    @security.public
    def getNumberOfRemainingVerifications(self):
        required = self.getNumberOfRequiredVerifications()
        done = self.getNumberOfVerifications()
        if done >= required:
            return 0
        return required - done

    # TODO Workflow - analysis . Remove?
    @security.public
    def getLastVerificator(self):
        verifiers = self.getVerificators()
        return verifiers and verifiers[-1] or None

    @security.public
    def getVerificators(self):
        """Returns the user ids of the users that verified this analysis
        """
        verifiers = list()
        actions = ["retest", "verify", "multi_verify"]
        for event in api.get_review_history(self, rev=False):
            if event.get("review_state") == "verified":
                # include all transitions their end state is 'verified'
                verifiers.append(event["actor"])
            elif event.get("action") in actions:
                # include some transitions their end state is not 'verified'
                verifiers.append(event["actor"])
        return verifiers

    @security.public
    def getDefaultUncertainty(self, result=None):
        """Return the uncertainty value, if the result falls within
        specified ranges for the service from which this analysis was derived.
        """

        if result is None:
            result = self.getResult()

        uncertainties = self.getUncertainties()
        if uncertainties:
            try:
                res = float(result)
            except (TypeError, ValueError):
                # if analysis result is not a number, then we assume in range
                return None

            for d in uncertainties:

                # convert to min/max
                unc_min = api.to_float(d["intercept_min"], default=0)
                unc_max = api.to_float(d["intercept_max"], default=0)

                if unc_min <= res and res <= unc_max:
                    _err = str(d["errorvalue"]).strip()
                    if _err.endswith("%"):
                        try:
                            percvalue = float(_err.replace("%", ""))
                        except ValueError:
                            return None
                        # calculate uncertainty from result
                        uncertainty = res / 100 * percvalue
                    else:
                        uncertainty = api.to_float(_err, default=0)

                    # convert back to string value
                    return api.float_to_string(uncertainty, default=None)
        return None

    @security.public
    def getUncertainty(self, result=None):
        """Returns the uncertainty for this analysis and result.

        Returns the value from Schema's Uncertainty field if the Service has
        the option 'Allow manual uncertainty'.
        Otherwise, do a callback to getDefaultUncertainty().

        Returns empty string if no result specified and the current result for this
        analysis is below or above detections limits.
        """
        uncertainty = self.getField("Uncertainty").get(self)
        if result is None:
            if self.isAboveUpperDetectionLimit():
                return None
            if self.isBelowLowerDetectionLimit():
                return None

        if uncertainty and self.getAllowManualUncertainty():
            return api.float_to_string(uncertainty, default=None)

        return self.getDefaultUncertainty(result)

    @security.public
    def setUncertainty(self, unc):
        """Sets the uncertainty for this analysis

        If the result is a Detection Limit or the value is below LDL or upper
        UDL, set the uncertainty to None``
        """
        # Uncertainty calculation on DL
        # https://jira.bikalabs.com/browse/LIMS-1808
        if self.isAboveUpperDetectionLimit():
            unc = None
        if self.isBelowLowerDetectionLimit():
            unc = None

        field = self.getField("Uncertainty")
        field.set(self, api.float_to_string(unc, default=None))

    @security.public
    def setDetectionLimitOperand(self, value):
        """Set detection limit operand for this analysis
        Allowed detection limit operands are `<` and `>`.
        """
        manual_dl = self.getAllowManualDetectionLimit()
        selector = self.getDetectionLimitSelector()
        if not manual_dl and not selector:
            # Don't allow the user to set the limit operand if manual assignment
            # is not allowed and selector is not visible
            return

        # Changing the detection limit operand has a side effect on the result
        result = self.getResult()
        if value in [LDL, UDL]:
            # flush uncertainty
            self.setUncertainty("")

            # If no previous result or user is not allowed to manually set the
            # the detection limit, override the result with default LDL/UDL
            has_result = api.is_floatable(result)
            if not has_result or not manual_dl:
                # set the result according to the system default UDL/LDL values
                if value == LDL:
                    result = self.getLowerDetectionLimit()
                else:
                    result = self.getUpperDetectionLimit()

        else:
            value = ""

        # Set the result
        self.getField("Result").set(self, result)

        # Set the detection limit to the field
        self.getField("DetectionLimitOperand").set(self, value)

    # Method getLowerDetectionLimit overrides method of class BaseAnalysis
    @security.public
    def getLowerDetectionLimit(self):
        """Returns the Lower Detection Limit (LDL) that applies to this
        analysis in particular. If no value set or the analysis service
        doesn't allow manual input of detection limits, returns the value set
        by default in the Analysis Service
        """
        if self.isLowerDetectionLimit():
            result = self.getResult()
            if api.is_floatable(result):
                return result

            logger.warn("The result for the analysis %s is a lower detection "
                        "limit, but not floatable: '%s'. Returning AS's "
                        "default LDL." % (self.id, result))
        return AbstractBaseAnalysis.getLowerDetectionLimit(self)

    # Method getUpperDetectionLimit overrides method of class BaseAnalysis
    @security.public
    def getUpperDetectionLimit(self):
        """Returns the Upper Detection Limit (UDL) that applies to this
        analysis in particular. If no value set or the analysis service
        doesn't allow manual input of detection limits, returns the value set
        by default in the Analysis Service
        """
        if self.isUpperDetectionLimit():
            result = self.getResult()
            if api.is_floatable(result):
                return result

            logger.warn("The result for the analysis %s is an upper detection "
                        "limit, but not floatable: '%s'. Returning AS's "
                        "default UDL." % (self.id, result))
        return AbstractBaseAnalysis.getUpperDetectionLimit(self)

    @security.public
    def isBelowLowerDetectionLimit(self):
        """Returns True if the result is below the Lower Detection Limit or
        if Lower Detection Limit has been manually set
        """
        if self.isLowerDetectionLimit():
            return True

        result = self.getResult()
        if result and str(result).strip().startswith(LDL):
            return True

        if api.is_floatable(result):
            ldl = self.getLowerDetectionLimit()
            return api.to_float(result) < api.to_float(ldl, 0.0)

        return False

    @security.public
    def isAboveUpperDetectionLimit(self):
        """Returns True if the result is above the Upper Detection Limit or
        if Upper Detection Limit has been manually set
        """
        if self.isUpperDetectionLimit():
            return True

        result = self.getResult()
        if result and str(result).strip().startswith(UDL):
            return True

        if api.is_floatable(result):
            udl = self.getUpperDetectionLimit()
            return api.to_float(result) > api.to_float(udl, 0.0)

        return False

    # TODO: REMOVE:  nowhere used
    @deprecated("This Method will be removed in version 2.5")
    @security.public
    def getDetectionLimits(self):
        """Returns a two-value array with the limits of detection (LDL and
        UDL) that applies to this analysis in particular. If no value set or
        the analysis service doesn't allow manual input of detection limits,
        returns the value set by default in the Analysis Service
        """
        ldl = self.getLowerDetectionLimit()
        udl = self.getUpperDetectionLimit()
        return [api.to_float(ldl, 0.0), api.to_float(udl, 0.0)]

    @security.public
    def isLowerDetectionLimit(self):
        """Returns True if the result for this analysis represents a Lower
        Detection Limit. Otherwise, returns False
        """
        return self.getDetectionLimitOperand() == LDL

    @security.public
    def isUpperDetectionLimit(self):
        """Returns True if the result for this analysis represents an Upper
        Detection Limit. Otherwise, returns False
        """
        return self.getDetectionLimitOperand() == UDL

    @security.public
    def getDependents(self):
        """Return a list of analyses who depend on us to calculate their result
        """
        raise NotImplementedError("getDependents is not implemented.")

    @security.public
    def getDependencies(self, with_retests=False):
        """Return a list of siblings who we depend on to calculate our result.
        :param with_retests: If false, siblings with retests are dismissed
        :type with_retests: bool
        :return: Analyses the current analysis depends on
        :rtype: list of IAnalysis
        """
        raise NotImplementedError("getDependencies is not implemented.")

    @security.public
    def setResult(self, value):
        """Validate and set a value into the Result field, taking into
        account the Detection Limits.
        :param value: is expected to be a string.
        """
        # Convert to list ff the analysis has result options set with multi
        if self.getResultOptions() and "multi" in self.getResultType():
            if not isinstance(value, (list, tuple)):
                value = filter(None, [value])

        # Handle list results
        if isinstance(value, (list, tuple)):
            value = json.dumps(value)

        # Ensure result integrity regards to None, empty and 0 values
        val = str("" if not value and value != 0 else value).strip()

        # Check if an string result is expected
        string_result = self.getStringResult()

        # UDL/LDL directly entered in the results field
        if not string_result and val[:1] in [LDL, UDL]:
            # Strip off the detection limit operand from the result
            operand = val[0]
            val = val.replace(operand, "", 1).strip()

            # Result becomes the detection limit
            selector = self.getDetectionLimitSelector()
            allow_manual = self.getAllowManualDetectionLimit()
            if any([selector, allow_manual]):

                # Set the detection limit operand
                self.setDetectionLimitOperand(operand)

                if not allow_manual:
                    # Manual introduction of DL is not permitted
                    if operand == LDL:
                        # Result is default LDL
                        val = self.getLowerDetectionLimit()
                    else:
                        # Result is default UDL
                        val = self.getUpperDetectionLimit()

        elif not self.getDetectionLimitSelector():
            # User cannot choose the detection limit from a selection list,
            # but might be allowed to manually enter the dl with the result.
            # If so, reset the detection limit operand, cause the previous
            # entered result might be an DL, but current doesn't
            self.setDetectionLimitOperand("")

        # Set the result field
        self.getField("Result").set(self, val)

    @security.public
    def calculateResult(self, override=False, cascade=False):
        """Calculates the result for the current analysis if it depends of
        other analysis/interim fields. Otherwise, do nothing
        """
        if self.getResult() and override is False:
            return False

        calc = self.getCalculation()
        if not calc:
            return False

        # get the formula from the calculation
        formula = calc.getMinifiedFormula()

        # Include the current context UID in the mapping, so it can be passed
        # as a param in built-in functions, like 'get_result(%(context_uid)s)'
        mapping = {"context_uid": '"{}"'.format(self.UID())}

        # Interims' priority order (from low to high):
        # Calculation < Analysis
        interims = calc.getInterimFields() + self.getInterimFields()

        # Add interims to mapping
        for i in interims:

            interim_keyword = i.get("keyword")
            if not interim_keyword:
                continue

            # skip unset values
            interim_value = i.get("value", "")
            if interim_value == "":
                continue

            # Convert to floatable if necessary
            if api.is_floatable(interim_value):
                interim_value = float(interim_value)
            else:
                # If the interim value is a string, since the formula is also a string,
                # it is needed to wrap the string interim values in between inverted commas.
                #
                # E.g. formula = '"ok" if %(var)s == "example_value" else "not ok"'
                #
                # if interim_value = "example_value" after
                # formula = eval("'%s'%%mapping" % formula, {'mapping': {'var': interim_value}})
                # print(formula)
                # > '"ok" if example_value == "example_value" else "not ok"' -> Error
                #
                # else if interim_value ='"example_value"' after
                # formula = eval("'%s'%%mapping" % formula, {'mapping': {'var': interim_value}})
                # print(formula)
                # > '"ok" if "example_value" == "example_value" else "not ok"' -> Correct
                interim_value = '"{}"'.format(interim_value)

            # Convert 'Numeric' interim values using `float`. Convert the rest using `str`
            converter = "s" if i.get("result_type") else "f"
            formula = formula.replace(
                "[" + interim_keyword + "]", "%(" + interim_keyword + ")" + converter
            )

            mapping[interim_keyword] = interim_value

        # Add dependencies results to mapping
        dependencies = self.getDependencies()
        for dependency in dependencies:
            result = dependency.getResult()
            # check if the dependency is a string result
            str_result = dependency.getStringResult()
            keyword = dependency.getKeyword()
            if not result:
                # Dependency without results found
                if cascade:
                    # Try to calculate the dependency result
                    dependency.calculateResult(override, cascade)
                    result = dependency.getResult()
                else:
                    return False
            if result:
                try:
                    # we need to quote a string result because of the `eval` below
                    result = '"%s"' % result if str_result else float(str(result))
                    key = dependency.getKeyword()
                    ldl = dependency.getLowerDetectionLimit()
                    udl = dependency.getUpperDetectionLimit()
                    bdl = dependency.isBelowLowerDetectionLimit()
                    adl = dependency.isAboveUpperDetectionLimit()
                    mapping[key] = result
                    mapping['%s.%s' % (key, 'RESULT')] = result
                    mapping['%s.%s' % (key, 'LDL')] = api.to_float(ldl, 0.0)
                    mapping['%s.%s' % (key, 'UDL')] = api.to_float(udl, 0.0)
                    mapping['%s.%s' % (key, 'BELOWLDL')] = int(bdl)
                    mapping['%s.%s' % (key, 'ABOVEUDL')] = int(adl)
                except (TypeError, ValueError):
                    return False

                # replace placeholder -> formatting string
                # https://docs.python.org/2.7/library/stdtypes.html?highlight=built#string-formatting-operations
                converter = "s" if str_result else "f"
                formula = formula.replace("[" + keyword + "]", "%(" + keyword + ")" + converter)

        # convert any remaining placeholders, e.g. from interims etc.
        # NOTE: we assume remaining values are all floatable!
        formula = formula.replace("[", "%(").replace("]", ")f")

        # Calculate
        try:
            formula = eval("'%s'%%mapping" % formula,
                           {"__builtins__": None,
                            'math': math,
                            'context': self},
                           {'mapping': mapping})
            result = eval(formula, calc._getGlobals())
        except ZeroDivisionError:
            self.setResult('0/0')
            return True
        except (KeyError, TypeError, ImportError) as e:
            msg = "Cannot eval formula ({}): {}".format(e.message, formula)
            logger.error(msg)
            self.setResult("NA")
            return True

        self.setResult(str(result))
        return True

    @security.public
    def getVATAmount(self):
        """Compute the VAT amount without member discount.
        :return: the result as a float
        """
        vat = self.getVAT()
        price = self.getPrice()
        return Decimal(price) * Decimal(vat) / 100

    @security.public
    def getTotalPrice(self):
        """Obtain the total price without client's member discount. The function
        keeps in mind the client's bulk discount.
        :return: the result as a float
        """
        return Decimal(self.getPrice()) + Decimal(self.getVATAmount())

    @security.public
    def getDuration(self):
        """Returns the time in minutes taken for this analysis.
        If the analysis is not yet 'ready to process', returns 0
        If the analysis is still in progress (not yet verified),
            duration = date_verified - date_start_process
        Otherwise:
            duration = current_datetime - date_start_process
        :return: time in minutes taken for this analysis
        :rtype: int
        """
        starttime = self.getStartProcessDate()
        if not starttime:
            # The analysis is not yet ready to be processed
            return 0
        endtime = self.getDateVerified() or DateTime()

        # Duration in minutes
        duration = (endtime - starttime) * 24 * 60
        return duration

    @security.public
    def getEarliness(self):
        """The remaining time in minutes for this analysis to be completed.
        Returns zero if the analysis is neither 'ready to process' nor a
        turnaround time is set.
            earliness = duration - max_turnaround_time
        The analysis is late if the earliness is negative
        :return: the remaining time in minutes before the analysis reaches TAT
        :rtype: int
        """
        maxtime = self.getMaxTimeAllowed()
        if not maxtime:
            # No Turnaround time is set for this analysis
            return 0
        if api.to_minutes(**maxtime) == 0:
            return 0
        return api.to_minutes(**maxtime) - self.getDuration()

    @security.public
    def isLateAnalysis(self):
        """Returns true if the analysis is late in accordance with the maximum
        turnaround time. If no maximum turnaround time is set for this analysis
        or it is not yet ready to be processed, or there is still time
        remaining (earliness), returns False.
        :return: true if the analysis is late
        :rtype: bool
        """
        return self.getEarliness() < 0

    @security.public
    def getLateness(self):
        """The time in minutes that exceeds the maximum turnaround set for this
        analysis. If the analysis has no turnaround time set or is not ready
        for process yet, returns 0. The analysis is not late if the lateness is
        negative
        :return: the time in minutes that exceeds the maximum turnaround time
        :rtype: int
        """
        return -self.getEarliness()

    @security.public
    def isInstrumentAllowed(self, instrument):
        """Checks if the specified instrument can be set for this analysis,

        :param instrument: string,Instrument
        :return: True if the assignment of the passed in instrument is allowed
        :rtype: bool
        """
        uid = api.get_uid(instrument)
        return uid in self.getRawAllowedInstruments()

    @security.public
    def isMethodAllowed(self, method):
        """Checks if the analysis can follow the method specified

        :param method: string,Method
        :return: True if the analysis can follow the method specified
        :rtype: bool
        """
        uid = api.get_uid(method)
        return uid in self.getRawAllowedMethods()

    @security.public
    def getAllowedMethods(self):
        """Returns the allowed methods for this analysis, either if the method
        was assigned directly (by using "Allows manual entry of results") or
        indirectly via Instrument ("Allows instrument entry of results") in
        Analysis Service Edit View.
        :return: A list with the methods allowed for this analysis
        :rtype: list of Methods
        """
        service = self.getAnalysisService()
        if not service:
            return []
        # get the available methods of the service
        return service.getMethods()

    @security.public
    def getRawAllowedMethods(self):
        """Returns the UIDs of the allowed methods for this analysis
        """
        service = self.getAnalysisService()
        if not service:
            return []
        return service.getRawMethods()

    @security.public
    def getAllowedInstruments(self):
        """Returns the allowed instruments from the service

        :return: A list of instruments allowed for this Analysis
        :rtype: list of instruments
        """
        service = self.getAnalysisService()
        if not service:
            return []
        return service.getInstruments()

    @security.public
    def getRawAllowedInstruments(self):
        """Returns the UIDS of the allowed instruments from the service
        """
        service = self.getAnalysisService()
        if not service:
            return []
        return service.getRawInstruments()

    @security.public
    def getExponentialFormatPrecision(self, result=None):
        """ Returns the precision for the Analysis Service and result
        provided. Results with a precision value above this exponential
        format precision should be formatted as scientific notation.

        If the Calculate Precision according to Uncertainty is not set,
        the method will return the exponential precision value set in the
        Schema. Otherwise, will calculate the precision value according to
        the Uncertainty and the result.

        If Calculate Precision from the Uncertainty is set but no result
        provided neither uncertainty values are set, returns the fixed
        exponential precision.

        Will return positive values if the result is below 0 and will return
        0 or positive values if the result is above 0.

        Given an analysis service with fixed exponential format
        precision of 4:
        Result      Uncertainty     Returns
        5.234           0.22           0
        13.5            1.34           1
        0.0077          0.008         -3
        32092           0.81           4
        456021          423            5

        For further details, visit https://jira.bikalabs.com/browse/LIMS-1334

        :param result: if provided and "Calculate Precision according to the
        Uncertainty" is set, the result will be used to retrieve the
        uncertainty from which the precision must be calculated. Otherwise,
        the fixed-precision will be used.
        :returns: the precision
        """
        if not result or self.getPrecisionFromUncertainty() is False:
            return self._getExponentialFormatPrecision()
        else:
            uncertainty = self.getUncertainty(result)
            if uncertainty is None:
                return self._getExponentialFormatPrecision()

            try:
                float(result)
            except ValueError:
                # if analysis result is not a number, then we assume in range
                return self._getExponentialFormatPrecision()

            return get_significant_digits(uncertainty)

    def _getExponentialFormatPrecision(self):
        field = self.getField('ExponentialFormatPrecision')
        value = field.get(self)
        if value is None:
            # https://github.com/bikalims/bika.lims/issues/2004
            # We require the field, because None values make no sense at all.
            value = self.Schema().getField(
                'ExponentialFormatPrecision').getDefault(self)
        return value

    @security.public
    def getFormattedResult(self, specs=None, decimalmark='.', sciformat=1,
                           html=True):
        """Formatted result:
        0: If the result type is StringResult, return it without being formatted
        1. If the result is a detection limit, returns '< LDL' or '> UDL'
        2. Print ResultText of matching ResultOptions
        3. If the result is not floatable, return it without being formatted
        4. If the analysis specs has hidemin or hidemax enabled and the
           result is out of range, render result as '<min' or '>max'
        5. If the result is below Lower Detection Limit, show '<LDL'
        6. If the result is above Upper Detecion Limit, show '>UDL'
        7. Otherwise, render numerical value
        :param specs: Optional result specifications, a dictionary as follows:
            {'min': <min_val>,
             'max': <max_val>,
             'error': <error>,
             'hidemin': <hidemin_val>,
             'hidemax': <hidemax_val>}
        :param decimalmark: The string to be used as a decimal separator.
            default is '.'
        :param sciformat: 1. The sci notation has to be formatted as aE^+b
                          2. The sci notation has to be formatted as a·10^b
                          3. As 2, but with super html entity for exp
                          4. The sci notation has to be formatted as a·10^b
                          5. As 4, but with super html entity for exp
                          By default 1
        :param html: if true, returns an string with the special characters
            escaped: e.g: '<' and '>' (LDL and UDL for results like < 23.4).
        """
        result = self.getResult()

        # If result options, return text of matching option
        choices = self.getResultOptions()
        if choices:
            # Create a dict for easy mapping of result options
            values_texts = dict(map(
                lambda c: (str(c["ResultValue"]), c["ResultText"]), choices
            ))

            # Result might contain a single result option
            match = values_texts.get(str(result))
            if match:
                return match

            # Result might be a string with multiple options e.g. "['2', '1']"
            try:
                raw_result = json.loads(result)
                texts = map(lambda r: values_texts.get(str(r)), raw_result)
                texts = filter(None, texts)
                return "<br/>".join(texts)
            except (ValueError, TypeError):
                pass

        # If string result, return without any formatting
        if self.getStringResult():
            if html:
                result = cgi.escape(result)
                result = result.replace("\n", "<br/>")
            return result

        # If a detection limit, return '< LDL' or '> UDL'
        dl = self.getDetectionLimitOperand()
        if dl:
            try:
                res = api.float_to_string(float(result))
                fdm = formatDecimalMark(res, decimalmark)
                hdl = cgi.escape(dl) if html else dl
                return '%s %s' % (hdl, fdm)
            except (TypeError, ValueError):
                logger.warn(
                    "The result for the analysis %s is a detection limit, "
                    "but not floatable: %s" % (self.id, result))
                return formatDecimalMark(result, decimalmark=decimalmark)

        # If not floatable, return without any formatting
        try:
            result = float(result)
        except (TypeError, ValueError):
            return formatDecimalMark(result, decimalmark=decimalmark)

        # If specs are set, evaluate if out of range
        specs = specs if specs else self.getResultsRange()
        hidemin = specs.get('hidemin', '')
        hidemax = specs.get('hidemax', '')
        try:
            belowmin = hidemin and result < float(hidemin) or False
        except (TypeError, ValueError):
            belowmin = False
        try:
            abovemax = hidemax and result > float(hidemax) or False
        except (TypeError, ValueError):
            abovemax = False

        # If below min and hidemin enabled, return '<min'
        if belowmin:
            fdm = formatDecimalMark('< %s' % hidemin, decimalmark)
            return fdm.replace('< ', '&lt; ', 1) if html else fdm

        # If above max and hidemax enabled, return '>max'
        if abovemax:
            fdm = formatDecimalMark('> %s' % hidemax, decimalmark)
            return fdm.replace('> ', '&gt; ', 1) if html else fdm

        # If below LDL, return '< LDL'
        ldl = self.getLowerDetectionLimit()
        ldl = api.to_float(ldl, 0.0)
        if result < ldl:
            # LDL must not be formatted according to precision, etc.
            ldl = api.float_to_string(ldl)
            fdm = formatDecimalMark('< %s' % ldl, decimalmark)
            return fdm.replace('< ', '&lt; ', 1) if html else fdm

        # If above UDL, return '< UDL'
        udl = self.getUpperDetectionLimit()
        udl = api.to_float(udl, 0.0)
        if result > udl:
            # UDL must not be formatted according to precision, etc.
            udl = api.float_to_string(udl)
            fdm = formatDecimalMark('> %s' % udl, decimalmark)
            return fdm.replace('> ', '&gt; ', 1) if html else fdm

        # Render numerical values
        return format_numeric_result(self, self.getResult(),
                                     decimalmark=decimalmark,
                                     sciformat=sciformat)

    @security.public
    def getPrecision(self, result=None):
        """Returns the precision for the Analysis.

        - If ManualUncertainty is set, calculates the precision of the result
          in accordance with the manual uncertainty set.

        - If Calculate Precision from Uncertainty is set in Analysis Service,
          calculates the precision in accordance with the uncertainty inferred
          from uncertainties ranges.

        - If neither Manual Uncertainty nor Calculate Precision from
          Uncertainty are set, returns the precision from the Analysis Service

        - If you have a number with zero uncertainty: If you roll a pair of
        dice and observe five spots, the number of spots is 5. This is a raw
        data point, with no uncertainty whatsoever. So just write down the
        number. Similarly, the number of centimeters per inch is 2.54,
        by definition, with no uncertainty whatsoever. Again: just write
        down the number.

        Further information at AbstractBaseAnalysis.getPrecision()
        """
        allow_manual = self.getAllowManualUncertainty()
        precision_unc = self.getPrecisionFromUncertainty()
        if allow_manual or precision_unc:
            uncertainty = self.getUncertainty(result)
            if uncertainty is None:
                return self.getField("Precision").get(self)
            if api.to_float(uncertainty) == 0 and result is None:
                return self.getField("Precision").get(self)
            if api.to_float(uncertainty) == 0:
                strres = str(result)
                numdecimals = strres[::-1].find('.')
                return numdecimals

            uncertainty = api.to_float(uncertainty)
            # Get the 'raw' significant digits from uncertainty
            sig_digits = get_significant_digits(uncertainty)
            # Round the uncertainty to its significant digit.
            # Needed because the precision for the result has to be based on
            # the *rounded* uncertainty. Note the following for a given
            # uncertainty value:
            #   >>> round(0.09404, 2)
            #   0.09
            #   >>> round(0.09504, 2)
            #   0.1
            # The precision when the uncertainty is 0.09504 is not 2, but 1
            uncertainty = abs(round(uncertainty, sig_digits))
            # Return the significant digit to apply
            return get_significant_digits(uncertainty)

        return self.getField('Precision').get(self)

    @security.public
    def getAnalyst(self):
        """Returns the stored Analyst or the user who submitted the result
        """
        analyst = self.getField("Analyst").get(self) or self.getAssignedAnalyst()
        if not analyst:
            analyst = self.getSubmittedBy()
        return analyst or ""

    @security.public
    def getAssignedAnalyst(self):
        """Returns the Analyst assigned to the worksheet this
        analysis is assigned to
        """
        worksheet = self.getWorksheet()
        if not worksheet:
            return ""
        return worksheet.getAnalyst() or ""

    @security.public
    def getSubmittedBy(self):
        """
        Returns the identifier of the user who submitted the result if the
        state of the current analysis is "to_be_verified" or "verified"
        :return: the user_id of the user who did the last submission of result
        """
        return getTransitionActor(self, 'submit')

    @security.public
    def getDateSubmitted(self):
        """Returns the time the result was submitted.
        :return: a DateTime object.
        :rtype: DateTime
        """
        return getTransitionDate(self, 'submit', return_as_datetime=True)

    @security.public
    def getDateVerified(self):
        """Returns the time the analysis was verified. If the analysis hasn't
        been yet verified, returns None
        :return: the time the analysis was verified or None
        :rtype: DateTime
        """
        return getTransitionDate(self, 'verify', return_as_datetime=True)

    @security.public
    def getStartProcessDate(self):
        """Returns the date time when the analysis is ready to be processed.
        It returns the datetime when the object was created, but might be
        different depending on the type of analysis (e.g. "Date Received" for
        routine analyses): see overriden functions.
        :return: Date time when the analysis is ready to be processed.
        :rtype: DateTime
        """
        return self.created()

    @security.public
    def getParentURL(self):
        """This method is used to populate catalog values
        This function returns the analysis' parent URL
        """
        parent = self.aq_parent
        if parent:
            return parent.absolute_url_path()

    @security.public
    def getWorksheetUID(self):
        """This method is used to populate catalog values
        Returns WS UID if this analysis is assigned to a worksheet, or None.
        """
        uids = get_backreferences(self, relationship="WorksheetAnalysis")
        if not uids:
            return None

        if len(uids) > 1:
            path = api.get_path(self)
            logger.error("More than one worksheet: {}".format(path))
            return None

        return uids[0]

    @security.public
    def getWorksheet(self):
        """Returns the Worksheet to which this analysis belongs to, or None
        """
        worksheet_uid = self.getWorksheetUID()
        return api.get_object_by_uid(worksheet_uid, None)

    @security.public
    def remove_duplicates(self, ws):
        """When this analysis is unassigned from a worksheet, this function
        is responsible for deleting DuplicateAnalysis objects from the ws.
        """
        for analysis in ws.objectValues():
            if IDuplicateAnalysis.providedBy(analysis) \
                    and analysis.getAnalysis().UID() == self.UID():
                ws.removeAnalysis(analysis)

    def setInterimValue(self, keyword, value):
        """Sets a value to an interim of this analysis
        :param keyword: the keyword of the interim
        :param value: the value for the interim
        """
        # Ensure value format integrity
        if value is None:
            value = ""
        elif isinstance(value, string_types):
            value = value.strip()
        elif isinstance(value, (list, tuple, set, dict)):
            value = json.dumps(value)

        # Ensure result integrity regards to None, empty and 0 values
        interims = copy.deepcopy(self.getInterimFields())
        for interim in interims:
            if interim.get("keyword") == keyword:
                interim["value"] = str(value)
        self.setInterimFields(interims)

    def getInterimValue(self, keyword):
        """Returns the value of an interim of this analysis
        """
        interims = filter(lambda item: item["keyword"] == keyword,
                          self.getInterimFields())
        if not interims:
            logger.warning("Interim '{}' for analysis '{}' not found"
                           .format(keyword, self.getKeyword()))
            return None
        if len(interims) > 1:
            logger.error("More than one interim '{}' found for '{}'"
                         .format(keyword, self.getKeyword()))
            return None
        return interims[0].get('value', '')

    def isRetest(self):
        """Returns whether this analysis is a retest or not
        """
        if self.getRawRetestOf():
            return True
        return False

    def getRetestOfUID(self):
        """Returns the UID of the retracted analysis this is a retest of
        """
        return self.getRawRetestOf()

    def getRawRetest(self):
        """Returns the UID of the retest that comes from this analysis, if any
        """
        relationship = self.getField("RetestOf").relationship
        uids = get_backreferences(self, relationship)
        if not uids:
            return None
        if len(uids) > 1:
            logger.warn("Analysis {} with multiple retests".format(self.id))
        return uids[0]

    def getRetest(self):
        """Returns the retest that comes from this analysis, if any
        """
        retest_uid = self.getRawRetest()
        return api.get_object(retest_uid, default=None)

    def isRetested(self):
        """Returns whether this analysis has been retested or not
        """
        if self.getRawRetest():
            return True
        return False
