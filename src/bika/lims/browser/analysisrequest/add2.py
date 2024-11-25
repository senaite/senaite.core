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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta

import six
import transaction
from bika.lims import POINTS_OF_CAPTURE
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api.analysisservice import get_calculation_dependencies_for
from bika.lims.api.analysisservice import get_service_dependencies_for
from bika.lims.api.security import check_permission
from bika.lims.decorators import returns_json
from bika.lims.interfaces import IAddSampleConfirmation
from bika.lims.interfaces import IAddSampleFieldsFlush
from bika.lims.interfaces import IAddSampleObjectInfo
from bika.lims.interfaces import IAddSampleRecordsValidator
from bika.lims.interfaces import IGetDefaultFieldValueARAddHook
from bika.lims.interfaces.field import IUIDReferenceField
from bika.lims.utils.analysisrequest import create_analysisrequest as crar
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from plone import protect
from plone.memoize import view as viewcache
from plone.memoize.volatile import DontCache
from plone.memoize.volatile import cache
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Archetypes.interfaces import IField
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.api import dtime
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.p3compat import cmp
from senaite.core.permissions import TransitionMultiResults
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapters
from zope.component import queryAdapter
from zope.i18n.locales import locales
from zope.i18nmessageid import Message
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

AR_CONFIGURATION_STORAGE = "bika.lims.browser.analysisrequest.manage.add"
SKIP_FIELD_ON_COPY = ["Sample", "PrimaryAnalysisRequest", "Remarks",
                      "NumSamples", "_ARAttachment"]


def cache_key(method, self, obj):
    if obj is None:
        raise DontCache
    return api.get_cache_key(obj)


