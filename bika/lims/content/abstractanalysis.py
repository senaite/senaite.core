# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import cgi
import math
from decimal import Decimal

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.Field import BooleanField, DateTimeField, \
    FixedPointField, IntegerField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims import bikaMessageFactory as _, deprecated
from bika.lims import logger
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.abstractbaseanalysis import AbstractBaseAnalysis
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.content.reflexrule import doReflexRuleAction
from bika.lims.interfaces import ISamplePrepWorkflow, IDuplicateAnalysis
from bika.lims.permissions import *
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.utils import changeWorkflowState, formatDecimalMark
from bika.lims.utils import drop_trailing_zeros_decimal
from bika.lims.utils.analysis import create_analysis, format_numeric_result
from bika.lims.utils.analysis import get_significant_digits
from bika.lims.workflow import doActionFor
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import isTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed
from bika.lims.workflow import skip
from bika.lims.workflow.analysis import guards
from plone.api.portal import get_tool
from plone.api.user import has_permission
from zope.interface import implements

# A link directly to the AnalysisService object used to create the analysis
AnalysisService = UIDReferenceField(
    'AnalysisService'
)

# Overrides the AbstractBaseAnalysis. Analyses have a versioned link to the
# calculation as it was when created.
Calculation = HistoryAwareReferenceField(
    'Calculation',
    allowed_types=('Calculation',),
    relationship='AnalysisCalculation',
    referenceClass=HoldingReference
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
    'Result'
)

# When the result is changed, this value is updated to the current time.
# Only the most recent result capture date is recorded here and used to
# populate catalog values, however the workflow review_history can be
# used to get all dates of result capture
ResultCaptureDate = DateTimeField(
    'ResultCaptureDate'
)

# If ReportDryMatter is True in the AnalysisService, the adjusted result
# is stored here.
ResultDM = StringField(
    'ResultDM'
)

# If the analysis has previously been retracted, this flag is set True
# to indicate that this is a re-test.
Retested = BooleanField(
    'Retested',
    default=False
)

# When the AR is published, the date of publication is recorded here.
# It's used to populate catalog values.
DateAnalysisPublished = DateTimeField(
    'DateAnalysisPublished',
    widget=DateTimeWidget(
        label=_("Date Published")
    )
)

# If the result is outside of the detection limits of the method or instrument,
# the operand (< or >) is stored here.  For routine analyses this is taken
# from the Result, if the result entered explicitly startswith "<" or ">"
DetectionLimitOperand = StringField(
    'DetectionLimitOperand'
)

# This is used to calculate turnaround time reports.
# The value is set when the Analysis is published.
Duration = IntegerField(
    'Duration',
)

# This is used to calculate turnaround time reports. The value is set when the
# Analysis is published.
Earliness = IntegerField(
    'Earliness',
)

# The ID of the logged in user who submitted the result for this Analysis.
Analyst = StringField(
    'Analyst'
)

# The actual uncertainty for this analysis' result, populated from the ranges
# specified in the analysis service when the result is submitted.
Uncertainty = FixedPointField(
    'Uncertainty',
    precision=10,
)

# transitioned to a 'verified' state. This value is set automatically
# when the analysis is created, based on the value set for the property
# NumberOfRequiredVerifications from the Analysis Service
NumberOfRequiredVerifications = IntegerField(
    'NumberOfRequiredVerifications',
    default=1
)

# This field keeps the user_ids of members who verified this analysis.
# After each verification, user_id will be added end of this string
# seperated by comma- ',' .
Verificators = StringField(
    'Verificators',
    default=''
)

schema = schema.copy() + Schema((
    AnalysisService,
    Analyst,
    Attachment,
    # Calculation overrides AbstractBaseClass
    Calculation,
    DateAnalysisPublished,
    DetectionLimitOperand,
    Duration,
    Earliness,
    # NumberOfRequiredVerifications overrides AbstractBaseClass
    NumberOfRequiredVerifications,
    Result,
    ResultCaptureDate,
    ResultDM,
    Retested,
    Uncertainty,
    Verificators
))


