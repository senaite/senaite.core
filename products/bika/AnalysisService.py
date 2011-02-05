import sys
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.bika.BikaContent import BikaSchema
from Products.bika.FixedPointField import FixedPointField
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.fixedpoint import FixedPoint
from Products.ATExtensions.ateapi import RecordsField
from Products.bika.config import ATTACHMENT_OPTIONS

class UncertaintiesField(RecordsField):
    """a list of uncertainty values per service"""
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'uncertainties',
        'subfields' : ('intercept_min', 'intercept_max', 'errorvalue'),
        'required_subfields' : ('intercept_min', 'intercept_max', 'errorvalue'),
        'subfield_sizes': {'intercept_min': 10,
                           'intercept_max': 10,
                           'errorvalue': 10,
                           },
        'subfield_labels':{'intercept_min': 'Min',
                           'intercept_max': 'Max',
                           'errorvalue': 'Actual value',
                           },
        })
    security = ClassSecurityInfo()

class ResultOptionsField(RecordsField):
    """an explicit list of possible analysis results per service"""
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'resultsoptions',
        'subfields' : ('Seq', 'Result',),
        'required_subfields' : ('Seq', 'Result',),
        'subfield_types': {'Seq':'int' },
        'subfield_labels':{'Result': 'Option Text' },
        })
    security = ClassSecurityInfo()

schema = BikaSchema.copy() + Schema((
    TextField('ServiceDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    TextField('Instructions',
        widget = TextAreaWidget(
            label = 'Instructions',
            label_msgid = 'label_instructions',
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
        default = 0,
        widget = DecimalWidget(
            label = 'Price excluding VAT',
            label_msgid = 'label_price_excl_vat',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    FixedPointField('CorporatePrice',
        default = 0,
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
    ReferenceField('CalcDependancy',
        required = 0,
        multiValued = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'AnalysisServiceAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Dependant Analyses',
            label_msgid = 'label_dependants',
            i18n_domain = I18N_DOMAIN,
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
    ReferenceField('Method',
        required = 0,
        multiValued = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Method',),
        relationship = 'AnalysisServiceMethod',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Method',
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
    ReferenceField('CalculationType',
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('CalculationType',),
        relationship = 'AnalysisServiceCalculationType',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'CalculationType',
            label_msgid = 'label_calculationtype',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
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
    ReferenceField('AnalysisCategory',
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
        default = False,
        widget = BooleanWidget(
            label = "Accredited",
            label_msgid = "label_accredited"
        ),
    ),
    ComputedField('CalcName',
        expression = 'context.getCalcTitle()',
        widget = ComputedWidget(
            label = "Calc",
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('CalcType',
        index = 'FieldIndex',
        expression = 'context.getCalcCode()',
        widget = ComputedWidget(
            label = "Calc code",
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('CategoryName',
        index = 'FieldIndex',
        expression = 'context.getAnalysisCategory().Title()',
        widget = ComputedWidget(
            label = "Analysis category",
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('CategoryUID',
        index = 'FieldIndex',
        expression = 'context.getAnalysisCategory().UID()',
        widget = ComputedWidget(
            label = "Analysis category",
            visible = {'edit':'hidden', }
        ),
    ),
    UncertaintiesField('Uncertainties'),
    ResultOptionsField('ResultOptions'),
))

class AnalysisService(VariableSchemaSupport, BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'AnalysisService'
    schema = schema
    allowed_content_types = ()
    default_view = 'analysisservice_edit'
    immediate_view = 'analysisservice_edit'
    content_icon = 'service.png'

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/analysisservice_edit',
        'permissions': (ModifyPortalContent,),
        },
    )

    factory_type_information = {
        'title': 'Analysis service'
    }

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
        discount = self.bika_settings.settings.getMemberDiscount()
        discount = discount and discount or 0
        return price - (price * discount) / 100

    security.declarePublic('getDiscountedCorporatePrice')
    def getDiscountedCorporatePrice(self):
        """ compute discounted corporate price excl. vat """
        price = self.getCorporatePrice()
        price = price and price or 0
        discount = self.bika_settings.settings.getMemberDiscount()
        discount = discount and discount or 0
        return price - (price * discount) / 100

    def getTotalPrice(self):
        """ compute total price """
        price = self.getPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return price + (price * vat) / 100

    def getTotalCorporatePrice(self):
        """ compute total price """
        price = self.getCorporatePrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return price + (price * vat) / 100

    security.declarePublic('getTotalDiscountedPrice')
    def getTotalDiscountedPrice(self):
        """ compute total discounted price """
        price = self.getDiscountedPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return price + (price * vat) / 100

    security.declarePublic('getTotalDiscountedCorporatePrice')
    def getTotalDiscountedCorporatePrice(self):
        """ compute total discounted corporate price """
        price = self.getDiscountedCorporatePrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return price + (price * vat) / 100

    def getDefaultVAT(self):
        """ return default VAT from bika_settings """
        try:
            vat = self.bika_settings.settings.getVAT()
            return FixedPoint(vat)
        except ValueError:
            return FixedPoint('0')

    security.declarePublic('getVATAmount')
    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            return self.getTotalPrice() - self.getPrice()
        except:
            return 0

    def getCalcTitle(self):
        """ get title of applicable calculation """
        calctype = self.getCalculationType()
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
            CalculationType = self.getCalculationType(),
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

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
