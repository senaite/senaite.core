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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets.durationwidget import DurationWidget
from bika.lims.browser.widgets.recordswidget import RecordsWidget
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.config import SERVICE_POINT_OF_CAPTURE
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IBaseAnalysis
from bika.lims.interfaces import IHaveDepartment
from bika.lims.interfaces import IHaveInstrument
from senaite.core.interfaces import IHaveAnalysisCategory
from senaite.core.permissions import FieldEditAnalysisHidden
from senaite.core.permissions import FieldEditAnalysisRemarks
from senaite.core.permissions import FieldEditAnalysisResult
from bika.lims.utils import to_utf8 as _c
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.Field import BooleanField
from Products.Archetypes.Field import FixedPointField
from Products.Archetypes.Field import FloatField
from Products.Archetypes.Field import IntegerField
from Products.Archetypes.Field import StringField
from Products.Archetypes.Field import TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import IntDisplayList
from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.Widget import DecimalWidget
from Products.Archetypes.Widget import IntegerWidget
from Products.Archetypes.Widget import SelectionWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFCore.permissions import View
from senaite.core.browser.fields.records import RecordsField
from senaite.core.catalog import SETUP_CATALOG
from zope.interface import implements

# Anywhere that there just isn't space for unpredictably long names,
# this value will be used instead.  It's set on the AnalysisService,
# but accessed on all analysis objects.
ShortTitle = StringField(
    'ShortTitle',
    schemata="Description",
    widget=StringWidget(
        label=_("Short title"),
        description=_(
            "If text is entered here, it is used instead of the title when "
            "the service is listed in column headings. HTML formatting is "
            "allowed.")
    )
)

# A simple integer to sort items.
SortKey = FloatField(
    'SortKey',
    schemata="Description",
    validators=('SortKeyValidator',),
    widget=DecimalWidget(
        label=_("Sort Key"),
        description=_(
            "Float value from 0.0 - 1000.0 indicating the sort order. "
            "Duplicate values are ordered alphabetically."),
    )
)

# Is the title of the analysis a proper Scientific Name?
ScientificName = BooleanField(
    'ScientificName',
    schemata="Description",
    default=False,
    widget=BooleanWidget(
        label=_("Scientific name"),
        description=_(
            "If enabled, the name of the analysis will be written in italics."),
    )
)

# The units of measurement used for representing results in reports and in
# manage_results screen.
Unit = StringField(
    'Unit',
    schemata="Description",
    write_permission=FieldEditAnalysisResult,
    widget=StringWidget(
        label=_(
            u"label_analysis_unit",
            default=u"Default Unit"
        ),
        description=_(
            u"description_analysis_unit",
            default=u"The measurement units for this analysis service' "
                    u"results, e.g. mg/l, ppm, dB, mV, etc."
        ),
    )
)

# A selection of units that are able to update Unit. 
UnitChoices = RecordsField(
    "UnitChoices",
    schemata="Description",
    type="UnitChoices",
    subfields=(
        "value",
    ),
    subfield_labels={
        "value": u"",
    },
    subfield_types={
        "value": "string",
    },
    subfield_sizes={
        "value": 20,
    },
    subfield_maxlength={
        "value": 50,
    },
    widget=RecordsWidget(
        label=_(
            u"label_analysis_unitchoices",
            default=u"Units for Selection"
        ),
        description=_(
            u"description_analysis_unitchoices",
            default=u"Provide a list of units that are suitable for the "
                    u"analysis. Ensure to include the default unit in this "
                    u"list"
        ),
    )
)

# Decimal precision for printing normal decimal results.
Precision = IntegerField(
    'Precision',
    schemata="Analysis",
    widget=IntegerWidget(
        label=_("Precision as number of decimals"),
        description=_(
            "Define the number of decimals to be used for this result."),
    )
)

# If the precision of the results as entered is higher than this value,
# the results will be represented in scientific notation.
ExponentialFormatPrecision = IntegerField(
    'ExponentialFormatPrecision',
    schemata="Analysis",
    required=True,
    default=7,
    widget=IntegerWidget(
        label=_("Exponential format precision"),
        description=_(
            "Define the precision when converting values to exponent "
            "notation.  The default is 7."),
    )
)

