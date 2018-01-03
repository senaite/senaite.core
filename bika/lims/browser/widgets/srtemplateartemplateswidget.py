# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName


class SRTemplateARTemplatesView(BikaListingView):
    """ BIKA listing to display ARTemplates for an SRTemplate.
    """

    def __init__(self, context, request, fieldvalue, allow_edit):
        super(SRTemplateARTemplatesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'ARTemplate',
            'sort_on': 'title',
            'inactive_state': 'active',
        }
        self.context_actions = {}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.show_categories = True
        self.expand_all_categories = True
        self.pagesize = 999999
        self.allow_edit = allow_edit
        self.clientUID = None
        self.form_id = "artemplates"
        self.columns = {
            'Title': {
                'title': _('Service'),
                'index': 'title',
                'replace_url': 'absolute_url',
                'sortable': False,
            },
        }
        self.review_states = [{
            'id':'default',
            'title': _('All'),
            'contentFilter':{},
            'columns': ['Title'],
            'transitions': [{'id':'empty'}],
        }]
        self.fieldvalue = fieldvalue
        self.selected = [o.UID() for o in fieldvalue]

    def isItemAllowed(self, obj):
        if self.clientUID is None:
            self.clientUID = self.context.aq_parent.aq_parent.UID()
        # Only display client's and lab's arts
        if obj.aq_parent.aq_inner.meta_type == 'Client':
            obj_client = obj.getClientUID()
            if obj_client != self.clientUID:
                return False
        return True

    def folderitem(self, obj, item, index):
        item['selected'] = item['uid'] in self.selected
        return item


class SRTemplateARTemplatesWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/srtemplateartemplateswidget",
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None,
        emptyReturnsMarker = False):
        bsc = getToolByName(instance, 'bika_setup_catalog')
        value = []
        service_uids = form.get('uids', None)
        return service_uids, {}

    security.declarePublic('ARTemplates')
    def ARTemplates(self, field, allow_edit = False):
        fieldvalue = getattr(field, field.accessor)()
        view = SRTemplateARTemplatesView(
            self,
            self.REQUEST,
            fieldvalue = fieldvalue,
            allow_edit = allow_edit
        )
        return view.contents_table(table_only = True)


registerWidget(
    SRTemplateARTemplatesWidget,
    title = 'SR Template AR Templates Selector',
    description = ('SR Template AR Templates Selector'),
)
