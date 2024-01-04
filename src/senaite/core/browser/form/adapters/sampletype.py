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
from bika.lims.vocabularies import getStickerTemplates


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Sample Type
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # filter default small/large sticker
        if name == "AdmittedStickerTemplates.admitted":
            # get the sticker
            templates = filter(
                lambda t: t.get("id") in value, getStickerTemplates())

            # prepare options for the select field
            opts = map(lambda t: dict(
                title=t.get("title"), value=t.get("id")), templates)

            # set default small sticker
            default_small = self.context.getDefaultSmallSticker()
            self.add_update_field("AdmittedStickerTemplates.small_default", {
                "selected": [default_small] if default_small else [],
                "options": opts})

            # set default large sticker
            default_large = self.context.getDefaultLargeSticker()
            self.add_update_field("AdmittedStickerTemplates.large_default", {
                "selected": [default_large] if default_large else [],
                "options": opts})

        return self.data