# If the value is below this limit, it means that the measurement lacks
# accuracy and this will be shown in manage_results and also on the final
# report.
LowerDetectionLimit = StringField(
    "LowerDetectionLimit",
    schemata="Analysis",
    default="0.0",
    widget=DecimalWidget(
        label=_("Lower Detection Limit (LDL)"),
        description=_(
            "The Lower Detection Limit is the lowest value to which the "
            "measured parameter can be measured using the specified testing "
            "methodology. Results entered which are less than this value will "
            "be reported as < LDL")
    )
)

# If the value is above this limit, it means that the measurement lacks
# accuracy and this will be shown in manage_results and also on the final
# report.
UpperDetectionLimit = StringField(
    "UpperDetectionLimit",
    schemata="Analysis",
    default="1000000000.0",
    widget=DecimalWidget(
        label=_("Upper Detection Limit (UDL)"),
        description=_(
            "The Upper Detection Limit is the highest value to which the "
            "measured parameter can be measured using the specified testing "
            "methodology. Results entered which are greater than this value "
            "will be reported as > UDL")
    )
)

# Allow to select LDL or UDL defaults in results with readonly mode
# Some behavior of AnalysisServices is controlled with javascript: If checked,
# the field "AllowManualDetectionLimit" will be displayed.
# See browser/js/bika.lims.analysisservice.edit.js
#
# Use cases:
# a) If "DetectionLimitSelector" is enabled and
# "AllowManualDetectionLimit" is enabled too, then:
# the analyst will be able to select an '>', '<' operand from the
# selection list and also set the LD manually.
#
# b) If "DetectionLimitSelector" is enabled and
# "AllowManualDetectionLimit" is unchecked, the analyst will be
# able to select an operator from the selection list, but not set
# the LD manually: the default LD will be displayed in the result
# field as usuall, but in read-only mode.
#
# c) If "DetectionLimitSelector" is disabled, no LD selector will be
# displayed in the results table.
DetectionLimitSelector = BooleanField(
    'DetectionLimitSelector',
    schemata="Analysis",
    default=False,
    widget=BooleanWidget(
        label=_("Display a Detection Limit selector"),
        description=_(
            "If checked, a selection list will be displayed next to the "
            "analysis' result field in results entry views. By using this "
            "selector, the analyst will be able to set the value as a "
            "Detection Limit (LDL or UDL) instead of a regular result"),
    )
)

# Behavior of AnalysisService controlled with javascript: Only visible when the
# "DetectionLimitSelector" is checked
# See browser/js/bika.lims.analysisservice.edit.js
# Check inline comment for "DetecionLimitSelector" field for
# further information.
AllowManualDetectionLimit = BooleanField(
    'AllowManualDetectionLimit',
    schemata="Analysis",
    default=False,
    widget=BooleanWidget(
        label=_("Allow Manual Detection Limit input"),
        description=_(
            "Allow the analyst to manually replace the default Detection "
            "Limits (LDL and UDL) on results entry views"),
    )
)

# Specify attachment requirements for these analyses
AttachmentRequired = BooleanField(
    'AttachmentRequired',
    schemata="Analysis",
    default=False,
    widget=BooleanWidget(
        label=_("Attachment required for verification"),
        description=_("Make attachments mandatory for verification")
    ),
)

# The keyword for the service is used as an identifier during instrument
# imports, and other places too.  It's also used as the ID analyses.
Keyword = StringField(
    'Keyword',
    schemata="Description",
    required=1,
    searchable=True,
    validators=('servicekeywordvalidator',),
    widget=StringWidget(
        label=_("Analysis Keyword"),
        description=_(
            "The unique keyword used to identify the analysis service in "
            "import files of bulk Sample requests and results imports from "
            "instruments. It is also used to identify dependent analysis "
            "services in user defined results calculations"),
    )
)

