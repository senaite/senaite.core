# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Archetypes.Widget import SelectionWidget as _s
from Products.Archetypes.Registry import registerWidget

from AccessControl import ClassSecurityInfo

class UIDSelectionWidget(_s):
    """
    SelectionWidget from Plone Archetypes didn't have correct selected value for UID Reference Fields. Overriding it
    for those cases in order to override template and set selected item correctly.
    """
    _properties = _s._properties.copy()
    _properties.update({
        'macro': "bika_widgets/uidselection",
    })

    security = ClassSecurityInfo()

registerWidget(UIDSelectionWidget)
