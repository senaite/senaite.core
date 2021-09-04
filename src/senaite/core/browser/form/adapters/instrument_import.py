# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.exportimport import instruments


class EditForm(EditFormAdapterBase):
    """Edit form adapter for instrument imports
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")

        # instrument selected
        if name == "instrument":
            value = data.get("value")
            uid = value[0] if value else None
            instrument = api.get_object_by_uid(uid)
            # check if the instrument is active
            if not api.is_active(instrument):
                self.add_readonly_field(
                    "exim", message=_("Instrument is inactive"))

            # populate the interfaces selection
            ifaces = self.get_import_interface_info_for(instrument)


            import pdb; pdb.set_trace()

            if not ifaces:
                self.add_readonly_field(
                    "exim", message=_("No import interfaces available"))
            else:
                self.add_show_field("exim")

            i_opts = map(lambda i: dict(
                title=i.get("title"), value=i.get("id")), ifaces)
            self.add_update_field("exim", {
                "options": i_opts})

            # show the import form

        return self.data

    def get_import_interface_info_for(self, instrument):
        """Return all import data interfaces for the given instrument
        """
        info = []
        ifaces = instrument.getImportDataInterface()
        for iface in ifaces:
            exim = instruments.getExim(iface)
            if exim:
                info.append({
                    "id": iface,
                    "title": exim.title,
                    "exim": exim,
                })
        return info
