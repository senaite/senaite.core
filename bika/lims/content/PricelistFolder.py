"""PricelistFolder is a container for Pricelist instances.

$Id: PricelistFolder.py 622 2007-03-17 22:32:34Z anneline $
"""
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATBTreeFolder, \
    ATBTreeFolderSchema
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import permissions

from bika.lims.config import ManagePricelists, PROJECTNAME

schema = ATBTreeFolderSchema.copy()
IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
TitleField = schema['title']
TitleField.widget.visible = {'edit':'hidden', 'view': 'invisible'}

class PricelistFolder(UniqueObject, ATBTreeFolder):
    security = ClassSecurityInfo()
    archetype_name = 'PricelistFolder'
    schema = schema
    id = 'pricelists'
    use_folder_tabs = 0
    allowed_content_types = ('Pricelist',)
    default_view = 'pricelistfolder_pricelists'
    global_allow = 0
    filter_content_types = 1

    security.declareObjectProtected(ManagePricelists)

    actions = (

        {'id': 'pricelists',
         'name': 'Price lists',
         'action': 'string:${object_url}/pricelistfolder_pricelists',
         'permissions': (ManagePricelists,),
        },
    )

registerType(PricelistFolder, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('edit', 'view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
