# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.api import get_tool
from bika.lims.browser import BrowserView
from bika.lims.browser.header_table import HeaderTableView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.permissions import *
from bika.lims.workflow import doActionFor
from . import SampleAnalysesView
from . import SamplePartitionsView


class SampleEdit(BrowserView):
    """
    Edit view
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/sample.pt")
    header_table = ViewPageTemplateFile("../templates/header_table.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/sample_big.png"
        self.allow_edit = True
        self.context_actions = {}

    def now(self):
        return DateTime()

    def getDefaultSpec(self):
        """ Returns 'lab' or 'client' to set the initial value of the
            specification radios
        """
        mt = getToolByName(self.context, 'portal_membership')
        pg = getToolByName(self.context, 'portal_groups')
        member = mt.getAuthenticatedMember()
        member_groups = [pg.getGroupById(group.id).getGroupName() \
                         for group in pg.getGroupsByUserId(member.id)]
        default_spec = ('Clients' in member_groups) and 'client' or 'lab'
        return default_spec

    def __call__(self):
        if 'transition' in self.request.form:
            doActionFor(self.context, self.request.form['transition'])
        # Add an Analysis request creation button
        mtool = get_tool('portal_membership', context=self.context)
        if mtool.checkPermission(AddAnalysisRequest, self.context):
            self.context_actions[_('Add Analysis Request')] = \
                {'url': "ar_add?ar_count=1",
                 'icon': '++resource++bika.lims.images/add.png'}
        ## render header table
        self.header_table = HeaderTableView(self.context, self.request)

        ## Create Sample Partitions table
        parts_table = None
        if not self.allow_edit:
            p = SamplePartitionsView(self.context, self.request)
            p.allow_edit = self.allow_edit
            p.show_select_column = self.allow_edit
            p.show_workflow_action_buttons = self.allow_edit
            p.show_column_toggles = False
            p.show_select_all_checkbox = False
            p.review_states[0]['transitions'] = [{'id': 'empty'},] # none
            parts_table = p.contents_table()
        self.parts = parts_table

        ## Create Field and Lab Analyses tables
        self.tables = {}
        if not self.allow_edit:
            for poc in POINTS_OF_CAPTURE:
                t = SampleAnalysesView(
                    self.context,
                    self.request,
                    getPointOfCapture=poc,
                    sort_on='getId')
                t.form_id = "sample_%s_analyses" % poc
                if poc == 'field':
                    t.review_states[0]['columns'].remove('DueDate')
                t.show_column_toggles = False
                t.review_states[0]['transitions'] = [{'id':'submit'},
                                                     {'id':'retract'},
                                                     {'id':'verify'}]
                self.tables[POINTS_OF_CAPTURE.getValue(poc)] = t.contents_table()

        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i
