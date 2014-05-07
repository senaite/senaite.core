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
from bika.lims.utils import t

class CoordinateField(RecordField):
    """ Stores angle in deg, min, sec, bearing """
    security = ClassSecurityInfo()
    _properties = RecordField._properties.copy()
    _properties.update({
        'type' : 'angle',
        'subfields' : ('degrees', 'minutes', 'seconds', 'bearing'),
##        'required_subfields' : ('degrees', 'minutes', 'seconds', 'bearing'),
        'subfield_labels':{'degrees':_('Degrees'),
                           'minutes':_('Minutes'),
                           'seconds':_('Seconds'),
                           'bearing':_('Bearing')},
        'subfield_sizes': {'degrees':3,
                           'minutes':2,
                           'seconds':2,
                           'bearing':1},
        'subfield_validators' : {'degrees':'coordinatevalidator',
                                 'minutes':'coordinatevalidator',
                                 'seconds':'coordinatevalidator',
                                 'bearing':'coordinatevalidator',},
        })

registerField(CoordinateField,
              title = "Coordinate",
              description = "Used for storing coordinates",
              )
