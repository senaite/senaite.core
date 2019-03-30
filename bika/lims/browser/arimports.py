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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import csv
from DateTime.DateTime import DateTime
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView, ulocalized_time
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IClient
from bika.lims.utils import tmpID
from bika.lims.workflow import getTransitionDate
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.layout.globals.interfaces import IViewView
from plone.protect import CheckAuthenticator
from Products.Archetypes.utils import addStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
from zope.interface import implements

import os


class ARImportsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ARImportsView, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', 1)
        alsoProvides(request, IContentListing)

        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'ARImport',
            'is_active': True,
            'sort_on': 'sortable_title',
        }
        self.context_actions = {}
        if IClient.providedBy(self.context):
            self.context_actions = {
                _('AR Import'): {
                    'url': 'arimport_add',
                    'icon': '++resource++bika.lims.images/add.png'}}

        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50
        self.form_id = "arimports"

        self.icon = \
            self.portal_url + "/++resource++bika.lims.images/arimport_big.png"
        self.title = self.context.translate(_("Sample Imports"))
        self.description = ""

        self.columns = {
            'Title': {'title': _('Title')},
            'Client': {'title': _('Client')},
            'Filename': {'title': _('Filename')},
            'Creator': {'title': _('Date Created')},
            'DateCreated': {'title': _('Date Created')},
            'DateValidated': {'title': _('Date Validated')},
            'DateImported': {'title': _('Date Imported')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Pending'),
             'contentFilter': {'review_state': ['invalid', 'valid']},
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'Client',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
            {'id': 'imported',
             'title': _('Imported'),
             'contentFilter': {'review_state': 'imported'},
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'Client',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
        ]

    def folderitems(self, **kwargs):
        items = super(ARImportsView, self).folderitems()
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.title_or_id()
            if items[x]['review_state'] == 'invalid':
                items[x]['replace']['Title'] = "<a href='%s/edit'>%s</a>" % (
                    obj.absolute_url(), items[x]['Title'])
            else:
                items[x]['replace']['Title'] = "<a href='%s/view'>%s</a>" % (
                    obj.absolute_url(), items[x]['Title'])
            items[x]['Creator'] = obj.Creator()
            items[x]['Filename'] = obj.getFilename()
            parent = obj.aq_parent
            items[x]['Client'] = parent if IClient.providedBy(parent) else ''
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % (
                parent.absolute_url(), parent.Title())
            items[x]['DateCreated'] = ulocalized_time(
                obj.created(), long_format=True, time_only=False, context=obj)
            date = getTransitionDate(obj, 'validate')
            items[x]['DateValidated'] = date if date else ''
            date = getTransitionDate(obj, 'import')
            items[x]['DateImported'] = date if date else ''

        return items


class ClientARImportsView(ARImportsView):
    def __init__(self, context, request):
        super(ClientARImportsView, self).__init__(context, request)
        self.contentFilter['path'] = {
            'query': '/'.join(context.getPhysicalPath())
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Pending'),
             'contentFilter': {'review_state': ['invalid', 'valid']},
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
            {'id': 'imported',
             'title': _('Imported'),
             'contentFilter': {'review_state': 'imported'},
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
        ]


class ClientARImportAddView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile('templates/arimport_add.pt')

    def __init__(self, context, request):
        super(ClientARImportAddView, self).__init__(context, request)
        alsoProvides(request, IContentListing)

    def __call__(self):
        request = self.request
        form = request.form
        CheckAuthenticator(form)
        if form.get('submitted'):
            # Validate form submission
            csvfile = form.get('csvfile')
            data = csvfile.read()
            lines = data.splitlines()
            filename = csvfile.filename
            if not csvfile:
                addStatusMessage(request, _("No file selected"))
                return self.template()
            if len(lines) < 3:
                addStatusMessage(request, _("Too few lines in CSV file"))
                return self.template()
            # Create the arimport object
            arimport = _createObjectByType("ARImport", self.context, tmpID())
            arimport.processForm()
            arimport.setTitle(self.mkTitle(filename))
            arimport.schema['OriginalFile'].set(arimport, data)
            # Save all fields from the file into the arimport schema
            arimport.save_header_data()
            arimport.save_sample_data()
            # immediate batch creation if required
            arimport.create_or_reference_batch()
            # Attempt first validation
            try:
                workflow = getToolByName(self.context, 'portal_workflow')
                workflow.doActionFor(arimport, 'validate')
            except WorkflowException:
                self.request.response.redirect(arimport.absolute_url() +
                                               "/edit")
        else:
            return self.template()

    def mkTitle(self, filename):
        pc = getToolByName(self.context, 'portal_catalog')
        nr = 1
        while True:
            newname = '%s-%s' % (os.path.splitext(filename)[0], nr)
            existing = pc(portal_type='ARImport', title=newname)
            if not existing:
                return newname
            nr += 1
