# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisServices
from bika.lims.utils import tmpID
from bika.lims.validators import ServiceKeywordValidator
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from transaction import savepoint
from zope.interface.declarations import implements


class AnalysisServiceCopy(BrowserView):
    template = ViewPageTemplateFile('templates/analysisservice_copy.pt')
    # should never be copied between services
    skip_fieldnames = [
        'UID',
        'id',
        'title',
        'ShortTitle',
        'Keyword',
    ]
    created = []

    def create_service(self, src_uid, dst_title, dst_keyword):
        folder = self.context.bika_setup.bika_analysisservices
        dst_service = _createObjectByType("AnalysisService", folder, tmpID())
        # manually set keyword and title
        dst_service.setKeyword(dst_keyword)
        dst_service.setTitle(dst_title)
        dst_service.unmarkCreationFlag()
        _id = renameAfterCreation(dst_service)
        dst_service = folder[_id]
        return dst_service

    def validate_service(self, dst_service):
        # validate entries
        validator = ServiceKeywordValidator()
        # baseschema uses uniquefieldvalidator on title, this is sufficient.
        res = validator(dst_service.getKeyword(), instance=dst_service)
        if res is not True:
            self.savepoint.rollback()
            self.created = []
            self.context.plone_utils.addPortalMessage(safe_unicode(res), 'info')
            return False
        return True

    def copy_service(self, src_uid, dst_title, dst_keyword):
        uc = getToolByName(self.context, 'uid_catalog')
        src_service = uc(UID=src_uid)[0].getObject()
        dst_service = self.create_service(src_uid, dst_title, dst_keyword)
        if self.validate_service(dst_service):
            # copy field values
            for field in src_service.Schema().fields():
                fieldname = field.getName()
                if field.getType() == "Products.Archetypes.Field.ComputedField" \
                        or fieldname in self.skip_fieldnames:
                    continue
                value = field.get(src_service)
                if value:
                    # https://github.com/bikalabs/bika.lims/issues/2015
                    if fieldname in ["UpperDetectionLimit", "LowerDetectionLimit"]:
                        value = str(value)
                    mutator_name = dst_service.getField(fieldname).mutator
                    mutator = getattr(dst_service, mutator_name)
                    mutator(value)
            dst_service.reindexObject()
            return dst_title
        else:
            return False

    def __call__(self):
        uc = getToolByName(self.context, 'uid_catalog')
        if 'copy_form_submitted' not in self.request:
            uids = self.request.form.get('uids', [])
            self.services = []
            for uid in uids:
                proxies = uc(UID=uid)
                if proxies:
                    self.services.append(proxies[0].getObject())
            return self.template()
        else:
            self.savepoint = savepoint()
            sources = self.request.form.get('uids', [])
            titles = self.request.form.get('dst_title', [])
            keywords = self.request.form.get('dst_keyword', [])
            self.created = []
            for i, s in enumerate(sources):
                if not titles[i]:
                    message = _('Validation failed: title is required')
                    message = safe_unicode(message)
                    self.context.plone_utils.addPortalMessage(message, 'info')
                    self.savepoint.rollback()
                    self.created = []
                    break
                if not keywords[i]:
                    message = _('Validation failed: keyword is required')
                    message = safe_unicode(message)
                    self.context.plone_utils.addPortalMessage(message, 'info')
                    self.savepoint.rollback()
                    self.created = []
                    break
                title = self.copy_service(s, titles[i], keywords[i])
                if title:
                    self.created.append(title)
            if len(self.created) > 1:
                message = _('${items} were successfully created.',
                            mapping={
                                'items': safe_unicode(', '.join(self.created))})
            elif len(self.created) == 1:
                message = _('${item} was successfully created.',
                            mapping={
                                'item': safe_unicode(self.created[0])})
            else:
                message = _('No new items were created.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(self.context.absolute_url())


class AnalysisServicesView(BikaListingView):
    """Listing table view for Analysis Services
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AnalysisServicesView, self).__init__(context, request)
        self.an_cats = None
        self.an_cats_order = None
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'AnalysisService'}
        self.context_actions = {
            _('Add'):
                {'url': 'createObject?type_name=AnalysisService',
                 'icon': '++resource++bika.lims.images/add.png'}}
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/analysisservice_big.png"
        self.title = self.context.translate(_("Analysis Services"))
        self.form_id = "list_analysisservices"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_select_all_checkbox = False
        self.pagesize = 25
        self.sort_on = 'Title'
        self.categories = []
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        if self.do_cats:
            self.pagesize = 999999  # hide batching controls
            self.show_categories = True
            self.expand_all_categories = False
            self.ajax_categories = True
            self.category_index = 'getCategoryTitle'

        self.columns = {
            'Title': {
                'title': _('Service'),
                'index': 'sortable_title',
                'replace_url': 'absolute_url',
                'sortable': not self.do_cats,
            },
            'Keyword': {
                'title': _('Keyword'),
                'index': 'getKeyword',
                'attr': 'getKeyword',
                'sortable': not self.do_cats,
            },
            'Category': {
                'title': _('Category'),
                'attr': 'getCategoryTitle',
                'sortable': not self.do_cats,
            },
            'Methods': {
                'title': _('Methods'),
                'sortable': not self.do_cats,
            },
            'Department': {
                'title': _('Department'),
                'toggle': False,
                'attr': 'getDepartment.Title',
                'sortable': not self.do_cats,
            },
            'Unit': {
                'title': _('Unit'),
                'attr': 'getUnit',
                'sortable': False,
            },
            'Price': {
                'title': _('Price'),
                'sortable': not self.do_cats,
            },
            'MaxTimeAllowed': {
                'title': _('Max Time'),
                'toggle': False,
                'sortable': not self.do_cats,
            },
            'DuplicateVariation': {
                'title': _('Dup Var'),
                'toggle': False,
                'sortable': False,
             },
            'Calculation': {
                'title': _('Calculation'),
                'sortable': False,
            },
            'CommercialID': {
                'title': _('Commercial ID'),
                'attr': 'getCommercialID',
                'toggle': False,
                'sortable': not self.do_cats,
            },
            'ProtocolID': {
                'title': _('Protocol ID'),
                'attr': 'getProtocolID',
                'toggle': False,
                'sortable': not self.do_cats,
            },
            'SortKey': {
                'title': _('Sort Key'),
                'attr': 'getSortKey',
                'sortable': False,
            },
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'columns': ['Title',
                         'Category',
                         'Keyword',
                         'Methods',
                         'Department',
                         'CommercialID',
                         'ProtocolID',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         'SortKey',
                         ],
             'custom_transitions': [{'id': 'duplicate',
                                 'title': _('Duplicate'),
                                 'url': 'copy'}, ]
             },
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'columns': ['Title',
                         'Category',
                         'Keyword',
                         'Methods',
                         'Department',
                         'CommercialID',
                         'ProtocolID',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         'SortKey',
                         ],
             'custom_transitions': [{'id': 'duplicate',
                                 'title': _('Duplicate'),
                                 'url': 'copy'}, ]
             },
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Keyword',
                         'Category',
                         'Methods',
                         'Department',
                         'CommercialID',
                         'ProtocolID',
                         'Unit',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         'Calculation',
                         'SortKey',
                         ],
             'custom_transitions': [{'id': 'duplicate',
                                 'title': _('Duplicate'),
                                 'url': 'copy'}, ]
             },
        ]

        if not self.context.bika_setup.getShowPrices():
            for i in range(len(self.review_states)):
                self.review_states[i]['columns'].remove('Price')

    def isItemAllowed(self, obj):
        """
        It checks if the item can be added to the list depending on the
        department filter. If the analysis service is not assigned to a
        department, show it.
        If department filtering is disabled in bika_setup, will return True.
        """
        if not self.context.bika_setup.getAllowDepartmentFiltering():
            return True
        # Gettin the department from analysis service
        obj_dep = obj.getDepartment()
        result = True
        if obj_dep:
            # Getting the cookie value
            cookie_dep_uid = self.request.get('filter_by_department_info', 'no')
            # Comparing departments' UIDs
            result = True if obj_dep.UID() in\
                cookie_dep_uid.split(',') else False
            return result
        return result

    def folderitem(self, obj, item, index):
        cat = obj.getCategoryTitle()
        cat_order = self.an_cats_order.get(cat)
        if self.do_cats:
            # category is for bika_listing to groups entries
            item['category'] = cat
            if (cat, cat_order) not in self.categories:
                self.categories.append((cat, cat_order))

        calculation = obj.getCalculation()
        item['Calculation'] = calculation.Title() if calculation else ''
        if calculation:
            item['replace']['Calculation'] = "<a href='%s'>%s</a>" % (
                calculation.absolute_url() + "/edit", calculation.Title())

        item['Price'] = "%s.%02d" % obj.Price

        # Fill Methods column
        methods = obj.getMethods()
        m_dict = {method.Title(): method.absolute_url() for method in methods}
        m_titles = sorted(m_dict.keys())
        m_anchors = []
        for title in m_titles:
            url = m_dict[title]
            anchor = '<a href="{}">{}</a>'.format(url, title)
            m_anchors.append(anchor)
        item['Methods'] = ', '.join(m_titles)
        item['replace']['Methods'] = ', '.join(m_anchors)

        maxtime = obj.MaxTimeAllowed
        maxtime_string = ""
        for field in ('days', 'hours', 'minutes'):
            if field in maxtime:
                try:
                    val = int(maxtime[field])
                    if val > 0:
                        maxtime_string += "%s%s " % (val, _(field[0]))
                except:
                    pass
        item['MaxTimeAllowed'] = maxtime_string

        if obj.DuplicateVariation:
            item['DuplicateVariation'] = "%s.%02d" % obj.DuplicateVariation
        else:
            item['DuplicateVariation'] = ""

        after_icons = ''
        ipath = "++resource++bika.lims.images"
        if obj.getAccredited():
            after_icons += "<img src='%s/accredited.png' title='%s'>" % (
                ipath, _("Accredited"))
        if obj.getReportDryMatter():
            after_icons += "<img src='%s/dry.png' title='%s'>" % (
                ipath, _("Can be reported as dry matter"))
        if obj.getAttachmentOption() == 'r':
            after_icons += "<img src='%s/attach_reqd.png' title='%s'>" % (
                ipath, _("Attachment required"))
        if obj.getAttachmentOption() == 'n':
            after_icons += "<img src='%s/attach_no.png' title='%s'>" % (
                ipath, _('Attachment not permitted'))
        if after_icons:
            item['after']['Title'] = after_icons
        return item

    def folderitems(self, full_objects=False, classic=True):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.an_cats = bsc(
            portal_type="AnalysisCategory",
            sort_on="sortable_title")
        self.an_cats_order = dict([
            (b.Title, "{:04}".format(a))
            for a, b in enumerate(self.an_cats)])
        items = super(AnalysisServicesView, self).folderitems()
        if self.do_cats:
            self.categories = map(lambda x: x[0],
                                  sorted(self.categories, key=lambda x: x[1]))
        else:
            self.categories.sort()
        return items


schema = ATFolderSchema.copy()
finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)


class AnalysisServices(ATFolder):
    implements(IAnalysisServices)
    displayContentsTab = False
    schema = schema


atapi.registerType(AnalysisServices, PROJECTNAME)
