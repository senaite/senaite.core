# -*- coding: utf-8 -*-

import json

from bika.lims import api
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IUIDReferenceField
from senaite.core.z3cform.interfaces import IUIDReferenceWidget
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.converter import TextLinesConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer


@adapter(IUIDReferenceField, interfaces.IWidget)
class UIDReferenceDataConverter(TextLinesConverter):
    """Converts the raw field data for widget/field usage
    """

    def toWidgetValue(self, value):
        """Converts a list of UIDs for the display/hidden widget

        returns a list of UIDs when widget is in "display" mode
        returns a unicode string when widget is in "hidden" mode
        """
        if self.widget.mode == "display":
            return value
        return super(UIDReferenceDataConverter, self).toWidgetValue(value)

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

    def get_value(self):
        return self.field.get_raw(self.context)

    def get_catalog(self):
        return getattr(self, "catalog", "portal_catalog")

    def get_query(self):
        return getattr(self, "query", {})

    def get_display_field(self):
        return getattr(self, "display_field", "title")

    def get_columns(self):
        return getattr(self, "columns", [])

    def get_limit(self):
        return getattr(self, "limit", 25)

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
            "data-items": dict(zip(uids, map(self.get_info_for, uids))),
            "data-query": self.get_query(),
            "data-catalog": self.get_catalog(),
            "data-columns": self.get_columns(),
            "data-display_field": self.get_display_field(),
            "data-limit": self.get_limit(),
            "data-multi_valued": self.is_multi_valued(),
            "data-disabled": self.disabled or False,
            "data-readonly": self.readonly or False,
        }

        # convert all attributes to JSON
        for key, value in attributes.items():
            attributes[key] = json.dumps(value)

        return attributes

    def get_info_for(self, uid):
        """Get display object information for the given UID
        """
        obj = api.get_object(uid)
        info = {
            "uid": uid,
            "title": api.get_title(obj),
            "path": api.get_path(obj),
            "url": api.get_url(obj),
        }

        display_key = self.display_field
        if display_key not in info:
            display_value = getattr(obj, display_key, None)
            if display_value is None:
                display_value = api.get_title(obj) or api.get_id(obj)
            info[display_key] = display_value

        return info


@adapter(IUIDReferenceField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def UIDReferenceWidgetFactory(field, request):
    """Widget factory for UIDReferenceField
    """
    return FieldWidget(field, UIDReferenceWidget(request))
