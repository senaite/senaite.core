from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.validation.ZService import ZService as Service
from Products.validation.interfaces.IValidator import IValidator
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import implements
from zope.site.hooks import getSite
import sys,re

validation = Service()

class interim_field_id_validator:
    implements(IValidator)
    name = "interim_field_id_validator"
    title = "Interim Field ID Validator"
    description = "Interim field IDs must not contain whitespace, and may not be the same as an AnalysisService Keyword."
    def __call__(self, value, *args, **kwargs):
        """return True if valid, error string if not"""
        if not value or len(value) == 0:
            return "Interim field IDs may not be blank"
        if re.search(r"\s", value):
            return "Interim field IDs may not contain spaces or tabs"
        pc = getSite().portal_catalog
        service = [s for s in pc(portal_type='AnalysisService') if s.getKeyword == value]
        if service:
            return "Interim field ID '%s' is the same as Analysis Service Keyword from '%s'"%\
                   (value, service[0].Title)
        return True
id_validator = interim_field_id_validator()

class interim_field_title_validator:
    implements(IValidator)
    name = "interim_field_title_validator"
    title = "Interim Field Title Validator"
    description = "Interim field Titles may not be the same as an AnalysisService Keyword."
    def __call__(self, value, *args, **kwargs):
        pc = getSite().portal_catalog
        service = [s for s in pc(portal_type='AnalysisService') if s.getKeyword == value]
        if service:
            return "Interim field ID '%s' is the same as Analysis Service Keyword from '%s'"%\
                   (value, service[0].Title)
        return True
title_validator = interim_field_title_validator()

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
            label = 'Dependent Analyses',
            label_msgid = 'label_dependent_analyses',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    TextField('Formula',
        widget = TextAreaWidget(
            label = 'Calculation Formula',
            label_msgid = 'label_calculation_description',
            description = 'The formula you type here will be dynamically calculated when an analysis using this calculation is displayed.',
            description_msgid = 'help_vat_percentage',
            i18n_domain = I18N_DOMAIN,
        )
    ),
))

class Calculation(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema

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
