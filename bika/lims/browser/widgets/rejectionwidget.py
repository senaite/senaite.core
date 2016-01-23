from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget


class RejectionWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/rejectionwidget",
        'helper_js': ("bika_widgets/rejectionwidget.js",),
        'helper_css': ("bika_widgets/rejectionwidget.css",),
    })

    security = ClassSecurityInfo()


registerWidget(RejectionWidget,
               title = 'Rejection Widget',
               description = ('Widget with the rejection reasons'),
               )
