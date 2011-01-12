"""CalculationType - the department in the laboratory. 

$Id: CalculationType.py 1000 2007-12-03 11:53:04Z anneline $
"""
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
from Products.bika.config import I18N_DOMAIN, PROJECTNAME


schema = BikaSchema.copy() + Schema((
    TextField('CalculationTypeDescription',
        widget = TextAreaWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('CalcTypeCode',
        widget = StringWidget(
            label = 'Code',
            label_msgid = 'label_code',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))

class CalculationType(VariableSchemaSupport, BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'CalculationType'
    schema = schema
    allowed_content_types = ()
    default_view = 'tool_base_edit'
    immediate_view = 'tool_base_edit'
    content_icon = 'calculation.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/tool_base_edit',
        'permissions': (ModifyPortalContent,),
        },
    )

    factory_type_information = {
        'title': 'Calculation Type'
    }

    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        pairs = []
        for contact in self.portal_catalog(portal_type = 'LabContact'):
            pairs.append((contact.UID, contact.Title))
        # sort the list by the second item
        pairs.sort(lambda x, y:cmp(x[1], y[1]))
        return DisplayList(pairs)

    security.declarePublic('getManagerName')
    def getManagerName(self):
        if self.getManager():
            return self.getManager().getFullname()
        else:
            return ''

registerType(CalculationType, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
