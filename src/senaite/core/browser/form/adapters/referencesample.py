# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.browser.form.adapters import EditFormAdapterBase


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Reference Samples
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")
        # Populate dependencies of the reference definition
        if name == "ReferenceDefinition":
            definitions = map(api.get_object_by_uid, filter(api.is_uid, value))
            if len(definitions) > 0:
                definition = definitions[0]
                self.add_update_field("Hazardous", definition.getHazardous())
                self.add_update_field("Blank", definition.getBlank())

                # set reference results
                selected = []
                records = definition.getReferenceResults()
                for rec in records:
                    uid = rec.get("uid")
                    selected.append(uid)
                    self.add_update_field("result.%s" % uid, rec.get("result"))
                    self.add_update_field("min.%s" % uid, rec.get("min"))
                    self.add_update_field("max.%s" % uid, rec.get("max"))
                    self.add_update_field("error.%s" % uid, rec.get("error"))

                self.add_state_listing("list", selected_uids=selected)

        return self.data
