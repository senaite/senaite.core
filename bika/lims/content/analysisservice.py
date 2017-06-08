# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


import transaction
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import DisplayList, registerType
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractbaseanalysis import AbstractBaseAnalysis
from bika.lims.content.schema.analysisservice import schema
from bika.lims.interfaces import IAnalysisService, IHaveIdentifiers
from bika.lims.vocabularies import getContainers
from plone.indexer import indexer
from zope.interface import implements


@indexer(IAnalysisService)
def sortable_title_with_sort_key(instance):
    sort_key = instance.getSortKey()
    if sort_key:
        return "{:010.3f}{}".format(sort_key, instance.Title())
    return instance.Title()


class AnalysisService(AbstractBaseAnalysis):
    implements(IAnalysisService, IHaveIdentifiers)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation

        return renameAfterCreation(self)

    security.declarePublic('getContainers')

    def getContainers(self, instance=None):
        # On first render, the containers must be filtered
        instance = instance or self
        separate = self.getSeparate()
        containers = getContainers(instance,
                                   allow_blank=True,
                                   show_container_types=not separate,
                                   show_containers=separate)
        return DisplayList(containers)

    def getPreservations(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(o.UID, o.Title) for o in
                 bsc(portal_type='Preservation', inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    @security.public
    def getAvailableMethods(self):
        """ Returns the methods available for this analysis.
            If the service has the getInstrumentEntryOfResults(), returns
            the methods available from the instruments capable to perform
            the service, as well as the methods set manually for the
            analysis on its edit view. If getInstrumentEntryOfResults()
            is unset, only the methods assigned manually to that service
            are returned.
        """
        methods = self.getMethods()
        muids = [m.UID() for m in methods]
        if self.getInstrumentEntryOfResults():
            # Add the methods from the instruments capable to perform
            # this analysis service
            for ins in self.getInstruments():
                for method in ins.getMethods():
                    if method and method.UID() not in muids:
                        methods.append(method)
                        muids.append(method.UID())

        return methods

    @security.public
    def getAvailableMethodUIDs(self):
        """
        Returns the UIDs of the available methods. it is used as a
        vocabulary to fill the selection list of 'Methods' field.
        """
        return [m.UID() for m in self.getAvailableMethods()]

    @security.public
    def getMethodUIDs(self):
        """
        Returns the UIDs of the assigned methods to this analysis service.
        This method returns the selected methods in the 'Method' field.
        If you want to obtain the available methods to assign to the service,
        use getAvailableMethodUIDs.
        """
        return [m.UID() for m in self.getMethods()]

    @security.public
    def getAvailableInstruments(self):
        """ Returns the instruments available for this service.
            If the service has the getInstrumentEntryOfResults(), returns
            the instruments capable to perform this service. Otherwhise,
            returns an empty list.
        """
        instruments = self.getInstruments() \
            if self.getInstrumentEntryOfResults() is True \
            else None
        return instruments if instruments else []

    @security.private
    def _getAvailableMethodsDisplayList(self):
        """ Returns a DisplayList with the available Methods
            registered in Bika-Setup. Only active Methods and those
            with Manual Entry field active are fetched.
            Used to fill the Methods MultiSelectionWidget when 'Allow
            Instrument Entry of Results is not selected'.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method',
                              inactive_state='active')
                 if i.getObject().isManualEntryOfResults()]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

    @security.private
    def _getAvailableCalculationsDisplayList(self):
        """ Returns a DisplayList with the available Calculations
            registered in Bika-Setup. Only active Calculations are
            fetched. Used to fill the Calculation field
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Calculation',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

    @security.private
    def _getAvailableInstrumentsDisplayList(self):
        """ Returns a DisplayList with the available Instruments
            registered in Bika-Setup. Only active Instruments are
            fetched. Used to fill the Instruments MultiSelectionWidget
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Instrument',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def workflow_script_activate(self):
        workflow = getToolByName(self, 'portal_workflow')
        pu = getToolByName(self, 'plone_utils')
        # A service cannot be activated if it's calculation is inactive
        calc = self.getCalculation()
        inactive_state = workflow.getInfoFor(calc, "inactive_state")
        if calc and inactive_state == "inactive":
            message = _(
                "This Analysis Service cannot be activated because it's "
                "calculation is inactive.")
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException

    def workflow_scipt_deactivate(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        pu = getToolByName(self, 'plone_utils')
        # A service cannot be deactivated if "active" calculations list it
        # as a dependency.
        active_calcs = bsc(portal_type='Calculation', inactive_state="active")
        calculations = (c.getObject() for c in active_calcs)
        for calc in calculations:
            deps = [dep.UID() for dep in calc.getDependentServices()]
            if self.UID() in deps:
                message = _(
                    "This Analysis Service cannot be deactivated because one "
                    "or more active calculations list it as a dependency")
                pu.addPortalMessage(message, 'error')
                transaction.get().abort()
                raise WorkflowException


registerType(AnalysisService, PROJECTNAME)
