"""WorksheetFolder is a container for Worksheet instances.

$Id: WorksheetFolder.py 70 2006-07-16 12:46:10Z rochecompaan $
"""
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATBTreeFolder, \
    ATBTreeFolderSchema
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import permissions

from Products.bika.config import ManageWorksheets, PROJECTNAME

schema = ATBTreeFolderSchema.copy()
IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
TitleField = schema['title']
TitleField.widget.visible = {'edit':'hidden', 'view': 'invisible'}


class WorksheetFolder(UniqueObject, ATBTreeFolder):
    security = ClassSecurityInfo()
    archetype_name = 'WorksheetFolder'
    schema = schema
    id = 'Worksheets'
    use_folder_tabs = 0
    allowed_content_types = ('Worksheet',)
    default_view = 'worksheetfolder_worksheets'
    global_allow = 0
    filter_content_types = 1

    security.declareObjectProtected(ManageWorksheets)

    actions = (
        {'id': 'worksheets',
         'name': 'Worksheets',
         'action': 'string:${object_url}/worksheetfolder_worksheets',
         'permissions': (ManageWorksheets,),
        },
    )


registerType(WorksheetFolder, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('edit', 'view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
