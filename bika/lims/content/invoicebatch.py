# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IInvoiceBatch
from Products.Archetypes.public import registerType
from Products.Archetypes.public import BaseFolder
from zope.interface import implements


class InvoiceBatch(BaseFolder):
    """REMOVE AFTER 1.3
    """
    implements(IInvoiceBatch)


registerType(InvoiceBatch, PROJECTNAME)
