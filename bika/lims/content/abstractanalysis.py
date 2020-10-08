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

import cgi
import math
from decimal import Decimal

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.Field import DateTimeField
from Products.Archetypes.Field import FixedPointField
from Products.Archetypes.Field import IntegerField
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims import workflow as wf
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields import ResultRangeField
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.config import LDL
from bika.lims.config import UDL
from bika.lims.content.abstractbaseanalysis import AbstractBaseAnalysis
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.permissions import FieldEditAnalysisResult
from bika.lims.utils import drop_trailing_zeros_decimal
from bika.lims.utils import formatDecimalMark
from bika.lims.utils.analysis import format_numeric_result
from bika.lims.utils.analysis import get_significant_digits
from bika.lims.workflow import getTransitionActor
from bika.lims.workflow import getTransitionDate

# A link directly to the AnalysisService object used to create the analysis
AnalysisService = UIDReferenceField(
    'AnalysisService'
)

# Attachments which are added manually in the UI, or automatically when
# results are imported from a file supplied by an instrument.
Attachment = UIDReferenceField(
    'Attachment',
    multiValued=1,
    allowed_types=('Attachment',)
)

# The final result of the analysis is stored here.  The field contains a
# String value, but the result itself is required to be numeric.  If
# a non-numeric result is needed, ResultOptions can be used.
Result = StringField(
    'Result',
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
)

# When the result is changed, this value is updated to the current time.
# Only the most recent result capture date is recorded here and used to
# populate catalog values, however the workflow review_history can be
# used to get all dates of result capture
ResultCaptureDate = DateTimeField(
    'ResultCaptureDate'
)

