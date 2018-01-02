# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Archetypes.Registry import registerWidget
from AccessControl import ClassSecurityInfo
from . import SelectionWidget

class PrioritySelectionWidget(SelectionWidget):
    """
    Displays a Selection List, but with styled options in accordance with the
    Priority value selected
    """
    _properties = SelectionWidget._properties.copy()
    security = ClassSecurityInfo()

registerWidget(PrioritySelectionWidget)
