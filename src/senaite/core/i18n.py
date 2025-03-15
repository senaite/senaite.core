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
from zope.i18n import translate as ztranslate
from zope.i18nmessageid import MessageFactory

_pl = MessageFactory("plonelocales")


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


def get_dt_format(msgid):
    """Returns the date/time msgstr format for the current locale
    :param id: locale msgid or "date"/"time"/"datetime"
    """
    mapping = {
        "date": "date_format_short",
        "datetime": "date_format_long",
        "time": "time_format",
    }
    defaults = {
        "time_format": "${H}:${M}",
        "date_format_short": "${Y}-${m}-${d}",
        "date_format_long": "${Y}-${m}-${d} ${H}:${M}",
    }

    # extract the current locale for the given msgid from TranslationService
    msgid = mapping.get(msgid, msgid)
    fmt = translate(msgid, to_utf8=False)
    if not fmt or fmt == msgid:
        return defaults.get(msgid)
    return fmt


def get_weekday_name(day, abbr=False, to_utf8=True):
    """Returns the name of the day of the week for the current locale, starting
    with Sunday == 0
    """
    ids = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
    msgid = "weekday_%s_abbr" if abbr else "weekday_%s"
    msgid = msgid % ids[day]
    return translate(_pl(msgid), to_utf8=to_utf8)


def get_month_name(month, abbr=False, to_utf8=True):
    """Returns the name of the month for the current locale, starting with
    """
    ids = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
           "oct", "nov", "dec"]
    msgid = "month_%s_abbr" if abbr else "month_%s"
    msgid = msgid % ids[month-1]
    return translate(_pl(msgid), to_utf8=to_utf8)
