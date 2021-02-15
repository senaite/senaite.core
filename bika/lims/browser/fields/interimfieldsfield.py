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

import copy

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Registry import registerField
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysisService


class InterimFieldsField(RecordsField):
    """a list of InterimFields for calculations """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'fixedSize': 0,
        'minimalSize': 0,
        'maximalSize': 9999,
        'type': 'InterimFields',
        'subfields': ('keyword', 'title', 'value', 'choices', 'unit', 'report', 'hidden', 'wide'),
        'required_subfields': ('keyword', 'title'),
        'subfield_labels': {
            'keyword': _('Keyword'),
            'title': _('Field Title'),
            'value': _('Default value'),
            'choices': _('Choices'),
            'unit': _('Unit'),
            'report': _('Report'),
            'hidden': _('Hidden Field'),
            'wide': _('Apply wide'),
        },
        'subfield_types': {
            'hidden': 'boolean',
            'value': 'float',
            'choices': 'string',
            'wide': 'boolean',
            'report': 'boolean',
        },
        'subfield_sizes': {
            'keyword': 20,
            'title': 20,
            'value': 10,
            'choices': 50,
            'unit': 10,
        },
        "subfield_maxlength": {
            "choices": -1,
        },
        'subfield_validators': {
            'keyword': 'interimfieldsvalidator',
            'title': 'interimfieldsvalidator',
            'value': 'interimfieldsvalidator',
            'unit': 'interimfieldsvalidator',
            'choices': 'interimfieldsvalidator'
        },
    })
    security = ClassSecurityInfo()

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        an_interims = RecordsField.get(self, instance, **kwargs) or []
        if not IAnalysisService.providedBy(instance):
            return an_interims

        # This instance implements IAnalysisService
        calculation = instance.getCalculation()
        if not calculation:
            return an_interims

        # Ensure the service includes the interims from the calculation
        an_keys = map(lambda interim: interim['keyword'], an_interims)
        # Avoid references from the service interims to the calculation interims
        calc_interims = copy.deepcopy(calculation.getInterimFields())
        calc_interims = filter(lambda inter: inter['keyword'] not in an_keys,
                               calc_interims)
        return an_interims + calc_interims


registerField(
    InterimFieldsField,
    title="Interim Fields",
    description="Used for storing Interim Fields or Interim Results."
)
