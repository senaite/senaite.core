# -*- coding: utf-8 -*-

from plone.dexterity.browser.add import DefaultAddForm as BaseAddForm
from plone.dexterity.browser.add import DefaultAddView as BaseAddView


class DefaultAddForm(BaseAddForm):
    """Patched Add Form to handle renameAfterCreation of DX objects
    """


class DefaultAddView(BaseAddView):
    form = DefaultAddForm
