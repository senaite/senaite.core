# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from datetime import datetime

from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from Products.Five.browser import BrowserView
from plone import protect
from plone.memoize.volatile import cache
from zope.annotation.interfaces import IAnnotations
from zope.i18n.locales import locales
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from bika.lims import api
from bika.lims import logger
from bika.lims.utils import cache_key
from bika.lims.utils import returns_json


class BaseManageAddView(BrowserView):
    """
    Base view to create a visibility and order manager for an Add View.
    """
    template = None

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.tmp_obj = None
        self.CONFIGURATION_STORAGE = None
        self.SKIP_FIELD_ON_COPY = []

    def __call__(self):
        protect.CheckAuthenticator(self.request.form)
        form = self.request.form
        if form.get("submitted", False) and form.get("save", False):
            order = form.get("order")
            self.set_field_order(order)
            visibility = form.get("visibility")
            self.set_field_visibility(visibility)
        if form.get("submitted", False) and form.get("reset", False):
            self.flush()
        return self.template()

    def get_obj(self):
        """
        This method should return a temporary object. This object should be
        of the same type as the one we are creating.
        :return: ATObjectType
        """
        raise NotImplementedError("get_obj is not implemented.")

    def get_annotation(self):
        bika_setup = api.get_bika_setup()
        return IAnnotations(bika_setup)

    @property
    def storage(self):
        annotation = self.get_annotation()
        if annotation.get(self.CONFIGURATION_STORAGE) is None:
            annotation[self.CONFIGURATION_STORAGE] = OOBTree()
        return annotation[self.CONFIGURATION_STORAGE]

    def flush(self):
        annotation = self.get_annotation()
        if annotation.get(self.CONFIGURATION_STORAGE) is not None:
            del annotation[self.CONFIGURATION_STORAGE]

    def set_field_order(self, order):
        self.storage.update({"order": order})

    def get_field_order(self):
        order = self.storage.get("order")
        if order is None:
            return map(lambda f: f.getName(), self.get_fields())
        return order

    def set_field_visibility(self, visibility):
        self.storage.update({"visibility": visibility})

    def get_field_visibility(self):
        return self.storage.get("visibility")

    def is_field_visible(self, field):
        if field.required:
            return True
        visibility = self.get_field_visibility()
        if visibility is None:
            return True
        return visibility.get(field.getName(), True)

    def get_field(self, name):
        """Get a field of the object by name
        """
        obj = self.get_obj()
        return obj.getField(name)

    def get_fields(self):
        """Return all Object fields
        """
        obj = self.get_obj()
        return obj.Schema().fields()

    def get_sorted_fields(self):
        """Return the sorted fields
        """
        inf = float("inf")
        order = self.get_field_order()

        def field_cmp(field1, field2):
            _n1 = field1.getName()
            _n2 = field2.getName()
            _i1 = _n1 in order and order.index(_n1) + 1 or inf
            _i2 = _n2 in order and order.index(_n2) + 1 or inf
            return cmp(_i1, _i2)

        return sorted(self.get_fields(), cmp=field_cmp)

    def get_fields_with_visibility(self, visibility="edit", mode="add"):
        """Return the fields with visibility
        """
        fields = self.get_sorted_fields()

        out = []

        for field in fields:
            v = field.widget.isVisible(
                self.context, mode, default='invisible', field=field)

            if self.is_field_visible(field) is False:
                v = "hidden"

            visibility_guard = True
            # visibility_guard is a widget field defined in the schema in order
            # to know the visibility of the widget when the field is related to
            # a dynamically changing content such as workflows. For instance
            # those fields related to the workflow will be displayed only if
            # the workflow is enabled, otherwise they should not be shown.
            if 'visibility_guard' in dir(field.widget):
                visibility_guard = eval(field.widget.visibility_guard)
            if v == visibility and visibility_guard:
                out.append(field)

        return out


