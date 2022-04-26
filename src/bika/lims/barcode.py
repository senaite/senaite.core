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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

import plone.protect
from bika.lims import api
from bika.lims import workflow as wf
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IAnalysisRequest
from Products.CMFCore.utils import getToolByName
from senaite.core.catalog import SAMPLE_CATALOG


class barcode_entry(BrowserView):
    """Decide the best redirect URL for any barcode scanned into the browser.
    """
    def __call__(self):
        try:
            plone.protect.CheckAuthenticator(self.request)
        except:
            return self.return_json({
                'success': False,
                'failure': True,
                'error': 'Cannot verify authenticator token'})

        entry = self.get_entry()
        if not entry:
            return self.return_json({
                'success': False,
                'failure': True,
                'error': 'No barcode entry submitted'})

        instance = self.resolve_item(entry)
        if not instance:
            return self.return_json({
                'success': False,
                'failure': True,
                'error': 'Cannot resolve ID or Title: %s' % entry})

        # If the instance is a Sample in sample_due, try to receive
        if IAnalysisRequest.providedBy(instance):
            wf.doActionFor(instance, "receive")

        return self.return_json({
            'success': True,
            'failure': False,
            'url': self.get_redirect_url(instance)})

    def get_redirect_url(self, instance):
        """Returns the url to be redirected to
        """
        if IAnalysisRequest.providedBy(instance):
            batch = instance.getBatch()
            if batch:
                return "{}/batchbook".format(api.get_url(batch))

        return api.get_url(instance)

    def get_entry(self):
        entry = self.request.get('entry', '')
        entry = entry.replace('*', '')
        entry = entry.strip()
        return entry

    def resolve_item(self, entry):
        ar_catalog = getToolByName(self.context, SAMPLE_CATALOG)
        catalogs = [
            self.senaite_catalog,
            self.senaite_catalog_setup,
            ar_catalog,
        ]
        for catalog in catalogs:
            brains = catalog(title=entry)
            if brains:
                return brains[0].getObject()
            brains = catalog(id=entry)
            if brains:
                return brains[0].getObject()

    def return_json(self, value):
        output = json.dumps(value)
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')
        self.request.RESPONSE.write(json.dumps(output))
        return output
