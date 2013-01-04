from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFPlone.i18nl10n import ulocalized_time

class ScheduleInputWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'ulocalized_time': ulocalized_time,
        'macro': "bika_widgets/scheduleinputwidget",
        'helper_js': ("bika_widgets/scheduleinputwidget.js",),
        'helper_css': ("bika_widgets/scheduleinputwidget.css",),
        'maxDate': '+0d',
        'yearRange': '-100:+0'
    })
    
    security = ClassSecurityInfo()

registerWidget(ScheduleInputWidget,
               title = 'ScheduleInputWidget',
               description = ('Control for scheduling'),
               )