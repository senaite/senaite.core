# -*- coding: utf-8 -*-

from datetime import datetime

from bika.lims import api
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import IASTMImporter
from senaite.core.interfaces import ISenaiteCore
from six import StringIO
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer


@adapter(Interface, Interface, ISenaiteCore)
@implementer(IASTMImporter)
class ASTMImporter(object):
    """Adapter imports JSON ASTM messages
    """
    def __init__(self, data, message, request):
        self.data = data
        self.message = message
        self.request = request

        # internals for properties
        self._importlog = None
        self._instrument = None
        self._sample = None

    def import_data(self):
        """Import the instrument JSON data
        """
        raise NotImplementedError("ASTM import logic must be implemented "
                                  "by a specific instrument importer")

    @property
    def instrument(self):
        """Query the instrument of this import
        """
        if self._instrument:
            return self._instrument

        instrument = None
        # get the instrument name, serial and version from the data
        name, serial, version = self.get_sender()
        query = {"portal_type": "Instrument"}
        results = api.search(query, SETUP_CATALOG)

        for brain in results:
            obj = api.get_object(brain)
            model = obj.getModel()
            serialno = obj.getSerialNo()
            if model == name and serial is None:
                instrument = obj
            elif model == name and serialno == serial:
                instrument = obj

        self._instrument = instrument
        return instrument

    @property
    def sample(self):
        """Query the sample of this import
        """
        if self._sample:
            return self._sample

        sample = None
        # get the sample ID from the data
        sid = self.get_sample_id()
        # Query by Sample ID
        query_sid = {"getId": sid}
        # Query by Client Sample ID
        query_csid = {"getClientSampleID": sid}

        results = api.search(query_sid, SAMPLE_CATALOG)
        if not results:
            results = api.search(query_csid, SAMPLE_CATALOG)
        if len(results) == 1:
            sample = api.get_object(results[0])

        self._sample = sample
        return sample

    def log(self, message, level="info"):
        """Append log to logs
        """
        timestamp = datetime.now()
        message = "{} {}: {}".format(timestamp, level.upper(), message)
        if self.instrument and self._importlog is None:
            self._importlog = api.create(self.instrument, "AutoImportLog")
            self._importlog.setInstrument(self.instrument)
            self._importlog.setInterface(", ".join(self.get_sender()))
            self._importlog.setImportFile("ASTM")
            self._importlog.setLogTime(timestamp.isoformat())
        if self._importlog:
            results = self._importlog.getResults()
            if results:
                results += "\n"
            messages = "{}{}".format(results, message)
            self._importlog.setResults(messages)
        return message

    def get_sender(self):
        """Return the instrument name, serial and version
        """
        header = self.get_header()
        if not header:
            return None
        sender = header.get("sender", {})
        name = sender.get("name", "")
        serial = sender.get("serial", "")
        version = sender.get("version", "")
        return name, serial, version

    def get_sample_id(self, default=None):
        """Return the sender information
        """
        order = self.get_order()
        if not order:
            return default
        sid = order.get("sample_id")
        if not sid:
            return default
        return sid

    def create_attachment(self, container, contents, filename=None):
        """Create a new attachment with the given contents
        """
        attachment = api.create(container, "Attachment", title=filename)
        attachment_file = StringIO(contents)
        attachment_file.filename = filename
        attachment.setAttachmentFile(attachment_file)
        return attachment

    def get_header(self):
        headers = self.get_headers()
        if len(headers) != 1:
            return {}
        return headers[0]

    def get_order(self):
        orders = self.get_orders()
        if len(orders) != 1:
            return {}
        return orders[0]

    def get_headers(self):
        return self.data.get("H", [])

    def get_orders(self):
        return self.data.get("O", [])

    def get_comments(self):
        return self.data.get("C", [])

    def get_patients(self):
        return self.data.get("P", [])

    def get_results(self):
        return self.data.get("R", [])

    def get_manufacturer_infos(self):
        return self.data.get("M", [])
