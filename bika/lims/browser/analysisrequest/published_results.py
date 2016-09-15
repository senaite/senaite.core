# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import getSecurityManager
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.permissions import *
from bika.lims.utils import to_utf8
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFCore.utils import getToolByName

import plone

class AnalysisRequestPublishedResults(BikaListingView):

    """ View of published results
        Prints the list of pdf files with each publication dates, the user
        responsible of that publication, the emails of the addressees (and/or)
        client contact names with the publication mode used (pdf, email, etc.)
    """
    # I took IViewView away, because transitions selected in the edit-bar
    # cause errors due to wrong context, when invoked from this view, and I
    # don't know why.
    # implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestPublishedResults, self).__init__(context, request)
        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'ARReport',
                              'sort_order': 'reverse'}
        self.context_actions = {}
        self.show_select_column = True
        self.show_workflow_action_buttons = False
        self.form_id = 'published_results'
        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"
        self.title = self.context.translate(_("Published results"))
        self.columns = {
            'Title': {'title': _('File')},
            'FileSize': {'title': _('Size')},
            'Date': {'title': _('Date')},
            'PublishedBy': {'title': _('Published By')},
            'Recipients': {'title': _('Recipients')},
        }
        self.review_states = [
            {'id': 'default',
             'title': 'All',
             'contentFilter': {},
             'columns': ['Title',
                         'FileSize',
                         'Date',
                         'PublishedBy',
                         'Recipients']},
        ]

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')
        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            childid = childar and childar.getRequestID() or None
            message = _('This Analysis Request has been withdrawn and is '
                        'shown for trace-ability purposes only. Retest: '
                        '${retest_child_id}.',
                        mapping={'retest_child_id': safe_unicode(childid) or ''})
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message), 'warning')
        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            message = _('This Analysis Request has been '
                        'generated automatically due to '
                        'the retraction of the Analysis '
                        'Request ${retracted_request_id}.',
                        mapping={'retracted_request_id': par.getRequestID()})
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message), 'info')
        template = BikaListingView.__call__(self)
        return template

    def contentsMethod(self, contentFilter):
        """
        ARReport objects associated to the current Analysis request.
        If the user is not a Manager or LabManager or Client, no items are
        displayed.
        """
        allowedroles = ['Manager', 'LabManager', 'Client', 'LabClerk']
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        allowed = [a for a in allowedroles if a in roles]
        return self.context.objectValues('ARReport') if allowed else []

    def folderitem(self, obj, item, index):
        obj_url = obj.absolute_url()
        pdf = obj.getPdf()
        filesize = 0
        title = _('Download')
        anchor = "<a href='%s/at_download/Pdf'>%s</a>" % \
                 (obj_url, _("Download"))
        try:
            filesize = pdf.get_size()
            filesize = filesize / 1024 if filesize > 0 else 0
        except:
            # POSKeyError: 'No blob file'
            # Show the record, but not the link
            title = _('Not available')
            anchor = title

        item['Title'] = title
        item['FileSize'] = '%sKb' % filesize
        fmt_date = self.ulocalized_time(obj.created(), long_format=1)
        item['Date'] = fmt_date
        item['PublishedBy'] = self.user_fullname(obj.Creator())
        recip = []
        for recipient in obj.getRecipients():
            email = recipient['EmailAddress']
            val = recipient['Fullname']
            if email:
                val = "<a href='mailto:%s'>%s</a>" % (email, val)
            recip.append(val)
        item['replace']['Recipients'] = ', '.join(recip)
        item['replace']['Title'] = anchor
        return item
