# -*- coding: utf-8 -*-

from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Analysis Profiles
    """

    def initialized(self, data):
        self.toggle_price_vat_fields(False)
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")
        if name == "UseAnalysisProfilePrice":
            self.toggle_price_vat_fields(value)
        return self.data

    def toggle_price_vat_fields(self, toggle=False):
        if toggle:
            self.add_show_field("AnalysisProfilePrice")
            self.add_show_field("AnalysisProfileVAT")
        else:
            self.add_hide_field("AnalysisProfilePrice")
            self.add_hide_field("AnalysisProfileVAT")
