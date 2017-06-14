# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims import PROJECTNAME
from bika.lims.content.schema.pricelistfolder import schema
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.interfaces import IPricelistFolder
from plone.app.folder import folder
from zope.interface import implements


class PricelistFolder(folder.ATFolder):
    implements(IPricelistFolder, IHaveNoBreadCrumbs)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema


registerType(PricelistFolder, PROJECTNAME)
