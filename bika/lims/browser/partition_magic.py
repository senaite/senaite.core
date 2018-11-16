# -*- coding: utf-8 -*-

from collections import OrderedDict
from collections import defaultdict

from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.decorators import returns_super_model
from bika.lims.workflow import doActionFor
from bika.lims import api
from bika.lims.interfaces import IProxyField
from bika.lims.utils.analysisrequest import create_analysisrequest as crar
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

DEFAULT_NUMBER_OF_PARTITIONS = 0

PARTITION_SKIP_FIELDS = [
    "Analyses",
    "Attachment",
    "Client",
    "Profile",
    "Profiles",
    "RejectionReasons",
    "Remarks",
    "ResultsInterpretation",
    "Sample",
    "SampleType",
    "Template",
    "creation_date",
    "id",
    "modification_date",
    "ParentAnalysisRequest",
]


class PartitionMagicView(BrowserView):
    """Manage Partitions of primary ARs
    """
    template = ViewPageTemplateFile("templates/partition_magic.pt")

    def __init__(self, context, request):
        super(PartitionMagicView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()

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
                analyses_uids = partition.get("analyses")
                if not analyses_uids or not primary_uid:
                    # Cannot create a partition w/o analyses!
                    continue

                partition = self.create_partition(
                    primary_uid, sampletype_uid, analyses_uids)
                partitions.append(partition)
                logger.info("Successfully created partition: {}".format(
                    api.get_path(partition)))

                # Force the reception of the partition
                doActionFor(partition, "receive")

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

    def create_partition(self, primary_uid, sampletype_uid, analyses_uids):
        """Create a new partition (AR)
        """
        logger.info("*** CREATE PARTITION ***")

        ar = self.get_object_by_uid(primary_uid)
        record = {
            "InternalUse": True,
            "ParentAnalysisRequest": primary_uid,
            "SampleType": sampletype_uid,
        }

        for fieldname, field in api.get_fields(ar).items():
            # if self.is_proxy_field(field):
            #     logger.info("Skipping proxy field {}".format(fieldname))
            #     continue
            if self.is_computed_field(field):
                logger.info("Skipping computed field {}".format(fieldname))
                continue
            if fieldname in PARTITION_SKIP_FIELDS:
                logger.info("Skipping field {}".format(fieldname))
                continue
            fieldvalue = field.get(ar)
            record[fieldname] = fieldvalue
            logger.info("Update record '{}': {}".format(
                fieldname, repr(fieldvalue)))

        client = ar.getClient()
        analyses = map(self.get_object_by_uid, analyses_uids)
        services = map(lambda an: an.getAnalysisService(), analyses)

        partition = crar(
            client,
            self.request,
            record,
            analyses=services,
            specifications=self.get_specifications_for(ar)
        )

        # Reindex Parent Analysis Request
        # TODO Workflow - AnalysisRequest - Partitions creation
        ar.reindexObject(idxs=["isRootAncestor"])

        return partition

    def get_specifications_for(self, ar):
        """Returns a mapping of service uid -> specification
        """
        spec = ar.getSpecification()
        if not spec:
            return []
        return spec.getResultsRange()

    def is_proxy_field(self, field):
        """Checks if the field is a proxy field
        """
        return IProxyField.providedBy(field)

    def is_computed_field(self, field):
        """Checks if the field is a coumputed field
        """
        return field.type == "computed"

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
            "inactive_state": "active",
        }
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
        analyses = ar.getAnalyses()
        out = []
        for an in analyses:
            info = self.get_base_info(an)
            info.update({
                "service_uid": an.getServiceUID,
            })
            out.append(info)
        return out

    def get_template_data_for(self, ar):
        """Return the Template data for this AR
        """
        info = None
        template = ar.getTemplate()
        ar_sampletype_uid = api.get_uid(ar.getSampleType())

        if template:
            info = self.get_base_info(template)

            analyses = template.getAnalyses()
            partition_analyses = map(
                lambda x: (x.get("partition"), x.get("service_uid")), analyses)

            analyses_by_partition = defaultdict(list)
            for partition, service_uid in partition_analyses:
                analyses_by_partition[partition].append(service_uid)

            sampletypes_by_partition = defaultdict(list)
            for part in template.getPartitions():
                part_id = part.get("part_id")
                sampletype_uid = part.get('sampletype_uid', ar_sampletype_uid)
                sampletypes_by_partition[part_id] = sampletype_uid

            partitions = map(lambda p: p.get("part_id"),
                             template.getPartitions())
            info.update({
                "analyses": analyses_by_partition,
                "partitions": partitions,
                "sample_types": sampletypes_by_partition,
            })
        else:
            info = {
                "analyses": {},
                "partitions": [],
                "sample_types": {},
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
