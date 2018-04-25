# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.
import collections
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView

class AnalysisSpecificationView(BikaListingView):
    """ bika listing to display Analysis Services (AS) table for an
        Analysis Specification.
    """

    def __init__(self, context, request, fieldvalue=[], allow_edit=True):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.contentFilter = {'inactive_state': 'active',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 999999
        self.allow_edit = allow_edit
        self.show_categories = True
        # self.expand_all_categories = False
        self.ajax_categories = True
        self.ajax_categories_url = self.context.absolute_url() + "/analysis_spec_widget_view"
        self.category_index = 'getCategoryTitle'

        self.specsresults = {}
        for specresults in fieldvalue:
            self.specsresults[specresults['keyword']] = specresults

        self.columns = collections.OrderedDict((
            ('service', {
                'title': _('Service'),
                'index': 'sortable_title',
                'sortable': False}),
            ('warn_min', {
                'title': _('Min warn'),
                'sortable': False}),
            ('min', {
                'title': _('Min'),
                'sortable': False}),
            ('max', {
                'title': _('Max'),
                'sortable': False}),
            ('warn_max', {
                'title': _('Max warn'),
                'sortable': False}),
            ('hidemin', {
                'title': _('< Min'),
                'sortable': False}),
            ('hidemax', {
                'title': _('> Max'),
                'sortable': False}),
            ('rangecomment', {
                'title': _('Range comment'),
                'sortable': False,
                'toggle': False}),
        ))

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns': self.columns.keys(),
             },
        ]


    def folderitems(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.categories = []

        # Check edition permissions
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = 'LabManager' in roles or 'Manager' in roles

        # Analysis Services retrieval and custom item creation
        items = []
        workflow = getToolByName(self.context, 'portal_workflow')
        self.contentFilter['portal_type'] = 'AnalysisService'
        services = bsc(self.contentFilter)
        for service in services:
            service = service.getObject()
            cat = service.getCategoryTitle()
            if cat not in self.categories:
                self.categories.append(cat)
            if service.getKeyword() in self.specsresults:
                specresults = self.specsresults[service.getKeyword()]
            else:
                specresults = {'keyword': service.getKeyword(),
                        'min': '',
                        'max': '',
                        'warn_min': '',
                        'warn_max': '',
                        'hidemin': '',
                        'hidemax': '',
                        'rangecomment': ''}

            after_icons = ' <span class="discreet">(%s)</span>&nbsp;&nbsp;' % service.getKeyword()
            if service.getAccredited():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/accredited.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Accredited"))
            if service.getAttachmentOption() == 'r':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_reqd.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _("Attachment required"))
            if service.getAttachmentOption() == 'n':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_no.png'\
                title='%s'>"%(self.context.absolute_url(),
                              _('Attachment not permitted'))

            # TRICK for AS keyword retrieval on form POST
            after_icons += '<input type="hidden" name="keyword.%s:records"\
            value="%s"></input>' % (service.UID(), service.getKeyword())

            state = workflow.getInfoFor(service, 'inactive_state', '')
            unit = service.getUnit()
            unitspan = unit and \
                "<span class='discreet'>%s</span>" % service.getUnit() or ''
            percspan = "<span class='discreet'>%</span>"

            item = {
                'obj': service,
                'id': service.getId(),
                'uid': service.UID(),
                'keyword': service.getKeyword(),
                'title': service.Title(),
                'category': cat,
                'selected': service.getKeyword() in self.specsresults.keys(),
                'type_class': 'contenttype-ReferenceResult',
                'url': service.absolute_url(),
                'relative_url': service.absolute_url(),
                'view_url': service.absolute_url(),
                'service': service.Title(),
                'min': specresults.get('min', ''),
                'max': specresults.get('max', ''),
                'warn_min': specresults.get('warn_min', ''),
                'warn_max': specresults.get('warn_max', ''),
                'hidemin': specresults.get('hidemin',''),
                'hidemax': specresults.get('hidemax',''),
                'rangecomment': specresults.get('rangecomment', ''),
                'replace': {},
                'before': {},
                'after': {'service':after_icons,
                          'min':unitspan,
                          'max':unitspan,
                          'warn_min':unitspan,
                          'warn_max':unitspan},
                'choices':{},
                'class': "state-%s" % (state),
                'state_class': "state-%s" % (state),
                'allow_edit': ['min', 'max', 'warn_min', 'warn_max', 'hidemin',
                               'hidemax', 'rangecomment'],
            }
            items.append(item)

        self.categories.sort()
        for i in range(len(items)):
            items[i]['table_row_class'] = "even"

        return items

class AnalysisSpecificationWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/analysisspecificationwidget",
    })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker = None, emptyReturnsMarker = False):
        """ Return a list of dictionaries fit for AnalysisSpecsResultsField
            consumption. If neither hidemin nor hidemax are specified, only
            services which have float()able entries in result,min and max field
            will be included. If hidemin and/or hidemax specified, results
            might contain empty min and/or max fields.
        """
        values = []
        if 'service' not in form:
            return values, {}

        for uid, keyword in form['keyword'][0].items():
            s_min = self._get_spec_value(form, uid, 'min')
            s_max = self._get_spec_value(form, uid, 'max')
            if not s_min and not s_max:
                # If user has not set value neither for min nor max, omit this
                # record. Otherwise, since 'min' and 'max' are defined as
                # mandatory subfields, the following message will appear after
                # submission: "Specifications is required, please correct."
                continue

            values.append({
                'keyword': keyword,
                'uid': uid,
                'min': s_min,
                'max': s_max,
                'warn_min': self._get_spec_value(form, uid, 'warn_min'),
                'warn_max': self._get_spec_value(form, uid, 'warn_max'),
                'hidemin': self._get_spec_value(form, uid, 'hidemin'),
                'hidemax': self._get_spec_value(form, uid, 'hidemax'),
                'rangecomment': self._get_spec_value(form, uid, 'rangecomment',
                                                     check_floatable=False)})
        return values, {}

    def _get_spec_value(self, form, uid, key, check_floatable=True, default=''):
        """Returns the value assigned to the passed in key for the analysis
        service uid from the passed in form.

        If check_floatable is true, will return the passed in default if the
        obtained value is not floatable
        :param form: form being submitted
        :param uid: uid of the Analysis Service the specification relates
        :param key: id of the specs param to get (e.g. 'min')
        :param check_floatable: check if the value is floatable
        :param default: fallback value that will be returned by default
        :type default: str, None
        """
        if not form or not uid:
            return default
        values = form.get(key, None)
        if not values or len(values) == 0:
            return default
        value = values[0].get(uid, default)
        if not check_floatable:
            return value
        return api.is_floatable(value) and value or default

    security.declarePublic('AnalysisSpecificationResults')
    def AnalysisSpecificationResults(self, field, allow_edit = False):
        """ Prints a bika listing with categorized services.
            field contains the archetypes field with a list of services in it
        """
        fieldvalue = getattr(field, field.accessor)()
        view = AnalysisSpecificationView(self,
                                            self.REQUEST,
                                            fieldvalue = fieldvalue,
                                            allow_edit = allow_edit)
        return view.contents_table(table_only = True)

registerWidget(AnalysisSpecificationWidget,
               title = 'Analysis Specification Results',
               description = ('Analysis Specification Results'))
