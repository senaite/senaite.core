# -*- coding: utf-8 -*-

import json

from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.z3cform.interfaces import IQuerySelectWidget
from z3c.form.browser import widget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IField


@implementer_only(IQuerySelectWidget)
class QuerySelectWidget(widget.HTMLInputWidget, Widget):
    """
    """
    klass = u"queryselect-widget"

    def update(self):
        super(QuerySelectWidget, self).update()
        widget.addFieldClass(self)
        if self.mode == INPUT_MODE:
            self.addClass("form-control form-control-sm")

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component
        """
        attributes = {
            "data-id": self.id,
            "data-name": self.name,
        }

        # convert all attributes to JSON
        for key, value in attributes.items():
            attributes[key] = json.dumps(value)

        return attributes


@adapter(IField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def QuerySelectWidgetFactory(field, request):
    """Widget factory
    """
    return FieldWidget(field, QuerySelectWidget(request))
