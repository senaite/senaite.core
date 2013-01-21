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
import json

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit':'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit':'hidden', 'view': 'invisible'}

class ClientFolder(folder.ATFolder):
    implements(IClientFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

    def getContacts(self, dl=True):
        pc = getToolByName(self, 'portal_catalog')
        bc = getToolByName(self, 'bika_catalog')
        bsc = getToolByName(self, 'bika_setup_catalog')
        pairs = []
        objects = []
        for contact in self.objectValues('Contact'):
            if isActive(contact):
                pairs.append((contact.UID(), contact.Title()))
                if not dl:
                    objects.append(contact)
        pairs.sort(lambda x, y:cmp(x[1].lower(), y[1].lower()))
        return dl and DisplayList(pairs) or objects

    def getCCs(self):
        items = []
        for contact in self.getContacts(dl=False):
            item = {'uid': contact.UID(), 'title': contact.Title()}
            ccs = []
            if hasattr(contact, 'getCCContact'):
                for cc in contact.getCCContact():
                    if isActive(cc):
                        ccs.append({'title': cc.Title(),
                                    'uid': cc.UID(),})
            item['ccs_json'] = json.dumps(ccs)
            item['ccs'] = ccs
            items.append(item)
        items.sort(lambda x, y:cmp(x['title'].lower(), y['title'].lower()))
        return items


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(ClientFolder, PROJECTNAME)
