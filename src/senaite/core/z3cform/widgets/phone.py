# -*- coding: utf-8 -*-

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IPhoneField
from senaite.core.z3cform.interfaces import IPhoneWidget
from z3c.form import interfaces
from z3c.form.browser import text
from z3c.form.browser import widget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer_only


@implementer_only(IPhoneWidget)
class PhoneWidget(text.TextWidget):
    """Input type "tel" widget implementation.
    """
    klass = u"senaite-phone-widget"
    value = u""

    def update(self):
        super(PhoneWidget, self).update()
        widget.addFieldClass(self)
        if self.mode == INPUT_MODE:
            self.addClass("form-control form-control-sm")


@adapter(IPhoneField, ISenaiteFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def PhoneWidgetFactory(field, request):
    """IFieldWidget widget factory for NumberWidget.
    """
    return FieldWidget(field, PhoneWidget(request))
