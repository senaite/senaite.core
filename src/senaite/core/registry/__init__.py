# -*- coding: utf-8 -*-

from plone.registry.interfaces import IRegistry
from senaite.core.registry.schema import ISenaiteRegistry
from zope.component import getUtility
from zope.schema._bootstrapinterfaces import WrongType

PREFIX = "senaite.core"


def get_registry():
    """Returns the registry utility

    :returns: Registry object
    """
    return getUtility(IRegistry)


def get(name, default=None):
    """Get registry value by name
    """
    if not name.startswith(PREFIX):
        name = "{}.{}".format(PREFIX, name)
    registry = get_registry()
    try:
        return registry[name]
    except KeyError:
        return default


def set(name, value):
    """Set registry value
    """
    if not name.startswith(PREFIX):
        name = "{}.{}".format(PREFIX, name)

    registry = get_registry()
    try:
        registry[name] = value
    except WrongType:
        field_type = None
        for field in ISenaiteRegistry.namesAndDescriptions():
            if field[0] == name:
                field_type = field[1]
                break
        raise TypeError(
            u"The value parameter for the field {name} needs to be "
            u"{of_class} instead of {of_type}".format(
                name=name,
                of_class=str(field_type.__class__),
                of_type=type(value),
            ),
        )
