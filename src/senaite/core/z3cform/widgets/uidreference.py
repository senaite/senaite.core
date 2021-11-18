# -*- coding: utf-8 -*-

import json
import string

import six

from bika.lims import api
from Products.CMFPlone.utils import base_hasattr
from senaite.app.supermodel import SuperModel
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IUIDReferenceField
from senaite.core.z3cform.interfaces import IUIDReferenceWidget
from plone.z3cform.fieldsets.interfaces import IDescriptiveGroup
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.converter import TextLinesConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import ISubForm
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.interface import implementer

DISPLAY_TEMPLATE = "<a href='${url}' _target='blank'>${title}</a>"

_marker = object


@adapter(IUIDReferenceField, interfaces.IWidget)
class UIDReferenceDataConverter(TextLinesConverter):
    """Converts the raw field data for widget/field usage
    """

    def toWidgetValue(self, value):
        """Return the value w/o changes

        Note:

        All widget templates use the `get_value` method,
        which ensures a list of UIDs.

        However, `toWidgetValue` is called by `widget.update()` implicitly for
        `self.value`, which is then used by the `get_value` method again.
        """
        return value

    def toFieldValue(self, value):
        """Converts a unicode string to a list of UIDs
        """
        # remove any blank lines at the end
        value = value.rstrip("\r\n")
        return super(UIDReferenceDataConverter, self).toFieldValue(value)


@implementer(IUIDReferenceWidget)
class UIDReferenceWidget(TextLinesWidget):
    """Senaite UID reference widget
    """
    klass = u"senaite-uidreference-widget"

    def __init__(self, request, *args, **kw):
        super(UIDReferenceWidget, self).__init__(request)
        self.request = request

    def update(self):
        super(UIDReferenceWidget, self).update()
        widget.addFieldClass(self)

    def get_form(self):
        """Return the current form of the widget
        """
        form = self.form
        # form is a fieldset group
        if IDescriptiveGroup.providedBy(form):
            form = form.parentForm
        # form is a subform (e.g. DataGridFieldObjectSubForm)
        if ISubForm.providedBy(form):
            form = form.parentForm
        return form

    def get_context(self):
        """Get the current context

        NOTE: If we are in the ++add++ form, `self.context` is the container!
              Therefore, we create one here to have access to the methods.
        """
        schema_iface = self.field.interface
        if schema_iface and schema_iface.providedBy(self.context):
            return self.context

        # we might be in a subform, so try first to retrieve the object from
        # the base form itself first
        form = self.get_form()
        portal_type = getattr(form, "portal_type", None)
        context = getattr(form, "context", None)
        if api.is_object(context):
            if api.get_portal_type(context) == portal_type:
                return context

        # Hack alert!
        # we are in ++add++ form and have no context!
        # Create a temporary object to be able to access class methods
        if not portal_type:
            portal_type = api.get_portal_type(self.context)
        portal_types = api.get_tool("portal_types")
        fti = portal_types[portal_type]
        factory = getUtility(IFactory, fti.factory)
        context = factory("temporary")
        # hook into acquisition chain
        context = context.__of__(self.context)
        return context

    def attr(self, name, default=None):
        """Get the named attribute of the widget or the field
        """
        value = getattr(self, name, _marker)
        if value is _marker:
            return default
        if isinstance(value, six.string_types):
            context = self.get_context()
            if base_hasattr(context, value):
                attr = getattr(context, value)
                if callable(attr):
                    value = attr()
                else:
                    value = attr
        return value

    def get_value(self):
        """Extract the value from the request or get it from the field
        """
        # get the processed value from the `update` method
        value = self.value
        # the value might come from the request, e.g. on object creation
        if isinstance(value, six.string_types):
            value = IDataConverter(self).toFieldValue(value)
        # we handle always lists in the templates
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            value = [value]
        # just to be sure (paranoid)
        return [uid for uid in value if api.is_uid(uid)]

    def get_api_url(self):
        portal = api.get_portal()
        portal_url = api.get_url(portal)
        api_url = "{}/@@API/senaite/v1".format(portal_url)
        return api_url

    def get_display_template(self):
        return self.attr("display_template", DISPLAY_TEMPLATE)

    def get_catalog(self):
        return self.attr("catalog", "portal_catalog")

    def get_query(self):
        return self.attr("query", {})

    def get_columns(self):
        return self.attr("columns", [])

    def get_limit(self):
        return self.attr("limit", 25)

    def is_multi_valued(self):
        return getattr(self.field, "multi_valued", False)

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component
        """
        uids = self.get_value()
        attributes = {
            "data-id": self.id,
            "data-name": self.name,
            "data-uids": uids,
            "data-api_url": self.get_api_url(),
            "data-records": dict(zip(uids, map(self.get_obj_info, uids))),
            "data-query": self.get_query(),
            "data-catalog": self.get_catalog(),
            "data-columns": self.get_columns(),
            "data-display_template": self.get_display_template(),
            "data-limit": self.get_limit(),
            "data-multi_valued": self.is_multi_valued(),
            "data-disabled": self.disabled or False,
            "data-readonly": self.readonly or False,
        }

        # convert all attributes to JSON
        for key, value in attributes.items():
            attributes[key] = json.dumps(value)

        return attributes

    def get_obj_info(self, uid):
        """Returns a dictionary with the object info
        """
        model = SuperModel(uid)
        obj_info = model.to_dict()
        obj_info["uid"] = uid
        obj_info["url"] = api.get_url(model)
        return obj_info

    def render_reference(self, uid):
        """Returns a rendered HTML element for the reference
        """
        template = string.Template(self.get_display_template())
        obj_info = self.get_obj_info(uid)
        return template.safe_substitute(obj_info)


@adapter(IUIDReferenceField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def UIDReferenceWidgetFactory(field, request):
    """Widget factory for UIDReferenceField
    """
    return FieldWidget(field, UIDReferenceWidget(request))
