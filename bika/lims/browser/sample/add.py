# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from datetime import datetime

from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import protect
from plone.memoize.volatile import cache
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.base_add_view import BaseAddView
from bika.lims.browser.base_add_view import BaseManageAddView
from bika.lims.utils import cache_key
from bika.lims.utils import returns_json
from bika.lims.utils.sample import create_sample


def get_tmp_sample(view):
    if not view.tmp_obj:
        logger.info("*** CREATING TEMPORARY SAMPLE ***")
        view.tmp_obj = view.context.restrictedTraverse(
            "portal_factory/Sample/sample_tmp")
    return view.tmp_obj


class SampleAddView(BaseAddView):
    """Sample Add view
    """
    template = ViewPageTemplateFile("templates/sample_add.pt")

    def __call__(self):
        BaseAddView.__call__(self)
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/sample_big.png"
        self.fieldvalues = self.generate_fieldvalues(self.obj_count)
        logger.info(
            "*** Prepared data for {} Samples ***".format(self.obj_count))
        return self.template()

    def get_obj(self):
        """Create a temporary Sample to fetch the fields from
        """
        self.tmp_obj = get_tmp_sample(self)
        return self.tmp_obj

    def get_obj_count(self):
        """Return the obj_count request parameter
        """
        try:
            obj_count = int(self.request.form.get("sample_count", 1))
        except (TypeError, ValueError):
            obj_count = 1
        return obj_count

    def generate_fieldvalues(self, count=1):
        """Returns a mapping of '<fieldname>-<count>' to the default value
        of the field or the field value of the source Sample
        """
        sample_context = self.get_obj()
        out = {}
        # the original schema fields of a Sample (including extended fields)
        fields = self.get_obj_fields()

        # generate fields for all requested Samples
        for samplenum in range(count):
            for field in fields:
                # get the default value of this field
                value = self.get_default_value(field, sample_context)
                # store the value on the new fieldname
                new_fieldname = self.get_fieldname(field, samplenum)
                out[new_fieldname] = value
        return out

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

    def get_fields_with_visibility(self, visibility, mode="add"):
        """Return the Sample fields with the current visibility
        """
        sample = self.get_obj()
        mv = api.get_view("sample_add_manage", context=sample)
        mv.get_field_order()

        out = []
        for field in mv.get_fields_with_visibility(visibility, mode):
            # check custom field condition
            visible = self.is_field_visible(field)
            if visible is False and visibility != "hidden":
                continue
            out.append(field)
        return out


class SampleManageView(BaseManageAddView):
    """Sample Manage View
    """
    template = ViewPageTemplateFile("templates/sample_add_manage.pt")

    def __init__(self, context, request):
        BaseManageAddView.__init__(self, context, request)
        self.CONFIGURATION_STORAGE = "bika.lims.browser.sample.manage.add"

    def __call__(self):
        BaseManageAddView.__call__(self)
        return self.template()

    def get_obj(self):
        self.tmp_obj = get_tmp_sample(self)
        return self.tmp_obj


