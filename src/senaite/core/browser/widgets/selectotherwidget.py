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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from bika.lims import _
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import StringWidget
from senaite.core.i18n import translate as t
from senaite.core.z3cform.widgets.selectother.widget import OTHER_OPTION_VALUE


class SelectOtherWidget(StringWidget):
    """Select Other Widget for AT fields
    """
    # CSS class that is picked up by the ReactJS component
    klass = u"senaite-selectother-widget-input"

    _properties = StringWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/selectotherwidget",
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        value = form.get(field.getName(), "")
        if isinstance(value, list):
            if value[0] == OTHER_OPTION_VALUE:
                return value[1], {}
            value = value[0]

        return value, {}

    def get_input_widget_attributes(self, context, field, value):
        """Return input widget attributes for the ReactJS component

        This method get called from the page template to populate the
        attributes that are used by the ReactJS widget component.

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The current field value
        """
        option = ""
        other = ""

        # find out if the value is a predefined option
        choices = self.get_choices(context, field)
        options = dict(choices).keys()
        if value in options:
            option = value
        elif value:
            option = OTHER_OPTION_VALUE
            other = value

        attributes = {
            "data-id": field.getName(),
            "data-name": field.getName(),
            "data-choices": choices,
            "data-option": option,
            "data-option_other": OTHER_OPTION_VALUE,
            "data-other": other,
        }

        # convert all attributes to JSON
        for key, value in attributes.items():
            attributes[key] = json.dumps(value)

        return attributes

    def get_vocabulary(self, context, field):
        func = getattr(field, "Vocabulary", None)
        if callable(func):
            return func(context)
        return None

    def get_choices(self, context, field):
        """Returns the predefined options for this field
        """
        # generate a list of tuples (value, text) from vocabulary
        vocabulary = self.get_vocabulary(context, field)
        choices = list(vocabulary.items()) if vocabulary else []

        # insert the empty option
        choices.insert(0, ("", ""))

        # append the "Other..." choice
        other = (OTHER_OPTION_VALUE, t(_("Other...")))
        choices.append(other)

        return choices


registerWidget(SelectOtherWidget, title="Select Other Widget")
