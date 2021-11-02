# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from z3c.form.error import ErrorViewSnippet
from zope.component import adapter
from senaite.core.interfaces import ISenaiteFormLayer


@adapter(ValueError, ISenaiteFormLayer, None, None, None, None)
class ValueErrorViewSnippet(ErrorViewSnippet):
    """An error view for ValueError.
    """

    defaultMessage = _("Validation failed.")

    def createMessage(self):
        message = self.error.message
        return message or self.defaultMessage
