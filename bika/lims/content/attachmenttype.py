# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import registerType

from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IDeactivable

from zope.interface import implements

schema = BikaSchema.copy()

schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class AttachmentType(BaseContent):
    """AttachmentType - the type of attachment
    """
    implements(IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(AttachmentType, PROJECTNAME)
