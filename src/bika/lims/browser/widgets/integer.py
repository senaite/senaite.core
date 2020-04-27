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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes.Widget import IntegerWidget as _i
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget

from AccessControl import ClassSecurityInfo

_marker = []


class IntegerWidget(_i):
    _properties = _i._properties.copy()
    _properties.update({
        'macro': "bika_widgets/integer",
        'unit': '',
    })

    security = ClassSecurityInfo()

registerWidget(IntegerWidget,
               title='Integer',
               description=('Renders a HTML text input box which '
                            'accepts a integer value'),
               )

registerPropertyType('unit', 'string', IntegerWidget)
