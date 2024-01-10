# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

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
        name = self.get_instrument_name()
        serial = self.get_instrument_serial()
        query = {"portal_type": "Instrument"}
        results = api.search(query, SETUP_CATALOG)

        for brain in results:
            obj = api.get_object(brain)
            model = obj.getModel()
            title = obj.Title()
            serialno = obj.getSerialNo()
            # lookup instrument by model and serial
            if model == name and serialno == serial:
                instrument = obj
            # lookup instrument by title and serial
            elif title == name and serialno == serial:
                instrument = obj
            # lookup instrument by model only
            elif model == name:
                instrument = obj
            # lookup instrument by title only
            elif title == name:
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

    def get_sample_id(self, default=None):
        """Get the Sample ID
        """
        order = self.get_order()
        if not order:
            return default
        sid = order.get("sample_id")
        if not sid:
            return default
        return sid

    def get_instrument_name(self):
        """Get the instrument name
        """
        sender = self.get_sender()
        return sender[0]

    def get_instrument_serial(self):
        """Get the instrument serial number
        """
        sender = self.get_sender()
        return sender[1]

    def get_instrument_version(self):
        """Get the instrument serial number
        """
        sender = self.get_sender()
        return sender[2]

    def get_sender(self):
        """Return the instrument name, serial and version

        :returns: Tuple of instrument name, serial, version
        """
        header = self.get_header()
        if not header:
            return None
        sender = header.get("sender", {})
        name = sender.get("name", "")
        serial = sender.get("serial", "")
        version = sender.get("version", "")
        return name, serial, version

    def create_attachment(self, container, contents, filename=None):
        """Create a new attachment with the given contents
        """
        attachment = api.create(container, "Attachment", title=filename)
        attachment_file = StringIO(contents)
        attachment_file.filename = filename
        attachment.setAttachmentFile(attachment_file)
        # do not render in report
        attachment.setRenderInReport(False)
        return attachment

    def get_metadata(self):
        """Metadata provided by the instrument parser module
        """
        return self.data.get("metadata", {})

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
