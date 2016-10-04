# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.analyses import AnalysesView
from bika.lims.permissions import *
import os
import glob
import plone
import App


class SampleAnalysesView(AnalysesView):
    """ This renders the Field and Lab analyses tables for Samples
    """
    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request)
        self.show_select_column = False
        self.allow_edit = False
        self.show_workflow_action_buttons = False
        for k,v in kwargs.items():
            self.contentFilter[k] = v
        self.columns['Request'] = {'title': _("Request"),
                                   'sortable':False}
        self.columns['Priority'] = {'title': _("Priority"),
                                   'sortable':False}
        # Add Request and Priority columns
        pos = self.review_states[0]['columns'].index('Service') + 1
        self.review_states[0]['columns'].insert(pos, 'Request')
        pos += 1
        self.review_states[0]['columns'].insert(pos, 'Priority')

    def folderitems(self):
        self.contentsMethod = self.context.getAnalyses
        items = AnalysesView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            ar = obj.aq_parent
            items[x]['replace']['Request'] = \
                "<a href='%s'>%s</a>"%(ar.absolute_url(), ar.Title())
            items[x]['replace']['Priority'] = ' ' #TODO this space is required for it to work
        return items
