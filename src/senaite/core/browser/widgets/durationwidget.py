# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.ATExtensions.widget import RecordWidget


class DurationWidget(RecordWidget):
    security = ClassSecurityInfo()
    _properties = RecordWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/durationwidget",
    })


registerWidget(DurationWidget, title="DurationWidget", description=(""))
