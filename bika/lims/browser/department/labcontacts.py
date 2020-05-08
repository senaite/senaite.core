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
            'sort_on': 'sortable_title',
            'sort_order': 'ascending'
        }
        self.columns = {
            'Fullname': {'title': _('Name'),
                         'index': 'sortable_title'},
            'Department': {'title': _('Department')},
            'BusinessPhone': {'title': _('Phone')},
            'MobilePhone': {'title': _('Mobile Phone')},
            'EmailAddress': {'title': _('Email Address')},
        }
        self.review_states = [{
            'id': 'default',
            'title': _('Active'),
            'contentFilter': {'is_active': True},
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
        obj = api.get_object(obj)
        deps = [dep.UID() for dep in obj.getDepartments()]
        item['selected'] = self.context.UID() in deps
        return item
