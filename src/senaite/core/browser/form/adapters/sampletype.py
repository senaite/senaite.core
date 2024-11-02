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

from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.interfaces import ISampleType
from bika.lims.vocabularies import getStickerTemplates

_DGF_WIDGET_PREFIX = "form.widgets.admitted_sticker_templates.0.widgets."


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Sample Type
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # filter default small/large sticker
        if name == _DGF_WIDGET_PREFIX + "admitted":
            # get the sticker
            templates = filter(
                lambda t: t.get("id") in value, getStickerTemplates())

            # prepare options for the select field
            opts = map(lambda t: dict(
                title=t.get("title"), value=t.get("id")), templates)

            default_small = default_large = None
            if ISampleType.providedBy(self.context):
                default_small = self.context.getDefaultSmallSticker()
                default_large = self.context.getDefaultLargeSticker()

            # set default small sticker
            self.add_update_field(_DGF_WIDGET_PREFIX + "small_default", {
                "selected": [default_small] if default_small else [],
                "options": opts})

            # set default large sticker
            self.add_update_field(_DGF_WIDGET_PREFIX + "large_default", {
                "selected": [default_large] if default_large else [],
                "options": opts})

        return self.data
