# -*- coding: utf-8 -*-

from Products.CMFPlone.browser.admin import AddPloneSite


class AddSENAITESite(AddPloneSite):
    # Profiles that are installed by default
    default_extension_profiles = (
        "senaite.lims:default",
    )
