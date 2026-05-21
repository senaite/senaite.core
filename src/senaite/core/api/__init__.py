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

"""Public helper API for SENAITE.

Functions exposed here form the senaite.core.api namespace. Use
``from senaite.core import api`` and then ``api.get_portal_url()``,
mirroring the long-standing ``bika.lims.api`` module that this package
will gradually replace.

Domain-specific helpers live in submodules, e.g.
``from senaite.core.api import hazard``.
"""

from bika.lims import api as _bika_api
from Products.CMFPlone.utils import safe_callable
from senaite.core.i18n import translate  # noqa: F401
from zope.component.hooks import getSite


def get_portal():
    """Get the portal object

    :returns: Portal object
    """
    return getSite()


def get_portal_url():
    """Get the absolute URL of the portal

    :returns: Absolute portal URL
    :rtype: str
    """
    return get_portal().absolute_url()


def get_attr(obj, name, default=None, catalog=None):
    """Return an attribute from an object, brain or UID.

    Accepts any of the three forms `bika.lims.api.get_uid` handles:
    a content object, a catalog brain or a UID string. When
    `catalog` is given the input is normalized to a brain via a
    UID lookup in that catalog before reading the attribute, which
    avoids waking the object up. Without `catalog`, the input is
    read directly: a method is called, a bare attribute is returned
    as-is.

    Uses `Products.CMFPlone.utils.safe_callable` so a transient
    ConflictError in the callable check is not swallowed.

    :param obj: Content object, catalog brain or UID
    :param name: Attribute or method name
    :param default: Value returned when `obj` is empty, the
                    attribute is missing, the catalog lookup yields
                    no brain, or the call raises `TypeError`
    :param catalog: Catalog id or tool. When given, `obj` is
                    normalized to a brain via UID lookup before
                    reading the attribute.
    :returns: Attribute value (or call result) or `default`
    """
    if obj is None:
        return default
    if catalog is not None:
        if not (_bika_api.is_object(obj) or _bika_api.is_uid(obj)):
            return default
        uid = _bika_api.get_uid(obj)
        if not uid:
            return default
        brains = _bika_api.search({"UID": uid}, catalog=catalog)
        if not brains:
            return default
        obj = brains[0]
    value = getattr(obj, name, default)
    if safe_callable(value):
        try:
            return value()
        except TypeError:
            return default
    return value
