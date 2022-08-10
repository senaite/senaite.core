# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from senaite.core.registry import get_registry_interfaces
from senaite.core.registry.schema import ISenaiteRegistry
from zope.component import getUtility
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
            proxy = registry.forInterface(interface)
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
            proxy = registry.forInterface(interface)
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
