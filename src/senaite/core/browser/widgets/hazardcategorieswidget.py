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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.Registry import registerWidget
from senaite.core import api


class HazardCategoriesWidget(MultiSelectionWidget):
    """AT widget for the GHS HazardCategories field

    Edit mode reuses the standard MultiSelectionWidget checkbox
    layout. View mode renders the selected categories as inline GHS
    pictograms with tooltips.
    """
    security = ClassSecurityInfo()
    _properties = MultiSelectionWidget._properties.copy()
    _properties.update({
        "macro": "senaite_widgets/hazardcategorieswidget",
    })

    security.declarePublic("get_pictograms")
    def get_pictograms(self, codes):
        """Return view-model pictogram dicts for the selected codes

        :param codes: GHS category codes selected on the field
        :returns: List of pictogram dicts; empty when no code matches
        :rtype: list[dict]
        """
        return api.get_pictograms_for_codes(codes, hazardous=True)


registerWidget(
    HazardCategoriesWidget,
    title="HazardCategoriesWidget",
    description="Multi-select widget for GHS hazard categories")
