from AccessControl import ClassSecurityInfo
from Products.ATExtensions.Extensions.utils import makeDisplayList
from Products.ATExtensions.ateapi import RecordField, RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims.config import COUNTRY_NAMES
from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator
import sys

class StandardResultField(RecordsField):
    """a list of standard sample results """
    _properties = RecordsField._properties.copy()
    _properties.update({
        'type' : 'standardresult',
        'subfields' : ('service', 'result', 'min', 'max'),
        'required_subfields' : ('service'),
        'subfield_labels':{'service': 'Analysis Service',
                           'result': 'Result',
                           'min': 'Min',
                           'max': 'Max'},
        })
    security = ClassSecurityInfo()

registerField(StandardResultField,
              title = "Standard Results",
              description = "Used for storing standard results",
              )

