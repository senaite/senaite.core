# -*- coding: utf-8 -*-

from bika.lims.api.mail import is_valid_email_address
from plone.schema import _
from senaite.core.schema.interfaces import IEmailField
from senaite.core.schema.textlinefield import TextLineField
from zope.interface import implementer
from zope.schema.interfaces import ValidationError


class InvalidEmail(ValidationError):
    __doc__ = _("""The specified email is not valid.""")


@implementer(IEmailField)
class EmailField(TextLineField):
    """Email schema field

    NOTE: This is an "almost" copy of plone.schema.email.Email, but inherits
     from TextLineField instead of NativeStringLine. Thereby, accepts (and
     stores) unicode
    """

    def _validate(self, value):
        super(EmailField, self)._validate(value)
        if not value or is_valid_email_address(value):
            return

        raise InvalidEmail(value)