# XXX: HIDDEN -> TO BE REMOVED
ManualEntryOfResults = BooleanField(
    "ManualEntryOfResults",
    schemata="Method",
    default=True,
    widget=BooleanWidget(
        visible=False,
        label=_("Manual entry of results"),
        description=_("Allow to introduce analysis results manually"),
    )
)

# XXX Hidden and always True!
# -> We always allow results from instruments for simplicity!
# TODO: Remove if everywhere refactored (also the getter).
InstrumentEntryOfResults = BooleanField(
    'InstrumentEntryOfResults',
    schemata="Method",
    default=True,
    widget=BooleanWidget(
        visible=False,
        label=_("Instrument assignment is allowed"),
        description=_(
            "Select if the results for tests of this type of analysis can be "
            "set by using an instrument. If disabled, no instruments will be "
            "available for tests of this type of analysis in manage results "
            "view, even though the method selected for the test has "
            "instruments assigned."),
    )
)

Instrument = UIDReferenceField(
    "Instrument",
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
    schemata="Method",
    searchable=True,
    required=0,
    vocabulary="_default_instrument_vocabulary",
    allowed_types=("Instrument",),
    accessor="getInstrumentUID",
    widget=SelectionWidget(
        format="select",
        label=_("Default Instrument"),
        description=_("Default instrument used for analyses of this type"),
    )
)

Method = UIDReferenceField(
    "Method",
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
    schemata="Method",
    required=0,
    allowed_types=("Method",),
    vocabulary="_default_method_vocabulary",
    accessor="getRawMethod",
    widget=SelectionWidget(
        format="select",
        label=_("Default Method"),
        description=_("Default method used for analyses of this type"),
    )
)

# Max. time (from sample reception) allowed for the analysis to be performed.
# After this amount of time, a late alert is printed, and the analysis will be
# flagged in turnaround time report.
MaxTimeAllowed = DurationField(
    'MaxTimeAllowed',
    schemata="Analysis",
    widget=DurationWidget(
        label=_("Maximum turn-around time"),
        description=_(
            "Maximum time allowed for completion of the analysis. A late "
            "analysis alert is raised when this period elapses"),
    )
)

MaxHoldingTime = DurationField(
    'MaxHoldingTime',
    schemata="Analysis",
    widget=DurationWidget(
        label=_(
            u"label_analysis_maxholdingtime",
            default=u"Maximum holding time"
        ),
        description=_(
            u"description_analysis_maxholdingtime",
            default=u"This service will not appear for selection on the "
                    u"sample registration form if the elapsed time since "
                    u"sample collection exceeds the holding time limit. "
                    u"Exceeding this time limit may result in unreliable or "
                    u"compromised data, as the integrity of the sample can "
                    u"degrade over time. Consequently, any results obtained "
                    u"after this period may not accurately reflect the "
                    u"sample's true composition, impacting data validity. "
                    u"Note: This setting does not affect the test's "
                    u"availability in the 'Manage Analyses' view."
        )
    )
)

# The amount of difference allowed between this analysis, and any duplicates.
DuplicateVariation = FixedPointField(
    'DuplicateVariation',
    default='0.00',
    schemata="Analysis",
    widget=DecimalWidget(
        label=_("Duplicate Variation %"),
        description=_(
            "When the results of duplicate analyses on worksheets, carried "
            "out on the same sample, differ with more than this percentage, "
            "an alert is raised"),
    )
)

# True if the accreditation body has approved this lab's method for
# accreditation.
Accredited = BooleanField(
    'Accredited',
    schemata="Description",
    default=False,
    widget=BooleanWidget(
        label=_("Accredited"),
        description=_(
            "Check this box if the analysis service is included in the "
            "laboratory's schedule of accredited analyses"),
    )
)

# The physical location that the analysis is tested; for some analyses,
# the sampler may capture results at the point where the sample is taken,
# and these results can be captured using different rules.  For example,
# the results may be entered before the sample is received.
PointOfCapture = StringField(
    'PointOfCapture',
    schemata="Description",
    required=1,
    default='lab',
    vocabulary=SERVICE_POINT_OF_CAPTURE,
    widget=SelectionWidget(
        format='flex',
        label=_("Point of Capture"),
        description=_(
            "The results of field analyses are captured during sampling at "
            "the sample point, e.g. the temperature of a water sample in the "
            "river where it is sampled. Lab analyses are done in the "
            "laboratory"),
    )
)

