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

    def getSortKeys(self,keys):
        # return the option's keys in sorted in order to obtain a sorted set of
        # options.
        # checkbox object isn't an option
        if 'checkbox' in keys:
            keys.remove('checkbox')
        if len(keys) == 0:
            # Doing that in order to get one blank textfield
            keys = ['blank']
        return sorted(keys)


registerWidget(RejectionWidget,
               title = 'Rejection Widget',
               description = ('Widget with the rejection reasons'),
               )
