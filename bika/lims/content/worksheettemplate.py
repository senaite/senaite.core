# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.config import ANALYSIS_TYPES, PROJECTNAME
from bika.lims.content.schema.worksheettemplate import schema


class WorksheetTemplate(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('getAnalysisTypes')

    def getAnalysisTypes(self):
        """ return Analysis type displaylist """
        return ANALYSIS_TYPES

    def getInstruments(self):
        cfilter = {'portal_type': 'Instrument', 'inactive_state': 'active'}
        if self.getRestrictToMethod():
            cfilter['getMethodUIDs'] = {
                "query": self.getRestrictToMethod().UID(),
                "operator": "or"}
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', 'No instrument')] + [
            (o.UID, o.Title) for o in
            bsc(cfilter)]
        o = self.getInstrument()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getMethodUID(self):
        method = self.getRestrictToMethod()
        if method:
            return method.UID()
        return ''

    def _getMethodsVoc(self):
        """
        This function returns the registered methods in the system as a
        vocabulary.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("Not specified")))
        return DisplayList(list(items))


registerType(WorksheetTemplate, PROJECTNAME)
