# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget


class RemarksWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': 'bika_widgets/remarkswidget',
        })

    security = ClassSecurityInfo()
