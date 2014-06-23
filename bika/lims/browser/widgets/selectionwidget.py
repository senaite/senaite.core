from Products.Archetypes.Widget import SelectionWidget as _s
from Products.Archetypes.Registry import registerWidget

from AccessControl import ClassSecurityInfo

class SelectionWidget(_s):
    _properties = _s._properties.copy()
    _properties.update({
        'macro': "bika_widgets/selection",
    })

    security = ClassSecurityInfo()

registerWidget(SelectionWidget)
