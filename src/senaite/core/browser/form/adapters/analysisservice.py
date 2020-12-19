# -*- coding: utf-8 -*-

from six import string_types

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.catalog import SETUP_CATALOG
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

    @property
    def setup_catalog(self):
        return api.get_tool(SETUP_CATALOG)

    def validate_keyword(self, value):
        """Validate the service keyword
        """
        current_value = self.context.getKeyword()
        # Check if the values changed
        if current_value == value:
            # nothing changed
            return
        # Check if the new value is empty
        if not value:
            return _("Keyword required")
        # Check if the current value is used in a calculation
        ref = "[{}]".format(current_value)
        query = {"portal_type": "Calculation"}
        for brain in self.setup_catalog(query):
            calc = api.get_object(brain)
            if ref in calc.getFormula():
                return _("Current keyword '{}' used in calculation '{}'"
                         .format(current_value, api.get_title(calc)))
        # Check the current value with the validator
        validator = ServiceKeywordValidator()
        check = validator(value, instance=self.context)
        if isinstance(check, string_types):
            return _(check)
        return None
