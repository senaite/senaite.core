# -*- coding: utf-8 -*-

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IIntField
from senaite.core.z3cform.interfaces import INumberWidget
from z3c.form import interfaces
from z3c.form.browser import text
from z3c.form.browser import widget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer_only


@implementer_only(INumberWidget)
class NumberWidget(text.TextWidget):
    """Input type "number" widget implementation.
    """
    klass = u"number-widget"
    value = u""

    def update(self):
        super(NumberWidget, self).update()
        widget.addFieldClass(self)
        if self.mode == INPUT_MODE:
            self.addClass("form-control")

    @property
    def min(self):
        if not self.field:
            return None
        return self.field.min

    @property
    def max(self):
        if not self.field:
            return None
        return self.field.max


@adapter(IIntField, ISenaiteFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def IntFieldWidget(field, request):
    """IFieldWidget widget factory for NumberWidget.
    """
    return FieldWidget(field, NumberWidget(request))
