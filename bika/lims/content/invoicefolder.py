# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IInvoiceFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from zope.interface import implements


class InvoiceFolder(folder.ATFolder):
    """REMOVE AFTER 1.3
    """
    implements(IInvoiceFolder)


atapi.registerType(InvoiceFolder, PROJECTNAME)
