"""ReferenceDefinition represents a Reference Definition or sample type used for
    quality control testing
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.fields import ReferenceResultField
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
    ReferenceResultField('ReferenceResults',
        required = 1,
##        widget = ReferenceDefinitionEditWidget(
##            label = "Reference Results",
##            label_msgid = "label_reference_results",
##            i18n_domain = I18N_DOMAIN,
##        ),
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
        with_time = 0,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = 'Date created',
            label_msgid = 'label_datecreated',
        ),
    ),
    DateTimeField('ExpiryDate',
        required = 1,
        index = 'DateIndex',
        with_date = 1,
        with_time = 0,
        widget = DateTimeWidget(
            label = 'Expiry date',
            label_msgid = 'label_expirydate',
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
