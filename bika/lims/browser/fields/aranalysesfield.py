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
from bika.lims import api
from bika.lims import logger
from bika.lims.api.security import check_permission
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.interfaces import IAnalysis, ISubmitted
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IARAnalysesField
from bika.lims.permissions import AddAnalysis
from bika.lims.utils.analysis import create_analysis
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
        catalog = getToolByName(instance, CATALOG_ANALYSIS_LISTING)
        query = dict(
            [(k, v) for k, v in kwargs.items() if k in catalog.indexes()])
        query["portal_type"] = "Analysis"
        query["getRequestUID"] = api.get_uid(instance)
        analyses = catalog(query)
        if not kwargs.get("full_objects", False):
            return analyses

        return map(api.get_object, analyses)

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
        # This setter returns a list of new set Analyses
        new_analyses = []

        # Current assigned analyses
        analyses = instance.objectValues("Analysis")

        # Submitted analyses must be retained
        submitted = filter(lambda an: ISubmitted.providedBy(an), analyses)

        # Prevent removing all analyses
        #
        # N.B.: Submitted analyses are rendered disabled in the HTML form.
        #       Therefore, their UIDs are not included in the submitted UIDs.
        if not items and not submitted:
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

        # CREATE/MODIFY ANALYSES

        for service in services:
            service_uid = api.get_uid(service)
            keyword = service.getKeyword()

            # Create the Analysis if it doesn't exist
            if shasattr(instance, keyword):
                analysis = instance._getOb(keyword)
            else:
                analysis = create_analysis(instance, service)
                new_analyses.append(analysis)

            # set the hidden status
            analysis.setHidden(hidden.get(service_uid, False))

            # Set the price of the Analysis
            analysis.setPrice(prices.get(service_uid, service.getPrice()))

        # DELETE ANALYSES

        # Service UIDs
        service_uids = map(api.get_uid, services)

        # Analyses IDs to delete
        delete_ids = []

        # Assigned Attachments
        assigned_attachments = []

        for analysis in analyses:
            service_uid = analysis.getServiceUID()

            # Skip if the Service is selected
            if service_uid in service_uids:
                continue

            # Skip non-open Analyses
            if analysis in submitted:
                continue

            # Remember assigned attachments
            # https://github.com/senaite/senaite.core/issues/1025
            assigned_attachments.extend(analysis.getAttachment())
            analysis.setAttachment([])

            # If it is assigned to a worksheet, unassign it before deletion.
            worksheet = analysis.getWorksheet()
            if worksheet:
                worksheet.removeAnalysis(analysis)

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
