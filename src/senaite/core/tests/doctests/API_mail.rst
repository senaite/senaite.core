API for sending emails
======================

The mail API provides a simple interface to send emails in SENAITE.

NOTE: The API is called `mail` to avoid import conflicts with the Python `email`
      standard library.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_mail


Test Setup
----------

Imports:

    >>> import os
    >>> from __future__ import print_function

    >>> from bika.lims.api.mail import *

Variables:

    >>> cur_dir = os.path.dirname(__file__)
    >>> filename = "logo.png"
    >>> filepath = os.path.join(cur_dir, filename)
    

Email Address
-------------

This function converts an email address and name pair to a string value suitable
for an RFC 2822 `From`, `To` or `Cc` header:

    >>> to_address = to_email_address("rb@ridingbytes.com", "Ramon Bartl")

    >>> to_address
    'Ramon Bartl <rb@ridingbytes.com>'

    >>> to_email_address("rb@ridingbytes.com")
    'rb@ridingbytes.com'


Email Subject
-------------

This function converts a string to a compliant RFC 2822 subject header:

    >>> subject = u"Liberté"
    >>> email_subject = to_email_subject(subject)

    >>> email_subject
    <email.header.Header instance at ...>

    >>> print(email_subject)
    =?utf-8?q?Libert=C3=83=C2=A9?=


Email Body Text
---------------

This function coverts a given text to a text/plain MIME document:

    >>> text = "Check out SENAITE LIMS: $url"
    >>> email_body = to_email_body_text(text, url="https://www.senaite.com")

    >>> email_body
    <email.mime.text.MIMEText instance at ...>

    >>> print(email_body)
    From ...
    MIME-Version: 1.0
    Content-Type: text/plain; charset="utf-8"
    Content-Transfer-Encoding: quoted-printable
    <BLANKLINE>
    Check out SENAITE LIMS: https://www.senaite.com


Email Attachment
----------------

This function converts a filename with given filedata to a MIME attachment:

    >>> attachment1 = to_email_attachment(file(filepath), filename=filename)
    >>> attachment1
    <email.mime.base.MIMEBase instance at ...>

    >>> print(attachment1)
    From ...
    Content-Type: image/png
    MIME-Version: 1.0
    Content-Transfer-Encoding: base64
    Content-Disposition: attachment; filename=logo.png
    <BLANKLINE>
    iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABGdBTUEAALGPC/xhBQAAACBjSFJN
    ...
    5/sfV5M/kISv300AAAAASUVORK5CYII=


It is also possible to provide the full path to a file:

    >>> attachment2 = to_email_attachment(filepath)
    >>> attachment2
    <email.mime.base.MIMEBase instance at ...>

    >>> print(attachment2)
    From ...
    Content-Type: image/png
    MIME-Version: 1.0
    Content-Transfer-Encoding: base64
    Content-Disposition: attachment; filename=logo.png
    <BLANKLINE>
    iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABGdBTUEAALGPC/xhBQAAACBjSFJN
    ...
    5/sfV5M/kISv300AAAAASUVORK5CYII=


Providing an attachment works as well:


    >>> attachment3 = to_email_attachment(attachment2)
    >>> attachment3 == attachment2
    True


Email Address Validation
------------------------

This function checks if the given email address is valid:

    >>> is_valid_email_address("rb@ridingbytes.com")
    True

    >>> is_valid_email_address(u"rb@ridingbytes.de")
    True

    >>> is_valid_email_address("rb@ridingbytes")
    False

    >>> is_valid_email_address("@ridingbyte.com")
    False

    >>> is_valid_email_address("rb")
    False

    >>> is_valid_email_address(None)
    False

    >>> is_valid_email_address(object())
    False


Parse Email Address
-------------------

This function parses an email address string into a (name, email) tuple:

    >>> parse_email_address("Ramon Bartl <rb@ridingbytes.com>")
    ('Ramon Bartl', 'rb@ridingbytes.com')

    >>> parse_email_address("<rb@ridingbytes.com>")
    ('', 'rb@ridingbytes.com')

    >>> parse_email_address("rb@ridingbytes.com")
    ('', 'rb@ridingbytes.com')


Compose Email
-------------

This function composes a new MIME message:

    >>> message = compose_email("from@senaite.com",
    ...                         ["to@senaite.com", "to2@senaite.com"],
    ...                         "Test Émail",
    ...                         "Check out the new SENAITE website: $url",
    ...                         attachments=[filepath],
    ...                         url="https://www.senaite.com")

    >>> message
    <email.mime.multipart.MIMEMultipart instance at ...>

    >>> print(message)
    From ...
    Content-Type: multipart/mixed; boundary="..."
    MIME-Version: 1.0
    Subject: =?utf-8?q?Test_=C3=89mail?=
    From: from@senaite.com
    To: to@senaite.com, to2@senaite.com
    <BLANKLINE>
    This is a multi-part message in MIME format.
    <BLANKLINE>
    ...
    MIME-Version: 1.0
    Content-Type: text/plain; charset="utf-8"
    Content-Transfer-Encoding: quoted-printable
    <BLANKLINE>
    Check out the new SENAITE website: https://www.senaite.com
    ...
    Content-Type: image/png
    MIME-Version: 1.0
    Content-Transfer-Encoding: base64
    Content-Disposition: attachment; filename=logo.png
    <BLANKLINE>
    iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABGdBTUEAALGPC/xhBQAAACBjSFJN
    ...
    5/sfV5M/kISv300AAAAASUVORK5CYII=
    ...
    <BLANKLINE>
