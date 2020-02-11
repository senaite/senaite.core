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

from zope.interface import implements

from bika.lims import logger
from bika.lims.interfaces import IGetStickerTemplates
from bika.lims.vocabularies import getStickerTemplates


class GetSampleStickers(object):
    """
    Returns an array with the templates of stickers available for Sample
    object in context.
    Each array item is a dictionary with the following structure:
        [{'id': <template_id>,
         'title': <teamplate_title>,
         'selected: True/False'}, ]
    """

    implements(IGetStickerTemplates)

    def __init__(self, context):
        self.context = context
        self.request = None
        self.sample_type = None

    def __call__(self, request):
        self.request = request
        # Stickers admittance are saved in sample type
        if not hasattr(self.context, 'getSampleType'):
            logger.warning(
                "{} has no attribute 'getSampleType', so no sticker will be "
                "returned.". format(self.context.getId())
            )
            return []
        self.sample_type = self.context.getSampleType()
        sticker_ids = self.sample_type.getAdmittedStickers()
        default_sticker_id = self.get_default_sticker_id()
        result = []
        # Getting only existing templates and its info
        stickers = getStickerTemplates()
        for sticker in stickers:
            if sticker.get('id') in sticker_ids:
                sticker_info = sticker.copy()
                sticker_info['selected'] = \
                    default_sticker_id == sticker.get('id')
                result.append(sticker_info)
        return result

    def get_default_sticker_id(self):
        """
        Gets the default sticker for that content type depending on the
        requested size.

        :return: An sticker ID as string
        """
        size = self.request.get('size', '')
        if size == 'small':
            return self.sample_type.getDefaultSmallSticker()
        return self.sample_type.getDefaultLargeSticker()
