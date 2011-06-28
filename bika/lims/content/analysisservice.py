from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.widgets import ServicesWidget, RecordsWidget
from bika.lims.config import ATTACHMENT_OPTIONS, I18N_DOMAIN, PROJECTNAME, \
    POINTS_OF_CAPTURE
from bika.lims.content.bikaschema import BikaSchema
import sys

schema = BikaSchema.copy() + Schema((
    TextField('ServiceDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    BooleanField('ReportDryMatter',
        default = False,
        widget = BooleanWidget(
            label = "Report as dry matter",
            label_msgid = "label_report_dry_matter",
            description = "Select if result can be reported as dry matter",
            description_msgid = 'help_report_dry_matter',
        ),
    ),
    StringField('AttachmentOption',
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label = 'Attachment option',
            label_msgid = 'label_attachment_option',
        ),
    ),
    StringField('Unit',
        index = "FieldIndex:brains",
        widget = StringWidget(
            label_msgid = 'label_unit',
        ),
    ),
    IntegerField('Precision',
        widget = IntegerWidget(
            label = "Precision as number of decimals",
            label_msgid = 'label_precision',
            description = 'Define the number of decimals to be used for this result',
            description_msgid = 'help_precision',
        ),
    ),
    FixedPointField('Price',
        index = "FieldIndex:brains",
        default = '0.00',
        widget = DecimalWidget(
            label = 'Price excluding VAT',
            label_msgid = 'label_price_excl_vat',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    FixedPointField('CorporatePrice',
        default = '0.00',
        widget = DecimalWidget(
            label = 'Corporate price excluding VAT',
            label_msgid = 'label_corporate_price_excl_vat',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ComputedField('VATAmount',
        expression = 'context.getVATAmount()',
        widget = ComputedWidget(
            label = 'VAT',
            label_msgid = 'label_vat',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('TotalPrice',
        expression = 'context.getTotalPrice()',
        widget = ComputedWidget(
            label = 'Total price',
            label_msgid = 'label_totalprice',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden', }
        ),
    ),
    FixedPointField('VAT',
        index = 'FieldIndex:brains',
        default_method = 'getDefaultVAT',
        widget = DecimalWidget(
            label = 'VAT %',
            label_msgid = 'label_vat_percentage',
            description = 'Enter percentage value eg. 14',
            description_msgid = 'help_vat_percentage',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('InstrumentKeyword',
        index = 'FieldIndex',
        widget = StringWidget(
            label = 'Instrument Import Keyword',
            label_msgid = 'label_import_keyword',
            description = 'This is the name of the service in the CSV file exported by the analytic instrument',
            description_msgid = 'help_import_keyword',
        ),
    ),
    StringField('AnalysisKey',
        default_method = 'getInstrumentKeyword',
        index = 'FieldIndex',
        widget = StringWidget(
            label = 'Analysis Keyword',
            label_msgid = 'label_analysis_keyword',
            description = 'The analysis identifier',
            description_msgid = 'help_import_keyword',
        ),
    ),
    ReferenceField('Instrument',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Instrument',),
        relationship = 'AnalysisServiceInstrument',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Instrument',
            label_msgid = 'label_instrument',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Calculation',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Calculation',),
        relationship = 'AnalysisServiceCalculation',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Calculation',
            label_msgid = 'label_method',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    IntegerField('MaxHoursAllowed',
        widget = IntegerWidget(
            label = "Maximum Hours Allowed",
            label_msgid = 'label_maximum_hours_allowed',
            description = 'Maximum time allowed for ' \
                        'publication of results',
            description_msgid = 'help_max_hours_allowed',
        ),
    ),
    # XXX TitrationUnit goes into InterimFields?
    StringField('TitrationUnit',
        default = 'ml',
        widget = StringWidget(
            size = 10,
            label = "Titration Volume Unit",
            label_msgid = 'label_titrationunit',
        ),
    ),
    FixedPointField('DuplicateVariation',
        widget = DecimalWidget(
            label = 'Duplicate Variation',
            label_msgid = 'label_duplicate_variation',
            description = 'Enter duplicate variation permitted as percentage',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('PointOfCapture',
        required = 1,
        index = "FieldIndex:brains",
        default = 'lab',
        vocabulary = POINTS_OF_CAPTURE,
        widget = SelectionWidget(
            format = 'flex',
            label = 'Analysis Point of Capture',
            label_msgid = 'label_pointofcapture',
            description = "This decides when analyses are performed.  A sample's field analyses results are entered when an analysis request is created, and lab analyses are captured into existing ARs.",
        ),
    ),
    ReferenceField('Category',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'AnalysisServiceAnalysisCategory',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Analysis category',
            label_msgid = 'label_category',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Department',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Department',),
        relationship = 'AnalysisServiceDepartment',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Department',
            label_msgid = 'label_department',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    BooleanField('Accredited',
        index = "FieldIndex:brains",
        default = False,
        widget = BooleanWidget(
            label = "Accredited",
            label_msgid = "label_accredited"
        ),
    ),
    ComputedField('CategoryName',
        index = 'FieldIndex',
        expression = "context.getCategory() and context.getCategory().Title() or ''",
        widget = ComputedWidget(
            label = "Analysis category",
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('CategoryUID',
        index = 'FieldIndex',
        expression = "context.getCategory() and context.getCategory().UID() or ''",
        widget = ComputedWidget(
            label = "Analysis category",
            visible = {'edit':'hidden', }
        ),
    ),
    RecordsField('Uncertainties',
        type = 'uncertainties',
        subfields = ('intercept_min', 'intercept_max', 'errorvalue'),
        required_subfields = ('intercept_min', 'intercept_max', 'errorvalue'),
        subfield_sizes = {'intercept_min': 10,
                           'intercept_max': 10,
                           'errorvalue': 10,
                           },
        subfield_labels = {'intercept_min': 'Min',
                           'intercept_max': 'Max',
                           'errorvalue': 'Actual value',
                           },
        #widget = RecordsWidget(
        #    label = 'Uncertainties',
        #    label_msgid = 'label_uncertainties',
        #    i18n_domain = I18N_DOMAIN,
        #),
    ),
    RecordsField('ResultOptions',
        type = 'resultsoptions',
        subfields = ('Seq', 'Result',),
        required_subfields = ('Seq', 'Result',),
        subfield_types = {'Seq':'int'},
        subfield_labels = {'Result': 'Option Text'},
        #widget = RecordsWidget(
        #    label = 'Result Options',
        #    label_msgid = 'label_result_options',
        #    i18n_domain = I18N_DOMAIN,
        #),
    ),
))

class AnalysisService(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    security.declarePublic('getResultOptionsSorted')
    def getResultOptionsSorted(self):
        """ return the result options in the correct sequence """
        optionsdict = {}
        resultoptions = self.getResultOptions()
        result = []
        for option in resultoptions:
            optionsdict[option['Seq']] = option['Result']
        keys = optionsdict.keys()
        keys.sort()
        for key in keys:
            result.append(optionsdict[key])
        return result

    security.declarePublic('getDiscountedPrice')
    def getDiscountedPrice(self):
        """ compute discounted price excl. vat """
        price = self.getPrice()
        price = price and price or 0
        discount = self.bika_settings.getMemberDiscount()
        discount = discount and discount or 0
        return float(price) - (float(price) * float(discount)) / 100

    security.declarePublic('getDiscountedCorporatePrice')
    def getDiscountedCorporatePrice(self):
        """ compute discounted corporate price excl. vat """
        price = self.getCorporatePrice()
        price = price and price or 0
        discount = self.bika_settings.getMemberDiscount()
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
        """ return default VAT from bika_settings """
        try:
            vat = self.bika_settings.getVAT()
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

    def getCalcTitle(self):
        """ get title of applicable calculation """
        calctype = self.getCalculation()
        if calctype:
            return calctype.Title()
        else:
            return ''

    def getCalcCode(self):
        """ get title of applicable calculation """
        calctype = self.getCalculationType()
        if calctype:
            return calctype.getCalcTypeCode()
        else:
            return ''

    def getDependancyUIDS(self):
        """ get CalcDependancy, and send back a list of UIDS """
        deps = self.getCalcDependancy()
        return [d.UID() for d in deps]

    def duplicateService(self, context):
        """ Create a copy of the service and return the copy's id """
        dup_id = context.generateUniqueId(type_name = 'AnalysisService')
        context.invokeFactory(id = dup_id, type_name = 'AnalysisService')
        dup = context[dup_id]
        dup.setTitle('! Copy of %s' % self.Title())
        dup.edit(
            ServiceDescription = self.getServiceDescription(),
            Instructions = self.getInstructions(),
            ReportDryMatter = self.getReportDryMatter(),
            Unit = self.getUnit(),
            Precision = self.getPrecision(),
            Price = self.getPrice(),
            CorporatePrice = self.getCorporatePrice(),
            VAT = self.getVAT(),
            InstrumentKeyword = self.getInstrumentKeyword(),
            AnalysisKey = self.getAnalysisKey(),
            CalcDependancy = self.getCalcDependancy(),
            Instrument = self.getInstrument(),
            Method = self.getMethod(),
            MaxHoursAllowed = self.getMaxHoursAllowed(),
            Calculation = self.getCalculation(),
            TitrationUnit = self.getTitrationUnit(),
            DuplicateVariation = self.getDuplicateVariation(),
            AnalysisCategory = self.getAnalysisCategory(),
            Department = self.getDepartment(),
            Accredited = self.getAccredited(),
            Uncertainties = self.getUncertainties(),
            ResultOptions = self.getResultOptions(),
            )
        dup.reindexObject()
        return dup_id

registerType(AnalysisService, PROJECTNAME)
