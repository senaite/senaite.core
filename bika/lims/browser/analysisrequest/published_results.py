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
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_workflow_action_buttons = False
        self.pagesize = 50
        self.form_id = 'published_results'
        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"
        self.title = self.context.translate(_("Published results"))
        self.description = ""
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
        return self.context.objectValues('ARReport')

    def folderitems(self):
        items = super(AnalysisRequestPublishedResults, self).folderitems()
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        if 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'Client' not in roles:
            return []
        for x in range(len(items)):
            if 'obj' in items[x]:
                obj = items[x]['obj']
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
                items[x]['Title'] = title
                items[x]['FileSize'] = '%sKb' % filesize
                fmt_date = self.ulocalized_time(obj.created(), long_format=1)
                items[x]['Date'] = fmt_date
                items[x]['PublishedBy'] = self.user_fullname(obj.Creator())
                recip = ''
                for recipient in obj.getRecipients():
                    email = recipient['EmailAddress']
                    val = recipient['Fullname']
                    if email:
                        val = "<a href='mailto:%s'>%s</a>" % (email, val)
                    if len(recip) == 0:
                        recip = val
                    else:
                        recip += (", " + val)

                items[x]['replace']['Recipients'] = recip
                items[x]['replace']['Title'] = anchor
        return items
