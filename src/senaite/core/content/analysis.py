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
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.content.base import Container
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridRow
from senaite.core.schema.uidreferencefield import get_backrefs
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

    # AbstractBaseAnalysis.ShortTitle
    short_title = schema.TextLine(
        title=_(u"label_analysis_short_title", u"Short title")
    )

    # AbstractBaseAnalysis.Hidden
    #form.write_permission(result=FieldEditAnalysisHidden)
    hidden = schema.Bool(
        title=_(u"label_analysis_hidden", u"Hidden"),
    )

    # AnstractBaseAnalysis.Price
    price = schema.TextLine(
        title=_(u"label_analysis_price", u"Price (excluding VAT)"),
        default=u"0.00"
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

    @security.protected(permissions.ModifyPortalContent)
    def setService(self, value):
        mutator = self.mutator("service")
        mutator(self, value)

    @security.protected(permissions.View)
    def getResult(self):
        accessor = self.accessor("result")
        return api.to_utf8(accessor(self), "")

    @security.protected(permissions.ModifyPortalContent)
    def setResult(self, value):
        mutator = self.mutator("result")
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

    # RoutineAnalysis
    def getSample(self):
        return api.get_parent(self)

    # DEPRECATED
    @deprecated("Use getSample instead")
    def getRequest(self):
        return self.getSample()

    @deprecated("Use getSample().getId() instead")
    def getRequestID(self):
        sample = self.getSample()
        return sample.getId() if sample else None

    @deprecated("Use getSample().UID() instead")
    def getRequestUID(self):
        sample = self.getSample()
        return sample.UID() if sample else None

    @deprecated("Use getRequest().absolute_url() instead")
    def getRequestURL(self):
        sample = self.getSample()
        return sample.absolute_url() if sample else None

    def getClient(self):
        sample = self.getSample()
        return sample.getClient() if sample else None

    @deprecated("Use getClient().getId() instead")
    def getClientID(self):
        client = self.getClient()
        return client.getId() if client else None

    @deprecated("Use getClient().UID() instead")
    def getClientUID(self):
        client = self.getClient()
        return client.UID() if client else None

    @deprecated("Use getClient().Title() instead")
    def getClientTitle(self):
        client = self.getClient()
        return client.Title() if client else None

    @deprecated("Use getClient().getClientURL() instead")
    def getClientURL(self):
        client = self.getClient()
        return client.absolute_url() if client else None

    @deprecated("Use getSubmitted() instead")
    def getResultCaptureDate(self):
        return self.getSubmitted()

    @deprecated("Use setSubmitted(value) instead")
    def setResultCaptureDate(self, value):
        self.setSubmitted(value)

    @deprecated("Use getRawRetests() instead")
    def getRawRetest(self):
        uids = self.getRawRetests()
        return uids[0] if uids else None

    @deprecated("Use getRetests() instead")
    def getRetest(self):
        uids = self.getRawRetests()
        if not uids:
            return None
        return api.get_object(uids[0], default=None)

    @deprecated("Use getResultRanges() instead")
    def getResultsRange(self):
        return self.getResultRanges()

    @deprecated("Use setResultRanges(value) instead")
    def setResultsRange(self, value):
        self.setResultRanges(value)

    # Proxy to legacy AT content type
    @deprecated("Use getService() instead")
    def getAnalysisService(self):
        return self.getService()

    @deprecated("Use setService() instead")
    def setAnalysisService(self, value):
        self.setService(value)

    AnalysisService = property(getAnalysisService, setAnalysisService)
