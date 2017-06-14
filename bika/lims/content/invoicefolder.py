# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import folder
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.invoicefolder import schema
from bika.lims.interfaces import IHaveNoBreadCrumbs, IInvoiceFolder
from zope.interface import implements


class InvoiceFolder(folder.ATFolder):
    implements(IInvoiceFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


registerType(InvoiceFolder, PROJECTNAME)
