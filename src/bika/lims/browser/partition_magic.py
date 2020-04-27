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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from collections import OrderedDict
from collections import defaultdict

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.decorators import returns_super_model
from bika.lims.utils.analysisrequest import create_partition

DEFAULT_NUMBER_OF_PARTITIONS = 0


class PartitionMagicView(BrowserView):
    """Manage Partitions of primary ARs
    """
    template = ViewPageTemplateFile("templates/partition_magic.pt")

    def __init__(self, context, request):
        super(PartitionMagicView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()
        self.analyses_to_remove = dict()


    def __call__(self):
        form = self.request.form

        # Form submit toggle
        form_submitted = form.get("submitted", False)

        # Buttons
        form_preview = form.get("button_preview", False)
        form_create = form.get("button_create", False)
        form_cancel = form.get("button_cancel", False)

        objs = self.get_objects()

        # No ARs selected
        if not objs:
            return self.redirect(message=_("No items selected"),
                                 level="warning")

        # Handle preview
        if form_submitted and form_preview:
            logger.info("*** PREVIEW ***")

        # Handle create
        if form_submitted and form_create:
            logger.info("*** CREATE PARTITIONS ***")

            partitions = []

            # create the partitions
            for partition in form.get("partitions", []):
                primary_uid = partition.get("primary_uid")
                sampletype_uid = partition.get("sampletype_uid")
                container_uid = partition.get("container_uid")
                preservation_uid = partition.get("preservation_uid")
                internal_use = partition.get("internal_use")
                if not primary_uid:
                    continue

                # The creation of partitions w/o analyses is allowed. Maybe the
                # user wants to add the analyses later manually or wants to keep
                # this partition stored in a freezer for some time
                analyses_uids = partition.get("analyses", [])
                partition = create_partition(
                    request=self.request,
                    analysis_request=primary_uid,
                    sample_type=sampletype_uid,
                    container=container_uid,
                    preservation=preservation_uid,
                    analyses=analyses_uids,
                    internal_use=internal_use,
                )
                partitions.append(partition)

                # Remove analyses from primary once all partitions are created
                primary = api.get_object(primary_uid)
                self.push_primary_analyses_for_removal(primary, analyses_uids)

                logger.info("Successfully created partition: {}".format(
                    api.get_path(partition)))

            if not partitions:
                # If no partitions were created, show a warning message
                return self.redirect(message=_("No partitions were created"))

            message = _("Created {} partitions: {}".format(
                len(partitions), ", ".join(map(api.get_title, partitions))))
            return self.redirect(message=message)

        # Handle cancel
        if form_submitted and form_cancel:
            logger.info("*** CANCEL ***")
            return self.redirect(message=_("Partitioning canceled"))

        return self.template()

    def push_primary_analyses_for_removal(self, analysis_request, analyses):
        """Stores the analyses to be removed after partitions creation
        """
        to_remove = self.analyses_to_remove.get(analysis_request, [])
        to_remove.extend(analyses)
        self.analyses_to_remove[analysis_request] = list(set(to_remove))

    def get_ar_data(self):
        """Returns a list of AR data
        """
        for obj in self.get_objects():
            info = self.get_base_info(obj)
            info.update({
                "analyses": self.get_analysis_data_for(obj),
                "sampletype": self.get_base_info(obj.getSampleType()),
                "number_of_partitions": self.get_number_of_partitions_for(obj),
                "template": self.get_template_data_for(obj),
            })
            yield info

    def get_sampletype_data(self):
        """Returns a list of SampleType data
        """
        for obj in self.get_sampletypes():
            info = self.get_base_info(obj)
            yield info

    def get_container_data(self):
        """Returns a list of Container data
        """
        for obj in self.get_containers():
            info = self.get_base_info(obj)
            yield info

    def get_preservation_data(self):
        """Returns a list of Preservation data
        """
        for obj in self.get_preservations():
            info = self.get_base_info(obj)
            yield info

    def get_objects(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("uids", "")
        if not uids:
            # check for the `items` parammeter
            uids = self.request.form.get("items", "")
        if isinstance(uids, basestring):
            uids = uids.split(",")
        unique_uids = OrderedDict().fromkeys(uids).keys()
        return filter(None, map(self.get_object_by_uid, unique_uids))

    def get_sampletypes(self):
        """Returns the available SampleTypes of the system
        """
        query = {
            "portal_type": "SampleType",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "is_active": True,
        }
        results = api.search(query, "bika_setup_catalog")
        return map(api.get_object, results)

    def get_containers(self):
        """Returns the available Containers of the system
        """
        query = dict(portal_type="Container",
                     sort_on="sortable_title",
                     sort_order="ascending",
                     is_active=True)
        results = api.search(query, "bika_setup_catalog")
        return map(api.get_object, results)

    def get_preservations(self):
        """Returns the available Preservations of the system
        """
        query = dict(portal_type="Preservation",
                     sort_on="sortable_title",
                     sort_order="ascending",
                     is_active=True)
        results = api.search(query, "bika_setup_catalog")
        return map(api.get_object, results)

    @returns_super_model
    def to_super_model(self, obj_or_objs):
        """Returns a SuperModel for a given object or a list of Supermodels if
        a list of objects was passed in
        """
        return obj_or_objs

    def get_analysis_data_for(self, ar):
        """Return the Analysis data for this AR
        """
        # Exclude analyses from children (partitions)
        analyses = ar.objectValues("Analysis")
        out = []
        for an in analyses:
            info = self.get_base_info(an)
            info.update({
                "service_uid": an.getServiceUID(),
            })
            out.append(info)
        return out

    def get_template_data_for(self, ar):
        """Return the Template data for this AR
        """
        info = None
        template = ar.getTemplate()
        ar_sampletype_uid = api.get_uid(ar.getSampleType())
        ar_container_uid = ""
        if ar.getContainer():
            ar_container_uid = api.get_uid(ar.getContainer())
        ar_preservation_uid = ""
        if ar.getPreservation():
            ar_preservation_uid = api.get_uid(ar.getPreservation())

        if template:
            info = self.get_base_info(template)

            analyses = template.getAnalyses()
            partition_analyses = map(
                lambda x: (x.get("partition"), x.get("service_uid")), analyses)

            analyses_by_partition = defaultdict(list)
            for partition, service_uid in partition_analyses:
                analyses_by_partition[partition].append(service_uid)

            sampletypes_by_partition = defaultdict(list)
            containers_by_partition = defaultdict(list)
            preservations_by_partition = defaultdict(list)
            internal_use_by_partition = defaultdict(list)
            for part in template.getPartitions():
                part_id = part.get("part_id")
                sampletype_uid = part.get('sampletype_uid', ar_sampletype_uid)
                sampletypes_by_partition[part_id] = sampletype_uid
                container_uid = part.get("container_uid", ar_container_uid)
                containers_by_partition[part_id] = container_uid
                preserv_uid = part.get("preservation_uid", ar_preservation_uid)
                preservations_by_partition[part_id] = preserv_uid
                internal_use = part.get("internal_use", ar.getInternalUse())
                internal_use_by_partition[part_id] = internal_use


            partitions = map(lambda p: p.get("part_id"),
                             template.getPartitions())
            info.update({
                "analyses": analyses_by_partition,
                "partitions": partitions,
                "sample_types": sampletypes_by_partition,
                "containers": containers_by_partition,
                "preservations": preservations_by_partition,
                "internal_uses": internal_use_by_partition,
            })
        else:
            info = {
                "analyses": {},
                "partitions": [],
                "sample_types": {},
                "containers": {},
                "preservations": {},
                "internal_uses": {},
            }
        return info

    def get_number_of_partitions_for(self, ar):
        """Return the number of selected partitions
        """
        # fetch the number of partitions from the request
        uid = api.get_uid(ar)
        num = self.request.get("primary", {}).get(uid)

        if num is None:
            # get the number of partitions from the template
            template = ar.getTemplate()
            if template:
                num = len(template.getPartitions())
            else:
                num = DEFAULT_NUMBER_OF_PARTITIONS
        try:
            num = int(num)
        except (TypeError, ValueError):
            num = DEFAULT_NUMBER_OF_PARTITIONS
        return num

    def get_base_info(self, obj):
        """Extract the base info from the given object
        """
        obj = api.get_object(obj)
        review_state = api.get_workflow_status_of(obj)
        state_title = review_state.capitalize().replace("_", " ")
        return {
            "obj": obj,
            "id": api.get_id(obj),
            "uid": api.get_uid(obj),
            "title": api.get_title(obj),
            "path": api.get_path(obj),
            "url": api.get_url(obj),
            "review_state": review_state,
            "state_title": state_title,
        }

    def redirect(self, redirect_url=None, message=None, level="info"):
        """Redirect with a message
        """
        if redirect_url is None:
            redirect_url = self.back_url
        if message is not None:
            self.add_status_message(message, level)
        return self.request.response.redirect(redirect_url)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
