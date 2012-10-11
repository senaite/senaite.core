from AccessControl import ClassSecurityInfo
from Products.ATExtensions.Extensions.utils import makeDisplayList
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator
import sys
from bika.lims import bikaMessageFactory as _
from bika.lims.locales import COUNTRIES

class AddressField(RecordField):
    """ dedicated address field"""
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'address',
        'subfields' : ('address', 'city', 'zip', 'state', 'district', 'country'),
        'outerJoin':'<br />',
        })
    security = ClassSecurityInfo()

registerField(AddressField,
              title = "Address",
              description = "Used for storing address information",
              )

