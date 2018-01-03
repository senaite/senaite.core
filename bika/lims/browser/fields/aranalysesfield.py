# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from bika.lims import api, logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.interfaces import IARAnalysesField, IAnalysisService, IAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.permissions import ViewRetractedAnalyses
from bika.lims.utils.analysis import create_analysis
from plone.api.portal import get_tool
from zope.interface import implements


class ARAnalysesField(ObjectField):
    """A field that stores Analyses instances

    get() returns the list of Analyses contained inside the AnalysesRequest
    set() converts a sequence of UIDS to Analysis instances in the AR
    """
    implements(IARAnalysesField)

    _properties = Field._properties.copy()
    _properties.update({
        'type': 'analyses',
        'default': None,
    })

    security = ClassSecurityInfo()

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        """ get() returns the list of contained analyses
            By default, return a list of catalog brains.

            If you want objects, pass full_objects = True

            If you want to override "ViewRetractedAnalyses",
            pass retracted=True

            other kwargs are passed to bika_analysis_catalog

        """

        full_objects = False
        # If get_reflexed is false don't return the analyses that have been
        # reflexed, only the final ones
        get_reflexed = True

        if 'full_objects' in kwargs:
            full_objects = kwargs['full_objects']
            del kwargs['full_objects']
        if 'get_reflexed' in kwargs:
            get_reflexed = kwargs['get_reflexed']
            del kwargs['get_reflexed']

        if 'retracted' in kwargs:
            retracted = kwargs['retracted']
            del kwargs['retracted']
        else:
            mtool = getToolByName(instance, 'portal_membership')
            retracted = mtool.checkPermission(ViewRetractedAnalyses,
                                              instance)

        bac = getToolByName(instance, CATALOG_ANALYSIS_LISTING)
        contentFilter = dict([(k, v) for k, v in kwargs.items()
                              if k in bac.indexes()])
        contentFilter['portal_type'] = "Analysis"
        contentFilter['sort_on'] = "getKeyword"
        contentFilter['path'] = {'query': "/".join(instance.getPhysicalPath()),
                                 'level': 0}
        analyses = bac(contentFilter)
        if not retracted or full_objects or not get_reflexed:
            analyses_filtered = []
            for a in analyses:
                if not retracted and a.review_state == 'retracted':
                    continue
                if full_objects or not get_reflexed:
                    a_obj = a.getObject()
                    # Check if analysis has been reflexed
                    if not get_reflexed and \
                            a_obj.getReflexRuleActionsTriggered() != '':
                        continue
                    if full_objects:
                        a = a_obj
                analyses_filtered.append(a)
            analyses = analyses_filtered
        return analyses

    security.declarePrivate('set')

    def set(self, instance, items, prices=None, specs=None, **kwargs):
        """Set the 'Analyses' field value, by creating and removing Analysis
        objects from the AR.

        items is a list that contains the items to be set:
            The list can contain Analysis objects/brains, AnalysisService
            objects/brains and/or Analysis Service uids.

        prices is a dictionary:
            key = AnalysisService UID
            value = price

        specs is a dictionary:
            key = AnalysisService UID
            value = dictionary: defined in ResultsRange field definition

        """
        if not items:
            return

        assert isinstance(items,
                          (list, tuple)), "items must be a list or a tuple"

        # Convert the items list to a list of service uids and remove empties
        service_uids = map(self._get_service_uid, items)
        service_uids = filter(None, service_uids)

        bsc = getToolByName(instance, 'bika_setup_catalog')
        workflow = getToolByName(instance, 'portal_workflow')

        # one can only edit Analyses up to a certain state.
        ar_state = workflow.getInfoFor(instance, 'review_state', '')
        assert ar_state in ('sample_registered', 'sampled',
                            'to_be_sampled', 'to_be_preserved',
                            'sample_due', 'sample_received',
                            'attachment_due', 'to_be_verified')

        # - Modify existing AR specs with new form values for selected analyses.
        # - new analysis requests are also using this function, so ResultsRange
        #   may be undefined.  in this case, specs= will contain the entire
        #   AR spec.
        rr = instance.getResultsRange()
        specs = specs if specs else []
        for s in specs:
            s_in_rr = False
            for i, r in enumerate(rr):
                if s['keyword'] == r['keyword']:
                    rr[i].update(s)
                    s_in_rr = True
            if not s_in_rr:
                rr.append(s)
        instance.setResultsRange(rr)

        new_analyses = []
        proxies = bsc(UID=service_uids)
        for proxy in proxies:
            service = proxy.getObject()
            keyword = service.getKeyword()

            # analysis->InterimFields
            calc = service.getCalculation()
            interim_fields = calc and list(calc.getInterimFields()) or []

            # override defaults from service->InterimFields
            service_interims = service.getInterimFields()
            sif = dict([(x['keyword'], x.get('value', ''))
                        for x in service_interims])
            for i, i_f in enumerate(interim_fields):
                if i_f['keyword'] in sif:
                    interim_fields[i]['value'] = sif[i_f['keyword']]
                    service_interims = [x for x in service_interims
                                        if x['keyword'] != i_f['keyword']]
            # Add remaining service interims to the analysis
            for v in service_interims:
                interim_fields.append(v)

            # create the analysis if it doesn't exist
            if shasattr(instance, keyword):
                analysis = instance._getOb(keyword)
            else:
                analysis = create_analysis(instance, service)
                new_analyses.append(analysis)
            for i, r in enumerate(rr):
                if r['keyword'] == analysis.getKeyword():
                    r['uid'] = analysis.UID()

        # delete analyses
        delete_ids = []
        for analysis in instance.objectValues('Analysis'):
            service_uid = analysis.getServiceUID()
            if service_uid not in service_uids:
                # If it is verified or published, don't delete it.
                state = workflow.getInfoFor(analysis, 'review_state')
                if state in ('verified', 'published'):
                    continue
                # If it is assigned to a worksheet, unassign it before deletion.
                state = workflow.getInfoFor(analysis,
                                            'worksheetanalysis_review_state')
                if state == 'assigned':
                    ws = analysis.getBackReferences("WorksheetAnalysis")[0]
                    ws.removeAnalysis(analysis)
                # Unset the partition reference
                analysis.edit(SamplePartition=None)
                delete_ids.append(analysis.getId())

        if delete_ids:
            # Note: subscriber might promote the AR
            instance.manage_delObjects(ids=delete_ids)
        return new_analyses

    security.declarePublic('Vocabulary')

    def Vocabulary(self, content_instance=None):
        """ Create a vocabulary from analysis services
        """
        vocab = []
        for service in self.Services():
            vocab.append((service.UID(), service.Title()))
        return vocab

    security.declarePublic('Services')

    def Services(self):
        """ Return analysis services
        """
        bsc = get_tool('bika_setup_catalog')
        brains = bsc(portal_type='AnalysisService')
        return [proxy.getObject() for proxy in brains]

    def _get_service_uid(self, item):
        if api.is_uid(item):
            return item

        if not api.is_object(item):
            logger.warn("Not an UID: {}".format(item))
            return None

        obj = api.get_object(item)
        if IAnalysisService.providedBy(obj):
            return api.get_uid(obj)

        if IAnalysis.providedBy(obj) and IRequestAnalysis.providedBy(obj):
            return obj.getServiceUID()

        # An object, but neither an Analysis nor AnalysisService?
        # This should never happen.
        msg = "ARAnalysesField doesn't accept objects from {} type. " \
              "The object will be dismissed."
        logger.warn(msg.format(api.get_portal_type(obj)))
        return None


registerField(ARAnalysesField,
              title='Analyses',
              description='Used for Analysis instances'
              )
