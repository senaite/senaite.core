from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
import json

class RecordsWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/recordswidget",
        'helper_js': ("bika_widgets/recordswidget.js",),
        'helper_css': ("bika_widgets/recordswidget.css",),
        'allowDelete': True,
        'readOnly': False,
        'combogrid_options': '',
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """
        Basic impl for form processing in a widget plus allowing empty
        values to be saved
        """

        # a poor workaround for Plone repeating itself.
        # XXX this is important XXX
        key = field.getName() + '_value'
        if key in instance.REQUEST:
            return instance.REQUEST[key], {}
        value = form.get(field.getName(), empty_marker)

        if not value:
            return value, {}
        if value is empty_marker:
            return empty_marker
        if emptyReturnsMarker and value == '':
            return empty_marker

        # we make sure that empty "value" inputs are saved as "" empty string.
        for i in range(len(value)):
            value[i] = dict(value[i])
            if 'value' not in value[i]:
                value[i]['value'] = ''

        instance.REQUEST[key] = value
        return value, {}

    def jsondumps(self, val):
        return json.dumps(val)

registerWidget(RecordsWidget,
               title = 'RecordsWidget',
               description = '',
               )
