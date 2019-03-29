# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

import plone
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView


class ajaxGetMethodCalculation(BrowserView):
    """ Returns the calculation assigned to the defined method.
        uid: unique identifier of the method
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        calcdict = {}
        uc = getToolByName(self, 'uid_catalog')
        method = uc(UID=self.request.get("uid", '0'))
        if method and len(method) == 1:
            calc = method[0].getObject().getCalculation()
            if calc:
                calcdict = {'uid': calc.UID(),
                            'title': calc.Title()}
        return json.dumps(calcdict)
