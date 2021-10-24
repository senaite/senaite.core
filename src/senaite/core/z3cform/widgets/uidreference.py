# -*- coding: utf-8 -*-

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
    klass = u"uidreference-widget"

    def __init__(self, request, *args, **kw):
        super(UIDReferenceWidget, self).__init__(request)
        self.request = request

    def update(self):
        super(UIDReferenceWidget, self).update()
        widget.addFieldClass(self)

    def get_info_for(self, uid):
        obj = api.get_object(uid)
        return {
            "title": api.get_title(obj),
            "path": api.get_path(obj),
            "url": api.get_url(obj),
        }


@adapter(IUIDReferenceField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def UIDReferenceWidgetFactory(field, request):
    """Widget factory for UIDReferenceField
    """
    return FieldWidget(field, UIDReferenceWidget(request))
