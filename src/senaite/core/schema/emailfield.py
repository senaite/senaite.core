import re

from plone.schema import _
from senaite.core.schema.interfaces import IEmailField
from senaite.core.schema.textlinefield import TextLineField
from zope.interface import implementer
from zope.schema.interfaces import ValidationError

# Taken from http://www.regular-expressions.info/email.html
_isemail = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}"
_isemail = re.compile(_isemail).match


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
        if not value or _isemail(value):
            return

        raise InvalidEmail(value)
