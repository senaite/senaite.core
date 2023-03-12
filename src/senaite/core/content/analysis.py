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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.
import copy

import json
from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import deprecated
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IBaseAnalysis
from bika.lims.interfaces import IHaveAnalysisCategory
from bika.lims.interfaces import IHaveDepartment
from bika.lims.interfaces import IHaveInstrument
from bika.lims.interfaces import IInternalUse
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.workflow.analysis import STATE_REJECTED
from bika.lims.workflow.analysis import STATE_RETRACTED
from datetime import datetime
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.content.base import Container
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridRow
from senaite.core.schema.uidreferencefield import get_backrefs
from six import string_types
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides

RETEST_OF_RELATIONSHIP = "analysis_retest_of"


class IAdditionalValuesRecord(Interface):

    # TODO missing fields key, title, value, choices, result_type, etc.

    id = schema.TextLine(
        title=_(u"label_additional_values_record_id", u"id"),
        required=True,
    )


class IResultRangesRecord(Interface):

    # TODO Missing fields keyword, warn_min, etc.

    min_operator = schema.Choice(
        title=_(u"label_result_ranges_record_min_operator", u"Min operator"),
        vocabulary="senaite.core.vocabularies.operators.LowerThanOperators",
    )

    min_value = schema.TextLine(
        title=_(u"label_result_ranges_record_min", u"Min"),
    )

    max_operator = schema.Choice(
        title=_(u"label_result_ranges_record_max_operator", u"Max operator"),
        vocabulary="senaite.core.vocabularies.operators.GreaterThanOperators",
    )

    max_value = schema.TextLine(
        title=_(u"label_result_ranges_record_max", u"Max"),
    )


class IPythonLibraryRecord(Interface):

    module = schema.TextLine(
        title=_(u"label_python_library_record_module", u"Module")
    )

    func = schema.TextLine(
        title=_(u"label_python_library_record_func", u"Function")
    )


