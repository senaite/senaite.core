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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

import six

from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IAnalysisRequest
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger

OFF_VALUES = ["0", "off", "no"]


class MultiResultsClassicView(BrowserView):
    """Allows to edit results of multiple samples
    """
    template = ViewPageTemplateFile("templates/multi_results.pt")

    def __init__(self, context, request):
        super(MultiResultsClassicView, self).__init__(context, request)
        self.context = context
        self.request = request

        self.classic = True
        self.transposed_url = "{}/multi_results?uids={}".format(
            self.context.absolute_url(), self.request.form.get("uids"))

    def __call__(self):
        return self.template()

    @property
    def context_state(self):
        return api.get_view(
            "plone_context_state",
            context=self.context, request=self.request)

    def contents_table(self, sample, poc):
        view_name = "table_{}_analyses".format(poc)
        view = api.get_view(view_name, context=sample, request=self.request)
        # Inject additional hidden field in the listing form for redirect
        # https://github.com/senaite/senaite.app.listing/pull/80
        view.additional_hidden_fields = [{
            "name": "redirect_url",
            "value": self.context_state.current_page_url(),
        }]
        view.update()
        view.before_render()
        return view.contents_table()

    def show_lab_analyses(self, sample):
        """Show/Hide lab analyses
        """
        analyses = sample.getAnalyses(getPointOfCapture="lab")
        if len(analyses) == 0:
            return False
        lab_analyses = self.request.get("lab_analyses")
        if lab_analyses in OFF_VALUES:
            return False
        return True

    def show_field_analyses(self, sample):
        """Show/Hide field analyses
        """
        analyses = sample.getAnalyses(getPointOfCapture="field")
        if len(analyses) == 0:
            return False
        field_analyses = self.request.get("field_analyses", True)
        if field_analyses in OFF_VALUES:
            return False
        return True

    def get_samples(self):
        """Extract the samples from the request UIDs

        This might be either a samples container or a sample context
        """

        # fetch objects from request
        objs = self.get_objects_from_request()

        samples = []

        for obj in objs:
            # when coming from the samples listing
            if IAnalysisRequest.providedBy(obj):
                samples.append(obj)

        # when coming from the WF menu inside a sample
        if IAnalysisRequest.providedBy(self.context):
            samples.append(self.context)

        return self.uniquify_items(samples)

    def uniquify_items(self, items):
        """Uniquify the items with sort order
        """
        unique = []
        for item in items:
            if item in unique:
                continue
            unique.append(item)
        return unique

    def get_objects_from_request(self):
        """Returns a list of objects coming from the "uids" request parameter
        """
        unique_uids = self.get_uids_from_request()
        return filter(None, map(self.get_object_by_uid, unique_uids))

    def get_uids_from_request(self):
        """Return a list of uids from the request
        """
        uids = self.request.form.get("uids", "")
        if isinstance(uids, six.string_types):
            uids = uids.split(",")
        unique_uids = collections.OrderedDict().fromkeys(uids).keys()
        return filter(api.is_uid, unique_uids)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj
