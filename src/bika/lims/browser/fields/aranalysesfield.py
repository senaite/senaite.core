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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import itertools

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from bika.lims import api
from bika.lims import logger
from bika.lims.api.security import check_permission
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IARAnalysesField
from bika.lims.interfaces import ISubmitted
from bika.lims.permissions import AddAnalysis
from bika.lims.utils.analysis import create_analysis
from Products.Archetypes.public import Field
from Products.Archetypes.public import ObjectField
from Products.Archetypes.Registry import registerField
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from zope.interface import implements

DETACHED_STATES = ["cancelled", "retracted", "rejected"]


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
        Other keyword arguments are passed to senaite_catalog_analysis

        :param instance: Analysis Request object
        :param kwargs: Keyword arguments to inject in the search query
        :returns: A list of Analysis Objects/Catalog Brains
        """
        # Do we need to return objects or brains
        full_objects = kwargs.get("full_objects", False)

        # Bail out parameters from kwargs that don't match with indexes
        catalog = api.get_tool(ANALYSIS_CATALOG)
        indexes = catalog.indexes()
        query = dict([(k, v) for k, v in kwargs.items() if k in indexes])

        # Do the search against the catalog
        query["portal_type"] = "Analysis"
        query["getAncestorsUIDs"] = api.get_uid(instance)
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
        if items is None:
            items = []

        # Bail out if the items is not a list type
        if not isinstance(items, (list, tuple)):
            raise TypeError(
                "Items parameter must be a tuple or list, got '{}'".format(
                    type(items)))

        # Bail out if the AR is inactive
        if not api.is_active(instance):
            raise Unauthorized("Inactive ARs can not be modified")

        # Bail out if the user has not the right permission
        if not check_permission(AddAnalysis, instance):
            raise Unauthorized("You do not have the '{}' permission"
                               .format(AddAnalysis))

        # Convert the items to a valid list of AnalysisServices
        services = filter(None, map(self._to_service, items))

        # Calculate dependencies
        dependencies = map(lambda s: s.getServiceDependencies(), services)
        dependencies = list(itertools.chain.from_iterable(dependencies))

        # Merge dependencies and services
        services = set(services + dependencies)

        # Modify existing AR specs with new form values of selected analyses
        specs = self.resolve_specs(instance, specs)

        # Add analyses
        params = dict(prices=prices, hidden=hidden, specs=specs)
        map(lambda serv: self.add_analysis(instance, serv, **params), services)

        # Get all analyses (those from descendants included)
        analyses = instance.objectValues("Analysis")
        analyses.extend(self.get_analyses_from_descendants(instance))

        # Bail out those not in services list or submitted
        uids = map(api.get_uid, services)
        to_remove = filter(lambda an: an.getServiceUID() not in uids, analyses)
        to_remove = filter(lambda an: not ISubmitted.providedBy(an), to_remove)

        # Remove analyses
        map(self.remove_analysis, to_remove)

    def resolve_specs(self, instance, results_ranges):
        """Returns a dictionary where the key is the service_uid and the value
        is its results range. The dictionary is made by extending the
        results_ranges passed-in with the Sample's ResultsRanges (a copy of the
        specifications initially set)
        """
        rrs = results_ranges or []

        # Sample's Results ranges
        sample_rrs = instance.getResultsRange()

        # Ensure all subfields from specification are kept and missing values
        # for subfields are filled in accordance with the specs
        rrs = map(lambda rr: self.resolve_range(rr, sample_rrs), rrs)

        # Append those from sample that are missing in the ranges passed-in
        service_uids = map(lambda rr: rr["uid"], rrs)
        rrs.extend(filter(lambda rr: rr["uid"] not in service_uids, sample_rrs))

        # Create a dict for easy access to results ranges
        return dict(map(lambda rr: (rr["uid"], rr), rrs))

    def resolve_range(self, result_range, sample_result_ranges):
        """Resolves the range by adding the uid if not present and filling the
        missing subfield values with those that come from the Sample
        specification if they are not present in the result_range passed-in
        """
        # Resolve result_range to make sure it contain uid subfield
        rrs = self.resolve_uid(result_range)
        uid = rrs.get("uid")

        for sample_rr in sample_result_ranges:
            if uid and sample_rr.get("uid") == uid:
                # Keep same fields from sample
                rr = sample_rr.copy()
                rr.update(rrs)
                return rr

        # Return the original with no changes
        return rrs

    def resolve_uid(self, result_range):
        """Resolves the uid key for the result_range passed in if it does not
        exist when contains a keyword
        """
        value = result_range.copy()
        uid = value.get("uid")
        if api.is_uid(uid) and uid != "0":
            return value

        # uid key does not exist or is not valid, try to infere from keyword
        keyword = value.get("keyword")
        if keyword:
            query = dict(portal_type="AnalysisService", getKeyword=keyword)
            brains = api.search(query, SETUP_CATALOG)
            if len(brains) == 1:
                uid = api.get_uid(brains[0])
        value["uid"] = uid
        return value

    def resolve_conditions(self, analysis):
        """Returns the conditions to be applied to this analysis by merging
        those already set at sample level with defaults
        """
        service = analysis.getAnalysisService()
        default_conditions = service.getConditions()

        # Extract the conditions set for this analysis already
        existing = analysis.getConditions()
        existing_titles = [cond.get("title") for cond in existing]

        def is_missing(condition):
            return condition.get("title") not in existing_titles

        # Add only those conditions that are missing
        missing = filter(is_missing, default_conditions)

        # Sort them to match with same order as in service
        titles = [condition.get("title") for condition in default_conditions]

        def index(condition):
            cond_title = condition.get("title")
            if cond_title in titles:
                return titles.index(cond_title)
            return len(titles)

        conditions = existing + missing
        return sorted(conditions, key=lambda con: index(con))

    def add_analysis(self, instance, service, **kwargs):
        service_uid = api.get_uid(service)

        # Ensure we have suitable parameters
        specs = kwargs.get("specs") or {}

        # Get the hidden status for the service
        hidden = kwargs.get("hidden") or []
        hidden = filter(lambda d: d.get("uid") == service_uid, hidden)
        hidden = hidden and hidden[0].get("hidden") or service.getHidden()

        # Get the price for the service
        prices = kwargs.get("prices") or {}
        price = prices.get(service_uid) or service.getPrice()

        # Get the default result for the service
        default_result = service.getDefaultResult()

        # Gets the analysis or creates the analysis for this service
        # Note this returns a list, because is possible to have multiple
        # partitions with same analysis
        analyses = self.resolve_analyses(instance, service)

        # Filter out analyses in detached states
        # This allows to re-add an analysis that was retracted or cancelled
        analyses = filter(
            lambda an: api.get_workflow_status_of(an) not in DETACHED_STATES,
            analyses)

        if not analyses:
            # Create the analysis
            new_id = self.generate_analysis_id(instance, service)
            logger.info("Creating new analysis '{}'".format(new_id))
            analysis = create_analysis(instance, service, id=new_id)
            analyses.append(analysis)

        for analysis in analyses:
            # Set the hidden status
            analysis.setHidden(hidden)

            # Set the price of the Analysis
            analysis.setPrice(price)

            # Set the internal use status
            parent_sample = analysis.getRequest()
            analysis.setInternalUse(parent_sample.getInternalUse())

            # Set the default result to the analysis
            if not analysis.getResult() and default_result:
                analysis.setResult(default_result)
                analysis.setResultCaptureDate(None)

            # Set the result range to the analysis
            analysis_rr = specs.get(service_uid) or analysis.getResultsRange()
            analysis.setResultsRange(analysis_rr)

            # Set default (pre)conditions
            conditions = self.resolve_conditions(analysis)
            analysis.setConditions(conditions)

            analysis.reindexObject()

    def generate_analysis_id(self, instance, service):
        """Generate a new analysis ID
        """
        count = 1
        keyword = service.getKeyword()
        new_id = keyword
        while new_id in instance.objectIds():
            new_id = "{}-{}".format(keyword, count)
            count += 1
        return new_id

    def remove_analysis(self, analysis):
        """Removes a given analysis from the instance
        """
        # Remember assigned attachments
        # https://github.com/senaite/senaite.core/issues/1025
        attachments = analysis.getAttachment()
        analysis.setAttachment([])

        # If assigned to a worksheet, unassign it before deletion
        worksheet = analysis.getWorksheet()
        if worksheet:
            worksheet.removeAnalysis(analysis)

        # handle retest source deleted
        retest = analysis.getRetest()
        if retest:
            # unset reference link
            retest.setRetestOf(None)

        # Remove the analysis
        # Note the analysis might belong to a partition
        analysis.aq_parent.manage_delObjects(ids=[api.get_id(analysis)])

        # Remove orphaned attachments
        for attachment in attachments:
            if not attachment.getLinkedAnalyses():
                # only delete attachments which are no further linked
                logger.info(
                    "Deleting attachment: {}".format(attachment.getId()))
                attachment_id = api.get_id(attachment)
                api.get_parent(attachment).manage_delObjects(attachment_id)

    def resolve_analyses(self, instance, service):
        """Resolves analyses for the service and instance
        It returns a list, cause for a given sample, multiple analyses for same
        service can exist due to the possibility of having multiple partitions
        """
        analyses = []

        # Does the analysis exists in this instance already?
        instance_analyses = self.get_from_instance(instance, service)

        if instance_analyses:
            analyses.extend(instance_analyses)

        # Does the analysis exists in an ancestor?
        from_ancestor = self.get_from_ancestor(instance, service)
        for ancestor_analysis in from_ancestor:
            # only move non-assigned analyses
            state = api.get_workflow_status_of(ancestor_analysis)
            if state != "unassigned":
                continue
            # Move the analysis into the partition
            analysis_id = api.get_id(ancestor_analysis)
            logger.info("Analysis {} is from an ancestor".format(analysis_id))
            cp = ancestor_analysis.aq_parent.manage_cutObjects(analysis_id)
            instance.manage_pasteObjects(cp)
            analyses.append(instance._getOb(analysis_id))

        # Does the analysis exists in descendants?
        from_descendant = self.get_from_descendant(instance, service)
        analyses.extend(from_descendant)

        return analyses

    def get_analyses_from_descendants(self, instance):
        """Returns all the analyses from descendants
        """
        analyses = []
        for descendant in instance.getDescendants(all_descendants=True):
            analyses.extend(descendant.objectValues("Analysis"))
        return analyses

    def get_from_instance(self, instance, service):
        """Returns analyses for the given service from the instance
        """
        service_uid = api.get_uid(service)
        analyses = instance.objectValues("Analysis")
        # Filter those analyses with same keyword. Note that a Sample can
        # contain more than one analysis with same keyword because of retests
        return filter(lambda an: an.getServiceUID() == service_uid, analyses)

    def get_from_ancestor(self, instance, service):
        """Returns analyses for the given service from ancestors
        """
        ancestor = instance.getParentAnalysisRequest()
        if not ancestor:
            return []

        analyses = self.get_from_instance(ancestor, service)
        return analyses or self.get_from_ancestor(ancestor, service)

    def get_from_descendant(self, instance, service):
        """Returns analyses for the given service from descendants
        """
        analyses = []
        for descendant in instance.getDescendants():
            # Does the analysis exists in the current descendant?
            descendant_analyses = self.get_from_instance(descendant, service)
            if descendant_analyses:
                analyses.extend(descendant_analyses)

            # Search in descendants from current descendant
            from_descendant = self.get_from_descendant(descendant, service)
            analyses.extend(from_descendant)

        return analyses

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


registerField(ARAnalysesField,
              title="Analyses",
              description="Manages Analyses of ARs")
