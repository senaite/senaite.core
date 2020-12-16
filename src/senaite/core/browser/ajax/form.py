# -*- coding: utf-8 -*-

import json

from bika.lims.browser import BrowserView
from bika.lims.decorators import returns_json


class AjaxFormView(BrowserView):
    """Ajax Form View
    """

    @returns_json
    def initialized(self):
        return {
            "hide": ["description", "title"],
            "show": [],
        }

    @returns_json
    def modified(self):
        data = self.get_json()
        if not data:
            return {}
        return {
            "hide": ["MethodID"],
            "show": ["title", "description"],
            "update": {
                "description": "hahahahaha",
            }
        }

    def get_json(self):
        body = self.request.get("BODY", "{}")
        return json.loads(body)
