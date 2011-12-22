from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IGenerateUniqueId
from bika.lims.browser.widgets import ServicesWidget, RecordsWidget, \
     DurationWidget
from bika.lims.config import ATTACHMENT_OPTIONS, I18N_DOMAIN, PROJECTNAME, \
    SERVICE_POINT_OF_CAPTURE
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import implements
import sys
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('Unit',
        schemata = _("Analysis"),
        widget = StringWidget(
            label = _("Unit"),
            description = _("The measurement units for this analysis service, e.g. mg/l, ppm, dB, mV, etc."),
        ),
    ),
    IntegerField('Precision',
        schemata = _("Analysis"),
        widget = IntegerWidget(
            label = _("Precision as number of decimals"),
            description = _("Define the number of decimals to be used for this result"),
        ),
    ),
    BooleanField('ReportDryMatter',
        schemata = _("Analysis"),
        default = False,
        widget = BooleanWidget(
            label = _("Report as dry matter"),
            description = _("Select if result can be reported as dry matter"),
        ),
    ),
    StringField('AttachmentOption',
        schemata = _("Analysis"),
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label = _("Attachment option"),
            description = _("Indicates whether file attachments, e.g. microscope images, "
                            "are required for this analysis and whether file upload function "
                            "will be available for it on data capturing screens"),
        ),
    ),
    FixedPointField('Price',
        schemata = _("Price"),
        default = '0.00',
        widget = DecimalWidget(
            label = _("Price (excluding VAT)"),
        ),
    ),
    FixedPointField('CorporatePrice',
        schemata = _("Price"),
        default = '0.00',
        widget = DecimalWidget(
            label = _("Bulk price (excluding VAT)"),
            description = _("The price charged per analysis for clients who qualify for bulk discounts"),
        ),
    ),
    ComputedField('VATAmount',
        schemata = _("Price"),
        expression = 'context.getVATAmount()',
        widget = ComputedWidget(
            label = _("VAT"),
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('TotalPrice',
        schemata = _("Price"),
        expression = 'context.getTotalPrice()',
        widget = ComputedWidget(
            label = _("Total price"),
            visible = {'edit':'hidden', }
        ),
    ),
    FixedPointField('VAT',
        schemata = _("Price"),
        default_method = 'getDefaultVAT',
        widget = DecimalWidget(
            label = _("VAT %"),
            description = _("Enter percentage e.g. 14"),
        ),
    ),
    StringField('Keyword',
        schemata = _("Description"),
        required = 1,
        validators = ('servicekeywordvalidator'),
        widget = StringWidget(
            label = _("Analysis Keyword"),
            description = _("The unique keyword used to identify the analysis service in "
                            "import files of bulk AR requests and results imports from instruments. "
                            "It is also used to identify dependent analysis services in user "
                            "defined results calculations"),
        ),
    ),
    ReferenceField('Method',
        schemata = _("Method"),
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Method',),
        vocabulary = 'getMethods',
        relationship = 'AnalysisServiceMethod',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Method"),
            description = _("Select analysis method"),
        ),
    ),
    ReferenceField('Instrument',
        schemata = _("Method"),
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        vocabulary = 'getInstruments',
        allowed_types = ('Instrument',),
        relationship = 'AnalysisServiceInstrument',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Instrument"),
            description = _("Select the preferred instrument for this analysis"),
        ),
    ),
    ComputedField('InstrumentTitle',
        expression = "context.getInstrument() and context.getInstrument().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    HistoryAwareReferenceField('Calculation',
        schemata = _("Method"),
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        vocabulary = 'getCalculations',
        allowed_types = ('Calculation',),
        relationship = 'AnalysisServiceCalculation',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Calculation"),
            description = _("If required, select a calculation for the analysis here. "
                            "Calculations can be configured under the calculations item "
                            "in the LIMS set-up"),
        ),
    ),
    ComputedField('CalculationTitle',
        expression = "context.getCalculation() and context.getCalculation().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('CalculationUID',
        expression = "context.getCalculation() and context.getCalculation().UID() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    DurationField('MaxTimeAllowed',
        schemata = _("Analysis"),
        widget = DurationWidget(
            label = _("Maximum turn-around time"),
            description = _("Maximum time allowed for completion of the analysis. "
                            "A late analysis alert is raised when this period elapses"),
        ),
    ),
    FixedPointField('DuplicateVariation',
        schemata = _("Method"),
        widget = DecimalWidget(
            label = _("Duplicate Variation %"),
            description = _("When the results of duplicate analyses on worksheets, "
                            "carried out on the same sample, differ with more than "
                            "this percentage, an alert is raised"),
        ),
    ),
    BooleanField('Accredited',
        schemata = _("Method"),
        default = False,
        widget = BooleanWidget(
            label = _("Accredited"),
            description = _("Check this box if the analysis service is included in the "
                            "laboratory's schedule of accredited analyses"),
        ),
    ),
    StringField('PointOfCapture',
        schemata = _("Description"),
        required = 1,
        default = 'lab',
        vocabulary = SERVICE_POINT_OF_CAPTURE,
        widget = SelectionWidget(
            format = 'flex',
            label = _("Point of Capture"),
            description = _("The results of field analyses are captured during sampling "
                            "at the sample point, e.g. the temperature of a water sample "
                            "in the river where it is sampled. Lab analyses are done in "
                            "the laboratory"),
        ),
    ),
    ReferenceField('Category',
        schemata = _("Description"),
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'AnalysisServiceAnalysisCategory',
        referenceClass = HoldingReference,
        vocabulary = 'getAnalysisCategories',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Analysis category"),
            description = _("The category the analysis service belongs to"),
        ),
    ),
    ComputedField('CategoryTitle',
        expression = "context.getCategory() and context.getCategory().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('CategoryUID',
        expression = "context.getCategory() and context.getCategory().UID() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ReferenceField('Department',
        schemata = _("Description"),
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Department',),
        vocabulary = 'getDepartments',
        relationship = 'AnalysisServiceDepartment',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Department"),
            description = _("The lab department responsible for the analysis service"),
        ),
    ),
    ComputedField('DepartmentTitle',
        expression = "context.getDepartment() and context.getDepartment().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    RecordsField('Uncertainties',
        schemata = _("Uncertainties"),
        type = 'uncertainties',
        subfields = ('intercept_min', 'intercept_max', 'errorvalue'),
        required_subfields = ('intercept_min', 'intercept_max', 'errorvalue'),
        subfield_sizes = {'intercept_min': 10,
                           'intercept_max': 10,
                           'errorvalue': 10,
                           },
        subfield_labels = {'intercept_min': _('Range min'),
                           'intercept_max': _('Range max'),
                           'errorvalue': _('Uncertainty value'),
                           },
        widget = RecordsWidget(
            label = _("Uncertainty"),
            description = _("Specify the uncertainty value for a given range, e.g. for results "
                            "in a range with minimum of 0 and maximum of 10, the uncertainty "
                            "value is 0.5 - a result of 6.67 will be reported as 6.67 +- 0.5. "
                            "Please ensure successive ranges are continuous, e.g. 0.00 - 10.00 "
                            "is followed by 10.01 - 20.00, 20.01 - 30 .00 etc."),
        ),
    ),
    RecordsField('ResultOptions',
        schemata = _("Result options"),
        type = 'resultsoptions',
        subfields = ('ResultValue','ResultText'),
        required_subfields = ('ResultValue','ResultText'),
        subfield_labels = {'ResultValue': _('Result Value'),
                           'ResultText': _('Display Value'),},
        subfield_validators = {'ResultValue': 'resultoptionsvalidator'},
        widget = RecordsWidget(
            label = _("Result Options"),
            description = _("Please list all options for the analysis result if you want to restrict "
                            "it to specific options only, e.g. 'Positive', 'Negative' and "
                            "'Indeterminable'.  The option's result value must be a number."),
        ),
    ),
))

