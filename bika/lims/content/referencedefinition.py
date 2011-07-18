"""ReferenceDefinition represents a Reference Definition or sample type used for
    quality control testing
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.fields import ReferenceResultsField
from bika.lims.browser.widgets import ReferenceResultsWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
import sys
import time

schema = BikaSchema.copy() + Schema((
    TextField('ReferenceDefinitionDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceResultsField('ReferenceResults',
        required = 1,
        widget = ReferenceResultsWidget(
            label = "Reference Results",
            label_msgid = "label_reference_results",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label = "Hazardous",
            label_msgid = "label_hazardous",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('DateCreated',
        index = 'DateIndex',
        with_date = 1,
        show_hm = False,
        default_method = 'current_date',
        widget = StringWidget(
            label = 'Date created',
            label_msgid = 'label_datecreated',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('ExpiryDate',
        required = 1,
        index = 'DateIndex',
        with_date = 1,
        show_hm = False,
        widget = StringWidget(
            label = 'Expiry date',
            label_msgid = 'label_expirydate',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))

schema['title'].required = False

class ReferenceDefinition(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    security.declarePublic('getResultsRangeDict')
    def getResultsRangeDict(self):
        results = {}
        for spec in self.getReferenceResults():
            uid = spec['service']
            results[uid] = {}
            try:
                results[uid]['result'] = float(spec['result'])
                results[uid]['min'] = '%.3f' % (float(spec['min']))
                results[uid]['max'] = '%.3f' % (float(spec['max']))
            except:
                results[uid]['result'] = ''
                results[uid]['min'] = ''
                results[uid]['max'] = ''

        return results

registerType(ReferenceDefinition, PROJECTNAME)
