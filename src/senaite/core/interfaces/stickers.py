# -*- coding: utf-8 -*-

from zope.interface import Interface


class IGetStickerTemplates(Interface):
    """Marker interface to get stickers for a specific content type.

    An IGetStickerTemplates adapter should return a result with the
    following format:

    :return: [{'id': <template_id>,
             'title': <template_title>}, ...]
    """