class AnalysisRequestAddView(BrowserView):
    """AR Add view
    """
    template = ViewPageTemplateFile("templates/ar_add2.pt")

    def __init__(self, context, request):
        super(AnalysisRequestAddView, self).__init__(context, request)
        # disable CSRF protection
        alsoProvides(request, IDisableCSRFProtection)
        self.request = request
        self.context = context
        self.fieldvalues = {}
        self.tmp_ar = None

    def __call__(self):
        self.portal = api.get_portal()
        self.portal_url = self.portal.absolute_url()
        self.setup = api.get_setup()
        self.came_from = "add"
        self.tmp_ar = self.get_ar()
        self.ar_count = self.get_ar_count()
        self.fieldvalues = self.generate_fieldvalues(self.ar_count)
        self.ShowPrices = self.setup.getShowPrices()
        self.theme = api.get_view("senaite_theme")
        self.icon = self.theme.icon_url("Sample")
        logger.debug("*** Prepared data for {} ARs ***".format(self.ar_count))
        return self.template()

    def get_view_url(self):
        """Return the current view url including request parameters
        """
        request = self.request
        url = request.getURL()
        qs = request.getHeader("query_string")
        if not qs:
            return url
        return "{}?{}".format(url, qs)

    # N.B.: We are caching here persistent objects!
    #       It should be safe to do this but only on the view object,
    #       because it get recreated per request (transaction border).
    @viewcache.memoize
    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID '%s' !!" % uid)
        return obj

    @viewcache.memoize
    def analyses_required(self):
        """Check if analyses are required
        """
        setup = api.get_setup()
        return setup.getSampleAnalysesRequired()

    def get_currency(self):
        """Returns the configured currency
        """
        setup = api.get_setup()
        currency = setup.getCurrency()
        currencies = locales.getLocale("en").numbers.currencies
        return currencies[currency]

    def get_ar_count(self):
        """Return the ar_count request paramteter
        """
        ar_count = 1
        try:
            ar_count = int(self.request.form.get("ar_count", 1))
        except (TypeError, ValueError):
            ar_count = 1
        return ar_count

    def get_ar(self):
        """Create a temporary AR to fetch the fields from
        """
        if not self.tmp_ar:
            logger.debug("*** CREATING TEMPORARY AR ***")
            self.tmp_ar = self.context.restrictedTraverse(
                "portal_factory/AnalysisRequest/Request new analyses")
        return self.tmp_ar

    def get_ar_schema(self):
        """Return the AR schema
        """
        logger.debug("*** GET AR SCHEMA ***")
        ar = self.get_ar()
        return ar.Schema()

    def get_ar_fields(self):
        """Return the AR schema fields (including extendend fields)
        """
        logger.debug("*** GET AR FIELDS ***")
        schema = self.get_ar_schema()
        return schema.fields()

    def get_fieldname(self, field, arnum):
        """Generate a new fieldname with a '-<arnum>' suffix
        """
        name = field.getName()
        # ensure we have only *one* suffix
        base_name = name.split("-")[0]
        suffix = "-{}".format(arnum)
        return "{}{}".format(base_name, suffix)

    def get_input_widget(self, fieldname, arnum=0, **kw):
        """Get the field widget of the AR in column <arnum>

        :param fieldname: The base fieldname
        :type fieldname: string
        """

        # temporary AR Context
        context = self.get_ar()
        # request = self.request
        schema = context.Schema()

        # get original field in the schema from the base_fieldname
        base_fieldname = fieldname.split("-")[0]
        field = context.getField(base_fieldname)

        # fieldname with -<arnum> suffix
        new_fieldname = self.get_fieldname(field, arnum)
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
        # XXX: This is a hack to make the widget available in the template
        schema._fields[new_fieldname] = new_field
        new_field.getAccessor = getAccessor
        new_field.getEditAccessor = getAccessor

        # set the default value
        form = dict()
        form[new_fieldname] = value
        self.request.form.update(form)
        logger.debug("get_input_widget: fieldname={} arnum={} "
                     "-> new_fieldname={} value={}".format(
                         fieldname, arnum, new_fieldname, value))
        widget = context.widget(new_fieldname, **kw)
        return widget

    def get_copy_from(self):
        """Returns a mapping of UID index -> AR object
        """
        # Create a mapping of source ARs for copy
        copy_from = self.request.form.get("copy_from", "").split(",")
        # clean out empty strings
        copy_from_uids = filter(lambda x: x, copy_from)
        out = dict().fromkeys(range(len(copy_from_uids)))
        for n, uid in enumerate(copy_from_uids):
            ar = self.get_object_by_uid(uid)
            if ar is None:
                continue
            out[n] = ar
        logger.info("get_copy_from: uids={}".format(copy_from_uids))
        return out

    def get_default_value(self, field, context, arnum):
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
        # only set default contact for first column
        if name == "Contact" and arnum == 0:
            contact = self.get_default_contact()
            if contact is not None:
                default = contact
        if name == "Sample":
            sample = self.get_sample()
            if sample is not None:
                default = sample
        # Querying for adapters to get default values from add-ons':
        # We don't know which fields the form will render since
        # some of them may come from add-ons. In order to obtain the default
        # value for those fields we take advantage of adapters. Adapters
        # registration should have the following format:
        # < adapter
        #   factory = ...
        #   for = "*"
        #   provides = "bika.lims.interfaces.IGetDefaultFieldValueARAddHook"
        #   name = "<fieldName>_default_value_hook"
        # / >
        hook_name = name + '_default_value_hook'
        adapter = queryAdapter(
            self.request,
            name=hook_name,
            interface=IGetDefaultFieldValueARAddHook)
        if adapter is not None:
            default = adapter(self.context)
        logger.debug("get_default_value: context={} field={} value={} arnum={}"
                     .format(context, name, default, arnum))
        return default

    def get_field_value(self, field, context):
        """Get the stored value of the field
        """
        name = field.getName()
        value = context.getField(name).get(context)
        logger.debug("get_field_value: context={} field={} value={}".format(
            context, name, value))
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

    def get_sample(self):
        """Returns the Sample
        """
        context = self.context
        if context.portal_type == "Sample":
            return context
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
        ar_context = self.get_ar()

        # mapping of UID index to AR objects {1: <AR1>, 2: <AR2> ...}
        copy_from = self.get_copy_from()

        out = {}
        # the original schema fields of an AR (including extended fields)
        fields = self.get_ar_fields()

        # generate fields for all requested ARs
        for arnum in range(count):
            source = copy_from.get(arnum)
            parent = None
            if source is not None:
                parent = self.get_parent_ar(source)
            for field in fields:
                value = None
                fieldname = field.getName()
                if source and fieldname not in SKIP_FIELD_ON_COPY:
                    # get the field value stored on the source
                    context = parent or source
                    value = self.get_field_value(field, context)
                else:
                    # get the default value of this field
                    value = self.get_default_value(
                        field, ar_context, arnum=arnum)
                # store the value on the new fieldname
                new_fieldname = self.get_fieldname(field, arnum)
                out[new_fieldname] = value

        return out

    def get_default_contact(self, client=None):
        """Logic refactored from JavaScript:

        * If client only has one contact, and the analysis request comes from
        * a client, then Auto-complete first Contact field.
        * If client only has one contect, and the analysis request comes from
        * a batch, then Auto-complete all Contact field.

        :returns: The default contact for the AR
        :rtype: Client object or None
        """
        catalog = api.get_tool(CONTACT_CATALOG)
        client = client or self.get_client()
        path = api.get_path(self.context)
        if client:
            path = api.get_path(client)
        query = {
            "portal_type": "Contact",
            "path": {
                "query": path,
                "depth": 1
            },
            "is_active": True,
        }
        contacts = catalog(query)
        if len(contacts) == 1:
            return api.get_object(contacts[0])
        elif client == api.get_current_client():
            # Current user is a Client contact. Use current contact
            current_user = api.get_current_user()
            return api.get_user_contact(current_user,
                                        contact_types=["Contact"])

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
        """Return the AR fields with the current visibility
        """
        ar = self.get_ar()
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
        bsc = api.get_tool("senaite_catalog_setup")
        query = {
            "portal_type": "AnalysisCategory",
            "is_active": True,
            "sort_on": "sortable_title",
        }
        categories = bsc(query)
        client = self.get_client()
        if client and restricted:
            restricted_categories = client.getRestrictedCategories()
            restricted_category_ids = map(
                lambda c: c.getId(), restricted_categories)
            # keep correct order of categories
            if restricted_category_ids:
                categories = filter(
                    lambda c: c.getId in restricted_category_ids, categories)
        return categories

    def get_points_of_capture(self):
        items = POINTS_OF_CAPTURE.items()
        return OrderedDict(items)

    def get_services(self, poc="lab"):
        """Return all Services

        :param poc: Point of capture (lab/field)
        :type poc: string
        :returns: Mapping of category -> list of services
        :rtype: dict
        """
        bsc = api.get_tool("senaite_catalog_setup")
        query = {
            "portal_type": "AnalysisService",
            "point_of_capture": poc,
            "is_active": True,
            "sort_on": "sortable_title",
        }
        services = bsc(query)
        categories = self.get_service_categories(restricted=False)
        analyses = {key: [] for key in map(lambda c: c.Title, categories)}

        # append the empty category as well
        analyses[""] = []

        for brain in services:
            category = self.get_category_title(brain)
            if category in analyses:
                analyses[category].append(brain)
        return analyses

    def get_category_title(self, service):
        """Return the title of the category the service is assigned to
        """
        service = api.get_object(service)
        cat_uid = service.getRawCategory()
        if not cat_uid:
            return ""
        cat = self.get_object_by_uid(cat_uid)
        return api.get_title(cat)

    @cache(cache_key)
    def get_service_uid_from(self, analysis):
        """Return the service from the analysis
        """
        analysis = api.get_object(analysis)
        return api.get_uid(analysis.getAnalysisService())

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


