from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t


class InterimFieldsField(RecordsField):

    """a list of InterimFields for calculations """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'fixedSize': 0,
        'minimalSize': 0,
        'maximalSize': 9999,
        'type': 'InterimFields',
        'subfields': ('keyword', 'title', 'value', 'unit', 'hidden', 'wide'),
        'required_subfields': ('keyword', 'title'),
        'subfield_labels': {'keyword': _('Keyword'),
                             'title': _('Field Title'),
                             'value': _('Default value'),
                             'unit': _('Unit'),
                             'hidden': _('Hidden Field'),
                             'wide': _('Apply wide')},
        'subfield_types': {'hidden': 'boolean', 'value': 'float', 'wide': 'boolean'},
        'subfield_sizes': {'keyword': 20,
                            'title': 20,
                            'value': 10,
                            'unit': 10},
        'subfield_validators': {'keyword': 'interimfieldsvalidator',
                                 'title': 'interimfieldsvalidator',
                                 'value': 'interimfieldsvalidator',
                                 'unit': 'interimfieldsvalidator'},
        })
    security = ClassSecurityInfo()

registerField(InterimFieldsField,
              title="Interim Fields",
              description="Used for storing Interim Fields or Interim Results.",
              )
