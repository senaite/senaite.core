from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget


class RejectionWidgetSetup(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/rejectionwidgetsetup",
        'helper_js': ("bika_widgets/rejectionwidgetsetup.js",),
        'helper_css': ("bika_widgets/rejectionwidgetsetup.css",),
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


registerWidget(RejectionWidgetSetup,
               title = "Setup's Rejection Widget",
               description = ('Widget to define the rejection reasons'),
               )
