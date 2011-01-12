"""StandardSupplierFolder is a container for StandardSupplier instances.

$Id: StandardSupplierFolder.py 621 2007-03-16 22:12:30Z anneline $
"""
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATBTreeFolder, \
    ATBTreeFolderSchema
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import permissions

from Products.bika.config import ManageStandardSuppliers, PROJECTNAME

schema = ATBTreeFolderSchema.copy()
IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
TitleField = schema['title']
TitleField.widget.visible = {'edit':'hidden', 'view': 'invisible'}

class StandardSupplierFolder(UniqueObject, ATBTreeFolder):
    security = ClassSecurityInfo()
    archetype_name = 'StandardSupplierFolder'
    schema = schema
    id = 'StandardSuppliers'
    use_folder_tabs = 0
    allowed_content_types = ('StandardSupplier',)
    default_view = 'standardsupplierfolder_contents'
    global_allow = 0
    filter_content_types = 1

    actions = (
        {'id': 'standardsuppliers',
         'name': 'Suppliers',
         'action': 'string:${object_url}/standardsupplierfolder_contents',
         'permissions': (ManageStandardSuppliers,),
        },
    )
    
registerType(StandardSupplierFolder, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('edit', 'view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
