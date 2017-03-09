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
        self.show_workflow_action_buttons = False
        for k,v in kwargs.items():
            self.contentFilter[k] = v
        self.contentFilter['getSampleUID'] = context.UID()
        self.columns['Request'] = {'title': _("Request"),
                                   'sortable':False}
        self.columns['Priority'] = {'title': _("Priority"),
                                   'sortable':False}
        # Add Request and Priority columns
        pos = self.review_states[0]['columns'].index('Service') + 1
        self.review_states[0]['columns'].insert(pos, 'Request')
        pos += 1
        self.review_states[0]['columns'].insert(pos, 'Priority')

    def folderitem(self, obj, item, index):
        """
        :obj: a brain
        """
        # Call the folderitem method from the base class
        item = AnalysesView.folderitem(self, obj, item, index)
        item['replace']['Request'] = \
            "<a href='%s'>%s</a>" % (obj.getParentURL, obj.getParentTitle)
        # TODO this space is required for it to work
        item['replace']['Priority'] = ' '
        return item
