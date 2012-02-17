from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.Extensions.utils import makeDisplayList
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.widgets import ServicesWidget, RecordsWidget, DurationWidget
from bika.lims.config import ATTACHMENT_OPTIONS, PROJECTNAME, SERVICE_POINT_OF_CAPTURE
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisService
from magnitude import mg, MagnitudeError
from zope.interface import implements
from zope import i18n
import sys

def getContainers(instance, preservation=None, minvol=None):
    """ Containers vocabulary

    This is a seperate class so that it can be called from ajax to
    filter the container list.

    >>> from bika.lims import bikaMessageFactory as _
    >>> from bika.lims.content.analysisservice import getContainers
    >>> folder = self.portal.bika_setup.bika_analysisservices
    >>> obj = folder.objectValues()[0]
    >>> obj
    <AnalysisService at ...>

    >>> getContainers(obj)

    """
    bsc = getToolByName(instance, 'bika_setup_catalog')
    items = [['','']]
    pres_c_types = preservation and preservation.getContainerType() or None

    containers = {}
    containers_notype = []
    ctype_to_uid = {}
    all_ctypes = [ct.title for ct in bsc(portal_type='ContainerType',
                                         sort_on='sortable_title')]
    for container in bsc(portal_type='Container', sort_on='sortable_title'):
        container = container.getObject()
        if minvol:
            try:
                # If the units match, verify container is large enough.
                # all other containers are considered valid
                cvol = container.getCapacity()
                cvol = cvol.split(" ")
                cvol = mg(float(cvol[0]), " ".join(cvol[1:]).strip())
                if cvol.out_unit == minvol.out_unit and cvol.val < minvol.val:
                    continue
            except MagnitudeError:
                pass

        ctype = container.getContainerType()
        if ctype:
            if ctype.Title() in all_ctypes:
                all_ctypes.remove(ctype.Title())
            if pres_c_types and ctype not in pres_c_types:
                continue
            if ctype.Title() in containers:
                containers[ctype.Title()].append((container.UID(), container.Title()))
            else:
                containers[ctype.Title()] = [(container.UID(), container.Title()),]
                ctype_to_uid[ctype.Title()] = ctype.UID()
        else:
            if not pres_c_types:
                containers_notype.append((container.UID(), container.Title()))

    translate = instance.translation_service.translate
    cat_str = translate(_('Container Type'))

    for ctype in containers.keys():
        items.append([ctype_to_uid[ctype], "%s: %s"%(cat_str, ctype) ])
        for container in containers[ctype]:
            items.append(container)
    # all remaining containers
    for container in containers_notype:
        items.append(list(container))

    items = tuple(items)
    return items

