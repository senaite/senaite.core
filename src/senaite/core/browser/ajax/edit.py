# -*- coding: utf-8 -*-

import json

from bika.lims.browser import BrowserView
from bika.lims.decorators import returns_json


class AjaxEditView(BrowserView):
    """Ajax Edit View
    """

    @returns_json
    def __call__(self):
        data = self.get_json()
        if not data:
            return "{}"

        import pdb; pdb.set_trace()
        view = self.context.restrictedTraverse("base_edit")
        html = view()
        return {
            "html": html
        }

    def get_json(self):
        body = self.request.get("BODY", "{}")
        return json.loads(body)
