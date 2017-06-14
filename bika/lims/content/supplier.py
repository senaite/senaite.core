# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFPlone.utils import safe_unicode
from bika.lims.config import PROJECTNAME
from bika.lims.content.organisation import Organisation
from bika.lims.content.schema.supplier import schema
from bika.lims.interfaces import ISupplier
from zope.interface import implements


class Supplier(Organisation):
    implements(ISupplier)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def Title(self):
        """ Return the Organisation's Name as its title """
        return safe_unicode(self.getField('Name').get(self)).encode('utf-8')

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Supplier, PROJECTNAME)
