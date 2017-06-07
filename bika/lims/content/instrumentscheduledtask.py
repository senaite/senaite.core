# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.instrumentscheduledtask import schema


class InstrumentScheduledTask(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getTaskTypes(self):
        """ Return the current list of task types
        """
        types = [
            ('Calibration', safe_unicode(_('Calibration')).encode('utf-8')),
            ('Enhancement', safe_unicode(_('Enhancement')).encode('utf-8')),
            ('Preventive', safe_unicode(_('Preventive')).encode('utf-8')),
            ('Repair', safe_unicode(_('Repair')).encode('utf-8')),
            ('Validation', safe_unicode(_('Validation')).encode('utf-8'))]

        return DisplayList(types)

    def getCriteria(self):
        criteria = ""
        criterias = self.getScheduleCriteria()
        if criterias and len(criterias) > 0:
            crit = criterias[0]
            if crit['fromenabled'] is True and crit['fromdate']:
                criteria += _('From') + " " + crit['fromdate'] + " "
            if crit['repeatenabled'] is True \
                    and crit['repeatunit'] and crit['repeatperiod']:
                criteria += _("repeating every") + " " + crit['repeatunit'] + \
                            " " + _(crit['repeatperiod']) + " "
            if crit['repeatuntilenabled'] is True and crit['repeatuntil']:
                criteria += _("until") + " " + crit['repeatuntil']
        return criteria


atapi.registerType(InstrumentScheduledTask, PROJECTNAME)
