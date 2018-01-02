# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""PricelistFolder is a container for Pricelist instances.
"""
from AccessControl import ClassSecurityInfo
from bika.lims.interfaces import IPricelistFolder
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
    implements(IPricelistFolder, IHaveNoBreadCrumbs)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(PricelistFolder, PROJECTNAME)