class PartitionSetupField(RecordsField):
    _properties = RecordsField._properties.copy()
    _properties.update({
        'subfields': ('sampletype',
                      'preservation',
                      'container',
                      'seperate',
                      'vol',
                      'retentionperiod'),
        'subfield_labels': {'sampletype':_('Sample Type'),
                            'preservation':_('Preservation'),
                            'container':_('Container'),
                            'seperate':_('Seperate Partition'),
                            'vol':_('Required Volume'),
                            'retentionperiod': _('Retention period')},
        'subfield_types': {'seperate':'boolean',
                           'vol':'int'},
        'subfield_vocabularies': {'sampletype':'SampleTypes',
                                  'preservation':'Preservations',
                                  'container':'Containers'},
        'subfield_sizes': {'vol':5,
                           'retentionperiod':10}
    })
    security = ClassSecurityInfo()

    security.declarePublic('SampleTypes')
    def SampleTypes(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = []
        for st in bsc(portal_type='SampleType',
                      inactive_state='active',
                      sort_on = 'sortable_title'):
            st = st.getObject()
            title = st.Title()
            if st.getUnit():
                title += " %s"%(st.getUnit())
            items.append((st.UID(), title))
        items = [['','']] + list(items)
        return DisplayList(items)

    security.declarePublic('Preservations')
    def Preservations(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = [(c.UID,c.title) for c in \
                 bsc(portal_type='Preservation',
                     inactive_state='active',
                     sort_on = 'sortable_title')]
        items = [['','']] + list(items)
        return DisplayList(items)

    security.declarePublic('ContainerTypes')
    def Containers(self, instance=None):
        instance = instance or self
        return DisplayList(getContainers(instance))

registerField(PartitionSetupField, title = "", description = "")

schema = BikaSchema.copy() + Schema((
    StringField('Unit',
        schemata = PMF("Description"),
        required = 1,
        widget = StringWidget(
            label = _("Unit"),
            description = _("The measurement units for this analysis service' results, "
                            "e.g. mg/l, ppm, dB, mV, etc."),
        ),
    ),
    IntegerField('Precision',
        schemata = PMF("Analysis"),
        widget = IntegerWidget(
            label = _("Precision as number of decimals"),
            description = _("Define the number of decimals to be used for this result"),
        ),
    ),
    BooleanField('ReportDryMatter',
        schemata = PMF("Analysis"),
        default = False,
        widget = BooleanWidget(
            label = _("Report as Dry Matter"),
            description = _("This result can be reported as dry matter"),
        ),
    ),
    StringField('AttachmentOption',
        schemata = PMF("Analysis"),
        default = 'p',
        vocabulary = ATTACHMENT_OPTIONS,
        widget = SelectionWidget(
            label = _("Attachment Option"),
            description = _("Indicates whether file attachments, e.g. microscope images, "
                            "are required for this analysis and whether file upload function "
                            "will be available for it on data capturing screens"),
        ),
    ),
    StringField('Keyword',
        schemata = PMF("Description"),
        required = 1,
        searchable = True,
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
        schemata = PMF("Method"),
        required = 0,
        searchable = True,
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
        schemata = PMF("Method"),
        searchable = True,
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        vocabulary = 'getInstruments',
        allowed_types = ('Instrument',),
        relationship = 'AnalysisServiceInstrument',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Instrument"),
            description = _("Select the preferred instrument"),
        ),
    ),
    ComputedField('InstrumentTitle',
        expression = "context.getInstrument() and context.getInstrument().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    HistoryAwareReferenceField('Calculation',
        schemata = PMF("Method"),
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
        searchable = True,
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
        schemata = PMF("Analysis"),
        widget = DurationWidget(
            label = _("Maximum turn-around time"),
            description = _("Maximum time allowed for completion of the analysis. "
                            "A late analysis alert is raised when this period elapses"),
        ),
    ),
    FixedPointField('DuplicateVariation',
        schemata = PMF("Method"),
        widget = DecimalWidget(
            label = _("Duplicate Variation %"),
            description = _("When the results of duplicate analyses on worksheets, "
                            "carried out on the same sample, differ with more than "
                            "this percentage, an alert is raised"),
        ),
    ),
    BooleanField('Accredited',
        schemata = PMF("Method"),
        default = False,
        widget = BooleanWidget(
            label = _("Accredited"),
            description = _("Check this box if the analysis service is included in the "
                            "laboratory's schedule of accredited analyses"),
        ),
    ),
    StringField('PointOfCapture',
        schemata = PMF("Description"),
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
        schemata = PMF("Description"),
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'AnalysisServiceAnalysisCategory',
        referenceClass = HoldingReference,
        vocabulary = 'getAnalysisCategories',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Analysis Category"),
            description = _("The category the analysis service belongs to"),
        ),
    ),
    FixedPointField('Price',
        schemata = PMF("Description"),
        default = '0.00',
        widget = DecimalWidget(
            label = _("Price (excluding VAT)"),
            ),
        ),
    FixedPointField('CorporatePrice',
        schemata = PMF("Description"),
        default = '0.00',
        widget = DecimalWidget(
            label = _("Bulk price (excluding VAT)"),
            description = _("The price charged per analysis for clients who qualify for bulk discounts"),
                        ),
        ),
    ComputedField('VATAmount',
        schemata = PMF("Description"),
        expression = 'context.getVATAmount()',
        widget = ComputedWidget(
            label = _("VAT"),
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('TotalPrice',
        schemata = PMF("Description"),
        expression = 'context.getTotalPrice()',
        widget = ComputedWidget(
            label = _("Total price"),
            visible = {'edit':'hidden', }
        ),
    ),
    FixedPointField('VAT',
        schemata = PMF("Description"),
        default_method = 'getDefaultVAT',
        widget = DecimalWidget(
            label = _("VAT %"),
            description = _("Enter percentage value eg. 14.0"),
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
        schemata = PMF("Description"),
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Department',),
        vocabulary = 'getDepartments',
        relationship = 'AnalysisServiceDepartment',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Department"),
            description = _("The laboratory department"),
        ),
    ),
    ComputedField('DepartmentTitle',
        expression = "context.getDepartment() and context.getDepartment().Title() or ''",
        searchable = True,
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    RecordsField('Uncertainties',
        schemata = PMF("Uncertainties"),
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
        schemata = PMF("Result Options"),
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
    PartitionSetupField('PartitionSetup',
        schemata = PMF('Partition Setup'),
##        accessor = 'getPartitionSetup',
##        edit_accessor = 'getPartitionSetup',
##        mutator = 'setPartitionSetup',
        widget = RecordsWidget(
            label = "",
            description = _("Select any combination of these fields to configure how "
                            "the LIMS will create sample partitions for new ARs. "
                            "Adding only a few very general rules will cause the empty "
                            "fields to be set to computed, empty or default values. "
                            "This field is ignored if a service calculation is specified."),
        ),
    ),
))

schema['id'].widget.visible = False
schema['description'].schemata = PMF('Description')
schema['description'].widget.visible = True
schema['title'].required = True
schema['title'].widget.visible = True
schema['title'].schemata = PMF('Description')

class AnalysisService(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IAnalysisService)

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        return renameAfterCreation(self)

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
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getMethods(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='Method',
                                   inactive_state = 'active')]
        o = self.getMethod()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getInstruments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='Instrument',
                                   inactive_state = 'active')]
        o = self.getInstrument()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getCalculations(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='Calculation',
                                   inactive_state = 'active')]
        o = self.getCalculation()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getDepartments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in \
                               bsc(portal_type='Department',
                                   inactive_state = 'active')]
        o = self.getDepartment()
        if o and o.UID() not in [i[0] for i in items]:
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

registerType(AnalysisService, PROJECTNAME)
