# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.app.textfield import RichText
from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IRichTextField
from zope.interface import implementer


@implementer(IRichTextField)
class RichTextField(RichText, BaseField):
    """A field that handles markup texts
    """

    def set(self, object, value):
        """Set field value

        :param object: the instance of the field
        :param value: value to set
        """
        # always ensure unicode
        if isinstance(value, str):
            value = api.safe_unicode(value)
        super(RichTextField, self).set(object, value)

    def get(self, object):
        """Get the field value

        :param object: the instance of the field
        :returns: RichTextValue
        """
        value = super(RichTextField, self).get(object)
        return value

    def _validate(self, value):
        """Validator when called from form submission
        """
        super(RichTextField, self)._validate(value)