class AnalysisRequestManageView(BrowserView):
    """AR Manage View
    """
    template = ViewPageTemplateFile("templates/ar_add_manage.pt")

    def __init__(self, context, request):
        # disable CSRF protection
        alsoProvides(request, IDisableCSRFProtection)
        self.context = context
        self.request = request
        self.tmp_ar = None

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

    def get_ar(self):
        if not self.tmp_ar:
            self.tmp_ar = self.context.restrictedTraverse(
                "portal_factory/AnalysisRequest/Request new analyses")
        return self.tmp_ar

    def get_annotation(self):
        setup = api.get_setup()
        return IAnnotations(setup)

    @property
    def storage(self):
        annotation = self.get_annotation()
        if annotation.get(AR_CONFIGURATION_STORAGE) is None:
            annotation[AR_CONFIGURATION_STORAGE] = OOBTree()
        return annotation[AR_CONFIGURATION_STORAGE]

    def flush(self):
        annotation = self.get_annotation()
        if annotation.get(AR_CONFIGURATION_STORAGE) is not None:
            del annotation[AR_CONFIGURATION_STORAGE]

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
        """Get AR field by name
        """
        ar = self.get_ar()
        return ar.getField(name)

    def get_fields(self):
        """Return all AR fields
        """
        ar = self.get_ar()
        return ar.Schema().fields()

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