class BaseAddView(BrowserView):
    """
    Base Object Add view

    This class offers the necessary methods to create a Add view.
    """
    template = None

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.request = request
        self.context = context
        self.fieldvalues = {}
        self.tmp_obj = None
        self.icon = None
        self.portal = None
        self.portal_url = None
        self.bika_setup = None
        self.came_from = None
        self.obj_count = None
        self.specifications = None
        self.ShowPrices = None
        self.SKIP_FIELD_ON_COPY = []

    def __call__(self):
        self.portal = api.get_portal()
        self.portal_url = self.portal.absolute_url()
        self.bika_setup = api.get_bika_setup()
        self.request.set('disable_plone.rightcolumn', 1)
        self.came_from = "add"
        self.tmp_obj = self.get_obj()
        self.obj_count = self.get_obj_count()
        self.ShowPrices = self.bika_setup.getShowPrices()

    def get_view_url(self):
        """Return the current view url including request parameters
        """
        request = self.request
        url = request.getURL()
        qs = request.getHeader("query_string")
        if not qs:
            return url
        return "{}?{}".format(url, qs)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

    def get_currency(self):
        """Returns the configured currency
        """
        bika_setup = api.get_bika_setup()
        currency = bika_setup.getCurrency()
        currencies = locales.getLocale('en').numbers.currencies
        return currencies[currency]

    def get_obj_count(self):
        """Return the obj_count request parameter
        """
        try:
            obj_count = int(self.request.form.get("obj_count", 1))
        except (TypeError, ValueError):
            obj_count = 1
        return obj_count

    def get_obj(self):
        """Create a temporary Object to fetch the fields from
        """
        raise NotImplementedError("get_obj is not implemented.")

    def get_obj_schema(self):
        """Return the Object schema
        """
        obj = self.get_obj()
        return obj.Schema()

    def get_obj_fields(self):
        """Return the Object schema fields (including extendend fields)
        """
        schema = self.get_obj_schema()
        return schema.fields()

    def get_fieldname(self, field, objnum):
        """Generate a new fieldname with a '-<objnum>' suffix
        """
        name = field.getName()
        # ensure we have only *one* suffix
        base_name = name.split("-")[0]
        suffix = "-{}".format(objnum)
        return "{}{}".format(base_name, suffix)

    def get_input_widget(self, fieldname, objnum=0, **kw):
        """Get the field widget of the Object in column <objnum>

        :param fieldname: The base fieldname
        :type fieldname: string
        """

        # temporary Object Context
        context = self.get_obj()
        # request = self.request
        schema = context.Schema()

        # get original field in the schema from the base_fieldname
        base_fieldname = fieldname.split("-")[0]
        field = context.getField(base_fieldname)

        # fieldname with -<objnum> suffix
        new_fieldname = self.get_fieldname(field, objnum)
        new_field = field.copy(name=new_fieldname)

        # get the default value for this field
        fieldvalues = self.fieldvalues
        field_value = fieldvalues.get(new_fieldname)
        # request_value = request.form.get(new_fieldname)
        # value = request_value or field_value
        value = field_value

        def getAccessor(instance):
            def accessor(**kw):
                return value
            return accessor

        # inject the new context for the widget renderer
        # see: Products.Archetypes.Renderer.render
        kw["here"] = context
        kw["context"] = context
        kw["fieldName"] = new_fieldname

        # make the field available with this name
        # XXX: This is actually a hack to make the widget
        # available in the template
        schema._fields[new_fieldname] = new_field
        new_field.getAccessor = getAccessor

        # set the default value
        form = dict()
        form[new_fieldname] = value
        self.request.form.update(form)

        logger.info(
            "get_input_widget: fieldname={} objnum={} -> "
            "new_fieldname={} value={}"
            .format(fieldname, objnum, new_fieldname, value))
        widget = context.widget(new_fieldname, **kw)
        return widget

    def get_copy_from(self):
        """Returns a mapping of UID index -> Object
        """
        # Create a mapping of source Objects for copy
        copy_from = self.request.form.get("copy_from", "").split(",")
        # clean out empty strings
        copy_from_uids = filter(lambda x: x, copy_from)
        out = dict().fromkeys(range(len(copy_from_uids)))
        for n, uid in enumerate(copy_from_uids):
            obj = self.get_object_by_uid(uid)
            if obj is None:
                continue
            out[n] = obj
        logger.info("get_copy_from: uids={}".format(copy_from_uids))
        return out

    def get_default_value(self, field, context):
        """Get the default value of the field
        """
        name = field.getName()
        default = field.getDefault(context)
        if name == "Batch":
            batch = self.get_batch()
            if batch is not None:
                default = batch
        if name == "Client":
            client = self.get_client()
            if client is not None:
                default = client
        if name == "Contact":
            contact = self.get_default_contact()
            if contact is not None:
                default = contact
        logger.info(
            "get_default_value: context={} field={} value={}"
            .format(context, name, default))
        return default

    def get_field_value(self, field, context):
        """Get the stored value of the field
        """
        name = field.getName()
        value = context.getField(name).get(context)
        logger.info(
            "get_field_value: context={} field={} value={}"
            .format(context, name, value))
        return value

    def get_client(self):
        """Returns the Client
        """
        context = self.context
        parent = api.get_parent(context)
        if context.portal_type == "Client":
            return context
        elif parent.portal_type == "Client":
            return parent
        elif context.portal_type == "Batch":
            return context.getClient()
        elif parent.portal_type == "Batch":
            return context.getClient()
        return None

    def get_batch(self):
        """Returns the Batch
        """
        context = self.context
        parent = api.get_parent(context)
        if context.portal_type == "Batch":
            return context
        elif parent.portal_type == "Batch":
            return parent
        return None

    def generate_fieldvalues(self, count=1):
        """Returns a mapping of '<fieldname>-<count>' to the default value
        of the field or the field value of the source Object (copy from)
        """
        raise NotImplementedError("generate_fieldvalues is not implemented.")

    def is_field_visible(self, field):
        """Check if the field is visible
        """
        context = self.context
        fieldname = field.getName()

        # hide the Client field on client and batch contexts
        if fieldname == "Client" and context.portal_type in ("Client", ):
            return False

        # hide the Batch field on batch contexts
        if fieldname == "Batch" and context.portal_type in ("Batch", ):
            return False

        return True

    def get_fields_with_visibility(self, visibility, mode="add"):
        """Return the Object fields with the current visibility.

        It is recommended to get those values from an AddManagerView
        """
        raise NotImplementedError(
            "get_fields_with_visibility is not implemented.")


