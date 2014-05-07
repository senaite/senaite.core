from bika.lims.utils import isActive
"""ClientFolder is a container for Client instances.
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from AccessControl import ClassSecurityInfo
from bika.lims.interfaces import IClientFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit': 'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit': 'hidden', 'view': 'invisible'}


class ClientFolder(folder.ATFolder):
    implements(IClientFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(ClientFolder, PROJECTNAME)
