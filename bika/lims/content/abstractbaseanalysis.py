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

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.Field import BooleanField
from Products.Archetypes.Field import FixedPointField
from Products.Archetypes.Field import FloatField
from Products.Archetypes.Field import IntegerField
from Products.Archetypes.Field import StringField
from Products.Archetypes.Field import TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.Widget import DecimalWidget
from Products.Archetypes.Widget import IntegerWidget
from Products.Archetypes.Widget import SelectionWidget
from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import IntDisplayList
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets.durationwidget import DurationWidget
from bika.lims.browser.widgets.recordswidget import RecordsWidget
from bika.lims.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import ATTACHMENT_OPTIONS
from bika.lims.config import SERVICE_POINT_OF_CAPTURE
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IBaseAnalysis
from bika.lims.interfaces import IHaveAnalysisCategory
from bika.lims.interfaces import IHaveDepartment
from bika.lims.interfaces import IHaveInstrument
from bika.lims.permissions import FieldEditAnalysisHidden
from bika.lims.permissions import FieldEditAnalysisRemarks
from bika.lims.permissions import FieldEditAnalysisResult
from bika.lims.utils import to_utf8 as _c

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
    widget=StringWidget(
        label=_("Unit"),
        description=_(
            "The measurement units for this analysis service' results, e.g. "
            "mg/l, ppm, dB, mV, etc."),
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
LowerDetectionLimit = FixedPointField(
    'LowerDetectionLimit',
    schemata="Analysis",
    default='0.0',
    precision=7,
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
UpperDetectionLimit = FixedPointField(
    'UpperDetectionLimit',
    schemata="Analysis",
    default='1000000000.0',
    precision=7,
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
AttachmentOption = StringField(
    'AttachmentOption',
    schemata="Analysis",
    default='p',
    vocabulary=ATTACHMENT_OPTIONS,
    widget=SelectionWidget(
        label=_("Attachment Option"),
        description=_(
            "Indicates whether file attachments, e.g. microscope images, "
            "are required for this analysis and whether file upload function "
            "will be available for it on data capturing screens"),
        format='select',
    )
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

# Allow/Disallow manual entry of results
# Behavior of AnalysisServices controlled by javascript depending on
# Instruments field:
# - If InstrumentEntry not checked, set checked and readonly
# - If InstrumentEntry checked, set as not readonly
# See browser/js/bika.lims.analysisservice.edit.js
ManualEntryOfResults = BooleanField(
    'ManualEntryOfResults',
    schemata="Method",
    default=True,
    widget=BooleanWidget(
        label=_("Instrument assignment is not required"),
        description=_(
            "Select if the results for tests of this type of analysis can be "
            "set manually. If selected, the user will be able to set a result "
            "for a test of this type of analysis in manage results view "
            "without the need of selecting an instrument, even though the "
            "method selected for the test has instruments assigned."),
    )
)

# Allow/Disallow instrument entry of results
# Behavior controlled by javascript depending on Instruments field:
# - If no instruments available, hide and uncheck
# - If at least one instrument selected, checked, but not readonly
# See browser/js/bika.lims.analysisservice.edit.js
InstrumentEntryOfResults = BooleanField(
    'InstrumentEntryOfResults',
    schemata="Method",
    default=False,
    widget=BooleanWidget(
        label=_("Instrument assignment is allowed"),
        description=_(
            "Select if the results for tests of this type of analysis can be "
            "set by using an instrument. If disabled, no instruments will be "
            "available for tests of this type of analysis in manage results "
            "view, even though the method selected for the test has "
            "instruments assigned."),
    )
)

# Default instrument to be used.
# Gets populated with the instruments selected in the Instruments field.
# Behavior of AnalysisServices controlled by js depending on
# ManualEntry/Instruments:
# - Populate dynamically with selected Instruments
# - If InstrumentEntry checked, set first selected instrument
# - If InstrumentEntry not checked, hide and set None
# See browser/js/bika.lims.analysisservice.edit.js
Instrument = UIDReferenceField(
    "Instrument",
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
    schemata="Method",
    searchable=True,
    required=0,
    vocabulary="_getAvailableInstrumentsDisplayList",
    allowed_types=("Instrument",),
    accessor="getInstrumentUID",
    widget=SelectionWidget(
        format="select",
        label=_("Default Instrument"),
        description=_(
            "This is the instrument that is assigned to  tests from this type "
            "of analysis in manage results view. The method associated to "
            "this instrument will be assigned as the default method too.Note "
            "the instrument's method will prevail over any of the methods "
            "choosen if the 'Instrument assignment is not required' option is "
            "enabled.")
    )
)

# Default method to be used. This field is used in Analysis Service
# Edit view, use getMethod() to retrieve the Method to be used in
# this Analysis Service.
# Gets populated with the methods selected in the multiselection
# box above or with the default instrument's method.
# Behavior controlled by js depending on ManualEntry/Instrument/Methods:
# - If InstrumentEntry checked, set instrument's default method, and readonly
# - If InstrumentEntry not checked, populate dynamically with
#   selected Methods, set the first method selected and non-readonly
# See browser/js/bika.lims.analysisservice.edit.js
Method = UIDReferenceField(
    "Method",
    read_permission=View,
    write_permission=FieldEditAnalysisResult,
    schemata="Method",
    required=0,
    searchable=True,
    allowed_types=("Method",),
    vocabulary="_getAvailableMethodsDisplayList",
    accessor="getMethodUID",
    widget=SelectionWidget(
        format="select",
        label=_("Default Method"),
        description=_(
            "If 'Allow instrument entry of results' is selected, the method "
            "from the default instrument will be used. Otherwise, only the "
            "methods selected above will be displayed.")
    )
)

# Maximum time (from sample reception) allowed for the analysis to be performed.
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

# The amount of difference allowed between this analysis, and any duplicates.
DuplicateVariation = FixedPointField(
    'DuplicateVariation',
    default='0.00',
    schemata="Method",
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
    schemata="Method",
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
    'Category',
    schemata="Description",
    required=1,
    allowed_types=('AnalysisCategory',),
    vocabulary='getAnalysisCategories',
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Analysis Category"),
        description=_("The category the analysis service belongs to"),
        catalog_name='bika_setup_catalog',
        base_query={'is_active': True},
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
    'Department',
    schemata="Description",
    required=0,
    allowed_types=('Department',),
    widget=ReferenceWidget(
        label=_("Department"),
        description=_("The laboratory department"),
        showOn=True,
        catalog_name=SETUP_CATALOG,
        base_query=dict(
            is_active=True,
            sort_on="sortable_title",
            sort_order="ascending",
        ),
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
            "Specify the uncertainty value for a given range, e.g. for "
            "results in a range with minimum of 0 and maximum of 10, "
            "where the uncertainty value is 0.5 - a result of 6.67 will be "
            "reported as 6.67 +- 0.5. You can also specify the uncertainty "
            "value as a percentage of the result value, by adding a '%' to "
            "the value entered in the 'Uncertainty Value' column, e.g. for "
            "results in a range with minimum of 10.01 and a maximum of 100, "
            "where the uncertainty value is 2% - a result of 100 will be "
            "reported as 100 +- 2. Please ensure successive ranges are "
            "continuous, e.g. 0.00 - 10.00 is followed by 10.01 - 20.00, "
            "20.01 - 30 .00 etc."),
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
        label=_("Result Options"),
        description=_(
            "Please list all options for the analysis result if you want to "
            "restrict it to specific options only, e.g. 'Positive', "
            "'Negative' and 'Indeterminable'.  The option's result value must "
            "be a number"),
    )
)

# Allow/disallow the capture of text as the result of the analysis
StringResult = BooleanField(
    "StringResult",
    schemata="Analysis",
    default=False,
    widget=BooleanWidget(
        label=_("String result"),
        description=_(
            "Enable this option to allow the capture of text as result"
        )
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
    Precision,
    ExponentialFormatPrecision,
    LowerDetectionLimit,
    UpperDetectionLimit,
    DetectionLimitSelector,
    AllowManualDetectionLimit,
    AttachmentOption,
    Keyword,
    ManualEntryOfResults,
    InstrumentEntryOfResults,
    Instrument,
    Method,
    MaxTimeAllowed,
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
    ResultOptions,
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
    def getAnalysisCategories(self):
        """A vocabulary listing available (and activated) categories.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        cats = bsc(portal_type='AnalysisCategory', is_active=True)
        items = [(o.UID, o.Title) for o in cats]
        o = self.getCategory()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    @security.public
    def getLowerDetectionLimit(self):
        """Returns the Lower Detection Limit for this service as a floatable
        """
        ldl = self.getField('LowerDetectionLimit').get(self)
        try:
            return float(ldl)
        except ValueError:
            return 0

    @security.public
    def getUpperDetectionLimit(self):
        """Returns the Upper Detection Limit for this service as a floatable
        """
        udl = self.getField('UpperDetectionLimit').get(self)
        try:
            return float(udl)
        except ValueError:
            return 0

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

    @security.public
    def getMethodUID(self):
        """Returns the UID of the assigned method

        NOTE: This is the default accessor of the `Method` schema field
        and needed for the selection widget to render the selected value
        properly in _view_ mode.

        :returns: Method UID
        """
        method = self.getMethod()
        if not method:
            return None
        return api.get_uid(method)

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

    @security.public
    def getInstrumentUID(self):
        """Returns the UID of the assigned instrument

        NOTE: This is the default accessor of the `Instrument` schema field
        and needed for the selection widget to render the selected value
        properly in _view_ mode.

        :returns: Method UID
        """
        instrument = self.getInstrument()
        if not instrument:
            return None
        return api.get_uid(instrument)

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
        category = self.getCategory()
        if category:
            return category.UID()

    @security.public
    def getMaxTimeAllowed(self):
        """Returns the maximum turnaround time for this analysis. If no TAT is
        set for this particular analysis, it returns the value set at setup
        return: a dictionary with the keys "days", "hours" and "minutes"
        """
        tat = self.Schema().getField("MaxTimeAllowed").get(self)
        return tat or self.bika_setup.getDefaultTurnaroundTime()
