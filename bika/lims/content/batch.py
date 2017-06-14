# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes import DisplayList
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.batch import schema
from bika.lims.interfaces import IBatch, IClient
from bika.lims.workflow import BatchState, CancellationState, StateFlow, \
    getCurrentState
from plone.app.folder.folder import ATFolder
from plone.indexer import indexer
from zope.interface import implements


class Batch(ATFolder):
    implements(IBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Batch ID if title is not defined """
        titlefield = self.Schema().getField('title')
        if titlefield.widget.visible:
            return safe_unicode(self.title).encode('utf-8')
        else:
            return safe_unicode(self.id).encode('utf-8')

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def getClient(self):
        """ Retrieves the Client for which the current Batch is attached to
            Tries to retrieve the Client from the Schema property, but if not
            found, searches for linked ARs and retrieve the Client from the
            first one. If the Batch has no client, returns None.
        """
        client = self.Schema().getField('Client').get(self)
        if client:
            return client
        client = self.aq_parent
        if IClient.providedBy(client):
            return client

    def getClientTitle(self):
        client = self.getClient()
        if client:
            return client.Title()
        return ""

    def getContactTitle(self):
        return ""

    def getProfilesTitle(self):
        return ""

    def getAnalysisService(self):
        analyses = set()
        for ar in self.getAnalysisRequests():
            for an in ar.getAnalyses():
                analyses.add(an)
        value = []
        for analysis in analyses:
            val = analysis.Title
            if val not in value:
                value.append(val)
        return list(value)

    def getAnalysts(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    security.declarePublic('getBatchID')

    def getBatchID(self):
        return self.getId()

    def BatchLabelVocabulary(self):
        """ return all batch labels """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type='BatchLabel',
                     inactive_state='active',
                     sort_on='sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

    def getAnalysisRequestsBrains(self, **kwargs):
        """ Return all the Analysis Requests brains linked to the Batch
        kargs are passed directly to the catalog.
        """
        kwargs['getBatchUID'] = self.UID()
        catalog = getToolByName(self, CATALOG_ANALYSIS_REQUEST_LISTING)
        brains = catalog(kwargs)
        return brains

    def getAnalysisRequests(self, **kwargs):
        """ Return all the Analysis Requests objects linked to the Batch
        kargs are passed directly to the catalog.
        """
        brains = self.getAnalysisRequestsBrains(**kwargs)
        return [b.getObject() for b in brains]

    def isOpen(self):
        """ Returns true if the Batch is in 'open' state
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        if revstatus == BatchState.open \
                and canstatus == CancellationState.active:
            return True

    def getLabelNames(self):
        uc = getToolByName(self, 'uid_catalog')
        uids = [uid for uid in self.Schema().getField('BatchLabels').get(self)]
        labels = [label.getObject().title for label in uc(UID=uids)]
        return labels

    def workflow_guard_open(self):
        """ Permitted if current review_state is 'closed' or 'cancelled'
            The open transition is already controlled by 'Bika: Reopen Batch'
            permission, but left here for security reasons and also for the
            capability of being expanded/overrided by child products or
            instance-specific-needs.
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        if revstatus == BatchState.closed \
                and canstatus == CancellationState.active:
            return True

    def workflow_guard_close(self):
        """ Permitted if current review_state is 'open'.
            The close transition is already controlled by 'Bika: Close Batch'
            permission, but left here for security reasons and also for the
            capability of being expanded/overrided by child products or
            instance-specific needs.
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        if revstatus == BatchState.open \
                and canstatus == CancellationState.active:
            return True


registerType(Batch, PROJECTNAME)


@indexer(IBatch)
def BatchDate(instance):
    return instance.Schema().getField('BatchDate').get(instance)
