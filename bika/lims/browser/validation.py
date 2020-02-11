# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes.browser.validation import InlineValidationView as _IVV
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
import json


SKIP_VALIDATION_FIELDTYPES = (
    'image', 'file', 'datetime', 'reference', 'uidreference', 'proxy')

class InlineValidationView(_IVV):

    def __call__(self, uid, fname, value):
        '''Validate a given field. Return any error messages.
        '''
        res = {'errmsg': ''}

        rc = getToolByName(aq_inner(self.context), 'reference_catalog')
        instance = rc.lookupObject(uid)
        # make sure this works for portal_factory items
        if instance is None:
            instance = self.context

        field = instance.getField(fname)
        if field and field.type not in SKIP_VALIDATION_FIELDTYPES:
            return super(InlineValidationView, self).__call__(uid, fname, value)

        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(res)
