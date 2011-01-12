"""FixedPointField

$Id: FixedPointField.py 319 2006-11-05 20:27:14Z anneline $
"""
from types import TupleType, StringType
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import ObjectField, \
    DecimalWidget
from Products.Archetypes.Registry import registerField
from Products.bika.fixedpoint import FixedPoint

class FixedPointField(ObjectField):
    """A field for storing fixed point values"""

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'FixedPoint',
        'widget' : DecimalWidget,
        'validators' : ('isDecimal'),
        })

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        Check if value is an actual FixedPoint value. If not, attempt to
        convert it to one; Raise an error if value is a float. Assign
        all properties passed as kwargs to object.

        field.set( FixedPoint(10))
        field.set( FixedPointInstance)

        """
        assert type(value) != type(0.00)

        if isinstance(value, StringType) and value == '':
            value = None
        if not value is None and not isinstance(value, FixedPoint):
            value = FixedPoint(value)

        ObjectField.set(self, instance, value, **kwargs)


registerField(FixedPointField,
              title = 'FixedPoint',
              description = ('Used for storing FixedPoint'))

