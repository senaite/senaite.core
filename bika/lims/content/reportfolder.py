# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IHaveNoBreadCrumbs, IReportFolder
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface import implements

schema = ATFolderSchema.copy()

class ReportFolder(ATFolder):
    implements(IReportFolder, IHaveNoBreadCrumbs)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(ReportFolder, PROJECTNAME)
