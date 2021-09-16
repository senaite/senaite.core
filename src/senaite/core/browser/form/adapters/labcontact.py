# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Lab Contact
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # Populate the default department
        if name == "Departments":
            departments = map(api.get_object_by_uid, value)
            default_dpt = self.context.getDefaultDepartment()
            empty = [{"title": _("None"), "value": None}]
            opts = map(lambda o: dict(
                title=api.get_title(o), value=api.get_uid(o)), departments)
            self.add_update_field("DefaultDepartment", {
                "selected": [api.get_uid(default_dpt)] if default_dpt else [],
                "options": empty + opts})

        return self.data
