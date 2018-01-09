# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.


from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims import api
from bika.lims import logger

SAMPLE_CONFIGURATION_STORAGE = "bika.lims.browser.sample.manage.add"
SKIP_FIELD_ON_COPY = []


class SampleAddView(BrowserView):
    """Sample Add view
    """
    template = ViewPageTemplateFile("templates/sample_add.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.tmp_sample = None

    def __call__(self):
        self.portal = api.get_portal()
        self.portal_url = self.portal.absolute_url()
        self.bika_setup = api.get_bika_setup()
        self.request.set('disable_plone.rightcolumn', 1)
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/sample_big.png"
        self.came_from = "add"
        self.tmp_sample = self.get_sample()
        self.sample_count = self.get_sample_count()
        self.fieldvalues = self.generate_fieldvalues(self.sample_count)
        logger.info(
            "*** Prepared data for {} Samples ***".format(self.sample_count))
        return self.template()

    def get_sample_count(self):
        """Return the sample_count request paramteter
        """
        try:
            sample_count = int(self.request.form.get("sample_count", 1))
        except (TypeError, ValueError):
            sample_count = 1
        return sample_count

    def get_sample(self):
        """Create a temporary Sample to fetch the fields from
        """
        if not self.tmp_sample:
            logger.info("*** CREATING TEMPORARY SAMPLE ***")
            self.tmp_sample = self.context.restrictedTraverse(
                "portal_factory/Sample/sample_tmp")
        return self.tmp_sample

    def generate_fieldvalues(self, count=1):
        """Returns a mapping of '<fieldname>-<count>' to the default value
        of the field or the field value of the source Sample
        """
        sample_context = self.get_sample()

        # mapping of UID index to Sample objects
        # {1: <Sample1>, 2: <Sample2> ...}
        copy_from = self.get_copy_from()

        out = {}
        # the original schema fields of a Sample (including extended fields)
        fields = self.get_sample_fields()

        # generate fields for all requested Samples
        for samplenum in range(count):
            source = copy_from.get(samplenum)
            parent = None
            if source is not None:
                parent = self.get_parent_sample(source)
            for field in fields:
                value = None
                fieldname = field.getName()
                if source and fieldname not in SKIP_FIELD_ON_COPY:
                    # get the field value stored on the source
                    context = parent or source
                    value = self.get_field_value(field, context)
                else:
                    # get the default value of this field
                    value = self.get_default_value(field, sample_context)
                # store the value on the new fieldname
                new_fieldname = self.get_fieldname(field, samplenum)
                out[new_fieldname] = value

        return out

    def get_copy_from(self):
        """Returns a mapping of UID index -> Sample object
        """
        # Create a mapping of source Sample for copy
        copy_from = self.request.form.get("copy_from", "").split(",")
        # clean out empty strings
        copy_from_uids = filter(lambda x: x, copy_from)
        out = dict().fromkeys(range(len(copy_from_uids)))
        for n, uid in enumerate(copy_from_uids):
            sample = self.get_object_by_uid(uid)
            if sample is None:
                continue
            out[n] = sample
        logger.info("get_copy_from: uids={}".format(copy_from_uids))
        return out

    def get_default_value(self, field, context):
        """Get the default value of the field
        """
        name = field.getName()
        default = field.getDefault(context)
        if name == "Client":
            client = self.get_client()
            if client is not None:
                default = client
        logger.info("get_default_value: context={} field={} value={}".format(
            context, name, default))
        return default

    def get_sample_fields(self):
        """Return the Sample schema fields (including extendend fields)
        """
        logger.info("*** GET SAMPLE FIELDS ***")
        schema = self.get_sample_schema()
        return schema.fields()

    def get_sample_schema(self):
        """Return the Sample schema
        """
        logger.info("*** GET SAMPLE SCHEMA ***")
        sample = self.get_sample()
        return sample.Schema()

    def get_fieldname(self, field, samplenum):
        """Generate a new fieldname with a '-<samplenum>' suffix
        """
        name = field.getName()
        # ensure we have only *one* suffix
        base_name = name.split("-")[0]
        suffix = "-{}".format(samplenum)
        return "{}{}".format(base_name, suffix)
