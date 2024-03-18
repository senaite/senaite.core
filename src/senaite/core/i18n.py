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

from bika.lims import api
from zope.i18n import translate as ztranslate


def translate(msgid, to_utf8=True, **kwargs):
    """Translate any zope i18n msgid

    If msgid is from type i18n `Message`, the domain assigned to the msg has
    priority over the domain passed through kwargs. If no domain is set nor in
    kwargs neither in msgid, system defaults to "senaite.core"

    :param msgid: i18n message id or Message to translate
    :param to_utf8: whether the translated message should be encoded to utf8
    :returns: the translated string for msgid
    """
    msgid = api.safe_unicode(msgid)

    # XX: If the msgid is from type `Message`, Zope's i18n translate tool gives
    #     priority `Message.domain` over the domain passed through kwargs
    domain = kwargs.pop("domain", "senaite.core")
    params = {
        "domain": getattr(msgid, "domain", domain),
        "context": api.get_request(),
    }
    params.update(kwargs)

    message = ztranslate(msgid, **params)
    return api.to_utf8(message) if to_utf8 else message
