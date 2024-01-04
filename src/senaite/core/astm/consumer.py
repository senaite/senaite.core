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

from bika.lims import api
from senaite.core import logger
from senaite.core.interfaces import IASTMImporter
from senaite.jsonapi.interfaces import IPushConsumer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import implementer


@adapter(Interface)
@implementer(IPushConsumer)
class PushConsumer(object):
    """Adapter that handles push requests for name "enaite.core.lis2a.import"
    """
    def __init__(self, data):
        self.data = data
        self.request = api.get_request()

    def get_sender_name(self, json_data, default=""):
        """Parse the sender name from the header record
        """
        header = json_data.get("H")
        if not isinstance(header, list) and len(header) != 1:
            return default
        sender = header[0].get("sender", {})
        return sender.get("name", default)

    def process(self):
        """Processes the LIS2-A compliant message.
        """
        # Extract LIS2-A messages from the data
        messages = self.data.get("messages")
        if not messages:
            raise ValueError("No messages found: {}".format(repr(self.data)))

        # Just in case we got a message instead of a list of messages
        if api.is_string(messages):
            messages = (messages,)

        logger.info("Received {} messages".format(len(messages)))

        # process messages
        for message in messages:

            json_data = api.parse_json(message, None)
            if json_data is None:
                logger.error("Invalid JSON message: %r" % message)
                continue

            sender_name = self.get_sender_name(json_data)

            # ASTM Data Importer Adapter
            importer = queryMultiAdapter(
                (json_data, message, self.request), IASTMImporter,
                name=sender_name)
            if importer is None:
                importer = getMultiAdapter(
                    (json_data, message, self.request), IASTMImporter)

            # import the data
            try:
                result = importer.import_data()
            except Exception as exc:
                message = "An error occured in '{}.import_data()'".format(
                    importer.__class__.__name__)
                logger.error(exc)
                continue

            if api.is_string(result):
                logger.error("Failed to import ASTM data with importer '{}'"
                             .format(importer.__class__.__name__))
                logger.error("Reason: {}".format(result))

        return True
