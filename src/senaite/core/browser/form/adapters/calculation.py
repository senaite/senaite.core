# -*- coding: utf-8 -*-

from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Calculation
    """

    def initialized(self, data):
        self.add_hide_field("cmfeditions_version_comment")
        self.add_hide_field("TestResult")
        return self.data

    def modified(self, data):
        return self.data
