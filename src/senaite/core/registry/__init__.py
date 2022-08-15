# -*- coding: utf-8 -*-

from plone.registry.interfaces import IRegistry
from senaite.core.registry.schema import ISenaiteRegistry
from zope.component import getUtility
from zope.schema._bootstrapinterfaces import WrongType
from zope.dottedname.resolve import resolve


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
        proxy = registry.forInterface(interface)
        try:
            return getattr(proxy, name)
        except AttributeError:
            pass
    return default


def set_registry_record(name, value):
    """Set SENAITE registry record
    """
    registry = get_registry()
    for interface in get_registry_interfaces():
        proxy = registry.forInterface(interface)
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
