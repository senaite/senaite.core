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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import io
import mimetypes
import os
import re
import six
import socket
from email import encoders
from email.header import Header
from email.Message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from email.Utils import parseaddr
from smtplib import SMTPException
from string import Template
from StringIO import StringIO

import six

from bika.lims import api
from bika.lims import logger
from Products.CMFPlone.utils import safe_unicode

try:
    file_types = (file, io.IOBase)
except NameError:
    file_types = (io.IOBase,)

# RFC 2822 local-part: dot-atom or quoted-string
# characters allowed in atom: A-Za-z0-9!#$%&'*+-/=?^_`{|}~
# RFC 2821 domain: max 255 characters
_LOCAL_RE = re.compile(r'([A-Za-z0-9!#$%&\'*+\-/=?^_`{|}~]+'
                       r'(\.[A-Za-z0-9!#$%&\'*+\-/=?^_`{|}~]+)*|'
                       r'"[^(\|")]*")@[^@]{3,255}$')

# RFC 2821 local-part: max 64 characters
# RFC 2821 domain: sequence of dot-separated labels
# characters allowed in label: A-Za-z0-9-, first is a letter
# Even though the RFC does not allow it all-numeric domains do exist
_DOMAIN_RE = re.compile(r'[^@]{1,64}@[A-Za-z0-9][A-Za-z0-9-]*'
                        r'(\.[A-Za-z0-9][A-Za-z0-9-]*)+$')


def to_email_address(address, name=""):
    """Convert the given address, name pair to an email address

    :param address: The email address
    :type address: basestring
    :param name: The real name of the person owning the email address
    :type name: basestring
    :returns: Email address suitable for an RFC 2822 From, To or Cc header
    """
    pair = (name, address)
    return formataddr(pair)


def parse_email_address(address):
    """Parse a given name/email pair

    :param address: The name/email string to parse
    :type address: basestring
    :returns: Tuple of (name, email)
    """
    if not isinstance(address, six.string_types):
        raise ValueError("Expected a string, got {}".format(type(address)))
    return parseaddr(address)


def to_email_subject(subject):
    """Convert the given subject to an email subject

    :param subject: The email subject
    :type subject: basestring
    :returns: Encoded email subject header
    """
    if not isinstance(subject, six.string_types):
        raise TypeError("Expected string, got '{}'".format(type(subject)))
    return Header(s=safe_unicode(subject), charset="utf8")


def to_email_body_text(body, **kw):
    """Convert the given body template to a text/plain type MIME document

    :param body: The email body text or template
    :type body: basestring
    :returns: MIMEText
    """
    body_template = Template(safe_unicode(body)).safe_substitute(**kw)
    return MIMEText(body_template, _subtype="plain", _charset="utf8")


def to_email_attachment(filedata, filename="", **kw):
    """Create a new MIME Attachment

    The Content-Type: header is build from the maintype and subtype of the
    guessed filename mimetype. Additional parameters for this header are
    taken from the keyword arguments.

    :param filedata: File, file path, filedata
    :type filedata: FileIO, MIMEBase, str
    :param filename: Filename to use
    :type filename: str
    :returns: MIME Attachment
    """
    data = ""
    maintype = "application"
    subtype = "octet-stream"

    def is_file(s):
        try:
            return os.path.exists(s)
        except TypeError:
            return False

    # Handle attachment
    if isinstance(filedata, MIMEBase):
        # return immediately
        return filedata
    # Handle file/StringIO
    elif isinstance(filedata, (file_types, StringIO)):
        data = filedata.read()
    # Handle file paths
    if is_file(filedata):
        filename = filename or os.path.basename(filedata)
        with open(filedata, "r") as f:
            # read the filedata from the filepath
            data = f.read()
    # Handle raw filedata
    elif isinstance(filedata, six.string_types):
        data = filedata

    # Set MIME type from keyword arguments or guess it from the filename
    mime_type = kw.pop("mime_type", None) or mimetypes.guess_type(filename)[0]
    if mime_type is not None:
        maintype, subtype = mime_type.split("/")

    attachment = MIMEBase(maintype, subtype, **kw)
    attachment.set_payload(data)
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition",
                          "attachment; filename=%s" % filename)
    return attachment


def is_valid_email_address(address):
    """Check if the given address is a valid email address

    Code taken from `CMFDefault.utils.checkEmailAddress`

    :param address: The email address to check
    :type address: str
    :returns: True if the address is a valid email
    """
    if not isinstance(address, six.string_types):
        return False
    if not _LOCAL_RE.match(address):
        return False
    if not _DOMAIN_RE.match(address):
        return False
    return True


def compose_email(from_addr, to_addr, subj, body, attachments=[], **kw):
    """Compose a RFC 2822 MIME message

    :param from_address: Email from address
    :param to_address: An email or a list of emails
    :param subject: Email subject
    :param body: Email body
    :param attachments: List of email attachments
    :returns: MIME message
    """
    _preamble = "This is a multi-part message in MIME format.\n"
    _from = to_email_address(from_addr)
    if isinstance(to_addr, six.string_types):
        to_addr = [to_addr]
    _to = map(to_email_address, to_addr)
    _subject = to_email_subject(subj)
    _body = to_email_body_text(body, **kw)

    # Create the enclosing message
    mime_msg = MIMEMultipart()
    mime_msg.preamble = _preamble
    mime_msg["Subject"] = _subject
    mime_msg["From"] = _from
    mime_msg["To"] = ", ".join(_to)
    mime_msg.attach(_body)

    # Attach attachments
    for attachment in attachments:
        mime_msg.attach(to_email_attachment(attachment))

    return mime_msg


def send_email(email, immediate=True):
    """Send the email via the MailHost tool

    :param email: Email message or string
    :type email: Message or str
    :param immediate: True to send the email immediately
    :type immediately: bool
    :returns: True if the email delivery was successful
    """
    if not isinstance(email, (six.string_types, Message)):
        raise TypeError("Email must be a Message or str")

    try:
        mailhost = api.get_tool("MailHost")
        mailhost.send(email, immediate=immediate)
    except SMTPException as e:
        logger.error(e)
        return False
    except socket.error as e:
        logger.error(e)
        return False
    return True
