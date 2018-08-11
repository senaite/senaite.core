# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.controlpanel.bika_analysisspecs import BaseAnalysisSpecsView
from bika.lims.permissions import AddAnalysisSpec
from bika.lims.utils import tmpID


class ClientAnalysisSpecsView(BaseAnalysisSpecsView):

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.contentFilter["getClientUID"] = api.get_uid(context)

    def before_render(self):
        """Before template render hook
        """
        mtool = api.get_tool("portal_membership")
        if mtool.checkPermission(AddAnalysisSpec, self.context):
            del self.context_actions[_("Add")]


class SetSpecsToLabDefaults(BrowserView):
    """ Remove all client specs, and add copies of all lab specs
    """

    def __call__(self):
        form = self.request.form
        bsc = getToolByName(self.context, 'bika_setup_catalog')

        # find and remove existing specs
        cs = bsc(portal_type='AnalysisSpec',
                 getClientUID=self.context.UID())
        if cs:
            self.context.manage_delObjects([s.id for s in cs])

        # find and duplicate lab specs
        ls = bsc(portal_type='AnalysisSpec',
                 getClientUID=self.context.bika_setup.bika_analysisspecs.UID())
        ls = [s.getObject() for s in ls]
        for labspec in ls:
            clientspec = _createObjectByType(
                "AnalysisSpec", self.context, tmpID())
            clientspec.processForm()
            clientspec.edit(
                SampleType=labspec.getSampleType(),
                ResultsRange=labspec.getResultsRange(),
            )
        translate = self.context.translate
        message = _("Analysis specifications reset to lab defaults.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.request.RESPONSE.redirect(self.context.absolute_url() +
                                       "/analysisspecs")
        return
