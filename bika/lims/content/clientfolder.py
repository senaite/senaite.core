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

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class ClientFolder(folder.ATFolder):
    implements(IClientFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

    def getContacts(self):
        pc = getToolByName(self, 'portal_catalog')
        bc = getToolByName(self, 'bika_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        client = None
        if self.context.portal_type == 'Client':
            client = self.context
        if self.context.aq_parent.portal_type == 'Client':
            client = self.context.aq_parent
        if client:
            pairs = []
            for contact in client.objectValues('Contact'):
                if isActive(contact):
                    pairs.append((contact.UID(), contact.Title()))
            pairs.sort(lambda x, y:cmp(x[1], y[1]))
            return DisplayList(pairs)
        # fallback - all Lab Contacts
        pairs = []
        for contact in bsc(portal_type = 'LabContact',
                           inactive_state = 'active',
                           sort_on = 'sortable_title'):
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(ClientFolder, PROJECTNAME)
