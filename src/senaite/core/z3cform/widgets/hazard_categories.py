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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core.vocabularies.hazard_categories import get_category
from senaite.core.z3cform.interfaces import IHazardCategoriesWidget
from z3c.form.browser import checkbox
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only

PICTOGRAM_BASE_URL = (
    "{portal_url}/++plone++senaite.core.static/images/ghs/{pictogram}")


@implementer_only(IHazardCategoriesWidget)
class HazardCategoriesWidget(checkbox.CheckBoxWidget):
    """Multi-checkbox widget showing GHS pictograms next to each option."""

    klass = u"hazard-categories-widget"

    def pictogram_url(self, value):
        category = get_category(value)
        if not category:
            return u""
        portal_url = api.get_portal().absolute_url()
        return PICTOGRAM_BASE_URL.format(
            portal_url=portal_url,
            pictogram=category["pictogram"])


@implementer(IFieldWidget)
def HazardCategoriesFieldWidget(field, request):
    """Factory for the HazardCategoriesWidget."""
    return FieldWidget(field, HazardCategoriesWidget(request))
