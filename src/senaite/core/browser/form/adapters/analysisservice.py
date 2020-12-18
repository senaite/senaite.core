# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.catalog import SETUP_CATALOG
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
        # check for existing keyword
        catalog = api.get_tool(SETUP_CATALOG)
        query = {"portal_type": "AnalysisService", "getKeyword": value}
        brains = catalog.searchResults(query)
        if len(brains) > 0:
            brain = brains[0]
            return _(u"Keyword '{}' already used by analysis service '{}'"
                     .format(value, api.get_title(brain)))
        # check if current keyword is used in a calculation
        query = {"portal_type": "Calculation"}
        brains = catalog(query)
        ref = "[{}]".format(current_value)
        for brain in brains:
            calc = api.get_object(brain)
            if ref in calc.getFormula():
                return _(u"Current keyword used in calculation '{}'"
                         .format(api.get_title(calc)))
        return None
