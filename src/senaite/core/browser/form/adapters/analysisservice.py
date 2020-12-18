# -*- coding: utf-8 -*-

from six import string_types

from bika.lims import senaiteMessageFactory as _
from bika.lims.validators import ServiceKeywordValidator
from senaite.core.interfaces import IAjaxEditForm
from zope.interface import implementer


@implementer(IAjaxEditForm)
class EditForm(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = {
            "hide": [],
            "show": [],
            "update": {},
            "errors": {},
            "messages": [],
        }

    def initialized(self, data):
        self.response["hide"].append("Remarks")
        return self.response

    def modified(self, data):
        errors = {}
        name = data.get("name")
        value = data.get("value")
        if name == "Keyword":
            errors["Keyword"] = self.validate_keyword(value)
        self.response["errors"] = errors
        return self.response

    def validate_keyword(self, value):
        """Validate the service keyword
        """
        current_value = self.context.getKeyword()
        if current_value == value:
            # nothing changed
            return
        if not value:
            return _("Keyword required")
        validator = ServiceKeywordValidator()
        check = validator(value, instance=self.context)
        if isinstance(check, string_types):
            return _(check)
        return None
