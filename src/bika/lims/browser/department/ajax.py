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

from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
import plone
import json


class LabContactUpdate(BrowserView):
    """
    This function receives the path to a Department, a uid of a LabContact and
    a boolean variable. If the state of the boolean is 'True', the Department
    would be added to the LabContact 'departments' content field. If the
    boolean state is 'False', then the department should be removed from the
    LabContact content field.
    The data (form) of the ajax post will be a dictionary such as:
    {'data':'{
        "contact_uid":"7a5932b7efe4427385a0d07c52289116",
        "checkbox_value":false,
        "department":"/bika_setup/bika_departments/department-16"}
    '}
    """
    def __call__(self):
        # Getting the data from the json object
        dataset = json.loads(self.request.form.get('data', ''))
        pc = getToolByName(self.context, 'portal_catalog')
        # Getting the lab contact object
        labcontact_brain = pc(
            portal_type='LabContact', UID=dataset.get('contact_uid', ''))
        # If the lab contact exists, update it
        if labcontact_brain and dataset.get('checkbox_value', False):
            # Getting the department
            department = str(dataset.get('department'))
            department = department[1:] if\
                department.startswith('/') else department
            dep = self.context.unrestrictedTraverse(department)
            # Assign the lab contact to the department
            lab_contact = labcontact_brain[0].getObject()
            lab_contact.addDepartment(dep)
            ret = {"success": True, "error": False}
        elif labcontact_brain and 'checkbox_value' in dataset.keys() and\
                not dataset['checkbox_value']:
            # Getting the department
            department = str(dataset.get('department'))
            department = department[1:] if\
                department.startswith('/') else department
            dep = self.context.unrestrictedTraverse(department)
            # Unassign the lab contact to the department
            lab_contact = labcontact_brain[0].getObject()
            lab_contact.removeDepartment(dep)
            ret = {"success": True, "error": False}
        else:
            ret = {"success": False, "error": True}
        return json.dumps(ret)
