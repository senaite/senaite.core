from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Registry import registerPropertyType
from bika.lims.browser import ulocalized_time as ut


class DateTimeWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'show_time': False,
        'macro': "bika_widgets/datetimewidget",
        'helper_js': ("bika_widgets/datetimewidget.js",),
        'helper_css': ("bika_widgets/datetimewidget.css",),
    })

    security = ClassSecurityInfo()

    def ulocalized_time(self, time, context, request):
        val = ut(time,
                 long_format=self._properties['show_time'],
                 time_only=False,
                 context=context,
                 request=request)
        return val


registerWidget(
    DateTimeWidget,
    title='DateTimeWidget',
    description=('Simple text field, with a jquery date widget attached.')
)

registerPropertyType('show_time', 'boolean')
