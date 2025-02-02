# -*- coding: utf-8 -*-

from bika.lims.decorators import returns_json
from Products.Five.browser import BrowserView


class BaseActionView(BrowserView):
    """Base class for Action Views
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @returns_json
    def message(self, message, success=True, **kw):
        """Returns a JSON message
        """
        msg = {
            "message": message,
            "success": success,
        }
        msg.update(kw)
        return msg
