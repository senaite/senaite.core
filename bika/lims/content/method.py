# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes import DisplayList
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseFolder import BaseFolder
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.method import schema
from bika.lims.interfaces import IMethod
from bika.lims.utils import t
from zope.interface import implements


class Method(BaseFolder):
    implements(IMethod)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def isManualEntryOfResults(self):
        """ Indicates if manual entry of results is allowed.
            If no instrument is selected for this method, returns True.
            Otherwise, returns False by default, but its value can be
            modified using the ManualEntryOfResults Boolean Field
        """
        return len(self.getInstruments()) == 0 or self.getManualEntryOfResults()

    def _getCalculations(self):
        """ Returns a DisplayList with the available Calculations
            registered in Bika-Setup. Used to fill the Calculation
            ReferenceWidget.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        calculations = bsc(portal_type='Calculation', inactive_state='active')
        items = [(c.UID, c.Title) for c in calculations]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', t(_('None'))))
        return DisplayList(list(items))

    def getInstruments(self):
        """ Instruments capable to perform this method
        """
        return self.getBackReferences('InstrumentMethods')

    def getInstrumentUIDs(self):
        """ UIDs of the instruments capable to perform this method
        """
        return [i.UID() for i in self.getInstruments()]

    def getInstrumentsDisplayList(self):
        """ DisplayList containing the Instruments capable to perform
            this method.
        """
        items = [(i.UID(), i.Title()) for i in self.getInstruments()]
        return DisplayList(list(items))

    def _getAvailableInstrumentsDisplayList(self):
        """ Available instruments registered in the system
            Only instruments with state=active will be fetched
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        instruments = bsc(portal_type='Instrument', inactive_state='active')
        items = [(i.UID, i.Title) for i in instruments]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))


registerType(Method, PROJECTNAME)
