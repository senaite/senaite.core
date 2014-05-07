from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import ManageInvoices, PROJECTNAME
from bika.lims.interfaces import IInvoiceFolder, IHaveNoBreadCrumbs
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject
from ZODB.POSException import ConflictError
from zope.interface import implements

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view':'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view':'invisible'}


class InvoiceFolder(folder.ATFolder):
    implements(IInvoiceFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


atapi.registerType(InvoiceFolder, PROJECTNAME)
