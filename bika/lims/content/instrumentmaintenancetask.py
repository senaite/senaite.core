# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import atapi, DisplayList
from Products.Archetypes.BaseFolder import BaseFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.instrumentmaintenancetask import schema


class InstrumentMaintenanceTaskStatuses:
    def __init__(self):
        pass

    CLOSED = 'Closed'
    CANCELLED = 'Cancelled'
    OVERDUE = "Overdue"
    PENDING = "Pending"
    INQUEUE = "In queue"


class InstrumentMaintenanceTask(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getMaintenanceTypes(self):
        """ Return the current list of maintenance types
        """
        types = [('Preventive', safe_unicode(_('Preventive')).encode('utf-8')),
                 ('Repair', safe_unicode(_('Repair')).encode('utf-8')),
                 (
                     'Enhancement',
                     safe_unicode(_('Enhancement')).encode('utf-8'))]
        return DisplayList(types)

    def getCurrentStateI18n(self):
        return safe_unicode(_(self.getCurrentState()).encode('utf-8'))

    def getCurrentState(self):
        workflow = getToolByName(self, 'portal_workflow')
        if self.getClosed():
            return InstrumentMaintenanceTaskStatuses.CLOSED
        elif workflow.getInfoFor(self, 'cancellation_state', '') == 'cancelled':
            return InstrumentMaintenanceTaskStatuses.CANCELLED
        else:
            now = DateTime()
            dfrom = self.getDownFrom()
            dto = self.getDownTo() and self.getDownTo() or DateTime(9999, 12,
                                                                    31)
            if now > dto:
                return InstrumentMaintenanceTaskStatuses.OVERDUE
            if now >= dfrom:
                return InstrumentMaintenanceTaskStatuses.PENDING
            else:
                return InstrumentMaintenanceTaskStatuses.INQUEUE


atapi.registerType(InstrumentMaintenanceTask, PROJECTNAME)
