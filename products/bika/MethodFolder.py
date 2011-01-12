"""MethodFolder is a dummy folder for Methods.
   Does not actually contain the Method instances,
   but is used to access them from Nav.

$Id: MethodFolder.py 70 2008-08-20 12:46:10Z godfrey $
"""
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATBTreeFolder, \
    ATBTreeFolderSchema
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import permissions

from Products.bika.config import ViewMethods, PROJECTNAME
schema = ATBTreeFolderSchema.copy()

IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
TitleField = schema['title']
TitleField.widget.visible = {'edit':'hidden', 'view': 'invisible'}


class MethodFolder(UniqueObject, ATBTreeFolder):
    security = ClassSecurityInfo()
    archetype_name = 'MethodFolder'
    schema = schema
    id = 'Methods'
    use_folder_tabs = 0
    allowed_content_types = ()
    default_view = 'methodfolder_contents'
    global_allow = 0
    filter_content_types = 0

    security.declareObjectProtected(ViewMethods)

    actions = (
        {'id': 'methods',
         'name': 'Methods',
         'action': 'string:${object_url}/methodfolder_contents',
         'permissions': (ViewMethods,),
        },
    )


registerType(MethodFolder, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('edit', 'view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
