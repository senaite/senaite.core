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
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IInstruments
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from operator import itemgetter

class InstrumentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        super(InstrumentsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'Instrument',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Instrument',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Instruments"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/instrument_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Instrument'),
                      'index': 'sortable_title'},
            'Type': {'title': _('Type'),
                     'index': 'getInstrumentTypeName',
                     'toggle': True,
                     'sortable': True},
            'Brand': {'title': _('Brand'),
                      'toggle': True},
            'Model': {'title': _('Model'),
                      'index': 'getModel',
                      'toggle': True},
            'ExpiryDate': {'title': _('Expiry Date'),
                           'toggle': True},
            'WeeksToExpire': {'title': _('Weeks To Expire'),
                           'toggle': False},
            'Methods': {'title': _('Methods'),
                           'toggle': True},
            }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate',
                         'WeeksToExpire',
                         'Methods']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate',
                         'WeeksToExpire',
                         'Methods']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate',
                         'WeeksToExpire',
                         'Methods']},
            ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            itype = obj.getInstrumentType()
            items[x]['Type'] = itype.Title() if itype else ''
            ibrand = obj.getManufacturer()
            items[x]['Brand'] = ibrand.Title() if ibrand else ''
            items[x]['Model'] = obj.getModel()

            data = obj.getCertificateExpireDate()
            if data is None:
                items[x]['ExpiryDate'] = _("No date set")
            else:
                items[x]['ExpiryDate'] = data.asdatetime().strftime(self.date_format_short)

            if obj.isOutOfDate():
                items[x]['WeeksToExpire'] = _("Out of date")
            else:
                weeks, days = obj.getWeeksToExpire()
                weeks_to_expire = _("{} weeks and {} day(s)".format(str(weeks), str(days)))
                items[x]['WeeksToExpire'] = weeks_to_expire

            methods = obj.getMethods()
            urls = []
            titles = []
            for method in methods:
                url = method.absolute_url()
                title = method.Title()
                titles.append(title)
                urls.append("<a href='{0}'>{1}</a>".format(url, title))

            items[x]["Methods"] = ", ".join(titles)
            items[x]["replace"]["Methods"] = ", ".join(urls)
            items[x]["replace"]["Title"] = "<a href='{0}'>{1}</a>".format(
                obj.absolute_url(), obj.Title())

        return items

schema = ATFolderSchema.copy()
class Instruments(ATFolder):
    implements(IInstruments)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Instruments, PROJECTNAME)
