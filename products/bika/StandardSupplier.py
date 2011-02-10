"""StandardSupplier - the main organisational entity in bika. 

$Id: StandardSupplier.py 639 2007-03-20 09:35:32Z anneline $
"""
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent
from Products.CMFCore import permissions
from Products.Archetypes.public import *
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.utils import DisplayList
from Products.bika.Organisation import Organisation
from Products.bika.config import ManageStandardSuppliers, ManageStandard
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.bika.config import I18N_DOMAIN, PROJECTNAME

schema = Organisation.schema.copy() + Schema((
        StringField('StandardSupplierID',
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'StandardSupplier ID',
            label_msgid = 'label_standardsupplierid',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))
for field_id in ('Name', 'EmailAddress', 'Phone', 'Fax'):
    schema[field_id].index = 'FieldIndex:brains'

AccountNumber = schema['AccountNumber']
AccountNumber.write_permission = ManageStandardSuppliers

IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
TitleField = schema['title']

class StandardSupplier(VariableSchemaSupport, BrowserDefaultMixin, Organisation):
    security = ClassSecurityInfo()
    archetype_name = 'StandardSupplier'
    schema = schema
    content_icon = 'standardsupplier.png'
    allowed_content_types = ('StandardSample', 'SupplierContact')
    immediate_view = 'base_edit'
    default_view = 'standardsupplier_standardsamples'
    use_folder_tabs = 0
    global_allow = 0
    filter_content_types = 1

    actions = (
        # Make view action the same as edit
        {'id': 'view',
         'name': 'View',
         'action': 'string:${object_url}/base_edit',
         'permissions': (ModifyPortalContent,),
        },
        {'id': 'contacts',
         'name': 'Contacts',
         'action': 'string:${object_url}/standardsupplier_suppliercontacts',
         'permissions': (ListFolderContents,),
        },
        {'id': 'standards',
         'name': 'Standards',
         'action': 'string:${object_url}/standardsupplier_standardsamples',
         'permissions': (ListFolderContents,),
        },
    )

    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        pairs = []
        for contact in self.objectValues('SupplierContact'):
            pairs.append((contact.UID(), contact.Title()))
        return DisplayList(pairs)

    security.declarePublic('getStandardStockDisplayList')
    def getStandardStockDisplayList(self):
        """ return all standard stocks """
        stocks = []
        for st in self.portal_catalog(portal_type = 'StandardStock',
                                      sort_on = 'sortable_title'):
           stocks.append((st.UID, st.Title))
        return DisplayList(stocks)

registerType(StandardSupplier, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
