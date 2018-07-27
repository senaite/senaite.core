# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerField
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.interfaces import IRemarksField
from zope.interface import implements


class RemarksField(ObjectField):
    """A field that stores remarks.  The value submitted to the setter
    will always be appended to the actual value of the field.
    A divider will be included with extra information about the text.
    """

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'remarks',
        'widget': RemarksWidget,
        'default': '',
    })

    implements(IRemarksField)

    security = ClassSecurityInfo()

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """Adds the value to the existing text stored in the field,
        along with a small divider showing username and date of this entry.
        """
        if not value:
            return
        value = value.strip()
        date = DateTime().rfc822()
        user = getSecurityManager().getUser()
        username = user.getUserName()
        divider = "=== {} ({})".format(date, username)
        existing_remarks = instance.getRawRemarks()
        remarks = '\n'.join([divider, value, existing_remarks])
        return ObjectField.set(self, instance, remarks)

    def get_cooked_remarks(self, instance):
        text = self.get(instance)
        if not text:
            return ""
        return text.replace('\n', '<br/>')

    def get(self, instance, **kwargs):
        """Returns raw field value.
        """
        return self.getRaw(instance, **kwargs)

    def getRaw(self, instance, **kwargs):
        """Returns raw field value (possible wrapped in BaseUnit)
        """
        value = ObjectField.get(self, instance, **kwargs)
        # getattr(instance, "Remarks") returns a BaseUnit
        if callable(value):
            value = value()
        return value


registerField(RemarksField, title='Remarks', description='')
