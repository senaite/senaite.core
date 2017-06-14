# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes import DisplayList
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseFolder import BaseFolder
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.instrumentvalidation import schema


class InstrumentValidation(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = False

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getLabContacts(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        # fallback - all Lab Contacts
        labcontacts = bsc(portal_type='LabContact',
                          inactive_state='active',
                          sort_on='sortable_title')
        pairs = []
        for contact in labcontacts:
            pairs.append((contact.UID, contact.Title))
        return DisplayList(pairs)


registerType(InstrumentValidation, PROJECTNAME)