class ajaxAnalysisRequestAddView(AnalysisRequestAddView):
    """Ajax helpers for the analysis request add form
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ajaxAnalysisRequestAddView, self).__init__(context, request)
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

    @viewcache.memoize
    def is_uid_reference_field(self, fieldname):
        """Checks if the field is a UID reference field
        """
        schema = self.get_ar_schema()
        field = schema.get(fieldname)
        if field is None:
            return False
        return IUIDReferenceField.providedBy(field)

    @viewcache.memoize
    def is_multi_reference_field(self, fieldname):
        """Checks if the field is a multi UID reference field
        """
        if not self.is_uid_reference_field(fieldname):
            return False
        schema = self.get_ar_schema()
        field = schema.get(fieldname)
        return getattr(field, "multiValued", False)

    def get_records(self):
        """Returns a list of AR records

        Fields coming from `request.form` have a number prefix, e.g. Contact-0.
        Fields with the same suffix number are grouped together in a record.
        Each record represents the data for one column in the AR Add form and
        contains a mapping of the fieldName (w/o prefix) -> value.

        Example:
        [{"Contact": "Rita Mohale", ...}, {Contact: "Neil Standard"} ...]
        """
        form = self.request.form
        ar_count = self.get_ar_count()

        records = []
        # Group belonging AR fields together
        for arnum in range(ar_count):
            record = {}
            s1 = "-{}".format(arnum)
            keys = filter(lambda key: s1 in key, form.keys())
            for key in keys:
                new_key = key.replace(s1, "")
                value = form.get(key)
                if self.is_uid_reference_field(new_key):
                    # handle new UID reference fields that store references in
                    # a textarea (one UID per line)
                    uids = value.split("\r\n")
                    # remove empties
                    uids = list(filter(None, uids))
                    if self.is_multi_reference_field(new_key):
                        value = uids
                    else:
                        value = uids[0] if len(uids) > 0 else ""
                record[new_key] = value
            records.append(record)
        return records

    def get_uids_from_record(self, record, key):
        """Returns a list of parsed UIDs from a single form field identified by
        the given key.

        A form field of an UID reference can contain an empty value, a single
        UID or multiple UIDs separated by a \r\n.

        This method parses the UID value and returns a list of non-empty UIDs.
        """
        if not self.is_uid_reference_field(key):
            return []
        value = record.get(key, None)
        if not value:
            return []
        if api.is_string(value):
            value = value.split("\r\n")
        return list(filter(None, value))

    @cache(cache_key)
    def get_base_info(self, obj):
        """Returns the base info of an object
        """
        if obj is None:
            return {}

        info = {
            "id": api.get_id(obj),
            "uid": api.get_uid(obj),
            "url": api.get_url(obj),
            "title": api.get_title(obj),
            "field_values": {},
            "filter_queries": {},
        }

        return info

    @cache(cache_key)
    def get_client_info(self, obj):
        """Returns the client info of an object
        """
        info = self.get_base_info(obj)

        # Set the default contact, but only if empty. The Contact field is
        # flushed each time the Client changes, so we can assume that if there
        # is a selected contact, it belongs to current client already
        default_contact = self.get_default_contact(client=obj)
        if default_contact:
            contact_info = self.get_contact_info(default_contact)
            contact_info.update({"if_empty": True})
            info["field_values"].update({
                "Contact": contact_info
            })

        # Set default CC Email field
        info["field_values"].update({
            "CCEmails": {"value": obj.getCCEmails(), "if_empty": True}
        })

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
        cccontacts = []
        for contact in obj.getCCContact():
            uid = api.get_uid(contact)
            fullname = contact.getFullname()
            email = contact.getEmailAddress()
            cccontacts.append({
                "uid": uid,
                "title": fullname,
                "fullname": fullname,
                "email": email
            })

        info.update({
            "fullname": fullname,
            "email": email,
            "field_values": {
                "CCContact": cccontacts
            },
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
            "keyword": obj.getKeyword(),
            "methods": map(self.get_method_info, obj.getMethods()),
            "calculation": self.get_calculation_info(obj.getCalculation()),
            "price": obj.getPrice(),
            "currency_symbol": self.get_currency().symbol,
            "accredited": obj.getAccredited(),
            "category": obj.getCategoryTitle(),
            "poc": obj.getPointOfCapture(),
            "conditions": self.get_conditions_info(obj),
            "max_holding_time": obj.getMaxHoldingTime(),
        })

        dependencies = get_calculation_dependencies_for(obj).values()
        info["dependencies"] = map(self.get_base_info, dependencies)
        return info

    @cache(cache_key)
    def get_template_info(self, obj):
        """Returns the info for a Template
        """
        client = self.get_client()
        client_uid = api.get_uid(client) if client else ""

        sample_type = obj.getSampleType()
        sample_type_uid = api.get_uid(sample_type) if sample_type else ""
        sample_type_title = sample_type.Title() if sample_type else ""

        sample_point = obj.getSamplePoint()
        sample_point_uid = api.get_uid(sample_point) if sample_point else ""
        sample_point_title = sample_point.Title() if sample_point else ""

        service_uids = []
        analyses_partitions = {}
        services = obj.getRawServices()

        for record in services:
            service_uid = record.get("uid")
            service_uids.append(service_uid)
            analyses_partitions[service_uid] = record.get("part_id")

        info = self.get_base_info(obj)
        info.update({
            "analyses_partitions": analyses_partitions,
            "client_uid": client_uid,
            "composite": obj.getComposite(),
            "partitions": obj.getPartitions(),
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

        info.update({
            "prefix": obj.getPrefix(),
            "minimum_volume": obj.getMinimumVolume(),
            "hazardous": obj.getHazardous(),
            "retention_period": obj.getRetentionPeriod(),
        })

        return info

    @cache(cache_key)
    def get_primaryanalysisrequest_info(self, obj):
        """Returns the info for a Primary Sample
        """
        info = self.get_base_info(obj)

        batch = obj.getBatch()
        client = obj.getClient()
        sample_type = obj.getSampleType()
        sample_condition = obj.getSampleCondition()
        storage_location = obj.getStorageLocation()
        sample_point = obj.getSamplePoint()
        container = obj.getContainer()
        deviation = obj.getSamplingDeviation()
        cccontacts = obj.getCCContact() or []
        contact = obj.getContact()

        info.update({
            "composite": obj.getComposite(),
        })

        # Set the fields for which we want the value to be set automatically
        # when the primary sample is selected
        info["field_values"].update({
            "Client": self.to_field_value(client),
            "Contact": self.to_field_value(contact),
            "CCContact": map(self.to_field_value, cccontacts),
            "CCEmails": obj.getCCEmails(),
            "Batch": self.to_field_value(batch),
            "DateSampled": {"value": self.to_iso_date(obj.getDateSampled())},
            "SamplingDate": {"value": self.to_iso_date(obj.getSamplingDate())},
            "SampleType": self.to_field_value(sample_type),
            "EnvironmentalConditions": {
                "value": obj.getEnvironmentalConditions(),
            },
            "ClientSampleID": {"value": obj.getClientSampleID()},
            "ClientReference": {"value": obj.getClientReference()},
            "ClientOrderNumber": {"value": obj.getClientOrderNumber()},
            "SampleCondition": self.to_field_value(sample_condition),
            "SamplePoint": self.to_field_value(sample_point),
            "StorageLocation": self.to_field_value(storage_location),
            "Container": self.to_field_value(container),
            "SamplingDeviation": self.to_field_value(deviation),
            "Composite": {"value": obj.getComposite()}
        })

        return info

    @cache(cache_key)
    def get_conditions_info(self, obj):
        conditions = obj.getConditions()
        for condition in conditions:
            choices = condition.get("choices", "")
            options = filter(None, choices.split('|'))
            if options:
                condition.update({"options": options})
        return conditions

    @cache(cache_key)
    def to_field_value(self, obj):
        return {
            "uid": obj and api.get_uid(obj) or "",
            "title": obj and api.get_title(obj) or ""
        }

    def to_attachment_record(self, fileupload):
        """Returns a dict-like structure with suitable information for the
        proper creation of Attachment objects
        """
        if not fileupload.filename:
            # ZPublisher.HTTPRequest.FileUpload is empty
            return None
        return {
            "AttachmentFile": fileupload,
            "AttachmentType": "",
            "RenderInReport": False,
            "AttachmentKeys": "",
            "Service": "",
        }

    def create_attachment(self, sample, attachment_record):
        """Creates an attachment for the given sample with the information
        provided in attachment_record
        """
        # create the attachment object
        client = sample.getClient()
        attachment = api.create(client, "Attachment", **attachment_record)
        uid = attachment_record.get("Service")
        if not uid:
            # Link the attachment to the sample
            sample.addAttachment(attachment)
            return attachment

        # Link the attachment to analyses with this service uid
        ans = sample.objectValues(spec="Analysis")
        ans = filter(lambda an: an.getRawAnalysisService() == uid, ans)
        for analysis in ans:
            attachments = analysis.getRawAttachment()
            analysis.setAttachment(attachments + [attachment])

        # Assign the attachment to the given condition
        condition_title = attachment_record.get("Condition")
        if not condition_title:
            return attachment

        conditions = sample.getServiceConditions()
        for condition in conditions:
            is_uid = condition.get("uid") == uid
            is_title = condition.get("title") == condition_title
            is_file = condition.get("type") == "file"
            if all([is_uid, is_title, is_file]):
                condition["value"] = api.get_uid(attachment)
        sample.setServiceConditions(conditions)
        return attachment

    def ajax_get_global_settings(self):
        """Returns the global Bika settings
        """
        setup = api.get_setup()
        settings = {
            "show_prices": setup.getShowPrices(),
        }
        return settings

    def ajax_is_reference_value_allowed(self):
        """Checks if the current reference value is allowed for the query
        """
        payload = self.get_json()

        catalog = payload.get("catalog", "")
        query = payload.get("query", {})
        uids = payload.get("uids", [])
        name = payload.get("name", "")
        label = payload.get("label", "")
        field = label or name

        # Remove sort_limit to prevent false negatives
        query.pop("sort_limit", None)

        # Skip the catalog search if we can assume to be allowed
        white_keys = ["portal_type", "sort_on", "sort_order", "is_active"]
        if set(query.keys()).issubset(white_keys):
            return {"allowed": True}

        if all([catalog, query, uids]):
            # check if the current value is allowed for the new query
            brains = api.search(query, catalog=catalog)
            allowed_uids = list(map(api.get_uid, brains))
            if set(uids).issubset(allowed_uids):
                return {"allowed": True}

        message = {
            "title": _("Field flushed"),
            "text": _(u"The value of field '%s' was emptied. "
                      u"Please select a new value." % api.safe_unicode(field)),
        }

        return {
            "allowed": False,
            "message": message,
        }

    def ajax_get_flush_settings(self):
        """Returns the settings for fields flush

        NOTE: We automatically flush fields if the current value of a dependent
              reference field is *not* allowed by the set new query.
              -> see self.ajax_is_reference_value_allowed()
              Therefore, it makes only sense for non-reference fields!
        """
        flush_settings = {
            "Client": [
            ],
            "Contact": [
            ],
            "SampleType": [
            ],
            "PrimarySample": [
                "EnvironmentalConditions",
            ]
        }

        # Maybe other add-ons have additional fields that require flushing
        for name, ad in getAdapters((self.context,), IAddSampleFieldsFlush):
            logger.info("Additional flush settings from {}".format(name))
            additional_settings = ad.get_flush_settings()
            for key, values in additional_settings.items():
                new_values = flush_settings.get(key, []) + values
                flush_settings[key] = list(set(new_values))

        return flush_settings

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
        out = {}
        records = self.get_records()
        for num_sample, record in enumerate(records):
            # Get reference fields metadata
            metadata = self.get_record_metadata(record)

            # service_to_templates, template_to_services
            templates_additional = self.get_template_additional_info(metadata)
            metadata.update(templates_additional)

            # service_to_profiles, profiles_to_services
            profiles_additional = self.get_profiles_additional_info(metadata)
            metadata.update(profiles_additional)

            # dependencies
            dependencies = self.get_unmet_dependencies_info(metadata)
            metadata.update(dependencies)

            # services conducted beyond the holding time limit
            beyond = self.get_services_beyond_holding_time(record)
            metadata["beyond_holding_time"] = beyond

            # Set the metadata for current sample number (column)
            out[num_sample] = metadata

        return out

    @viewcache.memoize
    def get_services_max_holding_time(self):
        """Returns a dict where the key is the uid of active services and the
        value is a dict representing the maximum holding time in days, hours
        and minutes. The dictionary only contains uids for services that have
        a valid maximum holding time set
        """
        services = {}
        query = {
            "portal_type": "AnalysisService",
            "point_of_capture": "lab",
            "is_active": True,
        }
        brains = api.search(query, SETUP_CATALOG)
        for brain in brains:
            obj = api.get_object(brain)
            max_holding_time = obj.getMaxHoldingTime()
            if max_holding_time:
                uid = api.get_uid(brain)
                services[uid] = max_holding_time.copy()

        return services

    def get_services_beyond_holding_time(self, record):
        """Return a list with the uids of the services that cannot be selected
        because would be conducted past the holding time limit
        """
        # get the date to start count from
        start_date = self.get_start_holding_date(record)
        if not start_date:
            return []

        # get the timezone of the start date for correct comparisons
        tz = dtime.get_timezone(start_date)

        uids = []

        # get the max holding times grouped by service uid
        services = self.get_services_max_holding_time()
        for uid, max_holding_time in services.items():

            # calculate the maximum holding date
            delta = timedelta(minutes=api.to_minutes(**max_holding_time))
            max_holding_date = start_date + delta

            # TypeError: can't compare offset-naive and offset-aware datetimes
            max_date = dtime.to_ansi(max_holding_date)
            now = dtime.to_ansi(dtime.now(), timezone=tz)
            if now > max_date:
                uids.append(uid)

        return uids

    def get_start_holding_date(self, record):
        """Returns the datetime used to calculate the holding time limit,
        typically the sample collection date.
        """
        sampled = record.get("DateSampled")
        return dtime.to_dt(sampled)

    def get_record_metadata(self, record):
        """Returns the metadata for the record passed in
        """
        metadata = {}
        extra_fields = {}
        for key, value in record.items():
            metadata_key = "{}_metadata".format(key.lower())
            metadata[metadata_key] = {}

            if not value:
                continue

            # Get objects information (metadata)
            objs_info = self.get_objects_info(record, key)
            objs_uids = map(lambda obj: obj["uid"], objs_info)
            metadata[metadata_key] = dict(zip(objs_uids, objs_info))

            # Grab 'field_values' fields to be recalculated too
            for obj_info in objs_info:
                field_values = obj_info.get("field_values", {})
                for field_name, field_value in field_values.items():
                    if not isinstance(field_value, dict):
                        # this is probably a list, e.g. "Profiles" field
                        continue
                    uids = self.get_uids_from_record(field_value, "uid")
                    if len(uids) == 1:
                        extra_fields[field_name] = uids[0]

        # Populate metadata with object info from extra fields (hidden fields)
        for field_name, uid in extra_fields.items():
            key = "{}_metadata".format(field_name.lower())
            if metadata.get(key):
                # This object has been processed already, skip
                continue
            obj = self.get_object_by_uid(uid)
            if not obj:
                continue
            obj_info = self.get_object_info(
                obj, field_name, record=extra_fields)
            if not obj_info or "uid" not in obj_info:
                continue
            metadata[key] = {obj_info["uid"]: obj_info}

        return metadata

    def get_template_additional_info(self, metadata):
        template_to_services = {}
        service_to_templates = {}
        service_metadata = metadata.get("service_metadata", {})
        template = metadata.get("template_metadata", {})
        # We don't expect more than one template, but who knows about future?
        for uid, obj_info in template.items():
            obj = self.get_object_by_uid(uid)
            # get the template services
            # [{'part_id': 'part-1', 'uid': '...'},
            # {'part_id': 'part-1', 'uid': '...'}]
            services = obj.getRawServices() or []
            # get all UIDs of the template records
            service_uids = map(lambda rec: rec.get("uid"), services)
            # remember a mapping of template uid -> service
            template_to_services[uid] = service_uids
            # remember a mapping of service uid -> templates
            for service_uid in service_uids:
                # remember the template of all services
                if service_uid in service_to_templates:
                    service_to_templates[service_uid].append(uid)
                else:
                    service_to_templates[service_uid] = [uid]
                # remember the service metadata
                if service_uid not in service_metadata:
                    service = self.get_object_by_uid(service_uid)
                    service_info = self.get_service_info(service)
                    service_metadata[service_uid] = service_info

        return {
            "service_to_templates": service_to_templates,
            "template_to_services": template_to_services,
            "service_metadata": service_metadata,
        }

    def get_profiles_additional_info(self, metadata):
        profile_to_services = {}
        service_to_profiles = metadata.get("service_to_profiles", {})
        service_metadata = metadata.get("service_metadata", {})
        profiles = metadata.get("profiles_metadata", {})
        for uid, obj_info in profiles.items():
            obj = self.get_object_by_uid(uid)
            # get all services of this profile
            services = obj.getServices()
            # get all UIDs of the profile services
            service_uids = map(api.get_uid, services)
            # remember all services of this profile
            profile_to_services[uid] = service_uids
            # remember a mapping of service uid -> profiles
            for service in services:
                # get the UID of this service
                service_uid = api.get_uid(service)
                # remember the profiles of this service
                if service_uid in service_to_profiles:
                    service_to_profiles[service_uid].append(uid)
                else:
                    service_to_profiles[service_uid] = [uid]
                # remember the service metadata
                if service_uid not in service_metadata:
                    service_info = self.get_service_info(service)
                    service_metadata[service_uid] = service_info

        return {
            "profile_to_services": profile_to_services,
            "service_to_profiles": service_to_profiles,
            "service_metadata": service_metadata,
        }

    def get_unmet_dependencies_info(self, metadata):
        # mapping of service UID -> unmet service dependency UIDs
        unmet_dependencies = {}
        services = metadata.get("service_metadata", {}).copy()
        for uid, obj_info in services.items():
            obj = self.get_object_by_uid(uid)
            # get the dependencies of this service
            deps = get_service_dependencies_for(obj)

            # check for unmet dependencies
            for dep in deps["dependencies"]:
                # we use the UID to test for equality
                dep_uid = api.get_uid(dep)
                if dep_uid not in services:
                    if uid in unmet_dependencies:
                        unmet_dependencies[uid].append(self.get_base_info(dep))
                    else:
                        unmet_dependencies[uid] = [self.get_base_info(dep)]
            # remember the dependencies in the service metadata
            metadata["service_metadata"][uid].update({
                "dependencies": map(
                    self.get_base_info, deps["dependencies"]),
            })
        return {
            "unmet_dependencies": unmet_dependencies
        }

    def get_objects_info(self, record, key):
        """
        Returns a list with the metadata for the objects the field with
        field_name passed in refers to. Returns empty list if the field is not
        a reference field or the record for this key cannot be handled
        :param record: a record for a single sample (column)
        :param key: The key of the field from the record (e.g. Client_uid)
        :return: list of info objects
        """
        # Get the objects from this record. Returns a list because the field
        # can be multivalued
        uids = self.get_uids_from_record(record, key)
        objects = map(self.get_object_by_uid, uids)
        objects = map(lambda obj: self.get_object_info(
            obj, key, record=record), objects)
        return filter(None, objects)

    def object_info_cache_key(method, self, obj, key, **kw):
        if obj is None or not key:
            raise DontCache
        field_name = key.lower()
        obj_key = api.get_cache_key(obj)
        return "-".join([field_name, obj_key] + kw.keys())

    @cache(object_info_cache_key)
    def get_object_info(self, obj, key, record=None):
        """Returns the object info metadata for the passed in object and key
        :param obj: the object from which extract the info from
        :param key: The key of the field from the record (e.g. Client_uid)
        :return: dict that represents the object
        """
        # Check if there is a function to handle objects for this field
        field_name = key
        func_name = "get_{}_info".format(field_name.lower())
        func = getattr(self, func_name, None)

        # always ensure we have a record
        if record is None:
            record = {}

        # Get the info for each object
        info = callable(func) and func(obj) or self.get_base_info(obj)

        # update query filters based on record values
        func_name = "get_{}_queries".format(field_name.lower())
        func = getattr(self, func_name, None)
        if callable(func):
            info["filter_queries"] = func(obj, record)

        # Check if there is any adapter to handle objects for this field
        for name, adapter in getAdapters((obj, ), IAddSampleObjectInfo):
            logger.info("adapter for '{}': {}".format(field_name, name))
            ad_info = adapter.get_object_info_with_record(record)
            self.update_object_info(info, ad_info)

        return info

    def get_client_queries(self, obj, record=None):
        """Returns the filter queries to be applied to other fields based on
        both the Client object and record
        """
        # UID of the client
        uid = api.get_uid(obj)

        # catalog queries for UI field filtering
        queries = {
            "Contact": {
                "getParentUID": [uid]
            },
            "CCContact": {
                "getParentUID": [uid]
            },
            "SamplePoint": {
                "getClientUID": [uid, ""],
            },
            "Template": {
                "getClientUID": [uid, ""],
            },
            "Profiles": {
                "getClientUID": [uid, ""],
            },
            "Specification": {
                "getClientUID": [uid, ""],
            },
            "Sample": {
                "getClientUID": [uid],
            },
            "Batch": {
                "getClientUID": [uid, ""],
            },
            "PrimaryAnalysisRequest": {
                "getClientUID": [uid, ""],
            }
        }

        # additional filtering by sample type
        record = record if record else {}
        sample_type_uid = record.get("SampleType")
        if api.is_uid(sample_type_uid):
            fields = ["Template", "Specification", "Profiles", "SamplePoint"]
            for field in fields:
                queries[field]["sampletype_uid"] = [sample_type_uid, ""]

        return queries

    def get_sampletype_queries(self, obj, record=None):
        """Returns the filter queries to apply to other fields based on both
        the SampleType object and record
        """
        uid = api.get_uid(obj)
        queries = {
            # Display Sample Points that have this sample type assigned plus
            # those that do not have a sample type assigned
            "SamplePoint": {
                "sampletype_uid": [uid, ""],
            },
            # Display Analysis Profiles that have this sample type assigned
            # in addition to those that do not have a sample profile assigned
            "Profiles": {
                "sampletype_uid": [uid, ""],
            },
            # Display Specifications that have this sample type assigned only
            "Specification": {
                "sampletype_uid": uid,
            },
            # Display Sample Templates that have this sample type assigned plus
            # those that do not have a sample type assigned
            "Template": {
                "sampletype_uid": [uid, ""],
            }
        }

        # additional filters by client
        record = record if record else {}
        client = record.get("Client") or self.get_client()
        client_uid = api.get_uid(client) if client else None
        if client_uid:
            fields = ["Template", "Specification", "Profiles", "SamplePoint"]
            for field in fields:
                queries[field]["getClientUID"] = [client_uid, ""]

        return queries

    def update_object_info(self, base_info, additional_info):
        """Updates the dictionaries for keys 'field_values' and 'filter_queries'
        from base_info with those defined in additional_info. If base_info is
        empty or None, updates the whole base_info dict with additional_info
        """
        if not base_info:
            base_info.update(additional_info)
            return

        # Merge field_values info
        field_values = base_info.get("field_values", {})
        field_values.update(additional_info.get("field_values", {}))
        base_info["field_values"] = field_values

        # Merge filter_queries info
        filter_queries = base_info.get("filter_queries", {})
        filter_queries.update(additional_info.get("filter_queries", {}))
        base_info["filter_queries"] = filter_queries

    def show_recalculate_prices(self):
        setup = api.get_setup()
        return setup.getShowPrices()

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
        setup = api.get_setup()

        member_discount = float(setup.getMemberDiscount())
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

            profile_uids = record.get("Profiles", [])
            profiles = map(self.get_object_by_uid, profile_uids)
            services = map(self.get_object_by_uid, record.get("Analyses", []))

            # ANALYSIS PROFILES PRICE
            for profile in profiles:
                use_profile_price = profile.getUseAnalysisProfilePrice()
                if not use_profile_price:
                    continue

                profile_price = float(profile.getAnalysisProfilePrice())
                arprofiles_price += profile_price
                arprofiles_vat_amount += profile.getVATAmount()
                profile_services = profile.getServices()
                services_from_priced_profile.extend(profile_services)

            # ANALYSIS SERVICES PRICE
            for service in services:
                # skip services that are part of a priced profile
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
                logger.info("Member discount applies with {}%".format(
                    member_discount))
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

    def get_field(self, field_name):
        """Returns the field from the temporary sample with the given name
        """
        if IField.providedBy(field_name):
            return field_name

        for field in self.get_ar_fields():
            if field.getName() == field_name:
                return field
        return None

    def get_field_label(self, field):
        """Returns the translated label of the given field
        """
        field = self.get_field(field)
        if not field:
            return ""

        instance = self.get_ar()
        label = field.widget.Label(instance)
        if isinstance(label, Message):
            return self.context.translate(label)
        return label

    def check_confirmation(self):
        """Returns a dict when user confirmation is required for the creation of
        samples. Returns None otherwise
        """
        if self.request.form.get("confirmed") == "1":
            # User pressed the "yes" button in the confirmation pane already
            return None

        # Find out if there is a confirmation adapter available
        adapter = queryAdapter(self.request, IAddSampleConfirmation)
        if not adapter:
            return None

        # Extract records from the request and call the adapter
        records = self.get_records()
        return adapter.check_confirmation(records)

    def ajax_cancel(self):
        """Cancel and redirect to configured actions
        """
        message = _("Sample creation cancelled")
        self.context.plone_utils.addPortalMessage(message, "info")
        return self.handle_redirect([], message)

    def ajax_submit(self):
        """Create samples and redirect to configured actions
        """
        # Check if there is the need to display a confirmation pane
        confirmation = self.check_confirmation()
        if confirmation:
            return {"confirmation": confirmation}

        # Get the maximum number of samples to create per record
        max_samples_record = self.get_max_samples_per_record()

        # Get AR required fields (including extended fields)
        fields = self.get_ar_fields()
        required_keys = [field.getName() for field in fields if field.required]

        # extract records from request
        records = self.get_records()

        fielderrors = {}
        errors = {"message": "", "fielderrors": {}}

        valid_records = []

        # Validate required fields
        for num, record in enumerate(records):

            # Extract file uploads (fields ending with _file)
            # These files will be added later as attachments
            file_fields = filter(lambda f: f.endswith("_file"), record)
            uploads = map(lambda f: record.pop(f), file_fields)
            attachments = [self.to_attachment_record(f) for f in uploads]

            # Required fields and their values
            required_values = [record.get(key) for key in required_keys]
            required_fields = dict(zip(required_keys, required_values))

            # Client field is required but hidden in the AR Add form. We remove
            # it therefore from the list of required fields to let empty
            # columns pass the required check below.
            if record.get("Client", False):
                required_fields.pop("Client", None)

            # Check if analyses are required for sample registration
            if not self.analyses_required():
                required_fields.pop("Analyses", None)

            # Contacts get pre-filled out if only one contact exists.
            # We won't force those columns with only the Contact filled out to
            # be required.
            contact = required_fields.pop("Contact", None)

            # None of the required fields are filled, skip this record
            if not any(required_fields.values()):
                continue

            # Re-add the Contact
            required_fields["Contact"] = contact

            # Check if the contact belongs to the selected client
            contact_obj = api.get_object(contact, None)
            if not contact_obj:
                fielderrors["Contact"] = _("No valid contact")
            else:
                parent_uid = api.get_uid(api.get_parent(contact_obj))
                if parent_uid != record.get("Client"):
                    msg = _("Contact does not belong to the selected client")
                    fielderrors["Contact"] = msg

            # Check if the number of samples per record is permitted
            num_samples = self.get_num_samples(record)
            if num_samples > max_samples_record:
                msg = _(u"error_analyssirequest_numsamples_above_max",
                        u"The number of samples to create for the record "
                        u"'Sample ${record_index}' (${num_samples}) is above "
                        u"${max_num_samples}",
                        mapping={
                            "record_index": num+1,
                            "num_samples": num_samples,
                            "max_num_samples": max_samples_record,
                        })
                fielderrors["NumSamples"] = self.context.translate(msg)

            # Missing required fields
            missing = [f for f in required_fields if not record.get(f, None)]

            # Handle fields from Service conditions
            for condition in record.get("ServiceConditions", []):
                if condition.get("type") == "file":
                    # Add the file as an attachment
                    file_upload = condition.get("value")
                    att = self.to_attachment_record(file_upload)
                    if att:
                        # Add the file as an attachment
                        att.update({
                            "Service": condition.get("uid"),
                            "Condition": condition.get("title"),
                        })
                        attachments.append(att)
                    # Reset the condition value
                    filename = file_upload and file_upload.filename or ""
                    condition.value = filename

                if condition.get("required") == "on":
                    if not condition.get("value"):
                        title = condition.get("title")
                        if title not in missing:
                            missing.append(title)

            # If there are required fields missing, flag an error
            for field in missing:
                fieldname = "{}-{}".format(field, num)
                label = self.get_field_label(field)
                msg = self.context.translate(_("Field '{}' is required"))
                fielderrors[fieldname] = msg.format(label)

            # Process and validate field values
            valid_record = dict()
            tmp_sample = self.get_ar()
            for field in fields:
                field_name = field.getName()
                field_value = record.get(field_name)
                if field_value in ['', None]:
                    continue

                # process the value as the widget would usually do
                process_value = field.widget.process_form
                value, msgs = process_value(tmp_sample, field, record)
                if not value:
                    continue

                # store the processed value as the valid record
                valid_record[field_name] = value

                # validate the value
                error = field.validate(value, tmp_sample)
                if error:
                    field_name = "{}-{}".format(field_name, num)
                    fielderrors[field_name] = error

            # add the attachments to the record
            valid_record["attachments"] = filter(None, attachments)

            # append the valid record to the list of valid records
            valid_records.append(valid_record)

        # return immediately with an error response if some field checks failed
        if fielderrors:
            errors["fielderrors"] = fielderrors
            return {'errors': errors}

        # do a custom validation of records. For instance, we may want to rise
        # an error if a value set to a given field is not consistent with a
        # value set to another field
        validators = getAdapters((self.request, ), IAddSampleRecordsValidator)
        for name, validator in validators:
            validation_err = validator.validate(valid_records)
            if validation_err:
                # Not valid, return immediately with an error response
                return {"errors": validation_err}

        # create the samples
        try:
            samples = self.create_samples(valid_records)
        except Exception as e:
            errors["message"] = str(e)
            logger.error(e, exc_info=True)
            return {"errors": errors}

        # We keep the title to check if AR is newly created
        # and UID to print stickers
        ARs = OrderedDict()
        for sample in samples:
            ARs[sample.Title()] = sample.UID()

        level = "info"
        if len(ARs) == 0:
            message = _('No Samples could be created.')
            level = "error"
        elif len(ARs) > 1:
            message = _('Samples ${ARs} were successfully created.',
                        mapping={'ARs': safe_unicode(', '.join(ARs.keys()))})
        else:
            message = _('Sample ${AR} was successfully created.',
                        mapping={'AR': safe_unicode(ARs.keys()[0])})

        # Display a portal message
        self.context.plone_utils.addPortalMessage(message, level)

        return self.handle_redirect(ARs.values(), message)

    def create_samples(self, records):
        """Creates samples for the given records
        """
        samples = []
        for record in records:
            client_uid = record.get("Client")
            client = self.get_object_by_uid(client_uid)
            if not client:
                raise ValueError("No client found")

            # Pop the attachments
            attachments = record.pop("attachments", [])

            # Create as many samples as required
            num_samples = self.get_num_samples(record)
            for idx in range(num_samples):
                sample = crar(client, self.request, record)

                # Create the attachments
                for attachment_record in attachments:
                    self.create_attachment(sample, attachment_record)

                transaction.savepoint(optimistic=True)
                samples.append(sample)

        return samples

    def get_num_samples(self, record):
        """Return the number of samples to create for the given record
        """
        num_samples = record.get("NumSamples", 1)
        num_samples = api.to_int(num_samples, default=1)
        return num_samples if num_samples > 0 else 1

    @viewcache.memoize
    def get_max_samples_per_record(self):
        """Returns the maximum number of samples that can be created for each
        record/column from the sample add form
        """
        setup = api.get_senaite_setup()
        return setup.getMaxNumberOfSamplesAdd()

    def is_automatic_label_printing_enabled(self):
        """Returns whether the automatic printing of barcode labels is active
        """
        setup = api.get_setup()
        auto_print = setup.getAutoPrintStickers()
        auto_receive = setup.getAutoreceiveSamples()
        action = "receive" if auto_receive else "register"
        return action in auto_print

    def handle_redirect(self, uids, message):
        """Handle redirect after sample creation or cancel
        """
        # Automatic label printing
        setup = api.get_setup()
        auto_print = self.is_automatic_label_printing_enabled()
        # Check if immediate results entry is enabled in setup and the current
        # user has enough privileges to do so
        multi_results = setup.getImmediateResultsEntry() and check_permission(
            TransitionMultiResults, self.context)
        redirect_to = self.context.absolute_url()

        # UIDs of the new created samples
        sample_uids = ",".join(uids)
        # UIDs of previous created samples when save&copy was selected
        prev_sample_uids = self.request.get("sample_uids")
        if prev_sample_uids:
            sample_uids = ",".join([prev_sample_uids, sample_uids])
        # Get the submit action (either "Save" or "Save and Copy")
        submit_action = self.request.form.get("submit_action", "save")
        if submit_action == "save_and_copy":
            # redirect to the sample add form, but keep track of
            # previous created sample UIDs
            redirect_to = "{}/ar_add?copy_from={}&ar_count={}&sample_uids={}" \
                .format(self.context.absolute_url(),
                        ",".join(uids),  # copy_from
                        len(uids),  # ar_count
                        sample_uids)  # sample_uids
        elif auto_print and sample_uids:
            redirect_to = "{}/sticker?autoprint=1&items={}".format(
                self.context.absolute_url(), sample_uids)
        elif multi_results and sample_uids:
            redirect_to = "{}/multi_results?uids={}".format(
                self.context.absolute_url(),
                sample_uids)
        return {
            "success": message,
            "redirect_to": redirect_to,
        }

    def get_json(self, encoding="utf8"):
        """Extracts the JSON from the request
        """
        body = self.request.get("BODY", "{}")

        def encode_hook(pairs):
            """This hook is called for dicitionaries on JSON deserialization

            It is used to encode unicode strings with the given encoding,
            because ZCatalogs have sometimes issues with unicode queries.
            """
            new_pairs = []
            for key, value in pairs.iteritems():
                # Encode the key
                if isinstance(key, six.string_types):
                    key = key.encode(encoding)
                # Encode the value
                if isinstance(value, six.string_types):
                    value = value.encode(encoding)
                new_pairs.append((key, value))
            return dict(new_pairs)

        return json.loads(body, object_hook=encode_hook)
