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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import re

from Products.Archetypes.Field import StringField
from Products.Archetypes.Registry import registerField


class EmailsField(StringField):
    """Field for string representation of a list of emails
    """
    _properties = StringField._properties.copy()
    _properties.update({
        "type": "emails_field",
    })

    def set(self, instance, value, **kwargs):
        if value:
            # Standardize to comma-separated and remove duplicates
            validator = instance.plone_utils.validateSingleEmailAddress
            value = ", ".join(self.to_list(value, validator=validator))
        super(EmailsField, self).set(instance, value, **kwargs)

    def get(self, instance, **kwargs):
        if kwargs.get("as_list", False):
            # Return as a list
            validator = instance.plone_utils.validateSingleEmailAddress
            return self.to_list(self.get(instance), validator)
        return super(EmailsField, self).get(instance, **kwargs)

    def to_list(self, value, validator=None):
        """Transforms the value to a list of values
        """
        if not value:
            return []
        emails = map(lambda x: x.strip(), re.split("[;,]", value))
        emails = filter(None, emails)
        if validator:
            emails = filter(lambda email: validator(email), emails)
        return emails


registerField(EmailsField,
              title="Emails",
              description="Used for storing e-mail addresses in string format")
