# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from bika.lims.browser.analysisrequest.add2 import AnalysisRequestAddView
# from bika.lims.browser.analysisrequest.add2 import ajaxAnalysisRequestAddView

SKIP_FIELD_ON_COPY = []


class AnalysisRequestEditView(AnalysisRequestAddView):
    """AR edit view
    """
    SKIP_FIELD_ON_COPY = []

    def update(self):
        """Called before the template is rendered
        """
        super(AnalysisRequestEditView, self).update()
        self.came_from = "edit"
