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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerWidget


class RecordWidget(StringWidget):
    """Ported from Products.ATExtensions
    """

    _properties = StringWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/record_widget",
        "show_hm": True,  # only meaningful for DateTime subfields
        })
    security = ClassSecurityInfo()


InitializeClass(RecordWidget)

registerWidget(RecordWidget, title="Record", description="")
