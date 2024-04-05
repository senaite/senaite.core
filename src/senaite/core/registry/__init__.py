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

from plone.registry.interfaces import IRegistry
from senaite.core import logger
from senaite.core.registry.schema import ISenaiteRegistry
from senaite.core.interfaces import ISenaiteRegistryFactory
from zope.component import getUtility
from zope.component import queryUtility
from zope.dottedname.resolve import resolve
from zope.schema._bootstrapinterfaces import WrongType


def get_registry():
    """Returns the registry utility

    :returns: Registry object
    """
    return getUtility(IRegistry)


def get_registry_interfaces():
    """
    """
    registry = get_registry()

    interface_names = set(
        record.interfaceName for record in list(registry.records.values())
    )

    for name in interface_names:
        if not name:
            continue

        interface = None
        try:
            interface = resolve(name)
        except ImportError:
            # In case of leftover registry entries of uninstalled Products
            continue

        if interface.isOrExtends(ISenaiteRegistry):
            yield interface


def get_registry_record(name, default=None):
    """Get SENAITE registry record
    """
    registry = get_registry()
    for interface in get_registry_interfaces():
        factory = queryUtility(ISenaiteRegistryFactory,
                               name=interface.__identifier__,
                               default=None)
        try:
            proxy = registry.forInterface(interface, factory=factory)
            return getattr(proxy, name)
        except (AttributeError, KeyError):
            pass

    interfaces = map(lambda i: i.__identifier__, get_registry_interfaces())
    logger.error("No registry record found for '{}' in interfaces '{}'. "
                 "Returning default value: '{}'. Upgrade step not run?"
                 .format(name, interfaces, default))

    return default


def set_registry_record(name, value):
    """Set SENAITE registry record
    """
    registry = get_registry()
    for interface in get_registry_interfaces():
        factory = queryUtility(ISenaiteRegistryFactory,
                               name=interface.__identifier__,
                               default=None)
        proxy = registry.forInterface(interface, factory=factory)
        try:
            getattr(proxy, name)
        except AttributeError:
            pass
        else:
            try:
                return setattr(proxy, name, value)
            except WrongType:
                field_type = None
                for field in interface.namesAndDescriptions():
                    if field[0] == name:
                        field_type = field[1]
                        break
                raise TypeError(
                    u"The value parameter for the field {name} needs to be "
                    u"{of_class} instead of {of_type}".format(
                        name=name,
                        of_class=str(field_type.__class__),
                        of_type=type(value),
                    ))

    raise NameError("No registry record found for name '{}'".format(name))