schema['id'].widget.visible = False
schema['description'].schemata = 'Description'
schema['description'].widget.visible = True
schema['title'].required = True
schema['title'].widget.visible = True
schema['title'].schemata = 'Description'

class AnalysisService(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IAnalysisService, IGenerateUniqueId)

    security.declarePublic('getDiscountedPrice')
    def getDiscountedPrice(self):
        """ compute discounted price excl. vat """
        price = self.getPrice()
        price = price and price or 0
        discount = self.bika_setup.getMemberDiscount()
        discount = discount and discount or 0
        return float(price) - (float(price) * float(discount)) / 100

    security.declarePublic('getDiscountedCorporatePrice')
    def getDiscountedCorporatePrice(self):
        """ compute discounted corporate price excl. vat """
        price = self.getCorporatePrice()
        price = price and price or 0
        discount = self.bika_setup.getMemberDiscount()
        discount = discount and discount or 0
        return float(price) - (float(price) * float(discount)) / 100

    def getTotalPrice(self):
        """ compute total price """
        price = self.getPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    def getTotalCorporatePrice(self):
        """ compute total price """
        price = self.getCorporatePrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    security.declarePublic('getTotalDiscountedPrice')
    def getTotalDiscountedPrice(self):
        """ compute total discounted price """
        price = self.getDiscountedPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    security.declarePublic('getTotalDiscountedCorporatePrice')
    def getTotalDiscountedCorporatePrice(self):
        """ compute total discounted corporate price """
        price = self.getDiscountedCorporatePrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    def getDefaultVAT(self):
        """ return default VAT from bika_setup """
        try:
            vat = self.bika_setup.getVAT()
            return vat
        except ValueError:
            return "0.00"

    security.declarePublic('getVATAmount')
    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            return "%.2f" % (self.getTotalPrice() - self.getPrice())
        except:
            return "0.00"

    def getAnalysisCategories(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='AnalysisCategory',
                                   inactive_state = 'active')]
        o = self.getCategory()
        if o and (o.UID(), o.Title()) not in items:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getMethods(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='Method',
                                   inactive_state = 'active')]
        o = self.getMethod()
        if o and (o.UID(), o.Title()) not in items:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getInstruments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='Instrument',
                                   inactive_state = 'active')]
        o = self.getInstrument()
        if o and (o.UID(), o.Title()) not in items:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getCalculations(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='Calculation',
                                   inactive_state = 'active')]
        o = self.getCalculation()
        if o and (o.UID(), o.Title()) not in items:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getDepartments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='Department',
                                   inactive_state = 'active')]
        o = self.getDepartment()
        if o and (o.UID(), o.Title()) not in items:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getUncertainty(self, result=None):
        """ Return the uncertainty value, if the result falls within specified
            ranges for this service. """

        if result is None:
            return None

        uncertainties = self.getUncertainties()
        if uncertainties:
            try:
                result = float(result)
            except:
                # if analysis result is not a number, then we assume in range
                return None

            for d in uncertainties:
                if float(d['intercept_min']) <= result <= float(d['intercept_max']):
                    return d['errorvalue']
            return None
        else:
            return None

    def duplicateService(self, context):
        """ Create a copy of the service and return the copy's id """
        dup_id = context.generateUniqueId(type_name = 'AnalysisService')
        context.invokeFactory(id = dup_id, type_name = 'AnalysisService')
        dup = context[dup_id]
        dup.setTitle('! Copy of %s' % self.Title())
        dup.edit(
            description = self.Description(),
            Instructions = self.getInstructions(),
            ReportDryMatter = self.getReportDryMatter(),
            Unit = self.getUnit(),
            Precision = self.getPrecision(),
            Price = self.getPrice(),
            CorporatePrice = self.getCorporatePrice(),
            VAT = self.getVAT(),
            Keyword = self.getKeyword(),
            Instrument = self.getInstrument(),
            Calculation = self.getCalculation(),
            MaxTimeAllowed = self.getMaxTimeAllowed(),
            DuplicateVariation = self.getDuplicateVariation(),
            AnalysisCategory = self.getAnalysisCategory(),
            Department = self.getDepartment(),
            Accredited = self.getAccredited(),
            Uncertainties = self.getUncertainties(),
            ResultOptions = self.getResultOptions(),
            )
        dup.processForm()
        dup.reindexObject()
        return dup_id

registerType(AnalysisService, PROJECTNAME)
