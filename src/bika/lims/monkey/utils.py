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

from senaite.core.i18n import translate as t
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import getEmptyTitle
from Products.CMFPlone.utils import isIDAutoGenerated
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_unicode
from zope.i18nmessageid import MessageFactory

_marker = []


def _pretty_title_or_id(context, obj, empty_value=_marker):
    """Return the best possible title or id of an item, regardless
       of whether obj is a catalog brain or an object, but returning an
       empty title marker if the id is not set (i.e. it's auto-generated).
    """
    # if safe_hasattr(obj, "aq_explicit"):
    #    obj = obj.aq_explicit
    # title = getattr(obj, "Title", None)
    title = None
    if base_hasattr(obj, "Title"):
        title = getattr(obj, "Title", None)
    if safe_callable(title):
        title = title()
    if title:
        return title
    item_id = getattr(obj, "getId", None)
    if safe_callable(item_id):
        item_id = item_id()
    if item_id and not isIDAutoGenerated(context, item_id):
        return item_id
    if empty_value is _marker:
        empty_value = getEmptyTitle(context)
    return empty_value


def pretty_title_or_id(context, obj, empty_value=_marker, domain='plone'):
    _ = MessageFactory(domain)
    title = _pretty_title_or_id(context, obj, empty_value=_marker)
    return t(context.translate(_(safe_unicode(title))))
