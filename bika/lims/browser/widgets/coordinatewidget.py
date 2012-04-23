from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordWidget
from Products.Archetypes.Registry import registerWidget
import datetime

class CoordinateWidget(RecordWidget):
    security = ClassSecurityInfo()
    _properties = RecordWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/coordinatewidget",
    })

registerWidget(CoordinateWidget,
               title = 'CoordinateWidget',
               description = '',
               )
