from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _
import sys

schema = BikaSchema.copy() + Schema((
    TextField('CalculationDescription',
        widget = TextAreaWidget(
            label = 'Calculation description',
            label_msgid = 'label_calculation_description',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    RecordsField('InterimFields',
        # subfield values must be the identical twin of Analysis.InterimFields.
        type = 'InterimFields',
        subfields = ('id', 'title', 'type', 'value', 'unit'),
        subfield_labels = {'id':'Field ID', 'title':'Field Title', 'type':'Type', 'value':'Default', 'unit':'Unit'},
        required_subfields = ('id','name',),
        widget = RecordsWidget(
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
