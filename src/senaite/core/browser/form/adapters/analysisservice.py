# -*- coding: utf-8 -*-

from senaite.core.interfaces import IAjaxEditForm
from zope.interface import implementer


@implementer(IAjaxEditForm)
class EditForm(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def initialized(self, data):
        return {}

    def modified(self, data):
        return {}
