# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.content.labcontact import LabContact
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims.interfaces import ILabContacts
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class LabContactsView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        super(LabContactsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'LabContact',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=LabContact',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Lab Contacts"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/lab_contact_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Fullname': {'title': _('Name'),
                         'index': 'getFullname'},
            'Department': {'title': _('Department'),
                           'toggle': True},
            'BusinessPhone': {'title': _('Phone'),
                              'toggle': True},
            'Fax': {'title': _('Fax'),
                    'toggle': True},
            'MobilePhone': {'title': _('Mobile Phone'),
                            'toggle': True},
            'EmailAddress': {'title': _('Email Address'),
                             'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Fullname',
                         'Department',
                         'BusinessPhone',
                         'Fax',
                         'MobilePhone',
                         'EmailAddress']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Fullname',
                         'Department',
                         'BusinessPhone',
                         'Fax',
                         'MobilePhone',
                         'EmailAddress']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Fullname',
                         'Department',
                         'BusinessPhone',
                         'Fax',
                         'MobilePhone',
                         'EmailAddress']},
        ]

    def folderitem(self, obj, item, index):
        item['Fullname'] = obj.getFullname()
        deps_txt = ""
        deps_url = ""
        # Making the text for the departments column
        for dep in obj.getDepartments():
            if len(deps_txt) == 0:
                deps_txt += dep.Title()
                deps_url += \
                    "<a href='%s'>%s</a>" %\
                    (dep.absolute_url(), dep.Title())
            else:
                deps_txt += ', ' + dep.Title()
                deps_url += \
                    ", <a href='%s'>%s</a>" %\
                    (dep.absolute_url(), dep.Title())
        item['Department'] = deps_txt
        item['BusinessPhone'] = obj.getBusinessPhone()
        item['Fax'] = obj.getBusinessFax()
        item['MobilePhone'] = obj.getMobilePhone()
        item['EmailAddress'] = obj.getEmailAddress()
        item['replace']['Fullname'] = "<a href='%s'>%s</a>" % \
            (item['url'], item['Fullname'])
        item['replace']['Department'] = deps_url
        return item

schema = ATFolderSchema.copy()
class LabContacts(ATFolder):
    implements(ILabContacts)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabContacts, PROJECTNAME)
