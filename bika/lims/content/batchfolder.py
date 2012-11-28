"""BatchFolder contains AR Batches.
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from AccessControl import ClassSecurityInfo
from bika.lims.interfaces import IBatchFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from zope.interface import implements
from bika.lims import bikaMessageFactory as _

schema = folder.ATFolderSchema.copy()

class BatchFolder(folder.ATFolder):
    implements(IBatchFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()

    def getContacts(self):
        pc = getToolByName(self, 'portal_catalog')
        bc = getToolByName(self, 'bika_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        # fallback - all Lab Contacts
        pairs = []
        for contact in bsc(portal_type = 'LabContact',
                           inactive_state = 'active',
                           sort_on = 'sortable_title'):
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(BatchFolder, PROJECTNAME)