# The category of the analysis service, used for filtering, collapsing and
# reporting on analyses.
Category = UIDReferenceField(
    "Category",
    schemata="Description",
    required=1,
    allowed_types=("AnalysisCategory",),
    widget=ReferenceWidget(
        label=_(
            "label_analysis_category",
            default="Analysis Category"),
        description=_(
            "description_analysis_category",
            default="The category the analysis service belongs to"),
        catalog=SETUP_CATALOG,
        query={
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
    )
)

# The base price for this analysis
Price = FixedPointField(
    'Price',
    schemata="Description",
    default='0.00',
    widget=DecimalWidget(
        label=_("Price (excluding VAT)"),
    )
)

# Some clients qualify for bulk discounts.
BulkPrice = FixedPointField(
    'BulkPrice',
    schemata="Description",
    default='0.00',
    widget=DecimalWidget(
        label=_("Bulk price (excluding VAT)"),
        description=_(
            "The price charged per analysis for clients who qualify for bulk "
            "discounts"),
    )
)

# If VAT is charged, a different VAT value can be entered for each
# service.  The default value is taken from BikaSetup
VAT = FixedPointField(
    'VAT',
    schemata="Description",
    default_method='getDefaultVAT',
    widget=DecimalWidget(
        label=_("VAT %"),
        description=_("Enter percentage value eg. 14.0"),
    )
)

# The analysis service's Department.  This is used to filter analyses,
# and for indicating the responsibile lab manager in reports.
Department = UIDReferenceField(
    "Department",
    schemata="Description",
    required=0,
    allowed_types=("Department",),
    widget=ReferenceWidget(
        label=_(
            "label_analysis_department",
            default="Department"),
        description=_(
            "description_analysis_department",
            default="Select the responsible department"),
        catalog=SETUP_CATALOG,
        query={
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        },
        columns=[
            {"name": "Title", "label": _("Department Name")},
            {"name": "getDepartmentID", "label": _("Department ID")},
        ],
    )
)

# Uncertainty percentages in results can change depending on the results
# themselves.
Uncertainties = RecordsField(
    'Uncertainties',
    schemata="Uncertainties",
    type='uncertainties',
    subfields=('intercept_min', 'intercept_max', 'errorvalue'),
    required_subfields=(
        'intercept_min', 'intercept_max', 'errorvalue'),
    subfield_sizes={'intercept_min': 10,
                    'intercept_max': 10,
                    'errorvalue': 10,
                    },
    subfield_labels={'intercept_min': _('Range min'),
                     'intercept_max': _('Range max'),
                     'errorvalue': _('Uncertainty value'),
                     },
    subfield_validators={'intercept_min': 'uncertainties_validator',
                         'intercept_max': 'uncertainties_validator',
                         'errorvalue': 'uncertainties_validator',
                         },
    widget=RecordsWidget(
        label=_("Uncertainty"),
        description=_(
            u"description_analysis_uncertainty",
            default=u"Specify the uncertainty value for a given range, e.g. "
                    u"for results in a range with minimum of 0 and maximum of "
                    u"10, where the uncertainty value is 0.5 - a result of "
                    u"6.67 will be reported as 6.67 ± 0.5.<br/>"
                    u"You can also specify the uncertainty value as a "
                    u"percentage of the result value, by adding a '%' to the "
                    u"value entered in the 'Uncertainty Value' column, e.g. "
                    u"for results in a range with minimum of 10.01 and a "
                    u"maximum of 100, where the uncertainty value is 2%, a "
                    u"result of 100 will be reported as 100 ± 2.<br/>"
                    u"If you don't want uncertainty to be displayed for a "
                    u"given range, set 0 (or a value below 0) as the "
                    u"Uncertainty value.<br/>"
                    u"Please ensure successive ranges are continuous, e.g. "
                    u"0.00 - 10.00 is followed by 10.01 - 20.00, 20.01 - 30.00"
                    u" etc."
        ),
    )
)

# Calculate the precision from Uncertainty value
# Behavior controlled by javascript
# - If checked, Precision and ExponentialFormatPrecision are not displayed.
#   The precision will be calculated according to the uncertainty.
# - If checked, Precision and ExponentialFormatPrecision will be displayed.
# See browser/js/bika.lims.analysisservice.edit.js
PrecisionFromUncertainty = BooleanField(
    'PrecisionFromUncertainty',
    schemata="Uncertainties",
    default=False,
    widget=BooleanWidget(
        label=_("Calculate Precision from Uncertainties"),
        description=_(
            "Precision as the number of significant digits according to the "
            "uncertainty. The decimal position will be given by the first "
            "number different from zero in the uncertainty, at that position "
            "the system will round up the uncertainty and results. For "
            "example, with a result of 5.243 and an uncertainty of 0.22, "
            "the system will display correctly as 5.2+-0.2. If no uncertainty "
            "range is set for the result, the system will use the fixed "
            "precision set."),
    )
)

# If checked, an additional input with the default uncertainty will
# be displayed in the manage results view. The value set by the user
# in this field will override the default uncertainty for the analysis
# result
AllowManualUncertainty = BooleanField(
    'AllowManualUncertainty',
    schemata="Uncertainties",
    default=False,
    widget=BooleanWidget(
        label=_("Allow manual uncertainty value input"),
        description=_(
            "Allow the analyst to manually replace the default uncertainty "
            "value."),
    )
)

RESULT_TYPES = (
    ("numeric", _("Numeric")),
    ("string", _("String")),
    ("text", _("Text")),
    ("select", _("Selection list")),
    ("multiselect", _("Multiple selection")),
    ("multiselect_duplicates", _("Multiple selection (with duplicates)")),
    ("multichoice", _("Multiple choices")),
)

# Type of control to be rendered on results entry
ResultType = StringField(
    "ResultType",
    schemata="Result Options",
    default="numeric",
    vocabulary=DisplayList(RESULT_TYPES),
    widget=SelectionWidget(
        label=_("Result type"),
        format="select",
    )
)

# Results can be selected from a dropdown list.  This prevents the analyst
# from entering arbitrary values.  Each result must have a ResultValue, which
# must be a number - it is this number which is interpreted as the actual
# "Result" when applying calculations.
ResultOptions = RecordsField(
    'ResultOptions',
    schemata="Result Options",
    type='resultsoptions',
    subfields=('ResultValue', 'ResultText'),
    required_subfields=('ResultValue', 'ResultText'),
    subfield_labels={'ResultValue': _('Result Value'),
                     'ResultText': _('Display Value'), },
    subfield_validators={'ResultValue': 'result_options_value_validator',
                         'ResultText': 'result_options_text_validator'},
    subfield_sizes={'ResultValue': 5,
                    'ResultText': 25,},
    subfield_maxlength={'ResultValue': 5,
                        'ResultText': 255,},
    widget=RecordsWidget(
        label=_("Predefined results"),
        description=_(
            "List of possible final results. When set, no custom result is "
            "allowed on results entry and user has to choose from these values"
        ),
    )
)

# TODO Remove ResultOptionsType field. It was Replaced by ResultType
ResultOptionsType = StringField(
    "ResultOptionsType",
    readonly=True,
    widget=StringWidget(
        visible=False,
    )
)

RESULT_OPTIONS_SORTING = (
    ("", _("Keep order above")),
    ("ResultValue-asc", _("By 'Result Value' ascending")),
    ("ResultValue-desc", _("By 'Result Value' descending")),
    ("ResultText-asc", _("By 'Display Value' ascending")),
    ("ResultText-desc", _("By 'Display Value' descending")),
)

ResultOptionsSorting = StringField(
    "ResultOptionsSorting",
    schemata="Result Options",
    default="ResultText-asc",
    vocabulary=DisplayList(RESULT_OPTIONS_SORTING),
    widget=SelectionWidget(
        label=_(
            u"label_analysis_results_options_sorting",
            default=u"Sorting criteria"
        ),
        description=_(
            u"description_analysis_results_options_sorting",
            default=u"Criteria to use when result options are displayed for "
                    u"selection in results entry listings. Note this only "
                    u"applies to the options displayed in the selection list. "
                    u"It does not have any effect to the order in which "
                    u"results are displayed after being submitted"
        ),
    )
)

# Allow/disallow the capture of text as the result of the analysis
# TODO Remove StringResult field. It was Replaced by ResultType
StringResult = BooleanField(
    "StringResult",
    readonly=True,
    widget=BooleanWidget(
        visible=False,
    )
)

# If the service is meant for providing an interim result to another analysis,
# or if the result is only used for internal processes, then it can be hidden
# from the client in the final report (and in manage_results view)
Hidden = BooleanField(
    'Hidden',
    schemata="Analysis",
    default=False,
    read_permission=View,
    write_permission=FieldEditAnalysisHidden,
    widget=BooleanWidget(
        label=_("Hidden"),
        description=_(
            "If enabled, this analysis and its results will not be displayed "
            "by default in reports. This setting can be overrided in Analysis "
            "Profile and/or Sample"),
    )
)

# Permit a user to verify their own results.  This could invalidate the
# accreditation for the results of this analysis!
SelfVerification = IntegerField(
    'SelfVerification',
    schemata="Analysis",
    default=-1,
    vocabulary="_getSelfVerificationVocabulary",
    widget=SelectionWidget(
        label=_("Self-verification of results"),
        description=_(
            "If enabled, a user who submitted a result for this analysis "
            "will also be able to verify it. This setting take effect for "
            "those users with a role assigned that allows them to verify "
            "results (by default, managers, labmanagers and verifiers). "
            "The option set here has priority over the option set in Bika "
            "Setup"),
        format="select",
    )
)

# Require more than one verification by separate Verifier or LabManager users.
NumberOfRequiredVerifications = IntegerField(
    'NumberOfRequiredVerifications',
    schemata="Analysis",
    default=-1,
    vocabulary="_getNumberOfRequiredVerificationsVocabulary",
    widget=SelectionWidget(
        label=_("Number of required verifications"),
        description=_(
            "Number of required verifications from different users with "
            "enough privileges before a given result for this analysis "
            "being considered as 'verified'. The option set here has "
            "priority over the option set in Bika Setup"),
        format="select",
    )
)

# Just a string displayed on various views
CommercialID = StringField(
    'CommercialID',
    searchable=1,
    schemata='Description',
    required=0,
    widget=StringWidget(
        label=_("Commercial ID"),
        description=_("The service's commercial ID for accounting purposes")
    )
)

# Just a string displayed on various views
ProtocolID = StringField(
    'ProtocolID',
    searchable=1,
    schemata='Description',
    required=0,
    widget=StringWidget(
        label=_("Protocol ID"),
        description=_("The service's analytical protocol ID")
    )
)

# Remarks are used in various ways by almost all objects in the system.
Remarks = TextField(
    'Remarks',
    read_permission=View,
    write_permission=FieldEditAnalysisRemarks,
    schemata='Description'
)

schema = BikaSchema.copy() + Schema((
    ShortTitle,
    SortKey,
    CommercialID,
    ProtocolID,
    ScientificName,
    Unit,
    UnitChoices,
    Precision,
    ExponentialFormatPrecision,
    LowerDetectionLimit,
    UpperDetectionLimit,
    DetectionLimitSelector,
    AllowManualDetectionLimit,
    AttachmentRequired,
    Keyword,
    ManualEntryOfResults,
    InstrumentEntryOfResults,
    Instrument,
    Method,
    MaxTimeAllowed,
    MaxHoldingTime,
    DuplicateVariation,
    Accredited,
    PointOfCapture,
    Category,
    Price,
    BulkPrice,
    VAT,
    Department,
    Uncertainties,
    PrecisionFromUncertainty,
    AllowManualUncertainty,
    ResultType,
    ResultOptions,
    ResultOptionsType,
    ResultOptionsSorting,
    Hidden,
    SelfVerification,
    NumberOfRequiredVerifications,
    Remarks,
    StringResult,
))

schema['id'].widget.visible = False
schema['description'].schemata = 'Description'
schema['description'].widget.visible = True
schema['title'].required = True
schema['title'].widget.visible = True
schema['title'].schemata = 'Description'
schema['title'].validators = ()
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()


class AbstractBaseAnalysis(BaseContent):  # TODO BaseContent?  is really needed?
    implements(IBaseAnalysis, IHaveAnalysisCategory, IHaveDepartment, IHaveInstrument)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    @security.public
    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    @security.public
    def Title(self):
        return _c(self.title)

    @security.public
    def getDefaultVAT(self):
        """Return default VAT from bika_setup
        """
        try:
            vat = self.bika_setup.getVAT()
            return vat
        except ValueError:
            return "0.00"

    @security.public
    def getVATAmount(self):
        """Compute VAT Amount from the Price and system configured VAT
        """
        price, vat = self.getPrice(), self.getVAT()
        return float(price) * (float(vat) / 100)

    @security.public
    def getDiscountedPrice(self):
        """Compute discounted price excl. VAT
        """
        price = self.getPrice()
        price = price and price or 0
        discount = self.bika_setup.getMemberDiscount()
        discount = discount and discount or 0
        return float(price) - (float(price) * float(discount)) / 100

    @security.public
    def getDiscountedBulkPrice(self):
        """Compute discounted bulk discount excl. VAT
        """
        price = self.getBulkPrice()
        price = price and price or 0
        discount = self.bika_setup.getMemberDiscount()
        discount = discount and discount or 0
        return float(price) - (float(price) * float(discount)) / 100

    @security.public
    def getTotalPrice(self):
        """Compute total price including VAT
        """
        price = self.getPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    @security.public
    def getTotalBulkPrice(self):
        """Compute total bulk price
        """
        price = self.getBulkPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    @security.public
    def getTotalDiscountedPrice(self):
        """Compute total discounted price
        """
        price = self.getDiscountedPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    @security.public
    def getTotalDiscountedBulkPrice(self):
        """Compute total discounted corporate bulk price
        """
        price = self.getDiscountedCorporatePrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    @security.public
    def getLowerDetectionLimit(self):
        """Get the lower detection limit
        """
        field = self.getField("LowerDetectionLimit")
        value = field.get(self)
        # cut off trailing zeros
        if "." in value:
            value = value.rstrip("0").rstrip(".")
        return value

    @security.public
    def getUpperDetectionLimit(self):
        """Get the upper detection limit
        """
        field = self.getField("UpperDetectionLimit")
        value = field.get(self)
        # cut off trailing zeros
        if "." in value:
            value = value.rstrip("0").rstrip(".")
        return value

    @security.public
    def isSelfVerificationEnabled(self):
        """Returns if the user that submitted a result for this analysis must
        also be able to verify the result
        :returns: true or false
        """
        bsve = self.bika_setup.getSelfVerificationEnabled()
        vs = self.getSelfVerification()
        return bsve if vs == -1 else vs == 1

    @security.public
    def _getSelfVerificationVocabulary(self):
        """Returns a DisplayList with the available options for the
        self-verification list: 'system default', 'true', 'false'
        :returns: DisplayList with the available options for the
        self-verification list
        """
        bsve = self.bika_setup.getSelfVerificationEnabled()
        bsve = _('Yes') if bsve else _('No')
        bsval = "%s (%s)" % (_("System default"), bsve)
        items = [(-1, bsval), (0, _('No')), (1, _('Yes'))]
        return IntDisplayList(list(items))

    @security.public
    def getNumberOfRequiredVerifications(self):
        """Returns the number of required verifications a test for this
        analysis requires before being transitioned to 'verified' state
        :returns: number of required verifications
        """
        num = self.getField('NumberOfRequiredVerifications').get(self)
        if num < 1:
            return self.bika_setup.getNumberOfRequiredVerifications()
        return num

    @security.public
    def _getNumberOfRequiredVerificationsVocabulary(self):
        """Returns a DisplayList with the available options for the
        multi-verification list: 'system default', '1', '2', '3', '4'
        :returns: DisplayList with the available options for the
        multi-verification list
        """
        bsve = self.bika_setup.getNumberOfRequiredVerifications()
        bsval = "%s (%s)" % (_("System default"), str(bsve))
        items = [(-1, bsval), (1, '1'), (2, '2'), (3, '3'), (4, '4')]
        return IntDisplayList(list(items))

    @security.public
    def getMethodTitle(self):
        """This is used to populate catalog values
        """
        method = self.getMethod()
        if method:
            return method.Title()

    @security.public
    def getMethod(self):
        """Returns the assigned method

        :returns: Method object
        """
        return self.getField("Method").get(self)

    def getRawMethod(self):
        """Returns the UID of the assigned method

        NOTE: This is the default accessor of the `Method` schema field
        and needed for the selection widget to render the selected value
        properly in _view_ mode.

        :returns: Method UID
        """
        field = self.getField("Method")
        method = field.getRaw(self)
        if not method:
            return None
        return method

    @security.public
    def getMethodURL(self):
        """This is used to populate catalog values
        """
        method = self.getMethod()
        if method:
            return method.absolute_url_path()

    @security.public
    def getInstrument(self):
        """Returns the assigned instrument

        :returns: Instrument object
        """
        return self.getField("Instrument").get(self)

    def getRawInstrument(self):
        """Returns the UID of the assigned instrument

        :returns: Instrument UID
        """
        return self.getField("Instrument").getRaw(self)

    @security.public
    def getInstrumentUID(self):
        """Returns the UID of the assigned instrument

        NOTE: This is the default accessor of the `Instrument` schema field
        and needed for the selection widget to render the selected value
        properly in _view_ mode.

        :returns: Method UID
        """
        return self.getRawInstrument()

    @security.public
    def getInstrumentURL(self):
        """Used to populate catalog values
        """
        instrument = self.getInstrument()
        if instrument:
            return instrument.absolute_url_path()

    @security.public
    def getCategoryTitle(self):
        """Used to populate catalog values
        """
        category = self.getCategory()
        if category:
            return category.Title()

    @security.public
    def getCategoryUID(self):
        """Used to populate catalog values
        """
        return self.getRawCategory()

    @security.public
    def getMaxTimeAllowed(self):
        """Returns the maximum turnaround time for this analysis. If no TAT is
        set for this particular analysis, it returns the value set at setup
        return: a dictionary with the keys "days", "hours" and "minutes"
        """
        tat = self.Schema().getField("MaxTimeAllowed").get(self)
        return tat or self.bika_setup.getDefaultTurnaroundTime()

    @security.public
    def getMaxHoldingTime(self):
        """Returns the maximum time since it the sample was collected for this
        test/service to become available on sample creation. Returns None if no
        positive maximum hold time is set. Otherwise, returns a dict with the
        keys "days", "hours" and "minutes"
        """
        max_hold_time = self.Schema().getField("MaxHoldingTime").get(self)
        if not max_hold_time:
            return {}
        if api.to_minutes(**max_hold_time) <= 0:
            return {}
        return max_hold_time

    # TODO Remove. ResultOptionsType field was replaced by ResulType field
    def getResultOptionsType(self):
        if self.getStringResult():
            return "select"
        return self.getResultType()

    # TODO Remove. ResultOptionsType field was replaced by ResulType field
    def setResultOptionsType(self, value):
        self.setResultType(value)

    # TODO Remove. StringResults field was replaced by ResulType field
    def getStringResult(self):
        result_type = self.getResultType()
        return result_type in ["string", "text"]

    # TODO Remove. StringResults field was replaced by ResulType field
    def setStringResult(self, value):
        result_type = "string" if bool(value) else "numeric"
        self.setResultType(result_type)