class BaseAjaxAddView(BaseAddView):
    """Ajax helpers for an Object Add form
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        BaseAddView.__init__(self, context, request)
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
        raise TypeError("{} is neither an instance of DateTime nor datetime"
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
        obj_count = self.get_obj_count()

        records = []
        # Group belonging Object fields together
        for objenum in range(obj_count):
            record = {}
            s1 = "-{}".format(objenum)
            keys = filter(lambda key: s1 in key, form.keys())
            for key in keys:
                new_key = key.replace(s1, "")
                value = form.get(key)
                record[new_key] = value
            records.append(record)
        return records

    def get_objs_from_record(self, record, key):
        """Returns a mapping of UID -> object
        """
        uids = self.get_uids_from_record(record, key)
        objs = map(self.get_object_by_uid, uids)
        return dict(zip(uids, objs))

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
        bika_setup = api.get_bika_setup()
        settings = {
            "show_prices": bika_setup.getShowPrices(),
        }
        return settings

    def ajax_recalculate_records(self):
        """Recalculate all Object records and dependencies
        """
        raise NotImplementedError(
            "ajax_recalculate_records is not implemented.")

    def ajax_submit(self):
        """Submit & create the Object
        """
        raise NotImplementedError(
            "ajax_recalculate_records is not implemented.")
