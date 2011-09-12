from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.validation.ZService import ZService as Service
from Products.validation.interfaces.IValidator import IValidator
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.interfaces import ICalculation
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import implements
from zope.site.hooks import getSite
from zExceptions import Redirect
from plone.memoize import instance
import sys,re
from bika.lims import bikaMessageFactory as _

validation = Service()

schema = BikaSchema.copy() + Schema((
    InterimFieldsField('InterimFields',
        schemata = 'Calculation',
        widget = BikaRecordsWidget(
            label = _("Calculation Interim Fields"),
            description =_("Define interim fields such as vessel mass, dilution factors, "
                           "should your calculation require them. The field title specified "
                           "here will be used as column headers and field descriptors where"
                           "the interim fields are displayed"),
        )
    ),
    HistoryAwareReferenceField('DependentServices',
        schemata = 'Calculation',
        required = 0,
        multiValued = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'CalculationAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            visible = False,
            label = _("Dependent Analyses"),
        ),
    ),
    TextField('Formula',
        schemata = 'Calculation',
        validators = ('formulavalidator',),
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = _("Calculation Formula"),
            description_msgid = "msg_calculation_formula_help",
            description = "<p>The formula you type here will be dynamically calculated "
                           "when an analysis using this calculation is displayed. </p>"
                           "<p>The <a href='http://docs.python.org/release/2.6.7/library/stdtypes.html#string-formatting'>standard python string interpolation syntax</a> is used, "
                           "with all Analysis Service keywords available as values, as "
                           "well as keywords from this calculation's Interim Fields. "
                           "The calculation is evaluated as an unrestricted python code snippet.</p> "
                           "<p>For example, the calculation '%(SUG)f + %(field1)f' will "
                           "replace %(SUG)f with a floating point value (f) representing "
                           "the 'Sugars' Analysis Service, and '%(field1)f' with the value "
                           "of the service or interim field with the keyword 'field1'.</p>",
            i18n_domain = I18N_DOMAIN,
        )
    ),
))
schema['title'].widget.visible = True
schema['title'].schemata = 'Description'
schema['description'].widget.visible = True
schema['description'].schemata = 'Description'

class Calculation(BaseFolder, HistoryAwareMixin):
    security = ClassSecurityInfo()
    schema = schema
    implements(ICalculation)

    def setFormula(self, Formula=None):
        """Set the Dependent Services from the text of the calculation Formula
        """
        pc = getToolByName(self, 'portal_catalog')
        if Formula is None:
            self.setDependentServices(None)
            self.getField('Formula').set(self, Formula)
        else:
            pc = getToolByName(self, "portal_catalog")
            DependentServices = []
            keywords = re.compile(r"\%\(([^\)]+)\)").findall(Formula)
            for keyword in keywords:
                service = pc(getKeyword = keyword)
                if service:
                    DependentServices.append(service[0].getObject())

            self.getField('DependentServices').set(self, DependentServices)
            self.getField('Formula').set(self, Formula)

    def getCalculationDependencies(self):
        """ Recursively calculates all dependencies of this calculation.
            The return value is dictionary of dictionaries (of dictionaries....)

            {service_UID1:
                {service_UID2:
                    {service_UID3: {},
                     service_UID4: {},
                    },
                },
            }
        """
        deps = {}
        for service in self.getDependentServices():
            try: deps[service.UID()] = service.getCalculation().getCalculationDependencies()
            except AttributeError: deps[service.UID()] = {}
        return deps


registerType(Calculation, PROJECTNAME)
