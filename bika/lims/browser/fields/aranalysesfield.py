# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import itertools

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import Field
from Products.Archetypes.public import ObjectField
from zope.interface import implements

from bika.lims import api
from bika.lims import logger
from bika.lims.api.security import check_permission
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.interfaces import IARAnalysesField
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import ISubmitted
from bika.lims.permissions import AddAnalysis
from bika.lims.utils.analysis import create_analysis

"""Field to manage Analyses on ARs

Please see the assigned doctest at tests/doctests/ARAnalysesField.rst

Run this test from the buildout directory:

    bin/test test_textual_doctests -t ARAnalysesField
"""


class ARAnalysesField(ObjectField):
    """A field that stores Analyses instances
    """
    implements(IARAnalysesField)

    security = ClassSecurityInfo()
    _properties = Field._properties.copy()
    _properties.update({
        "type": "analyses",
        "default": None,
    })

    security.declarePrivate('get')

    def get(self, instance, **kwargs):
        """Returns a list of Analyses assigned to this AR

        Return a list of catalog brains unless `full_objects=True` is passed.
        Other keyword arguments are passed to bika_analysis_catalog

        :param instance: Analysis Request object
        :param kwargs: Keyword arguments to inject in the search query
        :returns: A list of Analysis Objects/Catalog Brains
        """
        # Do we need to return objects or brains
        full_objects = kwargs.get("full_objects", False)

        # Bail out parameters from kwargs that don't match with indexes
        catalog = api.get_tool(CATALOG_ANALYSIS_LISTING)
        indexes = catalog.indexes()
        query = dict([(k, v) for k, v in kwargs.items() if k in indexes])

        # Do the search against the catalog
        query["portal_type"] = "Analysis"
        query["getRequestUID"] = api.get_uid(instance)
        brains = catalog(query)
        if full_objects:
            return map(api.get_object, brains)
        return brains

    security.declarePrivate('set')

    def set(self, instance, items, prices=None, specs=None, hidden=None, **kw):
        """Set/Assign Analyses to this AR

        :param items: List of Analysis objects/brains, AnalysisService
                      objects/brains and/or Analysis Service uids
        :type items: list
        :param prices: Mapping of AnalysisService UID -> price
        :type prices: dict
        :param specs: List of AnalysisService UID -> Result Range mappings
        :type specs: list
        :param hidden: List of AnalysisService UID -> Hidden mappings
        :type hidden: list
        :returns: list of new assigned Analyses
        """
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
        if not check_permission(AddAnalysis, instance):
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

        # Modify existing AR specs with new form values of selected analyses.
        self._update_specs(instance, specs)

        # Create a mapping of Service UID -> Hidden status
        if hidden is None:
            hidden = []
        hidden = dict(map(lambda d: (d.get("uid"), d.get("hidden")), hidden))

        # Ensure we have a prices dictionary
        if prices is None:
            prices = dict()

        # Add analyses
        new_analyses = map(lambda service:
                           self.add_analysis(instance, service, prices, hidden),
                           services)
        new_analyses = filter(None, new_analyses)

        # Remove analyses
        # Since Manage Analyses view displays the analyses from partitions, we
        # also need to take them into consideration here. Analyses from
        # ancestors can be omitted.
        analyses = instance.objectValues("Analysis")
        analyses.extend(self.get_analyses_from_descendants(instance))

        # Service UIDs
        service_uids = map(api.get_uid, services)

        # Assigned Attachments
        assigned_attachments = []

        for analysis in analyses:
            service_uid = analysis.getServiceUID()

            # Skip if the Service is selected
            if service_uid in service_uids:
                continue

            # Skip non-open Analyses
            if ISubmitted.providedBy(analysis):
                continue

            # Remember assigned attachments
            # https://github.com/senaite/senaite.core/issues/1025
            assigned_attachments.extend(analysis.getAttachment())
            analysis.setAttachment([])

            # If it is assigned to a worksheet, unassign it before deletion.
            worksheet = analysis.getWorksheet()
            if worksheet:
                worksheet.removeAnalysis(analysis)

            # Remove the analysis
            # Note the analysis might belong to a partition
            analysis.aq_parent.manage_delObjects(ids=[api.get_id(analysis)])

        # Remove orphaned attachments
        for attachment in assigned_attachments:
            # only delete attachments which are no further linked
            if not attachment.getLinkedAnalyses():
                logger.info(
                    "Deleting attachment: {}".format(attachment.getId()))
                attachment_id = api.get_id(attachment)
                api.get_parent(attachment).manage_delObjects(attachment_id)

        return new_analyses

    def add_analysis(self, instance, service, prices, hidden):
        service_uid = api.get_uid(service)
        new_analysis = False

        # Gets the analysis or creates the analysis for this service
        # Note this analysis might not belong to this current instance, but
        # from a descendant (partition)
        analysis = self.resolve_analysis(instance, service)
        if not analysis:
            # Create the analysis
            new_analysis = True
            keyword = service.getKeyword()
            logger.info("Creating new analysis '{}'".format(keyword))
            analysis = create_analysis(instance, service)

        # Set the hidden status
        analysis.setHidden(hidden.get(service_uid, False))

        # Set the price of the Analysis
        analysis.setPrice(prices.get(service_uid, service.getPrice()))

        # Only return the analysis if is a new one
        if new_analysis:
            return analysis

        return None

    def resolve_analysis(self, instance, service):
        """Resolves an analysis for the service and instance
        """
        # Does the analysis exists in this instance already?
        analysis = self.get_from_instance(instance, service)
        if analysis:
            keyword = service.getKeyword()
            logger.info("Analysis for '{}' already exists".format(keyword))
            return analysis

        # Does the analysis exists in an ancestor?
        from_ancestor = self.get_from_ancestor(instance, service)
        if from_ancestor:
            # Move the analysis into this instance. The ancestor's
            # analysis will be masked otherwise
            analysis_id = api.get_id(from_ancestor)
            logger.info("Analysis {} is from an ancestor".format(analysis_id))
            cp = from_ancestor.aq_parent.manage_cutObjects(analysis_id)
            instance.manage_pasteObjects(cp)
            return instance._getOb(analysis_id)

        # Does the analysis exists in a descendant?
        from_descendant = self.get_from_descendant(instance, service)
        if from_descendant:
            # The analysis already exists in a partition, keep it. The
            # analysis from current instance will be masked otherwise
            analysis_id = api.get_id(from_descendant)
            logger.info("Analysis {} is from a descendant".format(analysis_id))
            return from_descendant

        return None

    def get_analyses_from_descendants(self, instance):
        """Returns all the analyses from descendants
        """
        analyses = []
        for descendant in instance.getDescendants(all_descendants=True):
            analyses.extend(descendant.objectValues("Analysis"))
        return analyses

    def get_from_instance(self, instance, service):
        """Returns an analysis for the given service from the instance
        """
        service_uid = api.get_uid(service)
        for analysis in instance.objectValues("Analysis"):
            if analysis.getServiceUID() == service_uid:
                return analysis
        return None

    def get_from_ancestor(self, instance, service):
        """Returns an analysis for the given service from ancestors
        """
        ancestor = instance.getParentAnalysisRequest()
        if not ancestor:
            return None

        analysis = self.get_from_instance(ancestor, service)
        return analysis or self.get_from_ancestor(ancestor, service)

    def get_from_descendant(self, instance, service):
        """Returns an analysis for the given service from descendants
        """
        for descendant in instance.getDescendants():
            # Does the analysis exists in the current descendant?
            analysis = self.get_from_instance(descendant, service)
            if analysis:
                return analysis

            # Search in descendants from current descendant
            analysis = self.get_from_descendant(descendant, service)
            if analysis:
                return analysis

        return None

    def _get_services(self, full_objects=False):
        """Fetch and return analysis service objects
        """
        bsc = api.get_tool("bika_setup_catalog")
        brains = bsc(portal_type="AnalysisService")
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
        portal_type = api.get_portal_type(obj)
        logger.error("ARAnalysesField doesn't accept objects from {} type. "
                     "The object will be dismissed.".format(portal_type))
        return None

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


registerField(ARAnalysesField,
              title="Analyses",
              description="Manages Analyses of ARs")
