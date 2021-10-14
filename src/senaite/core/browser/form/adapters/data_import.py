# -*- coding: utf-8 -*-

import json
import os
import traceback

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.catalog import SETUP_CATALOG
from Products.Archetypes.public import DisplayList
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.exportimport import instruments
from senaite.core.exportimport.load_setup_data import LoadSetupData


class EditForm(EditFormAdapterBase):
    """Edit form adapter for data import
    """

    def initialized(self, data):
        # hide instrument interface selection
        self.add_hide_field("exim")
        return self.data

    def submit(self, data):
        setupfile = self.request.form.get("setupfile")
        setupexisting = self.request.form.get("setupexisting")
        auto_import_results = self.request.form.get("auto_import_results")
        if setupfile or setupexisting:
            self.handle_data_import()
        elif auto_import_results:
            view = api.get_view("auto_import_results")
            self.add_inner_html(".autoimport-results", view())
        else:
            self.handle_instrument_import()
        return self.data

    def handle_data_import(self):
        try:
            LoadSetupData(self.context, self.request)()
        except Exception:
            tb = traceback.format_exc()
            self.add_status_message(
                message=tb, title="Error", level="danger", flush=True)
            logger.error(tb)
            return False
        self.add_status_message(
            message=_("Data import successful"),
            title="Info", level="success", flush=True)
        return True

    def handle_instrument_import(self):
        iface = self.request.form.get("exim")
        exim = self.get_exim_by_interface(iface)
        if not exim:
            self.add_status_message(
                message=_("No importer not found for interface '{}'"
                          .format(iface)),
                title="Error", level="danger", flush=True)
            return False

        results = exim.Import(self.context, self.request)

        # BBB: Importers return JSON
        results = json.loads(results)

        template = self.get_default_import_results_template()
        html = ViewPageTemplateFile(template)(self, import_results=results)
        self.add_inner_html("#import_results", html)

        self.add_status_message(
            message=_("Instrument import finished"),
            title="", level="info", flush=True)

        return True

    def modified(self, data):
        name = data.get("name")
        value = data.get("value")

        # instrument selected
        if name == "instrument":
            uid = value[0] if value else None
            instrument = api.get_object_by_uid(uid) if uid else None

            # hide instrument interface selection
            self.add_hide_field("exim")
            # flush import form container
            self.add_inner_html("#import_form", "")

            # no instrument selected
            if instrument is None:
                return self.data

            # query import interfacs for the selected instrument
            ifaces = self.get_import_interfaces_info_for(instrument)

            # no import interfaces avaialble
            if not ifaces:
                self.add_notification(
                    title="Warning",
                    message=_(
                        "No instrument import interfaces available for {}"
                        .format(instrument.title)))
                return self.data

            # show instrument interface selection
            self.add_show_field("exim")

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
            self.add_inner_html("#import_results", "")

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

    def get_default_import_results_template(self):
        """Returns the path of the default import template
        """
        import senaite.core.exportimport
        path = os.path.dirname(senaite.core.exportimport.__file__)
        template = "import_results.pt"
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
