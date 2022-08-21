# -*- coding: utf-8 -*-

from Products.CMFPlone.controlpanel.browser.quickinstaller import \
    ManageProductsView as BaseView


class ManageProductsView(BaseView):
    """
    """

    def get_available(self):
        """Available add-ons
        """
        available = []
        available_addons = self.get_addons(apply_filter="available").values()
        for addon in available_addons:
            id = addon.get("id")
            if id.startswith("plone."):
                continue
            elif id.startswith("Products."):
                continue
            elif id.startswith("collective."):
                continue
            elif id == "bika.lims":
                continue
            available.append(addon)
        return available
