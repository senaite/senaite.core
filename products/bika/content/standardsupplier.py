"""StandardSupplier. 

$Id: StandardSupplier.py 639 2007-03-20 09:35:32Z anneline $
"""

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from Products.CMFCore.permissions import ListFolderContents, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.config import I18N_DOMAIN, PROJECTNAME, \
    ManageStandardSuppliers
from Products.bika.content.organisation import Organisation

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

schema['AccountNumber'].write_permission = ManageStandardSuppliers

class StandardSupplier(VariableSchemaSupport, BrowserDefaultMixin, Organisation):
    security = ClassSecurityInfo()
    schema = schema

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
