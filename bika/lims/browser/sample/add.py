# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.


from plone import protect
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n.locales import locales

from bika.lims import api
from bika.lims import logger

SAMPLE_CONFIGURATION_STORAGE = "bika.lims.browser.sample.manage.add"
SKIP_FIELD_ON_COPY = []


def get_tmp_sample(view):
    if not view.tmp_sample:
        logger.info("*** CREATING TEMPORARY SAMPLE ***")
        view.tmp_sample = view.context.restrictedTraverse(
            "portal_factory/Sample/sample_tmp")
    return view.tmp_sample


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

    def get_currency(self):
        """Returns the configured currency
        """
        bika_setup = api.get_bika_setup()
        currency = bika_setup.getCurrency()
        currencies = locales.getLocale('en').numbers.currencies
        return currencies[currency]

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
        self.tmp_sample = get_tmp_sample(self)
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

    def get_client(self):
        """Returns the Client
        """
        context = self.context
        parent = api.get_parent(context)
        if context.portal_type == "Client":
            return context
        elif parent.portal_type == "Client":
            return parent
        logger.warn(
            'No client got from context {}'.format(context.getId()))
        return None

    def get_fieldname(self, field, samplenum):
        """Generate a new fieldname with a '-<samplenum>' suffix
        """
        name = field.getName()
        # ensure we have only *one* suffix
        base_name = name.split("-")[0]
        suffix = "-{}".format(samplenum)
        return "{}{}".format(base_name, suffix)

    def get_fields_with_visibility(self, visibility, mode="add"):
        """Return the Sample fields with the current visibility
        """
        sample = self.get_sample()
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

    def is_field_visible(self, field):
        """Check if the field is visible
        """
        context = self.context
        fieldname = field.getName()

        # hide the Client field on client and batch contexts
        if fieldname == "Client" and context.portal_type in ("Client", ):
            return False

        return True

    def get_input_widget(self, fieldname, samplenum=0, **kw):
        """Get the field widget of the Sample in column <samplenum>

        :param fieldname: The base fieldname
        :type fieldname: string
        """

        # temporary AR Context
        context = self.get_sample()
        # request = self.request
        schema = context.Schema()
        # get original field in the schema from the base_fieldname
        base_fieldname = fieldname.split("-")[0]
        field = context.getField(base_fieldname)
        if field is None:
            logger.warn(
                "Field {} not found for object type {}"
                .format(base_fieldname, context.portal_type))
            return None
        # fieldname with -<samplenum> suffix
        new_fieldname = self.get_fieldname(field, samplenum)
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
        # XXX: This is actually a hack to make the widget available
        # in the template
        schema._fields[new_fieldname] = new_field
        new_field.getAccessor = getAccessor

        # set the default value
        form = dict()
        form[new_fieldname] = value
        self.request.form.update(form)

        logger.info(
            "get_input_widget: fieldname={} sample={} -> "
            "new_fieldname={} value={}".format(
                fieldname, samplenum, new_fieldname, value))
        widget = context.widget(new_fieldname, **kw)
        return widget


class SampleManageView(BrowserView):
    """Sample Manage View
    """
    template = ViewPageTemplateFile("templates/sample_add_manage.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.tmp_sample = None

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

    def get_sample(self):
        self.tmp_sample = get_tmp_sample(self)
        return self.tmp_sample

    def get_annotation(self):
        bika_setup = api.get_bika_setup()
        return IAnnotations(bika_setup)

    @property
    def storage(self):
        annotation = self.get_annotation()
        if annotation.get(SAMPLE_CONFIGURATION_STORAGE) is None:
            annotation[SAMPLE_CONFIGURATION_STORAGE] = OOBTree()
        return annotation[SAMPLE_CONFIGURATION_STORAGE]

    def flush(self):
        annotation = self.get_annotation()
        if annotation.get(SAMPLE_CONFIGURATION_STORAGE) is not None:
            del annotation[SAMPLE_CONFIGURATION_STORAGE]

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
        """Get Sample field by name
        """
        sample = self.get_sample()
        return sample.getField(name)

    def get_fields(self):
        """Return all Sample fields
        """
        sample = self.get_sample()
        return sample.Schema().fields()

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
