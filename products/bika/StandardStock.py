"""StandardStock represents a standard stock or sample type used for 
    quality control testing
"""
import sys
import time
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.CustomFields import StandardResultField

schema = BikaSchema.copy() + Schema((
    TextField('StandardStockDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StandardResultField('StandardResults',
        required = 1,
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
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = 'Date created',
            label_msgid = 'label_datecreated',
        ),
    ),
    DateTimeField('ExpiryDate',
        required = 1,
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Expiry date',
            label_msgid = 'label_expirydate',
        ),
    ),
))

IdField = schema['id']
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}

class StandardStock(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'StandardStock'
    schema = schema
    allowed_content_types = ()
    immediate_view = 'standardstock_edit'
    default_view = 'standardstock_edit'
    content_icon = 'standardstock.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/standardstock_edit',
        'permissions': (ModifyPortalContent,),
        },
    )

    factory_type_information = {
        'title': 'Standard Stock'
    }  

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    security.declarePublic('getResultsRangeDict')
    def getResultsRangeDict(self): 
        results = {} 
        for spec in self.getStandardResults():
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

registerType(StandardStock, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
