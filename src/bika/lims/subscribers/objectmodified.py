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

from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING


def ObjectModifiedEventHandler(obj, event):
    """ Various types need automation on edit.
    """
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type == 'Calculation':
        pr = getToolByName(obj, 'portal_repository')
        uc = getToolByName(obj, 'uid_catalog')
        obj = uc(UID=obj.UID())[0].getObject()
        version_id = obj.version_id if hasattr(obj, 'version_id') else 0

        backrefs = obj.getBackReferences('MethodCalculation')
        for i, target in enumerate(backrefs):
            target = uc(UID=target.UID())[0].getObject()
            pr.save(obj=target, comment="Calculation updated to version %s" %
                (version_id + 1,))
            reference_versions = getattr(target, 'reference_versions', {})
            reference_versions[obj.UID()] = version_id + 1
            target.reference_versions = reference_versions

    elif obj.portal_type == 'Contact':
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

    elif obj.portal_type == 'AnalysisCategory':
        # If the analysis category's Title is modified, we must
        # re-index all services and analyses that refer to this title.
        query = dict(getCategoryUID=obj.UID())
        brains = api.search(query, CATALOG_ANALYSIS_LISTING)
        for brain in brains:
            obj = api.get_object(brain)
            obj.reindexObject(idxs=['getCategoryTitle'])

