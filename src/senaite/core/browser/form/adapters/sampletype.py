# -*- coding: utf-8 -*-

from senaite.core.browser.form.adapters import EditFormAdapterBase
from bika.lims.vocabularies import getStickerTemplates


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Sample Type
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # filter default small/large sticker
        if name == "AdmittedStickerTemplates.admitted":
            # get the sticker
            templates = filter(
                lambda t: t.get("id") in value, getStickerTemplates())

            # prepare options for the select field
            opts = map(lambda t: dict(
                title=t.get("title"), value=t.get("id")), templates)

            # set default small sticker
            default_small = self.context.getDefaultSmallSticker()
            self.add_update_field("AdmittedStickerTemplates.small_default", {
                "selected": [default_small] if default_small else [],
                "options": opts})

            # set default large sticker
            default_large = self.context.getDefaultLargeSticker()
            self.add_update_field("AdmittedStickerTemplates.large_default", {
                "selected": [default_large] if default_large else [],
                "options": opts})

        return self.data