class IAnalysisSchema(model.Schema):
    """Schema interface

    not ported:
        abstractanalysis.Attachment
        abstractanalysis.DetectionLimitOperand
        abstractanalysis.Calculation

    renamings:
        abstractanalysis.ResultCaptureDate -> submitted
        abstractanalysis.Analyst -> submitted_by
        abstractanalysis.InterimFields -> additional_values
        abstractanalysis.ResultsRange -> result_ranges
        abstractanalysis.Formula -> python_expression

    """

    title = schema.TextLine(
        title=u"Title",
        required=True,
    )

    description = schema.Text(
        title=u"Description",
        required=False,
    )

    # AbstractBaseAnalysis
    short_title = schema.TextLine(
        title=_(u"label_analysis_short_title", u"Short title"),
        description=_(
            u"description_analysis_short_title",
            u"Text to be used instead of the title when listed in column"
            u"headings. HTML formatting is allowed"
        ),
    )

    sort_key = schema.Float(
        title=_(u"label_analysis_sort_key", u"Sort key"),
        description=_(
            u"description_analysis_sort_key",
            u"Float value from 0.0 - 1000.0 indicating the sort order. "
            u"Duplicate values are sorted alphabetically"
        )
    )

    keyword = schema.TextLine(
        title=_(u"label_analysis_keyword", u"Keyword"),
    )

    #form.write_permission(result=FieldEditAnalysisHidden)
    hidden = schema.Bool(
        title=_(u"label_analysis_hidden", u"Hidden"),
    )

    # AnstractBaseAnalysis.Price
    price = schema.TextLine(
        title=_(u"label_analysis_price", u"Price (excluding VAT)"),
        default=u"0.00"
    )

    point_of_capture = schema.TextLine(
        default=u"lab",
    )

    self_verification_enabled = schema.Bool(
        default=False,
    )

    # AbstractAnalysis.AnalysisService
    service = UIDReferenceField(
        title=_(u"label_analysis_service", u"Service"),
        description=_(
            u"description_analysis_service",
            u"The service this analysis refers to",
        ),
        allowed_types=("AnalysisService", ),
        multi_valued=False,
        required=True,
    )

    # TODO Remove Calculation field
    calculation = UIDReferenceField(
        allowed_types=("Calculation", ),
        multi_valued=False,
        required=False
    )
    
    # AbstractAnalysis.Result
    #form.read_permission(result=ViewResults)
    #form.write_permission(result=FieldEditAnalysisResult)
    result = schema.TextLine(
        title=_(u"label_analysis_result", u"Result"),
        description=_(
            u"description_analysis_result", u"Result",
            u"The final result of the analysis"
        ),
    )

    # AbstractAnalysis.ResultCaptureDate
    submitted = schema.Datetime(
        title=_(u"label_analysis_submitted", u"Result capture date"),
        description=_(
            u"description_analysis_submitted",
            u"Date and time when the result was submitted"
        ),
    )

    # AbstractAnalysis.Analyst
    submitted_by = schema.TextLine(
        title=_(u"label_analysis_submitted_by", u"Submitted by"),
        description=_(
            u"description_analysis_submitted_by",
            u"The user who submitted the result",
        )
    )

    # AbstractAnalysis.RetestOf
    retest_of = UIDReferenceField(
        title=_(u"label_analysis_retest_of", u"Retest of"),
        description=_(
            u"description_analysis_retest_of",
            u"The source analysis this analysis is a retest of"
        ),
        relationship=RETEST_OF_RELATIONSHIP,
    )

    # AbstractAnalysis.Uncertainty
    uncertainty = schema.TextLine(
        title=_(u"label_analysis_uncertainty", u"Uncertainty"),
        description=_(
            u"description_analysis_uncertainty",
            u"The uncertainty of the result"
        )
    )

    # AbstractAnalysis.Calculation
    number_of_required_verifications = schema.Int(
        title=_(
            u"label_number_of_required_verifications",
            u"Number of required verifications"
        ),
        description=_(
            u"description_number_of_required_verifications",
            u"The number of times the action 'Verify' has to happen before "
            u"the status of the analysis transitions from 'To be verified' to "
            u"'Verified' status"
        ),
        default=1,
    )

    # AbstractAnalysis.InterimFields
    additional_values = schema.List(
        title=_(
            u"label_additional_values", u"Additional values or variables",
        ),
        description=_(
            u"description_additional_values",
            u"Additional values for this analysis. Can either be used as "
            u"complementary data or as variables for the automatic "
            u"calculation of the final result"
        ),
        value_type=DataGridRow(
            title=_(u"label_additional_values_row", u"Additional value"),
            schema=IAdditionalValuesRecord
        ),
    )

    # AbstractAnalysis.ResultsRange
    result_ranges = schema.List(
        title=_(u"label_result_ranges", u"Result ranges"),
        value_type=DataGridRow(
            title=_(u"label_result_ranges_row_title", u"Range"),
            schema=IResultRangesRecord
        )
    )

    python_expression = schema.Text(
        title=_(u"label_analysis_py_expression", u"Calculation expression"),
        description=_(
            u"description_analysis_py_expression",
            u"The python expression to evaluate for the calculation of the "
            u"final result. You can use additional values or results from "
            u"other analyses as input variables by enclose their keywords in "
            u"square brackets. For instance, given two analyses with keywords "
            u"'Ca' and 'Mg', once can use the expression [Ca] + [Mg] to "
            u"calculate the result of an analysis 'Total Hardness'"
        )
    )

    python_imports = schema.List(
        title=_(u"label_analysis_py_imports", u"Additional Python libraries"),
        description=_(
            u"description_analysis_py_imports",
            u"If your expression needs a special function from an external "
            u"Python library, you can import it here. E.g. if you want to use "
            u"the 'floor' function from the Python 'math' module, you add "
            u"'math' to the Module field and 'floor' to the function field. "
            u"The equivalent in Python would be 'from math import floor'. In "
            u"your python expression you could use then 'floor([Ca] + [Mg])'"
        ),
        value_type=DataGridRow(
            title=_(u"label_analysis_py_imports_row_title", u"Python library"),
            schema=IPythonLibraryRecord
        )
    )


@implementer(IBaseAnalysis,
             IAnalysis,
             IRequestAnalysis,
             IRoutineAnalysis,
             IHaveAnalysisCategory,
             IHaveDepartment,
             IHaveInstrument,
             IAnalysisSchema)
