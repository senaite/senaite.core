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
from Products.Archetypes.public import DateTimeField as BaseField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType
from senaite.core.browser.widgets.datetimewidget import DateTimeWidget


class DateTimeField(BaseField):
    """An improved DateTime Field. It allows to specify
    whether only dates or only times are interesting.

    This field is ported from Products.ATExtensions
    """

    _properties = BaseField._properties.copy()
    _properties.update({
        "type": "datetime_ng",
        "widget": DateTimeWidget,
        "with_time": 1,  # set to False if you want date only objects
        "with_date": 1,  # set to False if you want time only objects
        })
    security = ClassSecurityInfo()


InitializeClass(DateTimeField)


registerField(
    DateTimeField,
    title="DateTime Field",
    description="An improved DateTimeField, which also allows time "
                "or date only specifications.")


registerPropertyType("with_time", "boolean", DateTimeField)
registerPropertyType("with_date", "boolean", DateTimeField)
