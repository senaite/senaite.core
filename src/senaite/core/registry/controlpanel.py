# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from senaite.core.registry import PREFIX
from senaite.core.registry import ISenaiteRegistry


class SenaiteRegistryControlPanelForm(RegistryEditForm):
    schema = ISenaiteRegistry
    schema_prefix = PREFIX
    label = _("SENAITE Registry")


SenaiteRegistryControlPanelView = layout.wrap_form(
    SenaiteRegistryControlPanelForm, ControlPanelFormWrapper)
