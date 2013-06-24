from Products.Archetypes.Widget import IntegerWidget as _i
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Registry import registerWidget

from AccessControl import ClassSecurityInfo

_marker = []


class IntegerWidget(_i):
    _properties = _i._properties.copy()
    _properties.update({
        'macro': "bika_widgets/integer",
        'unit': '',
    })

    security = ClassSecurityInfo()

registerWidget(IntegerWidget,
               title='Integer',
               description=('Renders a HTML text input box which '
                            'accepts a integer value'),
               )

registerPropertyType('unit', 'string', IntegerWidget)
