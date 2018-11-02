# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
        'subfields': ('keyword', 'title', 'value', 'unit', 'report', 'hidden', 'wide'),
        'required_subfields': ('keyword', 'title'),
        'subfield_labels': {
            'keyword': _('Keyword'),
            'title': _('Field Title'),
            'value': _('Default value'),
            'unit': _('Unit'),
            'report': _('Report'),
            'hidden': _('Hidden Field'),
            'wide': _('Apply wide'),
        },
        'subfield_types': {
            'hidden': 'boolean',
            'value': 'float',
            'wide': 'boolean',
            'report': 'boolean',
        },
        'subfield_sizes': {
            'keyword': 20,
            'title': 20,
            'value': 10,
            'unit': 10,
        },
        'subfield_validators': {
            'keyword': 'interimfieldsvalidator',
            'title': 'interimfieldsvalidator',
            'value': 'interimfieldsvalidator',
            'unit': 'interimfieldsvalidator',
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
        calc_interims = calculation.getInterimFields()
        calc_interims = filter(lambda key: key not in an_keys, calc_interims)
        return an_interims + calc_interims


registerField(
    InterimFieldsField,
    title="Interim Fields",
    description="Used for storing Interim Fields or Interim Results."
)
