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
from Products.CMFCore.permissions import ModifyPortalContent

import plone

class AttachmentsView(BikaListingView):

    def __init__(self, context, request):
        super(AttachmentsView, self).__init__(context, request)
        self.contentFilter = {}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.pagesize = 50
        self.form_id = 'attachments'
        self.icon = self.portal_url + "/++resource++bika.lims.images/attachment_big.png"
        self.title = self.context.translate(_("Attachments"))
        self.description = ""
        self.columns = {
            'Title': {'title': _('File')},
            'FileSize': {'title': _('Size')},
            'Date': {'title': _('Date')},
            'getAttachmentKeys': {'title': _('Attachment Keys')},
            'AttachmentType': {'title': _('Attachment Type')},
        }
        self.review_states = [
            {'id': 'default',
             'title': 'All',
             'contentFilter': {},
             'columns': ['Title',
                         'FileSize',
                         'Date',
                         'getAttachmentKeys',
                         'AttachmentType']},
        ]

    def __call__(self):
        if self.portal_membership.checkPermission(ModifyPortalContent, self.portal.batches):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=Attachment',
                 'icon': self.portal.absolute_url() + '/++resource++bika.lims.images/add.png'}
        template = BikaListingView.__call__(self)
        return template

    def contentsMethod(self, contentFilter):
        return self.context.objectValues('Attachment')

    def folderitems(self):
        items = super(AttachmentsView, self).folderitems()
        for x in range(len(items)):
            if 'obj' in items[x]:
                obj = items[x]['obj']
                obj_url = obj.absolute_url()
                file = obj.getAttachmentFile()
                filesize = 0
                title = file.filename
                anchor = "<a href='%s/AttachmentFile'>%s</a>" % \
                         (obj_url, title)
                AttachmentType = obj.getAttachmentType().Title() if obj.getAttachmentType() else ''
                try:
                    filesize = file.get_size()
                    filesize = filesize / 1024 if filesize > 0 else 0
                except:
                    # POSKeyError: 'No blob file'
                    # Show the record, but not the link
                    title = _('Not available')
                    anchor = title 
                items[x]['Title'] = title
                items[x]['replace']['Title'] = anchor 
                items[x]['FileSize'] = '%sKb' % filesize
                fmt_date = self.ulocalized_time(obj.created(), long_format=1)
                items[x]['Date'] = fmt_date
                items[x]['AttachmentType'] = AttachmentType
                
        return items
