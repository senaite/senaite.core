from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget

class RecordsWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/recordswidget",
        'helper_js': ("bika_widgets/recordswidget.js",),
        'helper_css': ("bika_widgets/recordswidget.css",),
        'allowDelete': True,
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        Basic impl for form processing in a widget plus allowing empty
        values to be saved
        """

        value = form.get(field.getName(), empty_marker)

        if not value:
            return value, {}
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker

        return value, {}

registerWidget(RecordsWidget,
               title = 'RecordsWidget',
               description = (''),
               )
