# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.controlpanel.bika_labcontacts import LabContactsView


class LabContactsView(LabContactsView):
    """
    A list with all "Lab Contacts" registered in the system, sorted by
    "Firstname" ascending by default.
    A checkbox next to each "Lab Contact" will be displayed too. By
    selecting/unselecting the checboxes, the user will be able to assign
    "Lab Contacts" to the department. The submission can be done either by Ajax
    or via a "Submit" button placed at the bottom of the list.
    """

    def __init__(self, context, request):
        super(LabContactsView, self).__init__(context, request)
        self.show_select_all_checkbox = False
        self.description = self.context.translate(_(
            'By selecting/unselecting the checboxes, the user will be able ' \
            'to assign "Lab Contacts" to the department.'))
        self.context_actions = {}
        self.contentFilter = {
            'portal_type': 'LabContact',
            'sort_on': 'getFirstname',
            'sort_order': 'ascending'
        }
        self.columns = {
            'Fullname': {'title': _('Name'),
                         'index': 'getFullname'},
            'Department': {'title': _('Department')},
            'BusinessPhone': {'title': _('Phone')},
            'MobilePhone': {'title': _('Mobile Phone')},
            'EmailAddress': {'title': _('Email Address')},
        }
        self.review_states = [{
            'id': 'default',
            'title': _('Active'),
            'contentFilter': {'inactive_state': 'active'},
            'transitions': [{'id': 'empty'}, ],  # No transitions here
            # 'custom_transitions': [{'id': 'assign_labcontacts_button',
            #                     'title': _('Assign')}, ],
            'columns': ['Fullname',
                        'BusinessPhone',
                        'MobilePhone',
                        'EmailAddress']},
        ]

    def folderitem(self, obj, item, index):
        item = super(LabContactsView, self).folderitem(obj, item, index)
        deps = [dep.UID() for dep in obj.getDepartments()]
        item['selected'] = self.context.UID() in deps
        return item
