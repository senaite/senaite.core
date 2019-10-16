# -*- coding: utf-8 -*-
#
# TODO: Remove in senaite.core 1.3.3
#
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IIdentifierTypes
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes.public import registerType
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements


schema = ATFolderSchema.copy()


class IdentifierTypes(ATFolder):
    implements(IIdentifierTypes)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(IdentifierTypes, PROJECTNAME)
