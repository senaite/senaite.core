# ../../skins/bika/bika_widgets/artemplatepartitionswidget.pt
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from bika.lims.browser.widgets import RecordsWidget


class ARTemplatePartitionsWidget(RecordsWidget):
    _properties = RecordsWidget._properties.copy()
    _properties.update({
        'helper_js': ("bika_widgets/recordswidget.js",
                      "bika_widgets/artemplatepartitionswidget.js",)
    })

    security = ClassSecurityInfo()

registerWidget(ARTemplatePartitionsWidget,
               title='AR Template Partition Layout',
               description=('AR Template Partition Layout'),
               )
