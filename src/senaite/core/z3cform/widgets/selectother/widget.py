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
from bika.lims import _
from senaite.core.i18n import translate as t
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import ISelectOtherField
from senaite.core.z3cform.interfaces import ISelectOtherWidget
from senaite.core.z3cform.widgets.basewidget import BaseWidget
from z3c.form.browser import widget
from z3c.form.browser.widget import HTMLTextInputWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory

OTHER_OPTION_VALUE = "__other__"


@adapter(ISelectOtherField, ISelectOtherWidget)
class SelectOtherDataConverter(BaseDataConverter):
    """Converts the value between the field and the widget
    """

    def toWidgetValue(self, value):
        """Converts from field value to widget
        """
        return value

    def toFieldValue(self, value):
        """Converts from widget to field value
        """
        if isinstance(value, list):
            if value[0] == OTHER_OPTION_VALUE:
                return str(value[1])
            value = value[0]
        return str(value)


@implementer(ISelectOtherWidget)
class SelectOtherWidget(HTMLTextInputWidget, BaseWidget):
    """Widget for the selection of an option from a pre-populated list or
    manual introduction
    """
    klass = u"senaite-selectother-widget-input"

    def get_display_value(self):
        """Returns the value to display
        """
        choices = self.get_choices()
        choices = dict(choices)
        return choices.get(self.value) or self.value

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component
        """
        option = ""
        other = ""

        # find out if the value is a predefined option
        choices = self.get_choices()
        options = dict(choices).keys()
        if self.value in options:
            option = self.value
        elif self.value:
            option = OTHER_OPTION_VALUE
            other = self.value

        attributes = {
            "data-id": self.id,
            "data-name": self.name,
            "data-choices": choices,
            "data-option": option,
            "data-option_other": OTHER_OPTION_VALUE,
            "data-other": other,
        }

        # convert all attributes to JSON
        for key, value in attributes.items():
            attributes[key] = json.dumps(value)

        return attributes

    def update(self):
        """Computes self.value for the widget templates

        see z3c.form.widget.Widget
        """
        super(SelectOtherWidget, self).update()
        widget.addFieldClass(self)

    def get_vocabulary(self):
        if not self.field:
            return None

        vocabulary = getattr(self.field, "vocabularyName", None)
        if not vocabulary:
            return None

        factory = queryUtility(IVocabularyFactory, vocabulary,)
        if not factory:
            return None

        return factory(self.context)

    def get_choices(self):
        """Returns the predefined options for this field
        """
        # generate a list of tuples (value, text) from vocabulary
        vocabulary = self.get_vocabulary()
        choices = [(term.value, t(term.title)) for term in vocabulary]

        # insert the empty option
        choices.insert(0, ("", ""))

        # append the "Other..." choice
        other = (OTHER_OPTION_VALUE, t(_("Other...")))
        choices.append(other)

        return choices


@adapter(ISelectOtherField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def SelectOtherWidgetFactory(field, request):
    """Widget factory for SelectOther field
    """
    return FieldWidget(field, SelectOtherWidget(request))
