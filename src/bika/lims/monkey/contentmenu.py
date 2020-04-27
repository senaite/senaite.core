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

def contentmenu_factories_available(self):
    """These types will have their Add New... factories dropdown menu removed.
    """
    if hasattr(self._addContext(), 'portal_type') \
    and self._addContext().portal_type in [
        'Batch',
        'Client',
        'AnalysisRequest',
        'Worksheet',
        'AnalysisCategory',
        'AnalysisProfile',
        'ARTemplate',
        'AnalysisService',
        'AnalysisSpec',
        'Attachment',
        'Calculation',
        'Instrument',
        'LabContact',
        'Laboratory',
        'Method',
        'Department',
        'ReferenceDefinition',
        'ReportFolder',
        'SampleType',
        'SamplePoint',
        'StorageLocation',
        'WorksheetTemplate',
        'LabProduct',
        'ReferenceSample',
        'Preservation'
    ]:
        return False
    else:
        itemsToAdd = self._itemsToAdd()
        showConstrainOptions = self._showConstrainOptions()
        if self._addingToParent() and not self.context_state.is_default_page():
            return False
        return (len(itemsToAdd) > 0 or showConstrainOptions)
