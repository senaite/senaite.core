# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import isActive
from zope.component import getMultiAdapter
import plone

class LateAnalysesView(BikaListingView):
    """ Late analyses (click from portlet_late_analyses More... link)
    """
    def __init__(self, context, request):
        super(LateAnalysesView, self).__init__(context, request)
        self.catalog = 'bika_analysis_catalog'
        self.contentFilter = {
            'portal_type':'Analysis',
            'getDueDate': {'query': [DateTime(),], 'range': 'max'},
            'review_state':['assigned',
                            'sample_received',
                            'to_be_verified',
                            'verified'],
            'cancellation_state': 'active',
            'sort_on': 'getDateReceived'
        }
        self.title = self.context.translate(_("Late Analyses"))
        self.description = ""
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 100
        self.show_workflow_action_buttons = False
        self.view_url = self.view_url + "/late_analyses"

        request.set('disable_border', 1)

        self.columns = {'Analysis': {'title': _('Analysis'),
                                     'index': 'sortable_title'},
                        'getRequestID': {'title': _('Request ID'),
                                         'index': 'getRequestID'},
                        'Client': {'title': _('Client')},
                        'Contact': {'title': _('Contact')},
                        'DateReceived': {'title': _('Date Received'),
                                         'index': 'getDateReceived'},
                        'DueDate': {'title': _('Due Date'),
                                    'index': 'getDueDate'},
                        'Late': {'title': _('Late')},
                        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns':['Analysis',
                        'getRequestID',
                        'Client',
                        'Contact',
                        'DateReceived',
                        'DueDate',
                        'Late'],
             },
        ]

    def folderitems(self):
        items = super(LateAnalysesView, self).folderitems()
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            ar = obj.aq_parent
            sample = ar.getSample()
            client = ar.aq_parent
            contact = ar.getContact()
            items[x]['Analysis'] = obj.Title()
            items[x]['getRequestID'] = ''
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (ar.absolute_url(), ar.Title())
            items[x]['Client'] = ''
            if hideclientlink == False:
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                     (client.absolute_url(), client.Title())
            items[x]['Contact'] = ''
            if contact:
                items[x]['replace']['Contact'] = "<a href='mailto:%s'>%s</a>" % \
                                                 (contact.getEmailAddress(),
                                                  contact.getFullname())
            items[x]['DateReceived'] = self.ulocalized_time(sample.getDateReceived())
            items[x]['DueDate'] = self.ulocalized_time(obj.getDueDate())

            late = DateTime() - obj.getDueDate()
            days = int(late / 1)
            hours = int((late % 1 ) * 24)
            mins = int((((late % 1) * 24) % 1) * 60)
            late_str = days and "%s day%s" % (days, days > 1 and 's' or '') or ""
            if days < 2:
                late_str += hours and " %s hour%s" % (hours, hours > 1 and 's' or '') or ""
            if not days and not hours:
                late_str = "%s min%s" % (mins, mins > 1 and 's' or '')

            items[x]['Late'] = late_str
        return items

    def isItemAllowed(self, obj):
        """Checks if the passed in Analysis must be displayed in the list.

        If the 'filtering by department' option is enabled in Bika Setup, this
        function checks if the Analysis Service associated to the Analysis is
        assigned to any of the currently selected departments (information
        stored in a cookie).

        If department filtering is disabled in bika_setup, returns True. If the
        obj is None or empty, returns False.

        If the obj has no department assigned, returns True

        :param obj: A single Analysis brain or content object
        :type obj: ATContentType/CatalogBrain
        :returns: True if the item can be added to the list.
        :rtype: bool
        """
        if not obj:
            return False

        if not self.context.bika_setup.getAllowDepartmentFiltering():
            # Filtering by department is disabled. Return True
            return True

        # Department filtering is enabled. Check if the Analysis Service
        # associated to this Analysis is assigned to at least one of the
        # departments currently selected.
        dep_uid = obj.getDepartmentUID()
        departments = self.request.get('filter_by_department_info', '')
        return not dep_uid or dep_uid in departments.split(',')
