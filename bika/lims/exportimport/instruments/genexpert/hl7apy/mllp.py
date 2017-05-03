# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2015, CRS4
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import
from __future__ import unicode_literals

import re
import socket
try:
    from SocketServer import StreamRequestHandler, TCPServer, ThreadingMixIn
except ImportError:
    from socketserver import StreamRequestHandler, TCPServer, ThreadingMixIn

from bika.lims.exportimport.instruments.genexpert.hl7apy.parser import get_message_type
from bika.lims.exportimport.instruments.genexpert.hl7apy.exceptions import HL7apyException, ParserError


class UnsupportedMessageType(HL7apyException):
    """
    Error that occurs when the :class:`MLLPServer` receives a message without an associated handler
    """
    def __init__(self, msg_type):
        self.msg_type = msg_type

    def __str__(self):
        return 'Unsupported message type %s' % self.msg_type


class InvalidHL7Message(HL7apyException):
    """
    Error that occurs when the :class:`MLLPServer` receives a string which doesn't represent an ER7-encoded HL7 message
    """
    def __str__(self):
        return 'The string received is not a valid HL7 message'


class _MLLPRequestHandler(StreamRequestHandler):
    encoding = 'utf-8'

    def __init__(self, *args, **kwargs):
        StreamRequestHandler.__init__(self, *args, **kwargs)

    def setup(self):
        self.sb = b"\x0b"
        self.eb = b"\x1c"
        self.cr = b"\x0d"
        self.validator = re.compile(
            ''.join([self.sb.decode('ascii'), r"(([^\r]+\r)*([^\r]+\r?))", self.eb.decode('ascii'), self.cr.decode('ascii')]))
        self.handlers = self.server.handlers
        self.timeout = self.server.timeout

        StreamRequestHandler.setup(self)

    def handle(self):
        end_seq = self.eb + self.cr
        try:
            line = self.request.recv(3)
        except socket.timeout:
            self.request.close()
            return

        if line[:1] != self.sb:  # First MLLP char
            self.request.close()
            return

        while line[-2:] != end_seq:
            try:
                char = self.rfile.read(1)
                if not char:
                    break
                line += char
            except socket.timeout:
                self.request.close()
                return

        message = self._extract_hl7_message(line.decode(self.encoding))
        if message is not None:
            try:
                response = self._route_message(message)
            except Exception:
                self.request.close()
            else:
                # encode the response
                self.wfile.write(response.encode(self.encoding))
        self.request.close()

    def _extract_hl7_message(self, msg):
        message = None
        matched = self.validator.match(msg)
        if matched is not None:
            message = matched.groups()[0]
        return message

    def _route_message(self, msg):
        try:
            try:
                msg_type = get_message_type(msg)
            except ParserError:
                raise InvalidHL7Message

            try:
                handler, args = self.handlers[msg_type][0], self.handlers[msg_type][1:]
            except KeyError:
                raise UnsupportedMessageType(msg_type)

            h = handler(msg, *args)
            return h.reply()
        except Exception as e:
            try:
                err_handler, args = self.handlers['ERR'][0], self.handlers['ERR'][1:]
            except KeyError:
                raise e
            else:
                h = err_handler(e, msg, *args)
                return h.reply()


class MLLPServer(ThreadingMixIn, TCPServer):
    """
        A :class:`TCPServer <SocketServer.TCPServer>` subclass that implements an MLLP server.
        It receives MLLP-encoded HL7 and redirects them to the correct handler, according to the
        :attr:`handlers` dictionary passed in.

        The :attr:`handlers` dictionary is structured as follows. Every key represents a message type (i.e.,
        the MSH.9) to handle, and the associated value is a tuple containing a subclass of
        :class:`AbstractHandler` for that message type and additional arguments to pass to its
        constructor.

        It is possible to specify a special handler for errors using the ``ERR`` key.
        In this case the handler should subclass :class:`AbstractErrorHandler`,
        which receives, in addition to other parameters, the raised exception as the first argument.
        If the special handler is not specified the server will just close the connection.

        The class allows to specify the timeout to wait before closing the connection.

        :param host: the address of the listener
        :param port: the port of the listener
        :param handlers: the dictionary that specifies the handler classes for every kind of supported message.
        :param timeout: the timeout for the requests
    """
    allow_reuse_address = True

    def __init__(self, host, port, handlers, timeout=10):
        self.host = host
        self.port = port
        self.handlers = handlers
        self.timeout = timeout
        TCPServer.__init__(self, (host, port), _MLLPRequestHandler)


class AbstractHandler(object):
    """
        Abstract transaction handler. Handlers should implement the
        :func:`reply() <AbstractHandler.reply>` method which handle the incoming message.
        The incoming message is accessible using the attribute :attr:`incoming_message`

        :param message: the ER7-formatted HL7 message to handle
    """
    def __init__(self, message):
        self.incoming_message = message

    def reply(self):
        """
            Abstract method. It should implement the handling of the request message and return the response.
        """
        raise NotImplementedError("The method reply() must be implemented in subclasses")


class AbstractErrorHandler(AbstractHandler):
    """
    Abstract transaction handler for errors. It receives also the instance of the exception occurred, which will be
    accessible through the :attr:`exc` attribute.
    Specific exceptions that can be handled are :exc:`UnsupportedMessageType` and :exc:`InvalidHL7Message`

    :param exc: the :exc:`Exception` occurred
    """
    def __init__(self, exc, message):
        super(AbstractErrorHandler, self).__init__(message)
        self.exc = exc

    def reply(self):
        super(AbstractErrorHandler, self).reply()
