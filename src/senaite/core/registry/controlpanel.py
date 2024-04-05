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

from bika.lims import senaiteMessageFactory as _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from senaite.core.registry import get_registry_interfaces
from senaite.core.registry.schema import ISenaiteRegistry
from senaite.core.interfaces import ISenaiteRegistryFactory
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import alsoProvides


class ContextProxy(object):
    """Lookup fields from extended interfaces

    Code taken from here:
    https://github.com/bluedynamics/bda.plone.shop/blob/master/src/bda/plone/shop/browser/controlpanel.py
    """
    def __init__(self, interfaces):
        self.__interfaces = interfaces
        alsoProvides(self, *interfaces)

    def __setattr__(self, name, value):
        if name.startswith("__") or name.startswith("_ContextProxy__"):
            return object.__setattr__(self, name, value)

        registry = getUtility(IRegistry)
        for interface in self.__interfaces:
            factory = queryUtility(ISenaiteRegistryFactory,
                                   name=interface.__identifier__,
                                   default=None)
            proxy = registry.forInterface(interface, factory=factory)
            try:
                getattr(proxy, name)
            except AttributeError:
                pass
            else:
                return setattr(proxy, name, value)
        raise AttributeError(name)

    def __getattr__(self, name):
        if name.startswith("__") or name.startswith("_ContextProxy__"):
            return object.__getattr__(self, name)

        registry = getUtility(IRegistry)
        for interface in self.__interfaces:
            factory = queryUtility(ISenaiteRegistryFactory,
                                   name=interface.__identifier__,
                                   default=None)
            proxy = registry.forInterface(interface, factory=factory)
            try:
                return getattr(proxy, name)
            except AttributeError:
                pass
        raise AttributeError(name)


class SenaiteRegistryControlPanelForm(RegistryEditForm):
    schema = ISenaiteRegistry
    label = _("SENAITE Registry")

    def getContent(self):
        interfaces = [self.schema]
        interfaces.extend(self.additionalSchemata)
        return ContextProxy(interfaces)

    @property
    def additionalSchemata(self):
        for interface in get_registry_interfaces():
            yield interface

    def updateFields(self):
        super(SenaiteRegistryControlPanelForm, self).updateFields()

    def updateWidgets(self):
        super(SenaiteRegistryControlPanelForm, self).updateWidgets()


SenaiteRegistryControlPanelView = layout.wrap_form(
    SenaiteRegistryControlPanelForm, ControlPanelFormWrapper)
