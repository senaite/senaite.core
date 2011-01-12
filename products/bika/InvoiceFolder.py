"""InvoiceFolder is a container for Invoice instances.

$Id: InvoiceFolder.py 70 2006-07-16 12:46:10Z rochecompaan $
"""
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATBTreeFolder, \
    ATBTreeFolderSchema
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import permissions

from Products.bika.config import ManageInvoices, PROJECTNAME
schema = ATBTreeFolderSchema.copy()

IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
TitleField = schema['title']
TitleField.widget.visible = {'edit':'hidden', 'view': 'invisible'}


class InvoiceFolder(UniqueObject, ATBTreeFolder):
    security = ClassSecurityInfo()
    archetype_name = 'InvoiceFolder'
    schema = schema
    id = 'Invoices'
    use_folder_tabs = 0
    allowed_content_types = ('InvoiceBatch',)
    default_view = 'invoicefolder_invoicebatches'
    global_allow = 0
    filter_content_types = 1

    actions = (
        {'id': 'invoice_batches',
         'name': 'Invoice batches',
         'action': 'string:${object_url}/invoicefolder_invoicebatches',
         'permissions': (ManageInvoices,),
        },
    )


registerType(InvoiceFolder, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('edit', 'view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
