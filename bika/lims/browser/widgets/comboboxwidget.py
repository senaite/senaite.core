# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import re

from AccessControl import ClassSecurityInfo

from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget


class ComboBoxWidget(TypesWidget):
    """Widget which presents a list box with a vocabulary, and an text box
    for optionally typing a value.
    """

    security = ClassSecurityInfo()

    _properties = TypesWidget._properties.copy()
    _properties.update(
        {'macro': "bika_widgets/combobox",

         # size: defines the number of items displayed in the selection box.
         'size': '1',
         # width: defines the width of the selection box.
         'width': '10em',
         # width_absolute: set to 1 to make width fixed; else it defines the min-width only.
         'width_absolute': 0,
         # field_config: define
         'field_config': {},
         # field_regex: used by processForm to validate the user input.
         'field_regex': "",
         },
        )

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """A typed in value takes precedence over a selected value.
        """

        name = field.getName()
        otherName = "%s_other" % name
        value = form.get(otherName, empty_marker)
        regex = field.widget.field_regex

        # validate the custom value against the given regex
        if value and not re.match(regex, value):
            value = None
        # If value is an empty string we check if the selection box
        # has a usable value.
        if value is empty_marker or not value:
            value = form.get(name, empty_marker)
        if value is empty_marker:
            return empty_marker
        if not value and emptyReturnsMarker:
            return empty_marker
        return value, {}

registerWidget(
    ComboBoxWidget,
    title='Combo box widget',
    description=("Renders a selection box and a box for "
                 "optionally typing a value instead of selecting one",),
    used_for=('Products.Archetypes.Field.StringField',
              'Products.Archetypes.Field.IntegerField',
              'Products.Archetypes.Field.FloatField',
              'Products.Archetypes.Field.DecimalField',
    ))
