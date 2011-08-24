from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFCore.utils import getToolByName
from Products.validation.ZService import ZService as Service
from Products.validation.interfaces.IValidator import IValidator
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import implements
from zope.site.hooks import getSite
from zExceptions import Redirect
from plone.memoize import instance
import sys,re
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

validation = Service()

schema = BikaSchema.copy() + Schema((
    InterimFieldsField('InterimFields',
        widget = BikaRecordsWidget(
            label = 'Calculation Interim Fields',
            label_msgid = 'label_interim_fields',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ReferenceField('DependentServices',
        required = 0,
        multiValued = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisService',),
        relationship = 'CalculationAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            visible = False,
            label = 'Dependent Analyses',
            label_msgid = 'label_dependent_analyses',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    TextField('Formula',
        validators = ('formulavalidator',),
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = 'Calculation Formula',
            label_msgid = 'label_calculation_description',
            description = 'The formula you type here will be dynamically calculated when an analysis using this calculation is displayed.',
            description_msgid = 'help_vat_percentage',
            i18n_domain = I18N_DOMAIN,
        )
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Calculation(BaseFolder, HistoryAwareMixin):
    security = ClassSecurityInfo()
    schema = schema

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
