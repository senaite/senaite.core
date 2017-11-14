# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""PricelistFolder is a container for Pricelist instances.
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.interfaces import IPricelistFolder
from plone.app.folder import folder
from zope.interface import implements

schema = BikaFolderSchema.copy()
IdField = schema['id']
IdField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}
TitleField = schema['title']
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}


class PricelistFolder(folder.ATFolder):
    implements(IPricelistFolder, IHaveNoBreadCrumbs)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(PricelistFolder, PROJECTNAME)
