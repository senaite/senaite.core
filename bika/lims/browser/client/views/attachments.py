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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


class ClientAttachmentsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAttachmentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Attachment',
                              'sort_order': 'reverse'}
        self.context_actions = {}

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "attachments"

        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/attachment_big.png"
        self.title = self.context.translate(_("Attachments"))
        self.description = ""

        self.columns = {
            'Title': {'title': _('Request ID')},
            'AttachmentFile': {'title': _('File')},
            'AttachmentType': {'title': _('Attachment Type')},
            'ContentType': {'title': _('Content Type')},
            'FileSize': {'title': _('Size')},
            'DateLoaded': {'title': _('Date Loaded')},
        }
        self.review_states = [
            {'id': 'default',
             'title': 'All',
             'contentFilter': {},
             'columns': ['Title',
                         'AttachmentFile',
                         'AttachmentType',
                         'ContentType',
                         'FileSize',
                         'DateLoaded']},
        ]

    def lookupMime(self, name):
        mimetool = getToolByName(self, 'mimetypes_registry')
        mimetypes = mimetool.lookup(name)
        if len(mimetypes):
            return mimetypes[0].name()
        else:
            return name

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        obj_url = api.get_url(obj)
        file = obj.getAttachmentFile()
        icon = file.icon
        item['AttachmentFile'] = file.filename()
        item['AttachmentType'] = obj.getAttachmentType().Title()
        item['AttachmentType'] = obj.getAttachmentType().Title()
        item['ContentType'] = self.lookupMime(file.getContentType())
        item['FileSize'] = '%sKb' % (file.get_size() / 1024)
        item['DateLoaded'] = obj.getDateLoaded()

        item['replace']['Title'] = \
            "<a href='%s'>%s</a>" % (obj_url, item['Title'])

        item['replace']['AttachmentFile'] = \
            "<a href='%s/at_download/AttachmentFile'>%s</a>" % \
            (obj_url, item['AttachmentFile'])
        return item