class AbstractAnalysis(AbstractBaseAnalysis):
    implements(ISamplePrepWorkflow)
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
        logger.error("Cannot get ServiceUID for %s"%self)

    @security.public
    def getNumberOfVerifications(self):
        verificators = self.getVerificators()
        if not verificators:
            return 0
        return len(verificators.split(','))

    @security.public
    def addVerificator(self, username):
        verificators = self.getVerificators()
        if not verificators:
            self.setVerificators(username)
        else:
            self.setVerificators(verificators + "," + username)

    @security.public
    def deleteLastVerificator(self):
        verificators = self.getVerificators().split(',')
        del verificators[-1]
        self.setVerificators(",".join(verificators))

    @security.public
    def wasVerifiedByUser(self, username):
        verificators = self.getVerificators().split(',')
        return username in verificators

    @security.public
    def getLastVerificator(self):
        return self.getVerificators().split(',')[-1]

    @deprecated('[1705] Use Title() instead.')
    @security.public
    def getServiceTitle(self):
        """Returns the Title of the associated service. Analysis titles are
        always the same as the title of the service from which they are derived.
        """
        return self.Title()

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
        """Sets the detection limit operand for this analysis, so the result
        will be interpreted as a detection limit. The value will only be set
        if the Service has 'DetectionLimitSelector' field set to True,
        otherwise, the detection limit operand will be set to None. See
        LIMS-1775 for further information about the relation amongst
        'DetectionLimitSelector' and 'AllowManualDetectionLimit'.
        https://jira.bikalabs.com/browse/LIMS-1775
        """
        md = self.getDetectionLimitSelector()
        val = value if (md and value in '<>') else None
        self.getField('DetectionLimitOperand').set(self, val)

    # Method getLowerDetectionLimit overrides method of class BaseAnalysis
    @security.public
    def getLowerDetectionLimit(self):
        """Returns the Lower Detection Limit (LDL) that applies to this
        analysis in particular. If no value set or the analysis service
        doesn't allow manual input of detection limits, returns the value set
        by default in the Analysis Service
        """
        operand = self.getDetectionLimitOperand()
        if operand and operand == '<':
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
        operand = self.getDetectionLimitOperand()
        if operand and operand == '>':
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
        dl = self.getDetectionLimitOperand()
        if dl and dl == '<':
            return True
        result = self.getResult()
        if result and str(result).strip().startswith('<'):
            return True
        elif result:
            ldl = self.getLowerDetectionLimit()
            try:
                result = float(result)
                return result < ldl
            except (TypeError, ValueError):
                pass
        return False

    @security.public
    def isAboveUpperDetectionLimit(self):
        """Returns True if the result is above the Upper Detection Limit or
        if Upper Detection Limit has been manually set
        """
        dl = self.getDetectionLimitOperand()
        if dl and dl == '>':
            return True
        result = self.getResult()
        if result and str(result).strip().startswith('>'):
            return True
        elif result:
            udl = self.getUpperDetectionLimit()
            try:
                result = float(result)
                return result > udl
            except (TypeError, ValueError):
                pass
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
        if self.isBelowLowerDetectionLimit():
            if self.getDetectionLimitOperand() == '<':
                return True

    @security.public
    def isUpperDetectionLimit(self):
        """Returns True if the result for this analysis represents an Upper
        Detection Limit. Otherwise, returns False
        """
        if self.isAboveUpperDetectionLimit():
            if self.getDetectionLimitOperand() == '>':
                return True

    @security.public
    def getDependents(self):
        """Return a list of analyses who depend on us to calculate their result
        """
        raise NotImplementedError("getDependents is not implemented.")

    @security.public
    def getDependencies(self):
        """Return a list of analyses who we depend on to calculate our result.
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
        # Only allow DL if manually enabled in AS
        val = str(value).strip()
        if val and val[0] in '<>':
            self.setDetectionLimitOperand(None)
            oper = val[0]
            val = val.replace(oper, '', 1)

            # Check if the value is indeterminate / non-floatable
            try:
                str(float(val))
            except (ValueError, TypeError):
                val = value

            if self.getDetectionLimitSelector():
                if self.getAllowManualDetectionLimit():
                    # DL allowed, try to remove the operator and set the
                    # result as a detection limit
                    self.setDetectionLimitOperand(oper)
                else:
                    # Trying to set a result with an '<,>' operator,
                    # but manual DL not allowed, so override the
                    # value with the service's default LDL or UDL
                    # according to the operator, but only if the value
                    # is not an indeterminate.
                    if oper == '<':
                        val = self.getLowerDetectionLimit()
                    else:
                        val = self.getUpperDetectionLimit()
                    self.setDetectionLimitOperand(oper)
        elif val is '':
            # Reset DL
            self.setDetectionLimitOperand(None)

        self.getField('Result').set(self, val)

        # Uncertainty calculation on DL
        # https://jira.bikalabs.com/browse/LIMS-1808
        if self.isAboveUpperDetectionLimit() or \
                self.isBelowLowerDetectionLimit():
            self.getField('Uncertainty').set(self, None)

    @security.public
    def getSample(self):
        raise NotImplementedError("getSample is not implemented.")

    @security.public
    def getSampleUID(self):
        """Instances must implement getSample
        """
        sample = self.getSample()
        if sample:
            return sample.UID()

    @security.public
    def getAnalysisSpecs(self, specification=None):
        raise NotImplementedError("getAnalysisSpecs is not implemented.")

    @security.public
    def getResultsRange(self, specification=None):
        raise NotImplementedError("getResultsRange is not implemented.")

    @security.public
    def getResultsRangeNoSpecs(self):
        """This method is used to populate catalog values
        """
        return self.getResultsRange()

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
            result = eval(formula)
        except TypeError:
            self.setResult("NA")
            return True
        except ZeroDivisionError:
            self.setResult('0/0')
            return True
        except KeyError:
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
            price = self.getPrice()
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
        if isinstance(instrument, str):
            uid = instrument
        else:
            uid = instrument.UID()

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
        if isinstance(method, str):
            uid = method
        else:
            uid = method.UID()

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
        field = self.getField('ExponentialFormatPrecision')
        if not result or self.getPrecisionFromUncertainty() is False:
            return field.get(self)
        else:
            uncertainty = self.getUncertainty(result)
            if uncertainty is None:
                return field.get(self)

            try:
                float(result)
            except ValueError:
                # if analysis result is not a number, then we assume in range
                return field.get(self)

            return get_significant_digits(uncertainty)

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

        - ManualUncertainty not set: returns the precision from the
            AnalysisService.

        - ManualUncertainty set and Calculate Precision from Uncertainty
          is also set in Analysis Service: calculates the precision of the
          result according to the manual uncertainty set.

        - ManualUncertainty set and Calculatet Precision from Uncertainty
          not set in Analysis Service: returns the result as-is.

        Further information at AbstractBaseAnalysis.getPrecision()
        """
        schu = self.getField('Uncertainty').get(self)
        if all([schu,
                self.getAllowManualUncertainty(),
                self.getPrecisionFromUncertainty()]):
            uncertainty = self.getUncertainty(result)
            if uncertainty == 0:
                return 1
            return get_significant_digits(uncertainty)
        return self.getField('Precision').get(self)

    @security.public
    def getAnalyst(self):
        """Returns the identifier of the assigned analyst. If there is no
        analyst assigned, and this analysis is attached to a worksheet,
        retrieves the analyst assigned to the parent worksheet
        """
        field = self.getField('Analyst')
        analyst = field and field.get(self) or ''
        if not analyst:
            # Is assigned to a worksheet?
            wss = self.getBackReferences('WorksheetAnalysis')
            if len(wss) > 0:
                analyst = wss[0].getAnalyst()
                field.set(self, analyst)
        return analyst if analyst else ''

    @security.public
    def getAnalystName(self):
        """Returns the name of the currently assigned analyst
        """
        mtool = get_tool('portal_membership')
        analyst = self.getAnalyst().strip()
        analyst_member = mtool.getMemberById(analyst)
        if analyst_member:
            return analyst_member.getProperty('fullname')
        return ''

    # TODO Workflow, Analysis - Move to analysis.guard.verify?
    @security.public
    def isVerifiable(self):
        """Checks it the current analysis can be verified. This is, its not a
        cancelled analysis and has no dependenant analyses not yet verified
        :return: True or False
        """
        # Check if the analysis is active
        workflow = get_tool("portal_workflow")
        objstate = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if objstate == "cancelled":
            return False

        # Check if the analysis state is to_be_verified
        review_state = workflow.getInfoFor(self, "review_state")
        if review_state != 'to_be_verified':
            return False

        # Check if the analysis has dependencies not yet verified
        for d in self.getDependencies():
            review_state = workflow.getInfoFor(d, "review_state")
            if review_state in (
                    "to_be_sampled", "to_be_preserved", "sample_due",
                    "sample_received", "attachment_due", "to_be_verified"):
                return False

        # All checks passsed
        return True

    # TODO Workflow, Analysis - Move to analysis.guard.verify?
    @security.public
    def isUserAllowedToVerify(self, member):
        """
        Checks if the specified user has enough privileges to verify the
        current analysis. Apart of roles, the function also checks if the
        option IsSelfVerificationEnabled is set to true at Service or
        Bika Setup levels and validates if according to this value, together
        with the user roles, the analysis can be verified. Note that this
        function only returns if the user can verify the analysis, but not if
        the analysis is ready to be verified (see isVerifiable)
        :member: user to be tested
        :return: true or false
        """
        # Check if the user has "Bika: Verify" privileges
        username = member.getUserName()
        allowed = has_permission(VerifyPermission, username=username)
        if not allowed:
            return False

        # Check if the user who submited the result is the same as the current
        self_submitted = self.getSubmittedBy() == member.getUser().getId()

        # The submitter and the user must be different unless the analysis has
        # the option SelfVerificationEnabled set to true
        selfverification = self.isSelfVerificationEnabled()
        if self_submitted and not selfverification:
            return False

        # Checking verifiability depending on multi-verification type of
        # bika_setup
        if self.bika_setup.getNumberOfRequiredVerifications() > 1:
            mv_type = self.bika_setup.getTypeOfmultiVerification()
            # If user verified before and self_multi_disabled, then return False
            if mv_type == 'self_multi_disabled' and self.wasVerifiedByUser(
                    username):
                return False

            # If user is the last verificator and consecutively
            # multi-verification
            # is disabled, then return False
            # Comparing was added just to check if this method is called
            # before/after
            # verification
            elif mv_type == 'self_multi_not_cons' and username == \
                    self.getLastVerificator() and \
                            self.getNumberOfVerifications() < \
                            self.getNumberOfRequiredVerifications():
                return False

        # All checks pass
        return True

    @security.public
    def getObjectWorkflowStates(self):
        """This method is used to populate catalog values
        Returns a dictionary with the workflow id as key and workflow state as
        value.
        :return: {'review_state':'active',...}
        """
        workflow = get_tool('portal_workflow')
        states = {}
        for w in workflow.getWorkflowsFor(self):
            state = w._getWorkflowStateOf(self).id
            states[w.state_var] = state
        return states

    @security.public
    def getSampleConditionUID(self):
        """This method is used to populate catalog values
        """
        sample_cond = self.getSample().getSampleCondition()
        if sample_cond:
            return sample_cond.UID()
        return ''

    @security.public
    def getSubmittedBy(self):
        """
        Returns the identifier of the user who submitted the result if the
        state of the current analysis is "to_be_verified" or "verified"
        :return: the user_id of the user who did the last submission of result
        """
        workflow = get_tool("portal_workflow")
        try:
            review_history = workflow.getInfoFor(self, "review_history")
            review_history = self.reverseList(review_history)
            for event in review_history:
                if event.get("action") == "submit":
                    return event.get("actor")
            return ''
        except WorkflowException:
            return ''

    @security.public
    def getDateSubmitted(self):
        """Returns the time the result was submitted.
        :return: a DateTime object.
        """
        workflow = get_tool("portal_workflow")
        try:
            review_history = workflow.getInfoFor(self, "review_history")
            review_history = self.reverseList(review_history)
            for event in review_history:
                if event.get("action") == "submit":
                    return event.get("time")
            return ''
        except WorkflowException:
            return ''

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
        worksheet = self.getBackReferences("WorksheetAnalysis")
        if not worksheet:
            return None
        if len(worksheet) > 1:
            logger.error(
                "Analysis %s is assigned to more than one worksheet."
                % self.getId())
        return worksheet[0]

    def getExpiryDate(self):
        """It is used as a metacolumn.
        Returns the expiration date from the associated sample
        """
        # XXX getattr(getExpiryDate) is quite silly
        # it seems that ReferenceSample should have this attribute (but doesnt)
        # and that although nobody expected Sample to have it, it should.
        sample = self.getSample()
        if hasattr(sample, 'getExpiryDate'):
            return sample.getExpiryDate()

    @security.public
    def getInstrumentValid(self):
        """Used to populate catalog values. Delegates to isInstrumentValid()
        Returns false if an out-of-date or uncalibrated instrument is
        assigned.
        :return: True if the Analysis has no instrument assigned or is valid
        :rtype: bool
        """
        return self.isInstrumentValid()

    @deprecated('[1705] Orphan. Use getAttachmentUIDs')
    @security.public
    def hasAttachment(self):
        attachments = self.getAttachmentUIDs()
        return len(attachments) > 0

    @security.public
    def getAttachmentUIDs(self):
        """Used to populate metadata, so that we don't need full objects of
        analyses when working with their attachments.
        """
        attachments = self.getAttachment()
        uids = [att.UID() for att in attachments]
        return uids

    @security.public
    def remove_duplicates(self, ws):
        """When this analysis is unassigned from a worksheet, this function
        is responsible for deleting DuplicateAnalysis objects from the ws.
        """
        for analysis in ws.objectValues():
            if IDuplicateAnalysis.providedBy(analysis) \
                    and analysis.getAnalysis().UID() == self.UID():
                ws.removeAnalysis(analysis)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.sample')
    @security.public
    def guard_sample_transition(self):
        return guards.sample(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.retract')
    @security.public
    def guard_retract_transition(self):
        return guards.retract(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.sample_prep')
    @security.public
    def guard_sample_prep_transition(self):
        return guards.sample_prep(self)

    @deprecated('[1705] Use guards.sample_prep_complete from '
                'bika.lims.workflow.analysis.guards.sample_prep_complete')
    @security.public
    def guard_sample_prep_complete_transition(self):
        return guards.sample_prep_complete(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.receive')
    @security.public
    def guard_receive_transition(self):
        return guards.receive(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.publish')
    @security.public
    def guard_publish_transition(self):
        return guards.publish(self)

    @deprecated('[1705] Use guards.import_transition from '
                'bika.lims.workflow.analysis.guards.import_transition')
    @security.public
    def guard_import_transition(self):
        return guards.import_transition(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.attach')
    @security.public
    def guard_attach_transition(self):
        return guards.attach(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.verify')
    @security.public
    def guard_verify_transition(self):
        return guards.verify(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.assign')
    @security.public
    def guard_assign_transition(self):
        return guards.assign(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.guards.unassign')
    @security.public
    def guard_unassign_transition(self):
        return guards.unassign(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_submit')
    @security.public
    def workflow_script_submit(self):
        events.after_submit(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_retract')
    @security.public
    def workflow_script_retract(self):
        events.after_retract(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_verify')
    @security.public
    def workflow_script_verify(self):
        events.after_verify(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_publish')
    @security.public
    def workflow_script_publish(self):
        events.after_publish(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_cancel')
    @security.public
    def workflow_script_cancel(self):
        events.after_cancel(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_reject')
    @security.public
    def workflow_script_reject(self):
        events.after_reject(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_attach')
    @security.public
    def workflow_script_attach(self):
        events.after_attach(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_assign')
    @security.public
    def workflow_script_assign(self):
        events.after_assign(self)

    @deprecated('[1705] Use bika.lims.workflow.analysis.events.after_unassign')
    @security.public
    def workflow_script_unassign(self):
        events.after_unassign(self)
