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

import inspect

from bika.lims import api as _bika_api
from Products.CMFPlone.utils import safe_callable
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import IntIdMissingError
from zope.intid.interfaces import ObjectMissingError

_marker = object()


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


def get_object_by_intid(intid, default=_marker):
    """Returns the object by its IntId

    :param intid: the IntId of the object
    :type intid: int
    :returns: the object whose IntId matches with the intid provided
    :rtype: ATContentType/DexterityContentType
    """
    intids = getUtility(IIntIds)
    try:
        return intids.getObject(intid)
    except ObjectMissingError:
        if default is _marker:
            raise
        return default


def get_intid(obj, default=_marker):
    """Returns the IntId of the given object

    :param obj: object to get the IntId from
    :type obj: ATContentType/DexterityContentType
    :returns: The IntId of the given object
    :rtype: int
    """
    intids = getUtility(IIntIds)
    try:
        return intids.getId(obj)
    except IntIdMissingError:
        if default is _marker:
            raise
        return default


def add_intid(obj):
    """Registers the object to all IIntIds utilities

    :param obj: object to register to all IIntIds utilities
    :type obj: ATContentType/DexterityContentType
    :returns: The IntId of the object
    """
    for intids in getAllUtilitiesRegisteredFor(IIntIds):
        try:
            intids.register(obj)
        except KeyError:
            # already registered with this utility
            pass

    # return the newly created IntId
    return get_intid(obj)


def delete_intid(obj):
    """Unregister the object from all IIntIds utilities

    Useful when deleting an object without firing IObjectRemovedEvent,
    so its intid keyref does not survive as an orphan in storage.

    :param obj: object to unregister
    :type obj: ATContentType/DexterityContentType
    """
    for intids in getAllUtilitiesRegisteredFor(IIntIds):
        try:
            intids.unregister(obj)
        except KeyError:
            # not registered with this utility
            pass


def _accepts_no_args(callable_obj):
    """Return True when ``callable_obj`` can be invoked with no args."""
    try:
        spec = inspect.getargspec(callable_obj)
    except TypeError:
        # Builtin / C-extension function — best-effort, just try it.
        return True
    args = spec.args or []
    # Drop `self` for bound methods.
    if inspect.ismethod(callable_obj) and args:
        args = args[1:]
    defaults = spec.defaults or ()
    required = len(args) - len(defaults)
    return required <= 0


def get_attr(obj, name, default=None, catalog=None):
    """Return an attribute from an object, brain or UID.

    Accepts any of the three forms `bika.lims.api.get_uid` handles:
    a content object, a catalog brain or a UID string. When
    `catalog` is given the input is normalized to a brain via a
    UID lookup in that catalog before reading the attribute, which
    avoids waking the object up. Brains are passed through unchanged.
    Without `catalog`, the input is read directly: a parameterless
    callable is invoked, a bare attribute is returned as-is.

    :param obj: Content object, catalog brain or UID
    :param name: Attribute or method name
    :param default: Value returned when `obj` is empty, the
                    attribute is missing, the catalog lookup yields
                    no brain, or the callable requires arguments
    :param catalog: Catalog id or tool. When given, `obj` is
                    normalized to a brain via UID lookup before
                    reading the attribute.
    :returns: Attribute value (or call result) or `default`
    """
    if obj is None:
        return default
    if catalog is not None:
        if _bika_api.is_brain(obj):
            pass
        elif _bika_api.is_object(obj) or _bika_api.is_uid(obj):
            uid = _bika_api.get_uid(obj)
            if not uid:
                return default
            brains = _bika_api.search({"UID": uid}, catalog=catalog)
            if not brains:
                return default
            obj = brains[0]
        else:
            return default
    value = getattr(obj, name, default)
    if safe_callable(value):
        if not _accepts_no_args(value):
            return default
        return value()
    return value
