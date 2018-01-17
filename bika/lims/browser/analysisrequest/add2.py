# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import magnitude
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.volatile import cache
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.base_add_view import BaseAddView
from bika.lims.browser.base_add_view import BaseAjaxAddView
from bika.lims.browser.base_add_view import BaseManageAddView
from bika.lims.utils import cache_key
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import create_analysisrequest as crar


def mg(value):
    """Copied from bika.lims.jsonapi.v1.calculate_partitions
    """
    tokens = value.split(" ") if value else [0, '']
    val = float(tokens[0]) if isinstance(tokens[0], (int, long)) else 0
    unit = tokens[1] if len(tokens) > 1 else ''
    # Magnitude doesn't support mL units.
    # Since mL is commonly used instead of ml to avoid confusion with the
    # number one, add "L" (for liter) as a 'recognizable' unit.
    # L unit as liter is also recommended by the NIST Guide
    # http://physics.nist.gov/Pubs/SP811/sec05.html#table6
    # Further info: https://jira.bikalabs.com/browse/LIMS-1441
    unit = unit[:-1] + 'l' if unit.endswith('L') else unit
    return magnitude.mg(val, unit)


class AnalysisRequestAddView(BaseAddView):
    """AR Add view
    """
    template = ViewPageTemplateFile("templates/ar_add2.pt")

    def __init__(self, context, request):
        BaseAddView.__init__(self, context, request)
        self.SKIP_FIELD_ON_COPY = ["Sample"]

    def __call__(self):
        BaseAddView.__call__(self)
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/analysisrequest_big.png"
        self.fieldvalues = self.generate_fieldvalues(self.obj_count)
        self.specifications = self.generate_specifications(self.obj_count)
        logger.info("*** Prepared data for {} ARs ***".format(self.obj_count))
        return self.template()

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

    def is_ar_specs_allowed(self):
        """Checks if AR Specs are allowed
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getEnableARSpecs()

    def get_drymatter_service(self):
        """The analysis to be used for determining dry matter
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getDryMatterService()

    def get_obj(self):
        """Create a temporary AR to fetch the fields from
        """
        if not self.tmp_obj:
            logger.info("*** CREATING TEMPORARY AR ***")
            self.tmp_obj = self.context.restrictedTraverse(
                "portal_factory/AnalysisRequest/Request new analyses")
        return self.tmp_obj

    def generate_specifications(self, count=1):
        """Returns a mapping of count -> specification
        """

        out = {}

        # mapping of UID index to AR objects {1: <AR1>, 2: <AR2> ...}
        copy_from = self.get_copy_from()

        for arnum in range(count):
            # get the source object
            source = copy_from.get(arnum)

            if source is None:
                out[arnum] = {}
                continue

            # get the results range from the source object
            results_range = source.getResultsRange()

            # mapping of keyword -> rr specification
            specification = {}
            for rr in results_range:
                specification[rr.get("keyword")] = rr
            out[arnum] = specification

        return out

    def get_parent_ar(self, ar):
        """Returns the parent AR
        """
        parent = ar.getParentAnalysisRequest()

        # Return immediately if we have no parent
        if parent is None:
            return None

        # Walk back the chain until we reach the source AR
        while True:
            pparent = parent.getParentAnalysisRequest()
            if pparent is None:
                break
            # remember the new parent
            parent = pparent

        return parent

    def generate_fieldvalues(self, count=1):
        """Returns a mapping of '<fieldname>-<count>' to the default value
        of the field or the field value of the source AR
        """
        ar_context = self.get_obj()

        # mapping of UID index to AR objects {1: <AR1>, 2: <AR2> ...}
        copy_from = self.get_copy_from()

        out = {}
        # the original schema fields of an AR (including extended fields)
        fields = self.get_obj_fields()

        # generate fields for all requested ARs
        for arnum in range(count):
            source = copy_from.get(arnum)
            parent = None
            if source is not None:
                parent = self.get_parent_ar(source)
            for field in fields:
                value = None
                fieldname = field.getName()
                if source and fieldname not in self.SKIP_FIELD_ON_COPY:
                    # get the field value stored on the source
                    context = parent or source
                    value = self.get_field_value(field, context)
                else:
                    # get the default value of this field
                    value = self.get_default_value(field, ar_context)
                # store the value on the new fieldname
                new_fieldname = self.get_fieldname(field, arnum)
                out[new_fieldname] = value

        return out

    def get_default_contact(self):
        """Logic refactored from JavaScript:

        * If client only has one contact, and the analysis request comes from
        * a client, then Auto-complete first Contact field.
        * If client only has one contect, and the analysis request comes from
        * a batch, then Auto-complete all Contact field.

        :returns: The default contact for the AR
        :rtype: Client object or None
        """
        catalog = api.get_tool("portal_catalog")
        client = self.get_client()
        path = api.get_path(self.context)
        if client:
            path = api.get_path(client)
        query = {
            "portal_type": "Contact",
            "path": {
                "query": path,
                "depth": 1
            },
            "incactive_state": "active",
        }
        contacts = catalog(query)
        if len(contacts) == 1:
            return api.get_object(contacts[0])
        return None

    def getMemberDiscountApplies(self):
        """Return if the member discount applies for this client

        :returns: True if member discount applies for the client
        :rtype: bool
        """
        client = self.get_client()
        if client is None:
            return False
        return client.getMemberDiscountApplies()

    def get_fields_with_visibility(self, visibility, mode="add"):
        """Return the AR fields with the current visibility
        """
        ar = self.get_obj()
        mv = api.get_view("ar_add_manage", context=ar)
        mv.get_field_order()

        out = []
        for field in mv.get_fields_with_visibility(visibility, mode):
            # check custom field condition
            visible = self.is_field_visible(field)
            if visible is False and visibility != "hidden":
                continue
            out.append(field)
        return out

    def get_service_categories(self, restricted=True):
        """Return all service categories in the right order

        :param restricted: Client settings restrict categories
        :type restricted: bool
        :returns: Category catalog results
        :rtype: brains
        """
        bsc = api.get_tool("bika_setup_catalog")
        query = {
            "portal_type": "AnalysisCategory",
            "inactive_state": "active",
            "sort_on": "sortable_title",
        }
        categories = bsc(query)
        client = self.get_client()
        if client and restricted:
            restricted_categories = client.getRestrictedCategories()
            restricted_category_ids = map(lambda c: c.getId(), restricted_categories)
            # keep correct order of categories
            if restricted_category_ids:
                categories = filter(lambda c: c.getId in restricted_category_ids, categories)
        return categories

    def get_services(self, poc="lab"):
        """Return all Services

        :param poc: Point of capture (lab/field)
        :type poc: string
        :returns: Mapping of category -> list of services
        :rtype: dict
        """
        bsc = api.get_tool("bika_setup_catalog")
        query = {
            "portal_type": "AnalysisService",
            "getPointOfCapture": poc,
            "inactive_state": "active",
            "sort_on": "sortable_title",
        }
        services = bsc(query)
        categories = self.get_service_categories(restricted=False)
        analyses = {key: [] for key in map(lambda c: c.Title, categories)}

        # append the empty category as well
        analyses[""] = []

        for brain in services:
            category = brain.getCategoryTitle
            if category in analyses:
                analyses[category].append(brain)
        return analyses

    @cache(cache_key)
    def get_service_uid_from(self, analysis):
        """Return the service from the analysis
        """
        analysis = api.get_object(analysis)
        return api.get_uid(analysis.getAnalysisService())

    def get_calculation_dependencies_for(self, service):
        """Calculation dependencies of this service and the calculation of each
        dependent service (recursively).

        TODO: This needs to go to bika.lims.api
        """

        def calc_dependencies_gen(service, collector=None):
            """Generator for recursive dependency resolution.
            """

            # The UID of the service
            service_uid = api.get_uid(service)

            # maintain an internal dependency mapping
            if collector is None:
                collector = {}

            # Stop iteration if we processed this service already
            if service_uid in collector:
                raise StopIteration

            # Get the calculation of the service.
            # The calculation comes either from an assigned method or the user
            # has set a calculation manually (see content/analysisservice.py).
            calculation = service.getCalculation()

            # Stop iteration if there is no calculation
            if not calculation:
                raise StopIteration

            # The services used in this calculation.
            # These are the actual dependencies of the used formula.
            dep_services = calculation.getDependentServices()
            for dep_service in dep_services:
                # get the UID of the dependent service
                dep_service_uid = api.get_uid(dep_service)

                # remember the dependent service
                collector[dep_service_uid] = dep_service

                # yield the dependent service
                yield dep_service

                # check the dependencies of the dependent services
                for ddep_service in calc_dependencies_gen(dep_service,
                                                          collector=collector):
                    yield ddep_service

        dependencies = {}
        for dep_service in calc_dependencies_gen(service):
            # Skip the initial (requested) service
            if dep_service == service:
                continue
            uid = api.get_uid(dep_service)
            dependencies[uid] = dep_service

        return dependencies

    def get_calculation_dependants_for(self, service):
        """Calculation dependants of this service

        TODO: This needs to go to bika.lims.api
        """

        def calc_dependants_gen(service, collector=None):
            """Generator for recursive resolution of dependant sevices.
            """

            # The UID of the service
            service_uid = api.get_uid(service)

            # maintain an internal dependency mapping
            if collector is None:
                collector = {}

            # Stop iteration if we processed this service already
            if service_uid in collector:
                raise StopIteration

            # Get the dependant calculations of the service
            # (calculations that use the service in their formula).
            dep_calcs = service.getBackReferences('CalculationAnalysisService')
            for dep_calc in dep_calcs:
                # Get the methods linked to this calculation
                dep_methods = dep_calc.getBackReferences('MethodCalculation')
                for dep_method in dep_methods:
                    # Get the services that have this method linked
                    dep_services = dep_method.getBackReferences('AnalysisServiceMethod')
                    for dep_service in dep_services:

                        # get the UID of the dependent service
                        dep_service_uid = api.get_uid(dep_service)

                        # skip services with a different calculation, e.g. when
                        # the user selected a calculation manually.
                        if dep_service.getCalculation() != dep_calc:
                            continue

                        # remember the dependent service
                        collector[dep_service_uid] = dep_service

                        # yield the dependent service
                        yield dep_service

                        # check the dependants of the dependant services
                        for ddep_service in calc_dependants_gen(dep_service,
                                                                collector=collector):
                            yield ddep_service

        dependants = {}
        for dep_service in calc_dependants_gen(service):
            # Skip the initial (requested) service
            if dep_service == service:
                continue
            uid = api.get_uid(dep_service)
            dependants[uid] = dep_service

        return dependants

    def get_service_dependencies_for(self, service):
        """Calculate the dependencies for the given service.
        """

        dependants = self.get_calculation_dependants_for(service)
        dependencies = self.get_calculation_dependencies_for(service)

        return {
            "dependencies": dependencies.values(),
            "dependants": dependants.values(),
        }

    def is_service_selected(self, service):
        """Checks if the given service is selected by one of the ARs.
        This is used to make the whole line visible or not.
        """
        service_uid = api.get_uid(service)
        for arnum in range(self.ar_count):
            analyses = self.fieldvalues.get("Analyses-{}".format(arnum))
            if not analyses:
                continue
            service_uids = map(self.get_service_uid_from, analyses)
            if service_uid in service_uids:
                return True
        return False


