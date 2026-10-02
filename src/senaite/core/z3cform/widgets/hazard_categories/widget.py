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

from senaite.core.api import hazard as hazard_api
from senaite.core.z3cform.interfaces import IHazardCategoriesWidget
from z3c.form.browser import checkbox
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(IHazardCategoriesWidget)
class HazardCategoriesWidget(checkbox.CheckBoxWidget):
    """Multi-checkbox widget showing hazard pictograms next to each option."""

    klass = u"hazard-categories-widget"

    def pictogram_url(self, value):
        return hazard_api.get_pictogram_url(value)


@implementer(IFieldWidget)
def HazardCategoriesFieldWidget(field, request):
    """Factory for the HazardCategoriesWidget."""
    return FieldWidget(field, HazardCategoriesWidget(request))
