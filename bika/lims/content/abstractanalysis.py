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
from bika.lims.workflow import skip
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

    @deprecated("Currently returns the Analysis object itself.  If you really "
                "need to get the service, use getAnalysisService instead.")
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

    @deprecated("You should use the Analysis Title.")
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
        dependents = []
        ar = self.aq_parent
        for sibling in ar.getAnalyses(full_objects=True):
            if sibling == self:
                continue
            calculation = sibling.getCalculation()
            if not calculation:
                continue
            depservices = calculation.getDependentServices()
            dep_keywords = [x.getKeyword() for x in depservices]
            if self.getKeyword() in dep_keywords:
                dependents.append(sibling)
        return dependents

    @security.public
    def getDependencies(self):
        """Return a list of analyses who we depend on to calculate our result.
        """
        siblings = self.aq_parent.getAnalyses(full_objects=True)
        calculation = self.getCalculation()
        if not calculation:
            return []
        dep_services = [d.UID() for d in calculation.getDependentServices()]
        dep_analyses = [a for a in siblings if
                        a.getServiceUID() in dep_services]
        return dep_analyses

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
    def getAnalysisSpecs(self, specification=None):
        """Retrieves the analysis specs to be applied to this analysis.
        Allowed values for specification= 'client', 'lab', None If
        specification is None, client specification gets priority from lab
        specification. If no specification available for this analysis,
        returns None
        """

        sample = self.getSample()
        sampletype = sample.getSampleType()
        sampletype_uid = sampletype and sampletype.UID() or ''
        bsc = get_tool('bika_setup_catalog')

        # retrieves the desired specs if None specs defined
        if not specification:
            proxies = bsc(portal_type='AnalysisSpec',
                          getClientUID=self.getClientUID(),
                          getSampleTypeUID=sampletype_uid)

            if len(proxies) == 0:
                # No client specs available, retrieve lab specs
                proxies = bsc(portal_type='AnalysisSpec',
                              getSampleTypeUID=sampletype_uid)
        else:
            specuid = specification == "client" and self.getClientUID() or \
                      self.bika_setup.bika_analysisspecs.UID()
            proxies = bsc(portal_type='AnalysisSpec',
                          getSampleTypeUID=sampletype_uid,
                          getClientUID=specuid)

        outspecs = None
        for spec in (p.getObject() for p in proxies):
            if self.getKeyword() in spec.getResultsRangeDict():
                outspecs = spec
                break

        return outspecs

    @security.public
    def getResultsRange(self, specification=None):
        """Returns the valid results range for this analysis, a dictionary
        with the following keys: 'keyword', 'uid', 'min', 'max ', 'error',
        'hidemin', 'hidemax', 'rangecomment' Allowed values for
        specification='ar', 'client', 'lab', None If specification is None,
        the following is the priority to get the results range: AR > Client >
        Lab If no specification available for this analysis, returns {}
        """
        rr = {}
        an = self

        if specification == 'ar' or specification is None:
            if an.aq_parent and an.aq_parent.portal_type == 'AnalysisRequest':
                rr = an.aq_parent.getResultsRange()
                rr = [r for r in rr if r.get('keyword', '') == an.getKeyword()]
                rr = rr[0] if rr and len(rr) > 0 else {}
                if rr:
                    rr['uid'] = self.UID()
        if not rr:
            # Let's try to retrieve the specs from client and/or lab
            specs = an.getAnalysisSpecs(specification)
            rr = specs.getResultsRangeDict() if specs else {}
            rr = rr.get(an.getKeyword(), {}) if rr else {}
            if rr:
                rr['uid'] = self.UID()
        return rr

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
    def getPriority(self):
        """get priority from AR
        """
        # this analysis could be in a worksheet or instrument, careful
        if hasattr(self.aq_parent, 'getPriority'):
            return self.aq_parent.getPriority()

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
        priority = self.getPriority()
        if priority and priority.getPricePremium() > 0:
            price = Decimal(price) + \
                    (Decimal(price) * Decimal(priority.getPricePremium()) / 100)
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
    def getBatchUID(self):
        """This method is used to populate catalog values
        """
        return self.aq_parent.getBatchUID()

    @security.public
    def getSampleConditionUID(self):
        """This method is used to populate catalog values
        """
        sample_cond = self.getSample().getSampleCondition()
        if sample_cond:
            return sample_cond.UID()
        return ''

    @security.public
    def getAnalysisRequestPrintStatus(self):
        """This method is used to populate catalog values
        """
        return self.aq_parent.getPrinted()

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
    def getDueDate(self):
        """Used to populate getDueDate index and metadata.
        This very simply returns the expiry date of the parent reference sample.
        """
        ref_sample = self.aq_parent
        expiry_date = ref_sample.getExpiryDate()
        return expiry_date

    @security.public
    def getParentUID(self):
        """This method is used to populate catalog values
        This function returns the analysis' parent UID
        """
        return self.aq_parent.UID()

    @security.public
    def getParentURL(self):
        """This method is used to populate catalog values
        This function returns the analysis' parent URL
        """
        return self.aq_parent.absolute_url_path()

    @security.public
    def getWorksheetUID(self):
        """This method is used to populate catalog values
        Returns WS UID if this analysis is assigned to a worksheet, or None.
        """
        worksheet = self.getBackReferences("WorksheetAnalysis")
        if worksheet and len(worksheet) > 1:
            logger.error(
                "Analysis %s is assigned to more than one worksheet."
                % self.getId())
            return worksheet[0].UID()
        elif worksheet:
            return worksheet[0].UID()
        return ''

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

    @security.public
    def hasAttachment(self):
        """This method is used to populate catalog values
        Checks if the object has attachments or not. Returns a boolean.
        """
        attachments = self.getAttachment()
        return len(attachments) > 0

    @security.public
    def _reflex_rule_process(self, wf_action):
        """This function does all the reflex rule process.
        :param wf_action: is a string containing the workflow action triggered
        """
        workflow = get_tool('portal_workflow')
        # Check out if the analysis has any reflex rule bound to it.
        # First we have get the analysis' method because the Reflex Rule
        # objects are related to a method.
        a_method = self.getMethod()
        # After getting the analysis' method we have to get all Reflex Rules
        # related to that method.
        if a_method:
            all_rrs = a_method.getBackReferences('ReflexRuleMethod')
            # Once we have all the Reflex Rules with the same method as the
            # analysis has, it is time to get the rules that are bound to the
            # same analysis service that is using the analysis.
            for rule in all_rrs:
                state = workflow.getInfoFor(rule, 'inactive_state')
                if state == 'inactive':
                    continue
                # Getting the rules to be done from the reflex rule taking
                # in consideration the analysis service, the result and
                # the state change
                action_row = rule.getActionReflexRules(self, wf_action)
                # Once we have the rules, the system has to execute its
                # instructions if the result has the expected result.
                doReflexRuleAction(self, action_row)

    @security.public
    def guard_sample_transition(self):
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, "cancellation_state", "active")
        if state == "cancelled":
            return False
        return True

    @security.public
    def guard_retract_transition(self):
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, "cancellation_state", "active")
        if state == "cancelled":
            return False
        return True

    @security.public
    def guard_sample_prep_transition(self):
        sample = self.getSample()
        return sample.guard_sample_prep_transition()

    @security.public
    def guard_sample_prep_complete_transition(self):
        sample = self.getSample()
        return sample.guard_sample_prep_complete_transition()

    @security.public
    def guard_receive_transition(self):
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, "cancellation_state", "active")
        if state == "cancelled":
            return False
        return True

    @security.public
    def guard_publish_transition(self):
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, "cancellation_state", "active")
        if state == "cancelled":
            return False
        return True

    @security.public
    def guard_import_transition(self):
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, "cancellation_state", "active")
        if state == "cancelled":
            return False
        return True

    @security.public
    def guard_attach_transition(self):
        if not self.getAttachment():
            if self.getAttachmentOption() == "r":
                return False
        return True

    @security.public
    def guard_verify_transition(self):
        """Checks if the verify transition can be performed to the current
        Analysis by the current user depending on the user roles, as well as
        the status of the analysis
        :return: Boolean
        """
        mtool = get_tool("portal_membership")
        # Check if the analysis is in a "verifiable" state
        if self.isVerifiable():
            # Check if the user can verify the analysis
            member = mtool.getAuthenticatedMember()
            return self.isUserAllowedToVerify(member)
        return False

    @security.public
    def guard_assign_transition(self):
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if state == "cancelled":
            return False
        return True

    @security.public
    def guard_unassign_transition(self):
        """Check permission against parent worksheet
        """
        workflow = get_tool("portal_workflow")
        mtool = get_tool("portal_membership")
        ws = self.getBackReferences("WorksheetAnalysis")
        if not ws:
            return False
        ws = ws[0]
        state = workflow.getInfoFor(ws, "cancellation_state", "")
        if state == "cancelled":
            return False
        if mtool.checkPermission(Unassign, ws):
            return True
        return False

    @security.public
    def workflow_script_receive(self):
        if skip(self, "receive"):
            return
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if state == "cancelled":
            return False
        self.reindexObject()

    @security.public
    def workflow_script_submit(self):
        if skip(self, "submit"):
            return
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if state == "cancelled":
            return False
        ar = self.aq_parent
        # Dependencies are submitted already, ignore them.
        # -------------------------------------------------
        # Submit our dependents
        # Need to check for result and status of dependencies first
        dependents = self.getDependents()
        for dependent in dependents:
            if not skip(dependent, "submit", peek=True):
                can_submit = True
                if not dependent.getResult():
                    can_submit = False
                else:
                    interim_fields = False
                    calculation = dependent.getCalculation()
                    if calculation:
                        interim_fields = calculation.getInterimFields()
                    if interim_fields:
                        can_submit = False
                if can_submit:
                    dependencies = dependent.getDependencies()
                    for dependency in dependencies:
                        state = workflow.getInfoFor(dependency, "review_state")
                        if state in ("to_be_sampled", "to_be_preserved",
                                     "sample_due", "sample_received"):
                            can_submit = False
                if can_submit:
                    workflow.doActionFor(dependent, "submit")
        # Do all the reflex rules process
        self._reflex_rule_process('submit')
        # If all analyses in this AR have been submitted
        # escalate the action to the parent AR
        if not skip(ar, "submit", peek=True):
            all_submitted = True
            for a in ar.getAnalyses():
                if a.review_state in ("to_be_sampled", "to_be_preserved",
                                      "sample_due", "sample_received"):
                    all_submitted = False
                    break
            if all_submitted:
                workflow.doActionFor(ar, "submit")

        # If assigned to a worksheet and all analyses on the worksheet have
        # been submitted,
        # then submit the worksheet.
        ws = self.getBackReferences("WorksheetAnalysis")
        if ws:
            ws = ws[0]
            # if the worksheet analyst is not assigned, the worksheet can't
            # be transitioned.
            if ws.getAnalyst() and not skip(ws, "submit", peek=True):
                all_submitted = True
                for a in ws.getAnalyses():
                    if workflow.getInfoFor(a, "review_state") in \
                            ("to_be_sampled", "to_be_preserved",
                             "sample_due", "sample_received", "assigned",):
                        all_submitted = False
                        break
                if all_submitted:
                    workflow.doActionFor(ws, "submit")

        # If no problem with attachments, do 'attach' action for this instance.
        can_attach = True
        if not self.getAttachment():
            if self.getAttachmentOption() == "r":
                can_attach = False
        if can_attach:
            dependencies = self.getDependencies()
            for dependency in dependencies:
                if workflow.getInfoFor(dependency, "review_state") in \
                        ("to_be_sampled", "to_be_preserved", "sample_due",
                         "sample_received", "attachment_due",):
                    can_attach = False
        if can_attach:
            try:
                workflow.doActionFor(self, "attach")
            except WorkflowException:
                logger.error(
                    "Workflow transition error: 'attach' "
                    "action failed for analysis {0}".format(self.getId()))
        self.reindexObject()

    @security.public
    def workflow_script_retract(self):
        if skip(self, "retract"):
            return
        ar = self.aq_parent
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if state == "cancelled":
            return False
        # Rename the analysis to make way for it's successor.
        # Support multiple retractions by renaming to *-0, *-1, etc
        parent = self.aq_parent
        kw = self.getKeyword()
        analyses = [x for x in parent.objectValues("Analysis")
                    if x.getId().startswith(self.getId())]
        # LIMS-1290 - Analyst must be able to retract, which creates a new
        # Analysis.  So, _verifyObjectPaste permission check must be cancelled:
        parent._verifyObjectPaste = str
        parent.manage_renameObject(kw, "{0}-{1}".format(kw, len(analyses)))
        delattr(parent, '_verifyObjectPaste')
        # Create new analysis from the retracted self
        analysis = create_analysis(parent, self)
        changeWorkflowState(
            analysis, "bika_analysis_workflow", "sample_received")
        # We'll assign the new analysis to this same worksheet, if any.
        ws = self.getBackReferences("WorksheetAnalysis")
        if ws:
            ws = ws[0]
            ws.addAnalysis(analysis)
        analysis.reindexObject()
        # retract our dependencies
        if "retract all dependencies" not in self.REQUEST["workflow_skiplist"]:
            for dependency in self.getDependencies():
                if not skip(dependency, "retract", peek=True):
                    state = workflow.getInfoFor(dependency, "review_state")
                    if state in ("attachment_due", "to_be_verified",):
                        # (NB: don"t retract if it"s verified)
                        workflow.doActionFor(dependency, "retract")
        # Retract our dependents
        for dep in self.getDependents():
            if not skip(dep, "retract", peek=True):
                state = workflow.getInfoFor(dep, "review_state")
                if state not in ("sample_received", "retracted"):
                    self.REQUEST["workflow_skiplist"].append(
                        "retract all dependencies")
                    # just return to "received" state, no cascade
                    workflow.doActionFor(dep, 'retract')
                    self.REQUEST["workflow_skiplist"].remove(
                        "retract all dependencies")
        # Escalate action to the parent AR
        if not skip(ar, "retract", peek=True):
            if workflow.getInfoFor(ar, "review_state") == "sample_received":
                skip(ar, "retract")
            else:
                if "retract all analyses" \
                        not in self.REQUEST["workflow_skiplist"]:
                    self.REQUEST["workflow_skiplist"].append(
                        "retract all analyses")
                workflow.doActionFor(ar, "retract")
        # Escalate action to the Worksheet (if it's on one).
        ws = self.getBackReferences("WorksheetAnalysis")
        if ws:
            ws = ws[0]
            if not skip(ws, "retract", peek=True):
                if workflow.getInfoFor(ws, "review_state") == "open":
                    skip(ws, "retract")
                else:
                    if "retract all analyses" \
                            not in self.REQUEST['workflow_skiplist']:
                        self.REQUEST["workflow_skiplist"].append(
                            "retract all analyses")
                    try:
                        workflow.doActionFor(ws, "retract")
                    except WorkflowException:
                        pass
            # Add to worksheet Analyses
            analyses = list(ws.getAnalyses())
            analyses += [analysis, ]
            ws.setAnalyses(analyses)
            # Add to worksheet layout
            layout = ws.getLayout()
            pos = [x["position"] for x in layout
                   if x["analysis_uid"] == self.UID()][0]
            slot = {"position": pos,
                    "analysis_uid": analysis.UID(),
                    "container_uid": analysis.aq_parent.UID(),
                    "type": "a"}
            layout.append(slot)
            ws.setLayout(layout)
        self.reindexObject()

    @security.public
    def workflow_script_verify(self):
        if skip(self, "verify"):
            return
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if state == "cancelled":
            return False
        # Do all the reflex rules process
        self._reflex_rule_process('verify')
        # If all analyses in this AR are verified escalate the action to the
        # parent AR
        ar = self.aq_parent
        if not skip(ar, "verify", peek=True):
            all_verified = True
            for a in ar.getAnalyses():
                if a.review_state in ("to_be_sampled", "to_be_preserved",
                                      "sample_due", "sample_received",
                                      "attachment_due", "to_be_verified"):
                    all_verified = False
                    break
            if all_verified:
                if "verify all analyses" \
                        not in self.REQUEST['workflow_skiplist']:
                    self.REQUEST["workflow_skiplist"].append(
                        "verify all analyses")
                workflow.doActionFor(ar, "verify")
        # If this is on a worksheet and all it's other analyses are verified,
        # then verify the worksheet.
        ws = self.getBackReferences("WorksheetAnalysis")
        if ws:
            ws = ws[0]
            ws_state = workflow.getInfoFor(ws, "review_state")
            if ws_state == "to_be_verified" and not skip(ws, "verify",
                                                         peek=True):
                all_verified = True
                for a in ws.getAnalyses():
                    state = workflow.getInfoFor(a, "review_state")
                    if state in ("to_be_sampled", "to_be_preserved",
                                 "sample_due", "sample_received",
                                 "attachment_due", "to_be_verified",
                                 "assigned"):
                        all_verified = False
                        break
                if all_verified:
                    if "verify all analyses" \
                            not in self.REQUEST['workflow_skiplist']:
                        self.REQUEST["workflow_skiplist"].append(
                            "verify all analyses")
                    workflow.doActionFor(ws, "verify")
        self.reindexObject()

    @security.public
    def workflow_script_publish(self):
        if skip(self, "publish"):
            return
        workflow = get_tool("portal_workflow")
        state = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if state == "cancelled":
            return False
        endtime = DateTime()
        self.setDateAnalysisPublished(endtime)
        starttime = self.aq_parent.getDateReceived()
        starttime = starttime or self.created()
        maxtime = self.getMaxTimeAllowed()
        # set the instance duration value to default values
        # in case of no calendars or max hours
        if maxtime:
            duration = (endtime - starttime) * 24 * 60
            maxtime_delta = int(maxtime.get("hours", 0)) * 86400
            maxtime_delta += int(maxtime.get("hours", 0)) * 3600
            maxtime_delta += int(maxtime.get("minutes", 0)) * 60
            earliness = duration - maxtime_delta
        else:
            earliness = 0
            duration = 0
        self.setDuration(duration)
        self.setEarliness(earliness)
        self.reindexObject()

    @security.public
    def workflow_script_cancel(self):
        if skip(self, "cancel"):
            return
        workflow = get_tool("portal_workflow")
        # If it is assigned to a worksheet, unassign it.
        state = workflow.getInfoFor(self, 'worksheetanalysis_review_state')
        if state == 'assigned':
            ws = self.getBackReferences("WorksheetAnalysis")[0]
            skip(self, "cancel", unskip=True)
            ws.removeAnalysis(self)
        self.reindexObject()

    @security.public
    def workflow_script_reject(self):
        if skip(self, "reject"):
            return
        workflow = get_tool("portal_workflow")
        # If it is assigned to a worksheet, unassign it.
        state = workflow.getInfoFor(self, 'worksheetanalysis_review_state')
        if state == 'assigned':
            ws = self.getBackReferences("WorksheetAnalysis")[0]
            ws.removeAnalysis(self)
        self.reindexObject()

    @security.public
    def workflow_script_attach(self):
        if skip(self, "attach"):
            return
        workflow = get_tool("portal_workflow")
        # If all analyses in this AR have been attached escalate the action
        # to the parent AR
        ar = self.aq_parent
        state = workflow.getInfoFor(ar, "review_state")
        if state == "attachment_due" and not skip(ar, "attach", peek=True):
            can_attach = True
            for a in ar.getAnalyses():
                if a.review_state in ("to_be_sampled", "to_be_preserved",
                                      "sample_due", "sample_received",
                                      "attachment_due"):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ar, "attach")
        # If assigned to a worksheet and all analyses on the worksheet have
        # been attached, then attach the worksheet.
        ws = self.getBackReferences('WorksheetAnalysis')
        if ws:
            ws = ws[0]
            ws_state = workflow.getInfoFor(ws, "review_state")
            if ws_state == "attachment_due" \
                    and not skip(ws, "attach", peek=True):
                can_attach = True
                for a in ws.getAnalyses():
                    state = workflow.getInfoFor(a, "review_state")
                    if state in ("to_be_sampled", "to_be_preserved",
                                 "sample_due", "sample_received",
                                 "attachment_due", "assigned"):
                        can_attach = False
                        break
                if can_attach:
                    workflow.doActionFor(ws, "attach")
        self.reindexObject()

    @security.public
    def workflow_script_assign(self):
        if skip(self, "assign"):
            return
        workflow = get_tool("portal_workflow")
        uc = get_tool("uid_catalog")
        ws = uc(UID=self.REQUEST["context_uid"])[0].getObject()
        # retract the worksheet to 'open'
        ws_state = workflow.getInfoFor(ws, "review_state")
        if ws_state != "open":
            if "workflow_skiplist" not in self.REQUEST:
                self.REQUEST["workflow_skiplist"] = ["retract all analyses", ]
            else:
                self.REQUEST["workflow_skiplist"].append("retract all analyses")
            allowed_transitions = \
                [t["id"] for t in workflow.getTransitionsFor(ws)]
            if "retract" in allowed_transitions:
                workflow.doActionFor(ws, "retract")
        # If all analyses in this AR have been assigned,
        # escalate the action to the parent AR
        if not skip(self, "assign", peek=True):
            if not self.getAnalyses(
                    worksheetanalysis_review_state="unassigned"):
                try:
                    allowed_transitions = \
                        [t["id"] for t in workflow.getTransitionsFor(self)]
                    if "assign" in allowed_transitions:
                        workflow.doActionFor(self, "assign")
                except WorkflowException:
                    logger.error(
                        "assign action failed for analysis %s" % self.getId())
        self.reindexObject()

    def remove_duplicates(self, ws):
        """When this analysis is unassigned from a worksheet, this function
        is responsible for deleting DuplicateAnalysis objects from the ws.
        """
        for analysis in ws.objectValues():
            if IDuplicateAnalysis.providedBy(analysis) \
                    and analysis.getAnalysis().UID() == self.UID():
                ws.removeAnalysis(analysis)

    @security.public
    def workflow_script_unassign(self):
        if skip(self, "unassign"):
            return
        workflow = get_tool("portal_workflow")
        uc = get_tool("uid_catalog")
        ws = uc(UID=self.REQUEST["context_uid"])[0].getObject()
        # Escalate the action to the parent AR if it is assigned
        # Note: AR adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions/demotions (maybe by more than
        #       one instance).
        state = workflow.getInfoFor(self, "worksheetanalysis_review_state")
        if state == "assigned":
            workflow.doActionFor(self, "unassign")
            skip(self, "unassign", unskip=True)
        # If it has been duplicated on the worksheet, delete the duplicates.
        self.remove_duplicates(ws)
        # May need to promote the Worksheet's review_state
        # if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = True
        for a in ws.getAnalyses():
            ws_empty = False
            a_state = workflow.getInfoFor(a, "review_state")
            if a_state in ("to_be_sampled", "to_be_preserved", "assigned",
                           "sample_due", "sample_received"):
                can_submit = False
            else:
                if not ws.getAnalyst():
                    can_submit = False
            if a_state in ("to_be_sampled", "to_be_preserved", "assigned",
                           "sample_due", "sample_received", "attachment_due"):
                can_attach = False
            if a_state in ("to_be_sampled", "to_be_preserved", "assigned",
                           "sample_due", "sample_received", "attachment_due",
                           "to_be_verified"):
                can_verify = False
        if not ws_empty:
            # Note: WS adds itself to the skiplist so we have to take it
            # off again to allow multiple promotions (maybe by more than
            # one instance).
            state = workflow.getInfoFor(ws, "review_state")
            if can_submit and state == "open":
                workflow.doActionFor(ws, "submit")
                skip(ws, 'unassign', unskip=True)
            state = workflow.getInfoFor(ws, "review_state")
            if can_attach and state == "attachment_due":
                workflow.doActionFor(ws, "attach")
                skip(ws, 'unassign', unskip=True)
            state = workflow.getInfoFor(ws, "review_state")
            if can_verify and state == "to_be_verified":
                self.REQUEST['workflow_skiplist'].append("verify all analyses")
                workflow.doActionFor(ws, "verify")
                skip(ws, 'unassign', unskip=True)
        else:
            if workflow.getInfoFor(ws, "review_state") != "open":
                workflow.doActionFor(ws, "retract")
                skip(ws, "retract", unskip=True)
        self.reindexObject()
