# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Archetypes.Widget import SelectionWidget as _s
from Products.Archetypes.Registry import registerWidget
from AccessControl import ClassSecurityInfo

class UIDSelectionWidget(_s):
    """
    SelectionWidget from Plone Archetypes didn't have correct selected value
    for UID Reference Fields. Overriding it
    for those cases in order to override template and set selected item
    correctly.
    """
    _properties = _s._properties.copy()
    _properties.update({
        'macro': "bika_widgets/uidselection",
    })

    security = ClassSecurityInfo()

    def getValueToView(self, field, context):
        """
        Obtains the value stored in the field to be displayed as a string.
        :return:
        """
        object = field.get(context)
        if object and hasattr(object, 'title'):
            return object.title
        return ''

registerWidget(UIDSelectionWidget)
