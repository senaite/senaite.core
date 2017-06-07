# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from AccessControl import ClassSecurityInfo
from Products.ATExtensions.field import RecordsField
from Products.Archetypes.Registry import registerField


class PrefixesField(RecordsField):
    """A list of prefixes per portal_type
    """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type': 'prefixes',
        'subfields': ('portal_type',
                      'prefix',
                      'separator',
                      'padding',
                      'sequence_start'),
        'subfield_labels': {'portal_type': 'Portal type',
                            'prefix': 'Prefix',
                            'separator': 'Prefix Separator',
                            'padding': 'Padding',
                            'sequence_start': 'Sequence Start'},
        'subfield_readonly': {'portal_type': False,
                              'prefix': False,
                              'padding': False,
                              'separator': False,
                              'sequence_start': False},
        'subfield_sizes': {'portal_type': 32,
                           'prefix': 12,
                           'padding': 12,
                           'separator': 5,
                           'sequence_start': 12},
        'subfield_types': {'padding': 'int',
                           'sequence_start': 'int'},
    })

    security = ClassSecurityInfo()


registerField(PrefixesField,
              title="PrefixesField",
              description="UI for defining SampleType Prefixes in Bika Setup",
              )
