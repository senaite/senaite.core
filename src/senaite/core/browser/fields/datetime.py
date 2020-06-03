# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.public import DateTimeField as BaseField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType
from senaite.core.browser.widgets.datetimewidget import DateTimeWidget


class DateTimeField(BaseField):
    """An improved DateTime Field. It allows to specify
    whether only dates or only times are interesting.

    This field is ported from Products.ATExtensions
    """

    _properties = BaseField._properties.copy()
    _properties.update({
        "type": "datetime_ng",
        "widget": DateTimeWidget,
        "with_time": 1,  # set to False if you want date only objects
        "with_date": 1,  # set to False if you want time only objects
        })
    security = ClassSecurityInfo()


InitializeClass(DateTimeField)


registerField(
    DateTimeField,
    title="DateTime Field",
    description="An improved DateTimeField, which also allows time "
                "or date only specifications.")


registerPropertyType("with_time", "boolean", DateTimeField)
registerPropertyType("with_date", "boolean", DateTimeField)
