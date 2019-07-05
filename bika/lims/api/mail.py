# -*- coding: utf-8 -*-

import mimetypes
import os
import re
import socket
from email import encoders
from email.header import Header
from email.Message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from smtplib import SMTPException
from string import Template
from StringIO import StringIO

from bika.lims import api
from bika.lims import logger
from Products.CMFPlone.utils import safe_unicode

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


def to_email_subject(subject):
    """Convert the given subject to an email subject

    :param subject: The email subject
    :type subject: basestring
    :returns: Encoded email subject header
    """
    if not isinstance(subject, basestring):
        raise TypeError("Expected string, got '{}'".format(type(subject)))
    return Header(s=safe_unicode(subject), charset="utf8")


def to_email_body_text(body, **kw):
    """Convert the given body template to a text/* type MIME document

    :param body: The email body text or template
    :type body: basestring
    :returns: MIMEText
    """
    body_template = Template(safe_unicode(body)).safe_substitute(**kw)
    return MIMEText(body_template, _subtype="plain", _charset="utf8")


def to_email_attachment(file_or_path, filename="", **kw):
    """Create a new MIME Attachment

    The Content-Type: header is build from the maintype and subtype of the
    guessed filename mimetype. Additional parameters for this header are
    taken from the keyword arguments.

    :param file_or_path: OS-level file or absolute path
    :type file_or_path: str, FileIO, MIMEBase
    :param filename: Filename to use
    :type filedata: str
    :returns: MIMEBase
    """
    filedata = ""
    maintype = "application"
    subtype = "octet-stream"

    # Handle attachment
    if isinstance(file_or_path, MIMEBase):
        # return immediately
        return file_or_path
    # Handle file/StringIO
    elif isinstance(file_or_path, (file, StringIO)):
        filedata = file_or_path.read()
    # Handle file path
    elif os.path.isfile(file_or_path):
        filename = filename or os.path.basename(file_or_path)
        with open(file_or_path, "r") as f:
            # read the filedata from the filepath
            filedata = f.read()

    # file MIME-type
    mime_type = kw.pop("mime_type", None) or mimetypes.guess_type(filename)[0]
    if mime_type is not None:
        maintype, subtype = mime_type.split("/")

    attachment = MIMEBase(maintype, subtype, **kw)
    attachment.set_payload(filedata)
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition",
                          "attachment; filename=%s" % filename)
    return attachment


def is_valid_email_address(address):
    """Check if the given address is a valid email address

    Code taken from `CMFDefault.utils.checkEmailAddress`

    :param address: The email address to check
    :type address: basestring
    :returns: True if the address is a valid email
    """
    if not isinstance(address, basestring):
        return False
    if not _LOCAL_RE.match(address):
        return False
    if not _DOMAIN_RE.match(address):
        return False
    return True


def parse_email_address(address):
    """Parse a given email address

    :param address: The address string to parse
    :type address: basestring
    :returns: RFC 2822 email address
    """
    if not isinstance(address, basestring):
        raise ValueError("Expected a string, got {}".format(type(address)))

    # parse <name>, <email> recipient
    splitted = map(lambda s: s.strip(),
                   safe_unicode(address).rsplit(",", 1))

    pair = []
    for s in splitted:
        if is_valid_email_address(s):
            pair.insert(0, s)
        else:
            pair.append(s)

    return to_email_address(*pair)


def compose_email(from_addr, to_addr, subj, body, attachments=[], **kw):
    """Compose a RFC 2822 MIME message

    :param from_address: Email from address
    :param to_address: List of email or (name, email) pairs
    :param subject: Email subject
    :param body: Email body
    :param attachments: List of email attachments
    :returns: MIME message
    """
    _preamble = "This is a multi-part message in MIME format.\n"
    _from = to_email_address(from_addr)
    _to = to_email_address(to_addr)
    _subject = to_email_subject(subj)
    _body = to_email_body_text(body, **kw)

    # Create the enclosing message
    mime_msg = MIMEMultipart()
    mime_msg.preamble = _preamble
    mime_msg["Subject"] = _subject
    mime_msg["From"] = _from
    mime_msg["To"] = _to
    mime_msg.attach(_body)

    # Attach attachments
    for attachment in attachments:
        mime_msg.attach(to_email_attachment(attachment))

    return mime_msg


def send_email(email, immediate=True):
    """Send the email via the MailHost tool

    :param email: Email message or string
    :type email: Message or basestring
    :param immediate: True to send the email immediately
    :type immediately: bool
    :returns: True if the email delivery was successful
    """
    if not isinstance(email, (basestring, Message)):
        raise TypeError("Email must be an instance of MIMEBase or a string")

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
