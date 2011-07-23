from AccessControl import ClassSecurityInfo
from Products.ATExtensions.Extensions.utils import makeDisplayList
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator
from bika.lims import bikaMessageFactory as _
from bika.lims.config import COUNTRY_NAMES
import sys

class InterimFieldsField(RecordsField):
    """a list of InterimFields for calculations """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'InterimFields',
        'subfields' : ('id', 'title', 'value', 'unit'),
        'required_subfields' : ('id','title',),
        'subfield_labels':{'id': _('Field ID'),
                           'title': _('Field Title'),
                           'value': _('Default value'),
                           'unit': _('Unit')},
        })
    security = ClassSecurityInfo()

registerField(InterimFieldsField,
              title = "Interim Fields",
              description = "Used for storing Interim Fields or Interim Results.",
              )
