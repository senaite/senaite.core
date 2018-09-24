# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.log import LogView
from Products.CMFCore.utils import getToolByName

import plone

class AnalysisRequestLog(LogView):

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')
        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = ar.getRetest() or None
            childid = childar and childar.getId() or None
            message = _('This Analysis Request has been withdrawn and is shown '
                          'for trace-ability purposes only. Retest: '
                          '${retest_child_id}.',
                          mapping={'retest_child_id': safe_unicode(childid) or ''})
            self.context.plone_utils.addPortalMessage(message, 'warning')
        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        invalidated = ar.getInvalidated()
        if invalidated:
            message = _('This Analysis Request has been '
                        'generated automatically due to '
                        'the retraction of the Analysis '
                        'Request ${retracted_request_id}.',
                        mapping={'retracted_request_id': safe_unicode(
                            invalidated.getId())})
            self.context.plone_utils.addPortalMessage(
                t(message), 'info')
        template = LogView.__call__(self)
        return template
