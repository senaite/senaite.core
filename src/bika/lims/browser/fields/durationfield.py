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

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t


class DurationField(RecordField):

    """ Stores duration in Days/Hours/Minutes """
    security = ClassSecurityInfo()
    _properties = RecordField._properties.copy()
    _properties.update({
        'type': 'duration',
        'subfields': ('days', 'hours', 'minutes'),
        'subfield_labels': {'days': _('Days'),
                            'hours': _('Hours'),
                            'minutes': _('Minutes')},
        'subfield_sizes': {'days': 2,
                           'hours': 2,
                           'minutes': 2},
        'subfield_validators': {'days': 'duration_validator',
                                'hours': 'duration_validator',
                                'minutes': 'duration_validator'},
    })

registerField(DurationField,
              title="Duration",
              description="Used for storing durations",
              )
