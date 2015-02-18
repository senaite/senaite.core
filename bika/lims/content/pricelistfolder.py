"""PricelistFolder is a container for Pricelist instances.
"""
from AccessControl import ClassSecurityInfo
from bika.lims.interfaces import IPricelistFolder, IHaveNoByLine
from plone.app.folder import folder
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims import PROJECTNAME
from Products.Archetypes.public import *
from zope.interface import implements
from bika.lims.interfaces import IHaveNoBreadCrumbs

schema = BikaFolderSchema.copy()
IdField = schema['id']
IdField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}
TitleField = schema['title']
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}


class PricelistFolder(folder.ATFolder):
    implements(IPricelistFolder, IHaveNoBreadCrumbs, IHaveNoByLine)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(PricelistFolder, PROJECTNAME)
