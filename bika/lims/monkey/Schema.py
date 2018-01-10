# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Archetypes.mimetype_utils import getDefaultContentType
from Products.Archetypes.utils import shasattr, mapply
from bika.lims.interfaces import IAcquireFieldDefaults

from zope.component import getAdapters

_marker = []


def setDefaults(self, instance):
    """Only call during object initialization, this function sets fields
    to schema defaults.  It's adapted from the original to support
    IAcquireFieldDefaults adapters.  If IAcquireFieldDefaults adapter
    does not find a suitable field, or that field's value is Falseish,
    this function will not continue with the normal default machinery.
    """
    for field in self.values():

        # ## bika addition: we fire adapters for IAcquireFieldDefaults.
        # If IAcquireFieldDefaults returns None, this signifies "ignore" return.
        # First adapter found with non-None result, wins.
        value = None
        if shasattr(field, 'acquire'):
            adapters = {}
            for adapter in getAdapters((instance,), IAcquireFieldDefaults):
                sort_val = getattr(adapter[1], 'sort', 1000)
                if sort_val not in adapters:
                    adapters[sort_val] = []
                adapters[sort_val].append(adapter)
            if adapters:
                keys = sorted(adapters.keys())
                keys.reverse()
                adapter = adapters[keys[0]]
                _value = adapter[0][1](field)
                if _value is not None:
                    value = _value

        if field.getName().lower() == 'id':
            continue

        # If our adapter reflects a value for a reference field, it will
        # be permitted.
        if field.type == "reference" and not value:
            continue

        default = value if value else field.getDefault(instance)

        # always set defaults on writable fields
        mutator = field.getMutator(instance)
        if mutator is None:
            continue

        args = (default,)
        kw = {'field': field.__name__,
              '_initializing_': True}
        if shasattr(field, 'default_content_type'):
            # specify a mimetype if the mutator takes a mimetype argument if
            # the schema supplies a default, we honour that, otherwise we use
            # the site property
            default_content_type = field.default_content_type
            if default_content_type is None:
                default_content_type = getDefaultContentType(instance)
            kw['mimetype'] = default_content_type

        mapply(mutator, *args, **kw)
