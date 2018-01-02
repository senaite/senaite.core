# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims import config
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName


schema = BikaSchema.copy() + atapi.Schema((
    # Results File that system wanted to import
    atapi.StringField('ImportedFile', default=''),

    atapi.ReferenceField('Instrument',
                         allowed_types=('Instrument',),
                         referenceClass=HoldingReference,
                         relationship='InstrumentImportLogs',
                         ),

    atapi.StringField('Interface', default=''),

    atapi.StringField('Results', default=''),

    atapi.DateTimeField('LogTime', default=DateTime()),
))

schema['title'].widget.visible = False


class AutoImportLog(BaseContent):
    """
    This object will have some information/log about auto-import process
    once they are done(failed).
    """
    schema = schema

    def getInstrumentUID(self):
        if self.getInstrument():
            return self.getInstrument().UID()
        return None

    def getInstrumentTitle(self):
        if self.getInstrument():
            return self.getInstrument().Title()
        return None

    def getInstrumentUrl(self):
        if self.getInstrument():
            return self.getInstrument().absolute_url_path()
        return None

    def getObjectWorkflowStates(self):
        """
        This method is used as a metacolumn.
        Returns a dictionary with the workflow id as key and workflow state as
        value.
        :returns: {'review_state':'active',...}
        """
        workflow = getToolByName(self, 'portal_workflow')
        states = {}
        for w in workflow.getWorkflowsFor(self):
            state = w._getWorkflowStateOf(self).id
            states[w.state_var] = state
        return states


# Activating the content type in Archetypes' internal types registry
atapi.registerType(AutoImportLog, config.PROJECTNAME)
