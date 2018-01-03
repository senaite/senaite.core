# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import ISampleTypes
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from Products.CMFCore.utils import getToolByName
import json
import plone

class SampleTypesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(SampleTypesView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'SampleType',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=SampleType',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Sample Types"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/sampletype_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Sample Type'),
                      'index': 'sortable_title',},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'getHazardous': {'title': _('Hazardous'),
                             'toggle': True},
            'getPrefix': {'title': _('Prefix'),
                          'toggle': True},
            'getMinimumVolume': {'title': _('Minimum Volume'),
                                 'toggle': True},
            'RetentionPeriod': {'title': _('Retention Period'),
                             'toggle': True},
            'SampleMatrix': {'title': _('SampleMatrix'),
                             'toggle': True},
            'ContainerType': {'title': _('Default Container'),
                             'toggle': True},
            'getSamplePoints': {'title': _('Sample Points'),
                             'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'getHazardous',
                         'RetentionPeriod',
                         'SampleMatrix',
                         'ContainerType',
                         'getSamplePoints',
                         'getPrefix',
                         'getMinimumVolume']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'getHazardous',
                         'RetentionPeriod',
                         'SampleMatrix',
                         'ContainerType',
                         'getSamplePoints',
                         'getPrefix',
                         'getMinimumVolume']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description',
                         'getHazardous',
                         'RetentionPeriod',
                         'SampleMatrix',
                         'ContainerType',
                         'getSamplePoints',
                         'getPrefix',
                         'getMinimumVolume']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

            if obj.getRetentionPeriod():
                items[x]['RetentionPeriod'] = "hours: " + str(obj.getRetentionPeriod()['hours']) + " minutes: " + str(obj.getRetentionPeriod()['minutes']) + " days: " + str(obj.getRetentionPeriod()['days'])

            else:
                items[x]['RetentionPeriod'] = ''

            if obj.getSampleMatrix():
                items[x]['SampleMatrix'] = obj.getSampleMatrix().Title()
                items[x]['replace']['SampleMatrix'] = "<a href='%s'>%s</a>" % \
                    (obj.getSampleMatrix().absolute_url(), items[x]['SampleMatrix'])
            else:
                items[x]['SampleMatrix'] = ''

            if obj.getContainerType():
                items[x]['ContainerType'] = obj.getContainerType().Title()
                items[x]['replace']['ContainerType'] = "<a href='%s'>%s</a>" %(obj.getContainerType().absolute_url(), items[x]['ContainerType'])

            else:
                items[x]['ContainerType'] = ''

            if obj.getSamplePoints():
                if len(obj.getSamplePoints()) > 1:
                    SPLine = str()
                    urlStr = str()
                    for token in obj.getSamplePoints():
                        SPLine += token.Title() + ", "
                        urlStr += "<a href='%s'>%s</a>" % (token.absolute_url(),token.Title())
                    items[x]['replace']['getSamplePoints'] = urlStr

                else:
                    items[x]['getSamplePoints'] = obj.getSamplePoints()[0].Title()
                    items[x]['replace']['getSamplePoints'] = "<a href='%s'>%s</a>" % \
                        (obj.getSamplePoints()[0].absolute_url(), items[x]['getSamplePoints'])

            else:
                items[x]['getSamplePoints'] = ''

        return items

schema = ATFolderSchema.copy()

class SampleTypes(ATFolder):
    implements(ISampleTypes)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(SampleTypes, PROJECTNAME)

class ajax_SampleTypes(BrowserView):
    """ autocomplete data source for sample types field
        return JSON data [string,string]
        if "samplepoint" is in the request, it's expected to be a title string
        The objects returned will be filtered by samplepoint's SampleTypes.
        if no items are found, all items are returned.

        If term is a one or two letters, return items that begin with them
            If there aren't any, return items that contain them
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        term = safe_unicode(self.request.get('term', '')).lower()
        items = []
        if not term:
            return json.dumps(items)
        samplepoint = safe_unicode(self.request.get('samplepoint', ''))
        # Strip "Lab: " from sample point titles
        samplepoint = samplepoint.replace("%s: " % _("Lab"), '')
        if samplepoint and len(samplepoint) > 1:
            sp = bsc(portal_type = "SamplePoint",
                     inactive_state = 'active',
                     title=samplepoint)
            if not sp:
                return json.dumps([])
            sp = sp[0].getObject()
            items = sp.getSampleTypes()
        if not items:
            items = bsc(portal_type = "SampleType",
                        inactive_state = 'active',
                        sort_on='sortable_title')
            if term and len(term) < 3:
                # Items that start with A or AA
                items = [s.getObject()
                         for s in items
                         if s.title.lower().startswith(term)]
                if not items:
                    # or, items that contain A or AA
                    items = [s.getObject()
                             for s in items
                             if s.title.lower().find(term) > -1]
            else:
                # or, items that contain term.
                items = [s.getObject()
                         for s in items
                         if s.title.lower().find(term) > -1]

        items = [callable(s.Title) and s.Title() or s.title
                 for s in items]
        return json.dumps(items)
