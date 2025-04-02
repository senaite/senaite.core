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
from senaite.core import logger
from senaite.core.interfaces import IGetStickerTemplates
from senaite.core.vocabularies.stickers import get_sticker_templates
from zope.interface import implementer


@implementer(IGetStickerTemplates)
class GetSampleStickers(object):
    """Returns a list with of sticker templates for the sample

    Each item in the list is a dictionary with the following structure:

        {
            "id": <template_id>,
            "title": <teamplate_title>,
            "selected: True/False",
        }
    """

    def __init__(self, context):
        self.context = context
        self.sample_type = self.context.getSampleType()

    def __call__(self, request):
        # Stickers admittance are saved in sample type
        if not hasattr(self.context, "getSampleType"):
            logger.warning(
                "{} has no attribute 'getSampleType', so no sticker will be "
                "returned.". format(self.context.getId())
            )
            return []

        # get a copy of the admitted stickers set
        sticker_ids = set(self.sample_type.getAdmittedStickers())
        if not sticker_ids:
            return []

        default_template = self.default_template
        setup_default_sticker = self.get_setup_default_sticker()
        # ensure the setup default sticker is always contained
        sticker_ids.add(setup_default_sticker)

        result = []
        # Getting only existing templates and its info
        stickers = get_sticker_templates()
        for sticker in stickers:
            if sticker.get("id") in sticker_ids:
                sticker_info = sticker.copy()
                sticker_id = sticker.get("id")
                sticker_info["selected"] = sticker_id == default_template
                result.append(sticker_info)
        return result

    @property
    def default_template(self):
        """
        Gets the default sticker for that content type depending on the
        requested size.

        :return: An sticker ID as string
        """
        request = api.get_request()
        size = request.get("size", "")
        if size == "small":
            return self.sample_type.getDefaultSmallSticker()
        elif size == "large":
            return self.sample_type.getDefaultLargeSticker()
        # fall back to the default sticker from setup
        return self.get_setup_default_sticker()

    def get_setup_default_sticker(self):
        """Returns the default sticker from setup
        """
        setup = api.get_setup()
        return setup.getAutoStickerTemplate()
