# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import itertools

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from bika.lims import api
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IARAnalysesField
from bika.lims.permissions import AddAnalysis
from bika.lims.permissions import ViewRetractedAnalyses
from bika.lims.utils.analysis import create_analysis
from bika.lims.workflow import getReviewHistoryActionsList
from Products.Archetypes.public import Field
from Products.Archetypes.public import ObjectField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

"""Field to manage Analyses on ARs

Please see the assigned doctest at tests/doctests/ARAnalysesField.rst

Run this test from the buildout directory:

    bin/test test_textual_doctests -t ARAnalysesField
"""

FROZEN_STATES = ["verified", "published", "retracted"]
FROZEN_TRANSITIONS = ["verify", "retract"]


class ARAnalysesField(ObjectField):
    """A field that stores Analyses instances
    """
    implements(IARAnalysesField)

    security = ClassSecurityInfo()
    _properties = Field._properties.copy()
    _properties.update({
        'type': 'analyses',
        'default': None,
    })

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        """Returns a list of Analyses assigned to this AR

        Return a list of catalog brains unless `full_objects=True` is passed.
        Overrides "ViewRetractedAnalyses" when `retracted=True` is passed.
        Other keyword arguments are passed to bika_analysis_catalog

        :param instance: Analysis Request object
        :param kwargs: Keyword arguments to be passed to control the output
        :returns: A list of Analysis Objects/Catalog Brains
        """

        full_objects = False
        # If reflexed is false don't return the analyses that have been
        # reflexed, only the final ones
        reflexed = True

        if 'full_objects' in kwargs:
            full_objects = kwargs['full_objects']
            del kwargs['full_objects']

        if 'reflexed' in kwargs:
            reflexed = kwargs['reflexed']
            del kwargs['reflexed']

        if 'retracted' in kwargs:
            retracted = kwargs['retracted']
            del kwargs['retracted']
        else:
            mtool = getToolByName(instance, 'portal_membership')
            retracted = mtool.checkPermission(
                ViewRetractedAnalyses, instance)

        bac = getToolByName(instance, CATALOG_ANALYSIS_LISTING)
        contentFilter = dict([(k, v) for k, v in kwargs.items()
                              if k in bac.indexes()])
        contentFilter['portal_type'] = "Analysis"
        contentFilter['sort_on'] = "getKeyword"
        contentFilter['path'] = {'query': api.get_path(instance),
                                 'level': 0}
        analyses = bac(contentFilter)
        if not retracted or full_objects or not reflexed:
            analyses_filtered = []
            for a in analyses:
                if not retracted and a.review_state == 'retracted':
                    continue
                if full_objects or not reflexed:
                    a_obj = a.getObject()
                    # Check if analysis has been reflexed
                    if not reflexed and \
                            a_obj.getReflexRuleActionsTriggered() != '':
                        continue
                    if full_objects:
                        a = a_obj
                analyses_filtered.append(a)
            analyses = analyses_filtered
        return analyses

    security.declarePrivate('set')

    def set(self, instance, items, prices=None, specs=None, **kwargs):
        """Set/Assign Analyses to this AR

        :param items: List of Analysis objects/brains, AnalysisService
                      objects/brains and/or Analysis Service uids
        :type items: list
        :param prices: Mapping of AnalysisService UID -> price
        :type prices: dict
        :param specs: List of AnalysisService UID -> Result Range Record mappings
        :type specs: list
        :returns: list of new assigned Analyses
        """

        # This setter returns a list of new set Analyses
        new_analyses = []

        # Prevent removing all Analyses
        if not items:
            logger.warn("Not allowed to remove all Analyses from AR.")
            return new_analyses

        # Bail out if the items is not a list type
        if not isinstance(items, (list, tuple)):
            raise TypeError(
                "Items parameter must be a tuple or list, got '{}'".format(
                    type(items)))

        # Bail out if the AR is inactive
        if not api.is_active(instance):
            raise Unauthorized("Inactive ARs can not be modified"
                               .format(AddAnalysis))

        # Bail out if the user has not the right permission
        sm = getSecurityManager()
        if not sm.checkPermission(AddAnalysis, instance):
            raise Unauthorized("You do not have the '{}' permission"
                               .format(AddAnalysis))

        # Convert the items to a valid list of AnalysisServices
        services = filter(None, map(self._to_service, items))

        # Calculate dependencies
        # FIXME Infinite recursion error possible here, if the formula includes
        #       the Keyword of the Service that includes the Calculation
        dependencies = map(lambda s: s.getServiceDependencies(), services)
        dependencies = list(itertools.chain.from_iterable(dependencies))

        # Merge dependencies and services
        services = set(services + dependencies)

        # Service UIDs
        service_uids = map(api.get_uid, services)

        # Modify existing AR specs with new form values of selected analyses.
        self._update_specs(instance, specs)

        for service in services:
            keyword = service.getKeyword()

            # Create the Analysis if it doesn't exist
            if shasattr(instance, keyword):
                analysis = instance._getOb(keyword)
            else:
                # TODO Entry point for interims assignment and Calculation
                #      decoupling from Analysis. See comments PR#593
                analysis = create_analysis(instance, service)
                # TODO Remove when the `create_analysis` function supports this
                # Set the interim fields only for new created Analysis
                self._update_interims(analysis, service)
                new_analyses.append(analysis)

            # Set the price of the Analysis
            self._update_price(analysis, service, prices)

        # delete analyses
        delete_ids = []
        assigned_attachments = []

        for analysis in instance.objectValues('Analysis'):
            service_uid = analysis.getServiceUID()

            # Skip assigned Analyses
            if service_uid in service_uids:
                continue

            # Skip Analyses in frozen states
            if self._is_frozen(analysis):
                logger.warn("Inactive/verified/retracted Analyses can not be "
                            "removed.")
                continue

            # Remember assigned attachments
            # https://github.com/senaite/senaite.core/issues/1025
            assigned_attachments.extend(analysis.getAttachment())
            analysis.setAttachment([])

            # If it is assigned to a worksheet, unassign it before deletion.
            if self._is_assigned_to_worksheet(analysis):
                backrefs = self._get_assigned_worksheets(analysis)
                ws = backrefs[0]
                ws.removeAnalysis(analysis)

            # Unset the partition reference
            part = analysis.getSamplePartition()
            if part:
                # From this partition, remove the reference to the current
                # analysis that is going to be removed to prevent inconsistent
                # states (Sample Partitions referencing to Analyses that do not
                # exist anymore
                an_uid = api.get_uid(analysis)
                part_ans = part.getAnalyses() or []
                part_ans = filter(lambda an: api.get_uid(an) != an_uid, part_ans)
                part.setAnalyses(part_ans)
            # Unset the Analysis-to-Partition reference
            analysis.setSamplePartition(None)
            delete_ids.append(analysis.getId())

        if delete_ids:
            # Note: subscriber might promote the AR
            instance.manage_delObjects(ids=delete_ids)

        # Remove orphaned attachments
        for attachment in assigned_attachments:
            # only delete attachments which are no further linked
            if not attachment.getLinkedAnalyses():
                logger.info(
                    "Deleting attachment: {}".format(attachment.getId()))
                attachment_id = api.get_id(attachment)
                api.get_parent(attachment).manage_delObjects(attachment_id)

        return new_analyses

    def _get_services(self, full_objects=False):
        """Fetch and return analysis service objects
        """
        bsc = api.get_tool('bika_setup_catalog')
        brains = bsc(portal_type='AnalysisService')
        if full_objects:
            return map(api.get_object, brains)
        return brains

    def _to_service(self, thing):
        """Convert to Analysis Service

        :param thing: UID/Catalog Brain/Object/Something
        :returns: Analysis Service object or None
        """

        # Convert UIDs to objects
        if api.is_uid(thing):
            thing = api.get_object_by_uid(thing, None)

        # Bail out if the thing is not a valid object
        if not api.is_object(thing):
            logger.warn("'{}' is not a valid object!".format(repr(thing)))
            return None

        # Ensure we have an object here and not a brain
        obj = api.get_object(thing)

        if IAnalysisService.providedBy(obj):
            return obj

        if IAnalysis.providedBy(obj):
            return obj.getAnalysisService()

        # An object, but neither an Analysis nor AnalysisService?
        # This should never happen.
        msg = "ARAnalysesField doesn't accept objects from {} type. " \
            "The object will be dismissed.".format(api.get_portal_type(obj))
        logger.warn(msg)
        return None

    def _is_frozen(self, brain_or_object):
        """Check if the passed in object is frozen: the object is cancelled,
        inactive or has been verified at some point
        :param brain_or_object: Analysis or AR Brain/Object
        :returns: True if the object is frozen
        """
        if not api.is_active(brain_or_object):
            return True
        if api.get_workflow_status_of(brain_or_object) in FROZEN_STATES:
            return True
        # Check the review history if one of the frozen transitions was done
        object = api.get_object(brain_or_object)
        performed_transitions = set(getReviewHistoryActionsList(object))
        if set(FROZEN_TRANSITIONS).intersection(performed_transitions):
            return True
        return False

    def _get_assigned_worksheets(self, analysis):
        """Return the assigned worksheets of this Analysis

        :param analysis: Analysis Brain/Object
        :returns: Worksheet Backreferences
        """
        analysis = api.get_object(analysis)
        return analysis.getBackReferences("WorksheetAnalysis")

    def _is_assigned_to_worksheet(self, analysis):
        """Check if the Analysis is assigned to a worksheet

        :param analysis: Analysis Brain/Object
        :returns: True if the Analysis is assigned to a WS
        """
        analysis = api.get_object(analysis)
        state = api.get_workflow_status_of(
            analysis, state_var='worksheetanalysis_review_state')
        return state == "assigned"

    def _update_interims(self, analysis, service):
        """Update Interim Fields of the Analysis

        :param analysis: Analysis Object
        :param service: Analysis Service Object
        """
        service_interims = service.getInterimFields()
        analysis.setInterimFields(service_interims)

    def _update_price(self, analysis, service, prices):
        """Update the Price of the Analysis

        :param analysis: Analysis Object
        :param service: Analysis Service Object
        :param prices: Price mapping
        """
        prices = prices or {}
        price = prices.get(service.UID(), service.getPrice())
        analysis.setPrice(price)

    def _update_specs(self, instance, specs):
        """Update AR specifications

        :param instance: Analysis Request
        :param specs: List of Specification Records
        """

        if specs is None:
            return

        # N.B. we copy the records here, otherwise the spec will be written to
        #      the attached specification of this AR
        rr = {item["keyword"]: item.copy()
              for item in instance.getResultsRange()}
        for spec in specs:
            keyword = spec.get("keyword")
            if keyword in rr:
                # overwrite the instance specification only, if the specific
                # analysis spec has min/max values set
                if all([spec.get("min"), spec.get("max")]):
                    rr[keyword].update(spec)
                else:
                    rr[keyword] = spec
            else:
                rr[keyword] = spec
        return instance.setResultsRange(rr.values())

    # DEPRECATED: The following code should not be in the field's domain

    security.declarePublic('Vocabulary')

    @deprecated("Please refactor, this method will be removed in senaite.core 1.5")
    def Vocabulary(self, content_instance=None):
        """Create a vocabulary from analysis services
        """
        vocab = []
        for service in self._get_services():
            vocab.append((api.get_uid(service), api.get_title(service)))
        return vocab

    security.declarePublic('Services')

    @deprecated("Please refactor, this method will be removed in senaite.core 1.5")
    def Services(self):
        """Fetch and return analysis service objects
        """
        return self._get_services(full_objects=True)


registerField(ARAnalysesField,
              title="Analyses",
              description="Manages Analyses of ARs")
