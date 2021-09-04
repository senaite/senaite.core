# -*- coding: utf-8 -*-

import os

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.catalog import SETUP_CATALOG
from Products.Archetypes.public import DisplayList
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.exportimport import instruments


class EditForm(EditFormAdapterBase):
    """Edit form adapter for instrument imports
    """

    def initialized(self, data):
        return self.data

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # instrument selected
        if name == "instrument":
            uid = value[0] if value else None
            instrument = api.get_object_by_uid(uid)

            # check if the instrument is active
            if not api.is_active(instrument):
                self.add_readonly_field(
                    "exim", message=_("Instrument is inactive"))
                return self.data

            # populate the import interfaces selection list
            ifaces = self.get_import_interfaces_info_for(instrument)

            if not ifaces:
                # no interfaces available -> make selection field readonly
                self.add_readonly_field(
                    "exim", message=_("No import interfaces available"))
            else:
                self.add_editable_field(
                    "exim", message=_("Please select an import interface"))

                # populate the import interfaces selection
                i_opts = map(lambda i: dict(
                    title=i.get("title"), value=i.get("id")), ifaces)
                self.add_update_field("exim", {
                    "options": i_opts})

                # populate the import template
                exim = ifaces[0].get("exim")
                template = self.get_import_template(exim)
                self.add_inner_html("#import_form", template)

        # Import interface changed
        if name == "exim":
            iface = value[0]
            exim = self.get_exim_by_interface(iface)
            template = self.get_import_template(exim)
            self.add_inner_html("#import_form", template)

        return self.data

    def get_import_interfaces_info_for(self, instrument):
        """Return all import data interfaces for the given instrument
        """
        info = []
        ifaces = instrument.getImportDataInterface()
        for iface in ifaces:
            exim = self.get_exim_by_interface(iface)
            if exim:
                info.append({
                    "id": iface,
                    "title": exim.title,
                    "exim": exim,
                })
        return info

    def get_exim_by_interface(self, iface):
        """returns the exim module
        """
        return instruments.getExim(iface)

    def get_import_template(self, exim):
        """Returns the rendered exim template
        """
        template = self.get_instrument_import_template(exim)
        if os.path.isfile(template):
            return ViewPageTemplateFile(template)(self)
        # return the default instrument import template
        template = self.get_default_import_template()
        return ViewPageTemplateFile(template)(self)

    def get_instrument_import_template(self, exim):
        """Returns the import template path
        """
        exim_path = os.path.dirname(exim.__file__)
        exim_file = os.path.basename(exim.__file__)
        exim_name = os.path.splitext(exim_file)[0]
        template = "{}_import.pt".format(exim_name)
        return os.path.join(exim_path, template)

    def get_default_import_template(self):
        """Returns the path of the default import template
        """
        import senaite.core.exportimport.instruments
        path = os.path.dirname(senaite.core.exportimport.instruments.__file__)
        template = "instrument.pt"
        return os.path.join(path, template)

    def getAnalysisServicesDisplayList(self):
        """Returns a display list with the active Analysis Services available.

        The value is the keyword and the title is the text to be displayed.

        BBB: Keep camel case!

        This method is called by some instrument import templates
        -> see dynamic loading of import template above (called with `self`)
        """
        catalog = api.get_tool(SETUP_CATALOG)
        brains = catalog(
            portal_type="AnalysisService",
            is_active=True)
        items = []
        for item in brains:
            items.append((item.getKeyword, item.Title))
        items.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return DisplayList(list(items))
