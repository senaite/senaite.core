# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Archetypes.Widget import DecimalWidget as _d
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget

from AccessControl import ClassSecurityInfo

_marker = []


class DecimalWidget(_d):
    _properties = _d._properties.copy()
    _properties.update({
        'macro': "bika_widgets/decimal",
        'unit': '',
    })

    security = ClassSecurityInfo()


registerWidget(DecimalWidget,
               title='Decimal',
               description=('Renders a HTML text input box which '
                            'accepts a fixed point value'),
               )

registerPropertyType('unit', 'string', DecimalWidget)
