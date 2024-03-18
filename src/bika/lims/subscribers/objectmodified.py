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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from Products.CMFCore.utils import getToolByName
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import SETUP_CATALOG


def ObjectModifiedEventHandler(obj, event):
    """ Various types need automation on edit.
    """
    try:
        portal_type = api.get_portal_type(obj)
    except api.APIError:
        # BBB: Might be an `at_references` folder
        return

    if portal_type == 'Contact':
        # Verify that the Contact details are the same as the Plone user.
        contact_username = obj.Schema()['Username'].get(obj)
        if contact_username:
            contact_email = obj.Schema()['EmailAddress'].get(obj)
            contact_fullname = obj.Schema()['Fullname'].get(obj)
            mt = getToolByName(obj, 'portal_membership')
            member = mt.getMemberById(contact_username)
            if member:
                properties = {'username': contact_username,
                              'email': contact_email,
                              'fullname': contact_fullname}
                member.setMemberProperties(properties)

    elif portal_type == 'AnalysisCategory':
        # If the analysis category's Title is modified, we must
        # re-index all services and analyses that refer to this title.
        uid = obj.UID()

        # re-index all analysis services
        query = dict(category_uid=uid, portal_type="AnalysisService")
        brains = api.search(query, SETUP_CATALOG)
        for brain in brains:
            ob = api.get_object(brain)
            ob.reindexObject()

        # re-index analyses
        query = dict(getCategoryUID=uid)
        brains = api.search(query, ANALYSIS_CATALOG)
        for brain in brains:
            ob = api.get_object(brain)
            ob.reindexObject()