class AnalysisRequestManageView(BaseManageAddView):
    """AR Manage View
    """
    template = ViewPageTemplateFile("templates/ar_add_manage.pt")

    def __init__(self, context, request):
        BaseManageAddView.__init__(self, context, request)
        self.CONFIGURATION_STORAGE = \
            "bika.lims.browser.analysisrequest.manage.add"
        self.SKIP_FIELD_ON_COPY = ["Sample"]

    def __call__(self):
        BaseManageAddView.__call__(self)
        return self.template()

    def get_obj(self):
        if not self.tmp_obj:
            self.tmp_obj = self.context.restrictedTraverse(
                "portal_factory/AnalysisRequest/Request new analyses")
        return self.tmp_obj


class ajaxAnalysisRequestAddView(BaseAjaxAddView, AnalysisRequestAddView):
    """Ajax helpers for the analysis request add form
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        AnalysisRequestAddView.__init__(self, context, request)
        BaseAjaxAddView.__init__(self, context, request)

    @cache(cache_key)
    def get_client_info(self, obj):
        """Returns the client info of an object
        """
        info = self.get_base_info(obj)
        info.update({})

        # UID of the client
        uid = api.get_uid(obj)

        # Bika Setup folder
        bika_setup = api.get_bika_setup()

        # bika samplepoints
        bika_samplepoints = bika_setup.bika_samplepoints
        bika_samplepoints_uid = api.get_uid(bika_samplepoints)

        # bika artemplates
        bika_artemplates = bika_setup.bika_artemplates
        bika_artemplates_uid = api.get_uid(bika_artemplates)

        # bika analysisprofiles
        bika_analysisprofiles = bika_setup.bika_analysisprofiles
        bika_analysisprofiles_uid = api.get_uid(bika_analysisprofiles)

        # bika analysisspecs
        bika_analysisspecs = bika_setup.bika_analysisspecs
        bika_analysisspecs_uid = api.get_uid(bika_analysisspecs)

        # catalog queries for UI field filtering
        filter_queries = {
            "contact": {
                "getParentUID": [uid]
            },
            "cc_contact": {
                "getParentUID": [uid]
            },
            "invoice_contact": {
                "getParentUID": [uid]
            },
            "samplepoint": {
                "getClientUID": [uid, bika_samplepoints_uid],
            },
            "artemplates": {
                "getClientUID": [uid, bika_artemplates_uid],
            },
            "analysisprofiles": {
                "getClientUID": [uid, bika_analysisprofiles_uid],
            },
            "analysisspecs": {
                "getClientUID": [uid, bika_analysisspecs_uid],
            },
            "samplinground": {
                "getParentUID": [uid],
            },
            "sample": {
                "getClientUID": [uid],
            },
        }
        info["filter_queries"] = filter_queries

        return info

    @cache(cache_key)
    def get_contact_info(self, obj):
        """Returns the client info of an object
        """

        info = self.get_base_info(obj)
        fullname = obj.getFullname()
        email = obj.getEmailAddress()

        # Note: It might get a circular dependency when calling:
        #       map(self.get_contact_info, obj.getCCContact())
        cccontacts = {}
        for contact in obj.getCCContact():
            uid = api.get_uid(contact)
            fullname = contact.getFullname()
            email = contact.getEmailAddress()
            cccontacts[uid] = {
                "fullname": fullname,
                "email": email
            }

        info.update({
            "fullname": fullname,
            "email": email,
            "cccontacts": cccontacts,
        })

        return info

    @cache(cache_key)
    def get_service_info(self, obj):
        """Returns the info for a Service
        """
        info = self.get_base_info(obj)

        info.update({
            "short_title": obj.getShortTitle(),
            "scientific_name": obj.getScientificName(),
            "unit": obj.getUnit(),
            "report_dry_matter": obj.getReportDryMatter(),
            "keyword": obj.getKeyword(),
            "methods": map(self.get_method_info, obj.getMethods()),
            "calculation": self.get_calculation_info(obj.getCalculation()),
            "price": obj.getPrice(),
            "currency_symbol": self.get_currency().symbol,
            "accredited": obj.getAccredited(),
            "category": obj.getCategoryTitle(),
            "poc": obj.getPointOfCapture(),

        })

        dependencies = self.get_calculation_dependencies_for(obj).values()
        info["dependencies"] = map(self.get_base_info, dependencies)
        # dependants = self.get_calculation_dependants_for(obj).values()
        # info["dependendants"] = map(self.get_base_info, dependants)
        return info

    @cache(cache_key)
    def get_template_info(self, obj):
        """Returns the info for a Template
        """
        client = self.get_client()
        client_uid = api.get_uid(client) if client else ""

        profile = obj.getAnalysisProfile()
        profile_uid = api.get_uid(profile) if profile else ""
        profile_title = profile.Title() if profile else ""

        sample_type = obj.getSampleType()
        sample_type_uid = api.get_uid(sample_type) if sample_type else ""
        sample_type_title = sample_type.Title() if sample_type else ""

        sample_point = obj.getSamplePoint()
        sample_point_uid = api.get_uid(sample_point) if sample_point else ""
        sample_point_title = sample_point.Title() if sample_point else ""

        service_uids = []
        analyses_partitions = {}
        analyses = obj.getAnalyses()

        for record in analyses:
            service_uid = record.get("service_uid")
            service_uids.append(service_uid)
            analyses_partitions[service_uid] = record.get("partition")

        info = self.get_base_info(obj)
        info.update({
            "analyses_partitions": analyses_partitions,
            "analysis_profile_title": profile_title,
            "analysis_profile_uid": profile_uid,
            "client_uid": client_uid,
            "composite": obj.getComposite(),
            "partitions": obj.getPartitions(),
            "remarks": obj.getRemarks(),
            "report_dry_matter": obj.getReportDryMatter(),
            "sample_point_title": sample_point_title,
            "sample_point_uid": sample_point_uid,
            "sample_type_title": sample_type_title,
            "sample_type_uid": sample_type_uid,
            "service_uids": service_uids,
        })
        return info

    @cache(cache_key)
    def get_profile_info(self, obj):
        """Returns the info for a Profile
        """
        info = self.get_base_info(obj)
        info.update({})
        return info

    @cache(cache_key)
    def get_method_info(self, obj):
        """Returns the info for a Method
        """
        info = self.get_base_info(obj)
        info.update({})
        return info

    @cache(cache_key)
    def get_calculation_info(self, obj):
        """Returns the info for a Calculation
        """
        info = self.get_base_info(obj)
        info.update({})
        return info

    @cache(cache_key)
    def get_sampletype_info(self, obj):
        """Returns the info for a Sample Type
        """
        info = self.get_base_info(obj)

        # Bika Setup folder
        bika_setup = api.get_bika_setup()

        # bika samplepoints
        bika_samplepoints = bika_setup.bika_samplepoints
        bika_samplepoints_uid = api.get_uid(bika_samplepoints)

        # bika analysisspecs
        bika_analysisspecs = bika_setup.bika_analysisspecs
        bika_analysisspecs_uid = api.get_uid(bika_analysisspecs)

        # client
        client = self.get_client()
        client_uid = client and api.get_uid(client) or ""

        # sample matrix
        sample_matrix = obj.getSampleMatrix()
        sample_matrix_uid = sample_matrix and sample_matrix.UID() or ""
        sample_matrix_title = sample_matrix and sample_matrix.Title() or ""

        # container type
        container_type = obj.getContainerType()
        container_type_uid = container_type and container_type.UID() or ""
        container_type_title = container_type and container_type.Title() or ""

        # sample points
        sample_points = obj.getSamplePoints()
        sample_point_uids = map(lambda sp: sp.UID(), sample_points)
        sample_point_titles = map(lambda sp: sp.Title(), sample_points)

        info.update({
            "prefix": obj.getPrefix(),
            "minimum_volume": obj.getMinimumVolume(),
            "hazardous": obj.getHazardous(),
            "retention_period": obj.getRetentionPeriod(),
            "sample_matrix_uid": sample_matrix_uid,
            "sample_matrix_title": sample_matrix_title,
            "container_type_uid": container_type_uid,
            "container_type_title": container_type_title,
            "sample_point_uids": sample_point_uids,
            "sample_point_titles": sample_point_titles,
        })

        # catalog queries for UI field filtering
        filter_queries = {
            "samplepoint": {
                "getSampleTypeTitles": [obj.Title(), ''],
                "getClientUID": [client_uid, bika_samplepoints_uid],
                "sort_order": "descending",
            },
            "specification": {
                "getSampleTypeTitle": obj.Title(),
                "getClientUID": [client_uid, bika_analysisspecs_uid],
                "sort_order": "descending",
            }
        }
        info["filter_queries"] = filter_queries

        return info

    @cache(cache_key)
    def get_sample_info(self, obj):
        """Returns the info for a Sample
        """
        info = self.get_base_info(obj)

        # sample type
        sample_type = obj.getSampleType()
        sample_type_uid = sample_type and sample_type.UID() or ""
        sample_type_title = sample_type and sample_type.Title() or ""

        # sample condition
        sample_condition = obj.getSampleCondition()
        sample_condition_uid = sample_condition and sample_condition.UID() or ""
        sample_condition_title = sample_condition and sample_condition.Title() or ""

        # storage location
        storage_location = obj.getStorageLocation()
        storage_location_uid = storage_location and storage_location.UID() or ""
        storage_location_title = storage_location and storage_location.Title() or ""

        # sample point
        sample_point = obj.getSamplePoint()
        sample_point_uid = sample_point and sample_point.UID() or ""
        sample_point_title = sample_point and sample_point.Title() or ""

        # container type
        container_type = sample_type and sample_type.getContainerType() or None
        container_type_uid = container_type and container_type.UID() or ""
        container_type_title = container_type and container_type.Title() or ""

        info.update({
            "sample_id": obj.getSampleID(),
            "date_sampled": self.to_iso_date(obj.getDateSampled()),
            "sampling_date": self.to_iso_date(obj.getSamplingDate()),
            "sample_type_uid": sample_type_uid,
            "sample_type_title": sample_type_title,
            "container_type_uid": container_type_uid,
            "container_type_title": container_type_title,
            "sample_condition_uid": sample_condition_uid,
            "sample_condition_title": sample_condition_title,
            "storage_location_uid": storage_location_uid,
            "storage_location_title": storage_location_title,
            "sample_point_uid": sample_point_uid,
            "sample_point_title": sample_point_title,
            "environmental_conditions": obj.getEnvironmentalConditions(),
            "composite": obj.getComposite(),
            "client_sample_id": obj.getClientSampleID(),
            "client_reference": obj.getClientReference(),
            "sampling_workflow_enabled": obj.getSamplingWorkflowEnabled(),
            "adhoc": obj.getAdHoc(),
            "remarks": obj.getRemarks(),
        })
        return info

    @cache(cache_key)
    def get_specification_info(self, obj):
        """Returns the info for a Specification
        """
        info = self.get_base_info(obj)

        results_range = obj.getResultsRange()
        info.update({
            "results_range": results_range,
            "sample_type_uid": obj.getSampleTypeUID(),
            "sample_type_title": obj.getSampleTypeTitle(),
            "client_uid": obj.getClientUID(),
        })

        bsc = api.get_tool("bika_setup_catalog")

        def get_service_by_keyword(keyword):
            if keyword is None:
                return []
            return map(api.get_object, bsc({
                "portal_type": "AnalysisService",
                "getKeyword": keyword
            }))

        # append a mapping of service_uid -> specification
        specifications = {}
        for spec in results_range:
            service_uid = spec.get("uid")
            if service_uid is None:
                # service spec is not attached to a specific service, but to a keyword
                for service in get_service_by_keyword(spec.get("keyword")):
                    service_uid = api.get_uid(service)
                    specifications[service_uid] = spec
                continue
            specifications[service_uid] = spec
        info["specifications"] = specifications
        # spec'd service UIDs
        info["service_uids"] = specifications.keys()
        return info

    @cache(cache_key)
    def get_container_info(self, obj):
        """Returns the info for a Container
        """
        info = self.get_base_info(obj)
        info.update({})
        return info

    def get_service_partitions(self, service, sampletype):
        """Returns the Partition info for a Service and SampleType

        N.B.: This is actually not used as the whole partition, preservation
        and conservation settings are solely handled by AR Templates for all
        selected services.
        """

        partitions = []

        sampletype_uid = api.get_uid(sampletype)
        # partition setup of this service
        partition_setup = filter(lambda p: p.get("sampletype") == sampletype_uid,
                                 service.getPartitionSetup())

        def get_containers(container_uids):
            containers = []
            for container_uid in container_uids:
                container = api.get_object_by_uid(container_uid)
                if container.portal_type == "ContainerTypes":
                    containers.extend(container.getContainers())
                else:
                    containers.append(container)
            return containers

        for partition in partition_setup:
            containers = get_containers(partition.get("container", []))
            preservations = map(api.get_object_by_uid, partition.get("preservation", []))
            partitions.append({
                "separate": partition.get("separate", False) and True or False,
                "container": map(self.get_container_info, containers),
                "preservations": map(self.get_preservation_info, preservations),
                "minvol": partition.get("vol", ""),
            })
        else:
            containers = [service.getContainer()] or []
            preservations = [service.getPreservation()] or []
            partitions.append({
                "separate": service.getSeparate(),
                "container": map(self.get_container_info, containers),
                "preservations": map(self.get_preservation_info, preservations),
                "minvol": sampletype.getMinimumVolume() or "",
            })

        return partitions

    def ajax_get_service(self):
        """Returns the services information
        """
        uid = self.request.form.get("uid", None)

        if uid is None:
            return self.error("Invalid UID", status=400)

        service = self.get_object_by_uid(uid)
        if not service:
            return self.error("Service not found", status=404)

        info = self.get_service_info(service)
        return info

    def ajax_recalculate_records(self):
        """Recalculate all AR records and dependencies

            - samples
            - templates
            - profiles
            - services
            - dependecies

        XXX: This function has grown too much and needs refactoring!
        """
        out = {}

        # The sorted records from the request
        records = self.get_records()

        for n, record in enumerate(records):

            # Mapping of client UID -> client object info
            client_metadata = {}
            # Mapping of contact UID -> contact object info
            contact_metadata = {}
            # Mapping of sample UID -> sample object info
            sample_metadata = {}
            # Mapping of sampletype UID -> sampletype object info
            sampletype_metadata = {}
            # Mapping of drymatter UID -> drymatter service info
            dms_metadata = {}
            # Mapping of drymatter service (dms) -> list of dependent services
            dms_to_services = {}
            # Mapping of dependent services -> drymatter service (dms)
            service_to_dms = {}
            # Mapping of specification UID -> specification object info
            specification_metadata = {}
            # Mapping of specification UID -> list of service UIDs
            specification_to_services = {}
            # Mapping of service UID -> list of specification UIDs
            service_to_specifications = {}
            # Mapping of template UID -> template object info
            template_metadata = {}
            # Mapping of template UID -> list of service UIDs
            template_to_services = {}
            # Mapping of service UID -> list of template UIDs
            service_to_templates = {}
            # Mapping of profile UID -> list of service UIDs
            profile_to_services = {}
            # Mapping of service UID -> list of profile UIDs
            service_to_profiles = {}
            # Profile metadata for UI purposes
            profile_metadata = {}
            # Mapping of service UID -> service object info
            service_metadata = {}
            # mapping of service UID -> unmet service dependency UIDs
            unmet_dependencies = {}

            # Internal mappings of UID -> object of selected items in this record
            _clients = self.get_objs_from_record(record, "Client_uid")
            _contacts = self.get_objs_from_record(record, "Contact_uid")
            _specifications = self.get_objs_from_record(record, "Specification_uid")
            _templates = self.get_objs_from_record(record, "Template_uid")
            _samples = self.get_objs_from_record(record, "Sample_uid")
            _profiles = self.get_objs_from_record(record, "Profiles_uid")
            _services = self.get_objs_from_record(record, "Analyses")
            _sampletypes = self.get_objs_from_record(record, "SampleType_uid")

            # CLIENTS
            for uid, obj in _clients.iteritems():
                # get the client metadata
                metadata = self.get_client_info(obj)
                # remember the sampletype metadata
                client_metadata[uid] = metadata

            # CONTACTS
            for uid, obj in _contacts.iteritems():
                # get the client metadata
                metadata = self.get_contact_info(obj)
                # remember the sampletype metadata
                contact_metadata[uid] = metadata

            # SPECIFICATIONS
            for uid, obj in _specifications.iteritems():
                # get the specification metadata
                metadata = self.get_specification_info(obj)
                # remember the metadata of this specification
                specification_metadata[uid] = metadata
                # get the spec'd service UIDs
                service_uids = metadata["service_uids"]
                # remember a mapping of specification uid -> spec'd services
                specification_to_services[uid] = service_uids
                # remember a mapping of service uid -> specifications
                for service_uid in service_uids:
                    if service_uid in service_to_specifications:
                        service_to_specifications[service_uid].append(uid)
                    else:
                        service_to_specifications[service_uid] = [uid]

            # AR TEMPLATES
            for uid, obj in _templates.iteritems():
                # get the template metadata
                metadata = self.get_template_info(obj)
                # remember the template metadata
                template_metadata[uid] = metadata

                # XXX notify below to include the drymatter service as well
                record["ReportDryMatter"] = obj.getReportDryMatter()

                # profile from the template
                profile = obj.getAnalysisProfile()
                # add the profile to the other profiles
                if profile is not None:
                    profile_uid = api.get_uid(profile)
                    _profiles[profile_uid] = profile

                # get the template analyses
                # [{'partition': 'part-1', 'service_uid': 'a6c5ff56a00e427a884e313d7344f966'},
                # {'partition': 'part-1', 'service_uid': 'dd6b0f756a5b4b17b86f72188ee81c80'}]
                analyses = obj.getAnalyses() or []
                # get all UIDs of the template records
                service_uids = map(lambda rec: rec.get("service_uid"), analyses)
                # remember a mapping of template uid -> service
                template_to_services[uid] = service_uids
                # remember a mapping of service uid -> templates
                for service_uid in service_uids:
                    # append service to services mapping
                    service = self.get_object_by_uid(service_uid)
                    # remember the template of all services
                    if service_uid in service_to_templates:
                        service_to_templates[service_uid].append(uid)
                    else:
                        service_to_templates[service_uid] = [uid]

            # DRY MATTER
            dms = self.get_drymatter_service()
            if dms and record.get("ReportDryMatter"):
                # get the UID of the drymatter service
                dms_uid = api.get_uid(dms)
                # get the drymatter metadata
                metadata = self.get_service_info(dms)
                # remember the metadata of the drymatter service
                dms_metadata[dms_uid] = metadata
                # add the drymatter service to the service collection (processed later)
                _services[dms_uid] = dms
                # get the dependencies of the drymatter service
                dms_deps = self.get_calculation_dependencies_for(dms)
                # add the drymatter service dependencies to the service collection (processed later)
                _services.update(dms_deps)
                # remember a mapping of dms uid -> services
                dms_to_services[dms_uid] = dms_deps.keys() + [dms_uid]
                # remember a mapping of dms dependency uid -> dms
                service_to_dms[dms_uid] = [dms_uid]
                for dep_uid, dep in dms_deps.iteritems():
                    if dep_uid in service_to_dms:
                        service_to_dms[dep_uid].append(dms_uid)
                    else:
                        service_to_dms[dep_uid] = [dms_uid]

            # PROFILES
            for uid, obj in _profiles.iteritems():
                # get the profile metadata
                metadata = self.get_profile_info(obj)
                # remember the profile metadata
                profile_metadata[uid] = metadata
                # get all services of this profile
                services = obj.getService()
                # get all UIDs of the profile services
                service_uids = map(api.get_uid, services)
                # remember all services of this profile
                profile_to_services[uid] = service_uids
                # remember a mapping of service uid -> profiles
                for service in services:
                    # get the UID of this service
                    service_uid = api.get_uid(service)
                    # add the service to the other services
                    _services[service_uid] = service
                    # remember the profiles of this service
                    if service_uid in service_to_profiles:
                        service_to_profiles[service_uid].append(uid)
                    else:
                        service_to_profiles[service_uid] = [uid]

            # SAMPLES
            for uid, obj in _samples.iteritems():
                # get the sample metadata
                metadata = self.get_sample_info(obj)
                # remember the sample metadata
                sample_metadata[uid] = metadata

            # SAMPLETYPES
            for uid, obj in _sampletypes.iteritems():
                # get the sampletype metadata
                metadata = self.get_sampletype_info(obj)
                # remember the sampletype metadata
                sampletype_metadata[uid] = metadata

            # SERVICES
            for uid, obj in _services.iteritems():
                # get the service metadata
                metadata = self.get_service_info(obj)

                # N.B.: Partitions only handled via AR Template.
                #
                # # Partition setup for the give sample type
                # for st_uid, st_obj in _sampletypes.iteritems():
                #     # remember the partition setup for this service
                #     metadata["partitions"] = self.get_service_partitions(obj, st_obj)

                # remember the services' metadata
                service_metadata[uid] = metadata

            #  DEPENDENCIES
            for uid, obj in _services.iteritems():
                # get the dependencies of this service
                deps = self.get_service_dependencies_for(obj)

                # check for unmet dependencies
                for dep in deps["dependencies"]:
                    # we use the UID to test for equality
                    dep_uid = api.get_uid(dep)
                    if dep_uid not in _services.keys():
                        if uid in unmet_dependencies:
                            unmet_dependencies[uid].append(self.get_base_info(dep))
                        else:
                            unmet_dependencies[uid] = [self.get_base_info(dep)]
                # remember the dependencies in the service metadata
                service_metadata[uid].update({
                    "dependencies": map(self.get_base_info, deps["dependencies"]),
                    "dependants": map(self.get_base_info, deps["dependants"]),
                })

            # Each key `n` (1,2,3...) contains the form data for one AR Add
            # column in the UI.
            # All relevant form data will be set accoriding to this data.
            out[n] = {
                "client_metadata": client_metadata,
                "contact_metadata": contact_metadata,
                "sample_metadata": sample_metadata,
                "sampletype_metadata": sampletype_metadata,
                "dms_metadata": dms_metadata,
                "dms_to_services": dms_to_services,
                "service_to_dms": service_to_dms,
                "specification_metadata": specification_metadata,
                "specification_to_services": specification_to_services,
                "service_to_specifications": service_to_specifications,
                "template_metadata": template_metadata,
                "template_to_services": template_to_services,
                "service_to_templates": service_to_templates,
                "profile_metadata": profile_metadata,
                "profile_to_services": profile_to_services,
                "service_to_profiles": service_to_profiles,
                "service_metadata": service_metadata,
                "unmet_dependencies": unmet_dependencies,
            }

        return out

    def show_recalculate_prices(self):
        bika_setup = api.get_bika_setup()
        return bika_setup.getShowPrices()

    def ajax_recalculate_prices(self):
        """Recalculate prices for all ARs
        """
        # When the option "Include and display pricing information" in
        # Bika Setup Accounting tab is not selected
        if not self.show_recalculate_prices():
            return {}

        # The sorted records from the request
        records = self.get_records()

        client = self.get_client()
        bika_setup = api.get_bika_setup()

        member_discount = float(bika_setup.getMemberDiscount())
        member_discount_applies = False
        if client:
            member_discount_applies = client.getMemberDiscountApplies()

        prices = {}
        for n, record in enumerate(records):
            ardiscount_amount = 0.00
            arservices_price = 0.00
            arprofiles_price = 0.00
            arprofiles_vat_amount = 0.00
            arservice_vat_amount = 0.00
            services_from_priced_profile = []

            profile_uids = record.get("Profiles_uid", "").split(",")
            profile_uids = filter(lambda x: x, profile_uids)
            profiles = map(self.get_object_by_uid, profile_uids)
            services = map(self.get_object_by_uid, record.get("Analyses", []))

            # ANALYSIS PROFILES PRICE
            for profile in profiles:
                use_profile_price = profile.getUseAnalysisProfilePrice()
                if not use_profile_price:
                    continue

                profile_price = float(profile.getAnalysisProfilePrice())
                profile_vat = float(profile.getAnalysisProfileVAT())
                arprofiles_price += profile_price
                arprofiles_vat_amount += profile_vat
                profile_services = profile.getService()
                services_from_priced_profile.extend(profile_services)

            # ANALYSIS SERVICES PRICE
            for service in services:
                if service in services_from_priced_profile:
                    continue
                service_price = float(service.getPrice())
                # service_vat = float(service.getVAT())
                service_vat_amount = float(service.getVATAmount())
                arservice_vat_amount += service_vat_amount
                arservices_price += service_price

            base_price = arservices_price + arprofiles_price

            # Calculate the member discount if it applies
            if member_discount and member_discount_applies:
                logger.info("Member discount applies with {}%".format(member_discount))
                ardiscount_amount = base_price * member_discount / 100

            subtotal = base_price - ardiscount_amount
            vat_amount = arprofiles_vat_amount + arservice_vat_amount
            total = subtotal + vat_amount

            prices[n] = {
                "discount": "{0:.2f}".format(ardiscount_amount),
                "subtotal": "{0:.2f}".format(subtotal),
                "vat": "{0:.2f}".format(vat_amount),
                "total": "{0:.2f}".format(total),
            }
            logger.info("Prices for AR {}: Discount={discount} "
                        "VAT={vat} Subtotal={subtotal} total={total}"
                        .format(n, **prices[n]))

        return prices

    def ajax_submit(self):
        """Submit & create the ARs
        """

        # Get AR required fields (including extended fields)
        fields = self.get_obj_fields()

        # extract records from request
        records = self.get_records()

        fielderrors = {}
        errors = {"message": "", "fielderrors": {}}

        attachments = {}
        valid_records = []

        # Validate required fields
        for n, record in enumerate(records):

            # Process UID fields first and set their values to the linked field
            uid_fields = filter(lambda f: f.endswith("_uid"), record)
            for field in uid_fields:
                name = field.replace("_uid", "")
                value = record.get(field)
                if "," in value:
                    value = value.split(",")
                record[name] = value

            # Extract file uploads (fields ending with _file)
            # These files will be added later as attachments
            file_fields = filter(lambda f: f.endswith("_file"), record)
            attachments[n] = map(lambda f: record.pop(f), file_fields)

            # Process Specifications field (dictionary like records instance).
            # -> Convert to a standard Python dictionary.
            specifications = map(lambda x: dict(x), record.pop("Specifications", []))
            record["Specifications"] = specifications

            # Required fields and their values
            required_keys = [field.getName() for field in fields if field.required]
            required_values = [record.get(key) for key in required_keys]
            required_fields = dict(zip(required_keys, required_values))

            # Client field is required but hidden in the AR Add form. We remove
            # it therefore from the list of required fields to let empty
            # columns pass the required check below.
            if record.get("Client", False):
                required_fields.pop('Client', None)

            # Contacts get pre-filled out if only one contact exists.
            # We won't force those columns with only the Contact filled out to be required.
            contact = required_fields.pop("Contact", None)

            # None of the required fields are filled, skip this record
            if not any(required_fields.values()):
                continue

            # Re-add the Contact
            required_fields["Contact"] = contact

            # Missing required fields
            missing = [f for f in required_fields if not record.get(f, None)]

            # If there are required fields missing, flag an error
            for field in missing:
                fieldname = "{}-{}".format(field, n)
                msg = _("Field '{}' is required".format(field))
                fielderrors[fieldname] = msg

            # Selected Analysis UIDs
            selected_analysis_uids = record.get("Analyses", [])

            # Partitions defined in Template
            template_parts = {}
            template_uid = record.get("Template_uid")
            if template_uid:
                template = api.get_object_by_uid(template_uid)
                for part in template.getPartitions():
                    # remember the part setup by part_id
                    template_parts[part.get("part_id")] = part

            # The final data structure should look like this:
            # [{"part_id": "...", "container_uid": "...", "services": []}]
            partitions = {}
            parts = record.pop("Parts", [])
            for part in parts:
                part_id = part.get("part")
                service_uid = part.get("uid")
                # skip unselected Services
                if service_uid not in selected_analysis_uids:
                    continue
                # Container UID for this part
                container_uids = []
                template_part = template_parts.get(part_id)
                if template_part:
                    container_uid = template_part.get("container_uid")
                    if container_uid:
                        container_uids.append(container_uid)

                # remember the part id and the services
                if part_id not in partitions:
                    partitions[part_id] = {
                        "part_id": part_id,
                        "container_uid": container_uids,
                        "services": [service_uid],
                    }
                else:
                    partitions[part_id]["services"].append(service_uid)

            # Inject the Partitions to the record (will be picked up during the AR creation)
            record["Partitions"] = partitions.values()

            # Process valid record
            valid_record = dict()
            for fieldname, fieldvalue in record.iteritems():
                # clean empty
                if fieldvalue in ['', None]:
                    continue
                valid_record[fieldname] = fieldvalue

            # append the valid record to the list of valid records
            valid_records.append(valid_record)

        # return immediately with an error response if some field checks failed
        if fielderrors:
            errors["fielderrors"] = fielderrors
            return {'errors': errors}

        # Process Form
        ARs = []
        for n, record in enumerate(valid_records):
            client_uid = record.get("Client")
            client = self.get_object_by_uid(client_uid)

            if not client:
                raise RuntimeError("No client found")

            # get the specifications and pass them directly to the AR create function.
            specifications = record.pop("Specifications", {})

            # Create the Analysis Request
            try:
                ar = crar(client, self.request, record, specifications=specifications)
            except (KeyError, RuntimeError) as e:
                errors["message"] = e.message
                return {"errors": errors}
            ARs.append(ar.Title())

            _attachments = []
            for attachment in attachments.get(n, []):
                if not attachment.filename:
                    continue
                att = _createObjectByType("Attachment", self.context, tmpID())
                att.setAttachmentFile(attachment)
                att.processForm()
                _attachments.append(att)
            if _attachments:
                ar.setAttachment(_attachments)

        level = "info"
        if len(ARs) == 0:
            message = _('No Analysis Requests could be created.')
            level = "error"
        elif len(ARs) > 1:
            message = _('Analysis requests ${ARs} were successfully created.',
                        mapping={'ARs': safe_unicode(', '.join(ARs))})
        else:
            message = _('Analysis request ${AR} was successfully created.',
                        mapping={'AR': safe_unicode(ARs[0])})

        # Display a portal message
        self.context.plone_utils.addPortalMessage(message, level)

        # Automatic label printing won't print "register" labels for Secondary. ARs
        bika_setup = api.get_bika_setup()
        auto_print = bika_setup.getAutoPrintStickers()

        # https://github.com/bikalabs/bika.lims/pull/2153
        new_ars = [a for a in ARs if a[-1] == '1']

        if 'register' in auto_print and new_ars:
            return {
                'success': message,
                'stickers': new_ars,
                'stickertemplate': self.context.bika_setup.getAutoStickerTemplate()
            }
        else:
            return {'success': message}
