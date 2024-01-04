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

import json

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from bika.lims import api
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IPhoneField
from senaite.core.z3cform.interfaces import IPhoneWidget
from z3c.form import interfaces
from z3c.form.browser import text
from z3c.form.browser import widget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer_only


@implementer_only(IPhoneWidget)
class PhoneWidget(text.TextWidget):
    """Input type "tel" widget implementation.
    """
    klass = u"senaite-phone-widget"
    value = u""
    initial_country = None
    preferred_countries = None

    def update(self):
        super(PhoneWidget, self).update()
        widget.addFieldClass(self)
        if self.mode == INPUT_MODE:
            self.addClass("form-control form-control-sm")

    def attrs(self):
        """Return the template attributes for the date field

        :returns: dictionary of HTML attributes
        """
        attrs = {
            "data-name": self.name,
        }

        initial_country = self.initial_country
        if initial_country is None:
            initial_country = self.get_default_country()
        attrs["data-initial_country"] = initial_country

        preferred_countries = self.preferred_countries
        if not isinstance(preferred_countries, list):
            preferred_countries = []
        attrs["data-preferred_countries"] = json.dumps(preferred_countries)

        return attrs

    def get_default_country(self, default="us"):
        """Return the default country from the system
        """
        setup = api.get_setup()
        country = setup.getDefaultCountry()
        if not country:
            return default
        return country.lower()


@adapter(IPhoneField, ISenaiteFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def PhoneWidgetFactory(field, request):
    """IFieldWidget widget factory for NumberWidget.
    """
    return FieldWidget(field, PhoneWidget(request))