# Returns the retracted analysis this analysis is a retest of
RetestOf = UIDReferenceField(
    'RetestOf'
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
Uncertainty = FixedPointField(
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
        service = self.getAnalysisService()
        if service:
            return service.UID()

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
        actions = ["verify", "multi_verify"]
        for event in wf.getReviewHistory(self):
            if event['action'] in actions:
                verifiers.append(event['actor'])
        sorted(verifiers, reverse=True)
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
                _min = float(d['intercept_min'])
                _max = float(d['intercept_max'])
                if _min <= res and res <= _max:
                    if str(d['errorvalue']).strip().endswith('%'):
                        try:
                            percvalue = float(d['errorvalue'].replace('%', ''))
                        except ValueError:
                            return None
                        uncertainty = res / 100 * percvalue
                    else:
                        uncertainty = float(d['errorvalue'])

                    return uncertainty
        return None

    @security.public
    def getUncertainty(self, result=None):
        """Returns the uncertainty for this analysis and result.
        Returns the value from Schema's Uncertainty field if the Service has
        the option 'Allow manual uncertainty'. Otherwise, do a callback to
        getDefaultUncertainty(). Returns None if no result specified and the
        current result for this analysis is below or above detections limits.
        """
        uncertainty = self.getField('Uncertainty').get(self)
        if result is None and (self.isAboveUpperDetectionLimit() or
                               self.isBelowLowerDetectionLimit()):
            return None

        if uncertainty and self.getAllowManualUncertainty() is True:
            try:
                uncertainty = float(uncertainty)
                return uncertainty
            except (TypeError, ValueError):
                # if uncertainty is not a number, return default value
                pass
        return self.getDefaultUncertainty(result)

    @security.public
    def setUncertainty(self, unc):
        """Sets the uncertainty for this analysis. If the result is a
        Detection Limit or the value is below LDL or upper UDL, sets the
        uncertainty value to 0
        """
        # Uncertainty calculation on DL
        # https://jira.bikalabs.com/browse/LIMS-1808
        if self.isAboveUpperDetectionLimit() or \
                self.isBelowLowerDetectionLimit():
            self.getField('Uncertainty').set(self, None)
        else:
            self.getField('Uncertainty').set(self, unc)

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
            # Restore the DetectionLimitSelector, cause maybe its visibility
            # was changed because allow manual detection limit was enabled and
            # the user set a result with "<" or ">"
            if manual_dl:
                service = self.getAnalysisService()
                selector = service.getDetectionLimitSelector()
                self.setDetectionLimitSelector(selector)

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
            try:
                # in this case, the result itself is the LDL.
                return float(result)
            except (TypeError, ValueError):
                logger.warn("The result for the analysis %s is a lower "
                            "detection limit, but not floatable: '%s'. "
                            "Returnig AS's default LDL." %
                            (self.id, result))
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
            try:
                # in this case, the result itself is the LDL.
                return float(result)
            except (TypeError, ValueError):
                logger.warn("The result for the analysis %s is a lower "
                            "detection limit, but not floatable: '%s'. "
                            "Returnig AS's default LDL." %
                            (self.id, result))
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
            return api.to_float(result) < self.getLowerDetectionLimit()

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
            return api.to_float(result) > self.getUpperDetectionLimit()

        return False

    @security.public
    def getDetectionLimits(self):
        """Returns a two-value array with the limits of detection (LDL and
        UDL) that applies to this analysis in particular. If no value set or
        the analysis service doesn't allow manual input of detection limits,
        returns the value set by default in the Analysis Service
        """
        return [self.getLowerDetectionLimit(), self.getUpperDetectionLimit()]

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
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())

        # Ensure result integrity regards to None, empty and 0 values
        val = str("" if not value and value != 0 else value).strip()

        # UDL/LDL directly entered in the results field
        if val and val[0] in [LDL, UDL]:
            # Result prefixed with LDL/UDL
            oper = val[0]
            # Strip off LDL/UDL from the result
            val = val.replace(oper, "", 1)
            # Check if the value is indeterminate / non-floatable
            try:
                val = float(val)
            except (ValueError, TypeError):
                val = value

            # We dismiss the operand and the selector visibility unless the user
            # is allowed to manually set the detection limit or the DL selector
            # is visible.
            allow_manual = self.getAllowManualDetectionLimit()
            selector = self.getDetectionLimitSelector()
            if allow_manual or selector:
                # Ensure visibility of the detection limit selector
                self.setDetectionLimitSelector(True)

                # Set the detection limit operand
                self.setDetectionLimitOperand(oper)

                if not allow_manual:
                    # Override value by default DL
                    if oper == LDL:
                        val = self.getLowerDetectionLimit()
                    else:
                        val = self.getUpperDetectionLimit()

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

        mapping = {}

        # Interims' priority order (from low to high):
        # Calculation < Analysis
        interims = calc.getInterimFields() + self.getInterimFields()

        # Add interims to mapping
        for i in interims:
            if 'keyword' not in i:
                continue
            # skip unset values
            if i['value'] == '':
                continue
            try:
                ivalue = float(i['value'])
                mapping[i['keyword']] = ivalue
            except (TypeError, ValueError):
                # Interim not float, abort
                return False

        # Add dependencies results to mapping
        dependencies = self.getDependencies()
        for dependency in dependencies:
            result = dependency.getResult()
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
                    result = float(str(result))
                    key = dependency.getKeyword()
                    ldl = dependency.getLowerDetectionLimit()
                    udl = dependency.getUpperDetectionLimit()
                    bdl = dependency.isBelowLowerDetectionLimit()
                    adl = dependency.isAboveUpperDetectionLimit()
                    mapping[key] = result
                    mapping['%s.%s' % (key, 'RESULT')] = result
                    mapping['%s.%s' % (key, 'LDL')] = ldl
                    mapping['%s.%s' % (key, 'UDL')] = udl
                    mapping['%s.%s' % (key, 'BELOWLDL')] = int(bdl)
                    mapping['%s.%s' % (key, 'ABOVEUDL')] = int(adl)
                except (TypeError, ValueError):
                    return False

        # Calculate
        formula = calc.getMinifiedFormula()
        formula = formula.replace('[', '%(').replace(']', ')f')
        try:
            formula = eval("'%s'%%mapping" % formula,
                           {"__builtins__": None,
                            'math': math,
                            'context': self},
                           {'mapping': mapping})
            result = eval(formula, calc._getGlobals())
        except TypeError:
            self.setResult("NA")
            return True
        except ZeroDivisionError:
            self.setResult('0/0')
            return True
        except KeyError:
            self.setResult("NA")
            return True
        except ImportError:
            self.setResult("NA")
            return True

        self.setResult(str(result))
        return True

    @security.public
    def getPrice(self):
        """The function obtains the analysis' price without VAT and without
        member discount
        :return: the price (without VAT or Member Discount) in decimal format
        """
        analysis_request = self.aq_parent
        client = analysis_request.aq_parent
        if client.getBulkDiscount():
            price = self.getBulkPrice()
        else:
            price = self.getField('Price').get(self)
        return price

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
    def isInstrumentValid(self):
        """Checks if the instrument selected for this analysis is valid.
        Returns false if an out-of-date or uncalibrated instrument is
        assigned.
        :return: True if the Analysis has no instrument assigned or is valid
        :rtype: bool
        """
        if self.getInstrument():
            return self.getInstrument().isValid()
        return True

    @security.public
    def isInstrumentAllowed(self, instrument):
        """Checks if the specified instrument can be set for this analysis,
        either if the instrument was assigned directly (by using "Allows
        instrument entry of results") or indirectly via Method ("Allows manual
        entry of results") in Analysis Service Edit view.
        Param instrument can be either an uid or an object
        :param instrument: string,Instrument
        :return: True if the assignment of the passed in instrument is allowed
        :rtype: bool
        """
        uid = api.get_uid(instrument)
        return uid in self.getAllowedInstrumentUIDs()

    @security.public
    def isMethodAllowed(self, method):
        """Checks if the analysis can follow the method specified, either if
        the method was assigned directly (by using "Allows manual entry of
        results") or indirectly via Instrument ("Allows instrument entry of
        results") in Analysis Service Edit view.
        Param method can be either a uid or an object
        :param method: string,Method
        :return: True if the analysis can follow the method specified
        :rtype: bool
        """
        uid = api.get_uid(method)
        return uid in self.getAllowedMethodUIDs()

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

        methods = []
        if self.getManualEntryOfResults():
            methods = service.getMethods()
        if self.getInstrumentEntryOfResults():
            for instrument in service.getInstruments():
                methods.extend(instrument.getMethods())

        return list(set(methods))

    @security.public
    def getAllowedMethodUIDs(self):
        """Used to populate getAllowedMethodUIDs metadata. Delegates to
        method getAllowedMethods() for the retrieval of the methods allowed.
        :return: A list with the UIDs of the methods allowed for this analysis
        :rtype: list of strings
        """
        return [m.UID() for m in self.getAllowedMethods()]

    @security.public
    def getAllowedInstruments(self):
        """Returns the allowed instruments for this analysis, either if the
        instrument was assigned directly (by using "Allows instrument entry of
        results") or indirectly via Method (by using "Allows manual entry of
        results") in Analysis Service edit view.
        :return: A list of instruments allowed for this Analysis
        :rtype: list of instruments
        """
        service = self.getAnalysisService()
        if not service:
            return []

        instruments = []
        if self.getInstrumentEntryOfResults():
            instruments = service.getInstruments()
        if self.getManualEntryOfResults():
            for meth in self.getAllowedMethods():
                instruments += meth.getInstruments()

        return list(set(instruments))

    @security.public
    def getAllowedInstrumentUIDs(self):
        """Used to populate getAllowedInstrumentUIDs metadata. Delegates to
        getAllowedInstruments() for the retrieval of the instruments allowed.
        :return: List of instruments' UIDs allowed for this analysis
        :rtype: list of strings
        """
        return [i.UID() for i in self.getAllowedInstruments()]

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

        # 1. The result is a detection limit, return '< LDL' or '> UDL'
        dl = self.getDetectionLimitOperand()
        if dl:
            try:
                res = float(result)  # required, check if floatable
                res = drop_trailing_zeros_decimal(res)
                fdm = formatDecimalMark(res, decimalmark)
                hdl = cgi.escape(dl) if html else dl
                return '%s %s' % (hdl, fdm)
            except (TypeError, ValueError):
                logger.warn(
                    "The result for the analysis %s is a detection limit, "
                    "but not floatable: %s" % (self.id, result))
                return formatDecimalMark(result, decimalmark=decimalmark)

        choices = self.getResultOptions()

        # 2. Print ResultText of matching ResulOptions
        match = [x['ResultText'] for x in choices
                 if str(x['ResultValue']) == str(result)]
        if match:
            return match[0]

        # 3. If the result is not floatable, return it without being formatted
        try:
            result = float(result)
        except (TypeError, ValueError):
            return formatDecimalMark(result, decimalmark=decimalmark)

        # 4. If the analysis specs has enabled hidemin or hidemax and the
        #    result is out of range, render result as '<min' or '>max'
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

        # 4.1. If result is below min and hidemin enabled, return '<min'
        if belowmin:
            fdm = formatDecimalMark('< %s' % hidemin, decimalmark)
            return fdm.replace('< ', '&lt; ', 1) if html else fdm

        # 4.2. If result is above max and hidemax enabled, return '>max'
        if abovemax:
            fdm = formatDecimalMark('> %s' % hidemax, decimalmark)
            return fdm.replace('> ', '&gt; ', 1) if html else fdm

        # Below Lower Detection Limit (LDL)?
        ldl = self.getLowerDetectionLimit()
        if result < ldl:
            # LDL must not be formatted according to precision, etc.
            # Drop trailing zeros from decimal
            ldl = drop_trailing_zeros_decimal(ldl)
            fdm = formatDecimalMark('< %s' % ldl, decimalmark)
            return fdm.replace('< ', '&lt; ', 1) if html else fdm

        # Above Upper Detection Limit (UDL)?
        udl = self.getUpperDetectionLimit()
        if result > udl:
            # UDL must not be formatted according to precision, etc.
            # Drop trailing zeros from decimal
            udl = drop_trailing_zeros_decimal(udl)
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
          calculates the precision in accordance with the uncertainty infered
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
                return self.getField('Precision').get(self)
            if uncertainty == 0 and result is None:
                return self.getField('Precision').get(self)
            if uncertainty == 0:
                strres = str(result)
                numdecimals = strres[::-1].find('.')
                return numdecimals
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
    def getAnalystName(self):
        """Returns the name of the currently assigned analyst
        """
        analyst = self.getAnalyst()
        if not analyst:
            return ""
        user = api.get_user(analyst.strip())
        return user and user.getProperty("fullname") or analyst

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
    def getParentUID(self):
        """This method is used to populate catalog values
        This function returns the analysis' parent UID
        """
        parent = self.aq_parent
        if parent:
            return parent.UID()

    @security.public
    def getParentURL(self):
        """This method is used to populate catalog values
        This function returns the analysis' parent URL
        """
        parent = self.aq_parent
        if parent:
            return parent.absolute_url_path()

    @security.public
    def getParentTitle(self):
        """This method is used to populate catalog values
        This function returns the analysis' parent Title
        """
        parent = self.aq_parent
        if parent:
            return parent.Title()

    @security.public
    def getWorksheetUID(self):
        """This method is used to populate catalog values
        Returns WS UID if this analysis is assigned to a worksheet, or None.
        """
        worksheet = self.getWorksheet()
        if worksheet:
            return worksheet.UID()

    @security.public
    def getWorksheet(self):
        """Returns the Worksheet to which this analysis belongs to, or None
        """
        worksheet = self.getBackReferences('WorksheetAnalysis')
        if not worksheet:
            return None
        if len(worksheet) > 1:
            logger.error(
                "Analysis %s is assigned to more than one worksheet."
                % self.getId())
        return worksheet[0]

    @security.public
    def getInstrumentValid(self):
        """Used to populate catalog values. Delegates to isInstrumentValid()
        Returns false if an out-of-date or uncalibrated instrument is
        assigned.
        :return: True if the Analysis has no instrument assigned or is valid
        :rtype: bool
        """
        return self.isInstrumentValid()

    @security.public
    def getAttachmentUIDs(self):
        """Used to populate metadata, so that we don't need full objects of
        analyses when working with their attachments.
        """
        attachments = self.getAttachment()
        uids = [att.UID() for att in attachments]
        return uids

    @security.public
    def getCalculationUID(self):
        """Used to populate catalog values
        """
        calculation = self.getCalculation()
        if calculation:
            return calculation.UID()

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
        # Ensure result integrity regards to None, empty and 0 values
        val = str('' if not value and value != 0 else value).strip()
        interims = self.getInterimFields()
        for interim in interims:
            if interim['keyword'] == keyword:
                interim['value'] = val
                self.setInterimFields(interims)
                return

        logger.warning("Interim '{}' for analysis '{}' not found"
                       .format(keyword, self.getKeyword()))

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
        return self.getRetestOf() and True or False

    def getRetestOfUID(self):
        """Returns the UID of the retracted analysis this is a retest of
        """
        retest_of = self.getRetestOf()
        if retest_of:
            return api.get_uid(retest_of)

    def getRetest(self):
        """Returns the retest that comes from this analysis, if any
        """
        relationship = "{}RetestOf".format(self.portal_type)
        back_refs = get_backreferences(self, relationship)
        if not back_refs:
            return None
        if len(back_refs) > 1:
            logger.warn("Analysis {} with multiple retests".format(self.id))
        return api.get_object_by_uid(back_refs[0])