class ajaxSampleAdd(SampleAddView):
    """Ajax helpers for the sample add form
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        SampleAddView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.traverse_subpath = []
        # Errors are aggregated here, and returned together to the browser
        self.errors = {}

    def publishTraverse(self, request, name):
        """ get's called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    @returns_json
    def __call__(self):
        """Dispatch the path to a method and return JSON.
        """
        protect.CheckAuthenticator(self.request.form)
        protect.PostOnly(self.request.form)

        if len(self.traverse_subpath) != 1:
            return self.error("Not found", status=404)
        func_name = "ajax_{}".format(self.traverse_subpath[0])
        func = getattr(self, func_name, None)
        if func is None:
            return self.error("Invalid function", status=400)
        return func()

    def error(self, message, status=500, **kw):
        """Set a JSON error object and a status to the response
        """
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message}
        result.update(kw)
        return result

    def to_iso_date(self, dt):
        """Return the ISO representation of a date object
        """
        if dt is None:
            return ""
        if isinstance(dt, DateTime):
            return dt.ISO8601()
        if isinstance(dt, datetime):
            return dt.isoformat()
        raise TypeError("{} is neiter an instance of DateTime nor datetime"
                        .format(repr(dt)))

    def get_records(self):
        """Returns a list of Sample records

        All fields coming from `request.form` have a number prefix,
        e.g. `Contact-0`.
        All fields with the same suffix number are grouped together in a
        record.
        Each record represents the data for one column in the Sample Add
        form and contains a mapping of the fieldName (w/o prefix) -> value.

        Example:
        [{"Contact": "Rita Mohale", ...}, {Contact: "Neil Standard"} ...]
        """
        form = self.request.form
        sample_count = self.get_obj_count()

        records = []
        # Group belonging Sample fields together
        for samplenum in range(sample_count):
            record = {}
            s1 = "-{}".format(samplenum)
            keys = filter(lambda key: s1 in key, form.keys())
            for key in keys:
                new_key = key.replace(s1, "")
                value = form.get(key)
                record[new_key] = value
            records.append(record)
        return records

    def get_uids_from_record(self, record, key):
        """Returns a list of parsed UIDs from a single form field identified
        by the given key.

        A form field ending with `_uid` can contain an empty value, a
        single UID or multiple UIDs separated by a comma.

        This method parses the UID value and returns a list of non-empty UIDs.
        """
        value = record.get(key, None)
        if value is None:
            return []
        if isinstance(value, basestring):
            value = value.split(",")
        return filter(lambda uid: uid, value)

    def get_objs_from_record(self, record, key):
        """Returns a mapping of UID -> object
        """
        uids = self.get_uids_from_record(record, key)
        objs = map(self.get_object_by_uid, uids)
        return dict(zip(uids, objs))

    @cache(cache_key)
    def get_base_info(self, obj):
        """Returns the base info of an object
        """
        if obj is None:
            return {}

        info = {
            "id": obj.getId(),
            "uid": obj.UID(),
            "title": obj.Title(),
            "description": obj.Description(),
            "url": obj.absolute_url(),
        }

        return info

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

        # catalog queries for UI field filtering
        filter_queries = {
            "samplepoint": {
                "getClientUID": [uid, bika_samplepoints_uid],
            },
        }
        info["filter_queries"] = filter_queries

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
        }
        info["filter_queries"] = filter_queries

        return info

    @cache(cache_key)
    def get_container_info(self, obj):
        """Returns the info for a Container
        """
        info = self.get_base_info(obj)
        info.update({})
        return info

    @cache(cache_key)
    def get_preservation_info(self, obj):
        """Returns the info for a Preservation
        """
        info = self.get_base_info(obj)
        info.update({})
        return info

    def ajax_get_global_settings(self):
        """Returns the global Bika settings
        """
        settings = {
        }
        return settings

    def ajax_recalculate_records(self):
        """Recalculate all Sample records and dependencies

            - profiles
        """
        out = {}

        # The sorted records from the request
        records = self.get_records()

        for n, record in enumerate(records):

            # Mapping of client UID -> client object info
            client_metadata = {}
            # Mapping of sampletype UID -> sampletype object info
            sampletype_metadata = {}

            # Internal mappings of UID -> object of selected items in this
            # record
            _clients = self.get_objs_from_record(record, "Client_uid")
            _sampletypes = self.get_objs_from_record(record, "SampleType_uid")

            # CLIENTS
            for uid, obj in _clients.iteritems():
                # get the client metadata
                metadata = self.get_client_info(obj)
                # remember the sampletype metadata
                client_metadata[uid] = metadata

            # SAMPLETYPES
            for uid, obj in _sampletypes.iteritems():
                # get the sampletype metadata
                metadata = self.get_sampletype_info(obj)
                # remember the sampletype metadata
                sampletype_metadata[uid] = metadata


            # Each key `n` (1,2,3...) contains the form data for one
            # Sample Add column in the UI.
            # All relevant form data will be set according to this data.
            out[n] = {
                "client_metadata": client_metadata,
                "sampletype_metadata": sampletype_metadata,
            }

        return out

    def ajax_submit(self):
        """Submit & create the Samples
        """

        # Get Sample required fields (including extended fields)
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

            # Required fields and their values
            required_keys = [field.getName() for field in fields if field.required]
            required_values = [record.get(key) for key in required_keys]
            required_fields = dict(zip(required_keys, required_values))

            # Client field is required but hidden in the sample Add form. We
            # remove
            # it therefore from the list of required fields to let empty
            # columns pass the required check below.
            if record.get("Client", False):
                required_fields.pop('Client', None)

            # None of the required fields are filled, skip this record
            if not any(required_fields.values()):
                continue

            # Missing required fields
            missing = [f for f in required_fields if not record.get(f, None)]

            # If there are required fields missing, flag an error
            for field in missing:
                fieldname = "{}-{}".format(field, n)
                msg = _("Field '{}' is required".format(field))
                fielderrors[fieldname] = msg

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
        samples = []
        for n, record in enumerate(valid_records):
            client_uid = record.get("Client")
            client = self.get_object_by_uid(client_uid)

            if not client:
                raise RuntimeError("No client found")

            # Create the Sample
            try:
                sample = create_sample(client, self.request, record)
            except (KeyError, RuntimeError) as e:
                errors["message"] = e.message
                return {"errors": errors}
            samples.append(sample.Title())

        level = "info"
        if len(samples) == 0:
            message = _('No Sample could be created.')
            level = "error"
        elif len(samples) > 1:
            message = _('Samples ${samples} were successfully created.',
                        mapping={'Samples': safe_unicode(', '.join(samples))})
        else:
            message = _('Analysis request ${Sample} was successfully created.',
                        mapping={'Sample': safe_unicode(samples[0])})

        # Display a portal message
        self.context.plone_utils.addPortalMessage(message, level)

        bika_setup = api.get_bika_setup()
        auto_print = bika_setup.getAutoPrintStickers()

        # https://github.com/bikalabs/bika.lims/pull/2153
        new_samples = [a for a in samples if a[-1] == '1']

        if 'register' in auto_print and new_samples:
            return {
                'success': message,
                'stickers': new_samples,
                'stickertemplate': self.context.bika_setup.getAutoStickerTemplate()
            }
        else:
            return {'success': message}
