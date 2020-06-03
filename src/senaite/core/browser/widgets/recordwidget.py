# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.public import StringWidget
from Products.Archetypes.Registry import registerWidget


class RecordWidget(StringWidget):
    """Ported from Products.ATExtensions
    """

    _properties = StringWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/record_widget",
        "show_hm": True,  # only meaningful for DateTime subfields
        })
    security = ClassSecurityInfo()


InitializeClass(RecordWidget)

registerWidget(RecordWidget, title="Record", description="")
