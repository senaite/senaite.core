# -*- coding: utf-8 -*-

from bika.lims.interfaces import ICalculation
from senaite.core.interfaces import IAjaxEditForm
from zope.component import adapter
from zope.interface import implementer


@adapter(ICalculation)
@implementer(IAjaxEditForm)
class EditForm(object):

    def initialized(self, data):
        return {}

    def modified(self, data):
        return {}