class Analysis(Container):

    # Catalogs where this type will be catalogued
    _catalogs = [ANALYSIS_CATALOG]

    security = ClassSecurityInfo()
    exclude_from_nav = True
    portal_type = "Analysis"

    # AbstractBaseAnalysis
    @security.protected(permissions.View)
    def getShortTitle(self):
        accessor = self.accessor("short_title")
        return api.to_utf8(accessor(self), default="")

    @security.protected(permissions.ModifyPortalContent)
    def setShortTitle(self, value):
        mutator = self.mutator("short_title")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getSortKey(self):
        accessor = self.accessor("sort_key")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSortKey(self, value):
        mutator = self.mutator("sort_key")
        mutator(self, value)

    @security.protected(permissions.View)
    def getKeyword(self):
        accessor = self.accessor("keyword")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setKeyword(self, value):
        mutator = self.mutator("keyword")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getHidden(self):
        accessor = self.accessor("hidden")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setHidden(self, value):
        mutator = self.mutator("hidden")
        mutator(self, value)

    @security.protected(permissions.View)
    def getPrice(self):
        accessor = self.accessor("price")
        return api.to_utf8(accessor(self))

    @security.protected(permissions.ModifyPortalContent)
    def setPrice(self, value):
        mutator = self.mutator("price")
        value = api.float_to_string(value)
        mutator(self, api.safe_unicode(value))

    # AbstractAnalysis
    @security.protected(permissions.View)
    def getService(self):
        accessor = self.accessor("service")
        return accessor(self)

    @security.protected(permissions.View)
    def getRawService(self):
        accessor = self.accessor("service", raw=True)
        return accessor(self)

    def getServiceUID(self):
        return self.getRawService()

    @security.protected(permissions.ModifyPortalContent)
    def setService(self, value):
        mutator = self.mutator("service")
        mutator(self, value)
    
    # TODO Remove Calculation field
    @security.protected(permissions.View)
    def getCalculation(self):
        accessor = self.accessor("calculation")
        return accessor(self)

    # TODO Remove Calculation field
    @security.protected(permissions.View)
    def getRawCalculation(self):
        accessor = self.accessor("calculation", raw=True)
        return accessor(self)
    
    # TODO Remove Calculation field
    @security.protected(permissions.View)
    def setCalculation(self, value):
        mutator = self.mutator("calculation")
        mutator(self, value)

    @security.protected(permissions.View)
    def getResult(self):
        accessor = self.accessor("result")
        return api.to_utf8(accessor(self), "")

    @security.protected(permissions.ModifyPortalContent)
    def setResult(self, value):
        mutator = self.mutator("result")
        value = str(value)
        mutator(self, api.safe_unicode(value))
        self.setResultCaptureDate(datetime.now())

    @security.protected(permissions.View)
    def getPointOfCapture(self):
        accessor = self.accessor("point_of_capture")
        return api.to_utf8(accessor(self), "")

    @security.protected(permissions.ModifyPortalContent)
    def setPointOfCapture(self, value):
        mutator = self.mutator("point_of_capture")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getSelfVerificationEnabled(self):
        accessor = self.accessor("self_verification_enabled")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSelfVerificationEnabled(self, value):
        mutator = self.mutator("self_verification_enabled")
        mutator(self, value)
        
    @security.protected(permissions.View)
    def getUncertainty(self):
        accessor = self.accessor("uncertainty")
        return api.to_utf8(accessor(self), "")

    @security.protected(permissions.ModifyPortalContent)
    def setUncertainty(self, value):
        mutator = self.mutator("uncertainty")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getSubmitted(self):
        accessor = self.accessor("submitted")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSubmitted(self, value):
        mutator = self.mutator("submitted")
        mutator(self, value)

    @security.protected(permissions.View)
    def getSubmittedBy(self):
        accessor = self.accessor("submitted_by")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSubmittedBy(self, value):
        # Done in the transition
        return

    @security.protected(permissions.View)
    def getRetestOf(self):
        accessor = self.accessor("retest_of")
        return accessor(self)

    @security.protected(permissions.View)
    def getRawRetestOf(self):
        accessor = self.accessor("retest_of", raw=True)
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setRetestOf(self, value):
        mutator = self.mutator("retest_of")
        mutator(self, value)

    @security.protected(permissions.View)
    def getRetests(self):
        return get_backrefs(self, RETEST_OF_RELATIONSHIP, as_objects=True)

    @security.protected(permissions.View)
    def getRawRetests(self):
        return get_backrefs(self, RETEST_OF_RELATIONSHIP)

    @security.protected(permissions.View)
    def getResultRanges(self):
        accessor = self.accessor("result_ranges")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setResultRanges(self, value):
        mutator = self.mutator("result_ranges")
        mutator(self, value)

    @security.protected(permissions.View)
    def getAdditionalValues(self):
        accessor = self.accessor("additional_values")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAdditionalValues(self, value):
        mutator = self.mutator("additional_values")
        mutator(self, value)

    # AbstractRoutineAnalysis
    @security.protected(permissions.View)
    def getInternalUse(self):
        # TODO Convert to a real field?
        return IInternalUse.providedBy(self)

    @security.protected(permissions.ModifyPortalContent)
    def setInternalUse(self, value):
        # TODO Convert to a real field?
        if value:
            alsoProvides(self, IInternalUse)
        else:
            noLongerProvides(self, IInternalUse)

    @security.protected(permissions.View)
    def getConditions(self, empties=False):
        # TODO Not yet implemented
        return []

    @security.protected(permissions.ModifyPortalContent)
    def setConditions(self, value):
        # TODO Not yet implemented
        pass

    @security.protected(permissions.View)
    def getDateReceived(self):
        request = self.getRequest()
        if request:
            ar_date = request.getDateReceived()
            if ar_date and self.created() > ar_date:
                return self.created()
            return ar_date
        return None

    @security.protected(permissions.View)
    def isSampleReceived(self):
        return self.getDateReceived() and True or False

    # RoutineAnalysis
    def getSample(self):
        return api.get_parent(self)


    def getRequest(self):
        return self.getSample()

    def getRequestID(self):
        sample = self.getSample()
        return sample.getId() if sample else None

    def getRequestUID(self):
        sample = self.getSample()
        return sample.UID() if sample else None

    def getRequestURL(self):
        sample = self.getSample()
        return sample.absolute_url() if sample else None

    def getClient(self):
        sample = self.getSample()
        return sample.getClient() if sample else None

    def getClientID(self):
        client = self.getClient()
        return client.getId() if client else None

    def getClientUID(self):
        client = self.getClient()
        return client.UID() if client else None

    def getClientTitle(self):
        client = self.getClient()
        return client.Title() if client else None

    def getClientURL(self):
        client = self.getClient()
        return client.absolute_url() if client else None

    def getResultCaptureDate(self):
        return self.getSubmitted()

    def setResultCaptureDate(self, value):
        self.setSubmitted(value)

    def getRawRetest(self):
        uids = self.getRawRetests()
        return uids[0] if uids else None

    def getRetest(self):
        uids = self.getRawRetests()
        if not uids:
            return None
        return api.get_object(uids[0], default=None)

    def getResultsRange(self):
        return self.getResultRanges()

    def setResultsRange(self, value):
        self.setResultRanges(value)

    def getAnalysisService(self):
        return self.getService()

    def getRawAnalysisService(self):
        return self.getRawService()

    def setAnalysisService(self, value):
        self.setService(value)

    def getInterimFields(self):
        return self.getAdditionalValues()

    def setInterimFields(self, values):
        return self.setAdditionalValues(values)

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
        interims = copy.deepcopy(self.getAdditionalValues())
        for interim in interims:
            if interim.get("keyword") == keyword:
                interim["value"] = str(value)
        self.setAdditionalValues(interims)

    @security.public
    def getDependents(self, with_retests=False, recursive=False):
        """
        Returns a list of siblings who depend on us to calculate their result.
        :param with_retests: If false, dependents with retests are dismissed
        :param recursive: If true, returns all dependents recursively down
        :type with_retests: bool
        :return: Analyses the current analysis depends on
        :rtype: list of IAnalysis
        """
        def is_dependent(analysis):
            # Never consider myself as dependent
            if analysis.UID() == self.UID():
                return False

            # Never consider analyses from same service as dependents
            self_service_uid = self.getRawAnalysisService()
            if analysis.getRawAnalysisService() == self_service_uid:
                return False

            # Without calculation, no dependency relationship is possible
            calculation = analysis.getCalculation()
            if not calculation:
                return False

            # Calculation must have the service I belong to
            services = calculation.getRawDependentServices()
            return self_service_uid in services

        request = self.getRequest()
        if request.isPartition():
            parent = request.getParentAnalysisRequest()
            siblings = parent.getAnalyses(full_objects=True)
        else:
            siblings = self.getSiblings(with_retests=with_retests)

        dependents = filter(lambda sib: is_dependent(sib), siblings)
        if not recursive:
            return dependents

        # Return all dependents recursively
        deps = dependents
        for dep in dependents:
            down_dependencies = dep.getDependents(with_retests=with_retests,
                                                  recursive=True)
            deps.extend(down_dependencies)
        return deps

    @security.public
    def getDependencies(self, with_retests=False, recursive=False):
        """
        Return a list of siblings who we depend on to calculate our result.
        :param with_retests: If false, siblings with retests are dismissed
        :param recursive: If true, looks for dependencies recursively up
        :type with_retests: bool
        :return: Analyses the current analysis depends on
        :rtype: list of IAnalysis
        """
        calc = self.getCalculation()
        if not calc:
            return []

        # If the calculation this analysis is bound does not have analysis
        # keywords (only interims), no need to go further
        service_uids = calc.getRawDependentServices()

        # Ensure we exclude ourselves
        service_uid = self.getRawAnalysisService()
        service_uids = filter(lambda serv: serv != service_uid, service_uids)
        if len(service_uids) == 0:
            return []

        dependencies = []
        for sibling in self.getSiblings(with_retests=with_retests):
            # We get all analyses that depend on me, also if retracted (maybe
            # I am one of those that are retracted!)
            deps = map(api.get_uid, sibling.getDependents(with_retests=True))
            if self.UID() in deps:
                dependencies.append(sibling)
                if recursive:
                    # Append the dependencies of this dependency
                    up_deps = sibling.getDependencies(with_retests=with_retests,
                                                      recursive=True)
                    dependencies.extend(up_deps)

        # Exclude analyses of same service as me to prevent max recursion depth
        return filter(lambda dep: dep.getRawAnalysisService() != service_uid,
                      dependencies)


    @security.public
    def getSiblings(self, with_retests=False):
        """
        Returns the list of analyses of the Analysis Request to which this
        analysis belongs to, but with the current analysis excluded.
        :param with_retests: If false, siblings with retests are dismissed
        :type with_retests: bool
        :return: list of siblings for this analysis
        :rtype: list of IAnalysis
        """
        request = self.getRequest()
        if not request:
            return []

        siblings = []
        retracted_states = [STATE_RETRACTED, STATE_REJECTED]
        for sibling in request.getAnalyses(full_objects=True):
            if api.get_uid(sibling) == self.UID():
                # Exclude me from the list
                continue

            if not with_retests:
                if api.get_workflow_status_of(sibling) in retracted_states:
                    # Exclude retracted analyses
                    continue
                elif sibling.isRetested():
                    # Exclude analyses with a retest
                    continue

            siblings.append(sibling)

        return siblings

    def isRetested(self):
        """Returns whether this analysis has been retested or not
        """
        if self.getRawRetest():
            return True
        return False

    @security.public
    def getNumberOfVerifications(self):
        return len(self.getVerificators())
    
    def getNumberOfRequiredVerifications(self):
        return 1

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
        for event in api.get_review_history(self):
            if event['action'] in actions:
                verifiers.append(event['actor'])
        sorted(verifiers, reverse=True)
        return verifiers

    def getAttachmentRequired(self):
        return False


    @security.public
    def getWorksheetUID(self):
        """This method is used to populate catalog values
        Returns WS UID if this analysis is assigned to a worksheet, or None.
        """
        uids = get_backrefs(self, relationship="WorksheetAnalysis")
        if not uids:
            return None

        if len(uids) > 1:
            return None

        return uids[0]

    @security.public
    def getWorksheet(self):
        """Returns the Worksheet to which this analysis belongs to, or None
        """
        worksheet_uid = self.getWorksheetUID()
        return api.get_object_by_uid(worksheet_uid, None)

    # Proxy to legacy AT content type
    AnalysisService = property(getAnalysisService, setAnalysisService)
    Calculation = property(getCalculation, setCalculation)
    Keyword = property(getKeyword, setKeyword)
    ShortTitle = property(getShortTitle, setShortTitle)
    SortKey = property(getSortKey, setSortKey)
    Uncertainty = property(getUncertainty, setUncertainty)
    InterimFields = property(getAdditionalValues, setAdditionalValues)
    PointOfCapture = property(getPointOfCapture, setPointOfCapture)
    Analyst = property(getSubmittedBy, setSubmittedBy)
    SelfVerificationEnabled = property(getSelfVerificationEnabled, setSelfVerificationEnabled)
