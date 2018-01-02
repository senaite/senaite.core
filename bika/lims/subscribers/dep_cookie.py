# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from plone import api

from bika.lims import logger


def SetDepartmentCookies(event):
    """
    Login event handler.
    When user logs in for the first time, we are setting department filtering cookie values.
    """
    if not is_bika_installed():
        logger.warn(
            "Package 'bika.lims' is not installed, skipping event handler "
            "for IUserLoggedInEvent.")
        return

    # get the bika_setup object
    portal = api.portal.get()
    bika_setup = portal.get("bika_setup")

    # just to be sure...
    # This should go into the api.py module once it is in place
    if bika_setup is None:
        raise RuntimeError(
            "bika_setup not found in this Bika LIMS installation")

    # Getting request, response and username

    request = api.env.getRequest()
    response = request.RESPONSE
    user = api.user.get_current()
    username = user and user.getUserName() or None
    portal_catalog = api.portal.get_tool("portal_catalog")

    if bika_setup.getAllowDepartmentFiltering():
        dep_for_cookie = ''

        if username == 'admin':
            departments = portal_catalog(
                portal_type='Department',
                sort_on='sortable_title',
                sort_order='ascending',
                inactive_state='active')

            for department in departments:
                dep_for_cookie += department.UID + ','

            response.setCookie(
                'dep_filter_disabled', 'true',  path='/',
                max_age=24 * 3600)

        else:
            brain = portal_catalog(getUsername=username)
            # It is possible that current user is created by Plone ZMI.
            # Just log it as a warning and go on
            if not brain:
                logger.warn(
                    "No lab Contact found... Plone user or Client "
                    "Contact logged in. " + username)
                response.setCookie(
                    'filter_by_department_info', None, path='/', max_age=0)
                response.setCookie(
                    'dep_filter_disabled', None, path='/', max_age=0)
                return

            # If it is Client Contact, enable all departments
            # no need to filter.
            elif brain[0].portal_type == 'Contact':
                departments = portal_catalog(
                    portal_type='Department',
                    sort_on='sortable_title',
                    sort_order='ascending',
                    inactive_state='active')
                for department in departments:
                    dep_for_cookie += department.UID + ','
                response.setCookie(
                    'dep_filter_disabled', None, path='/', max_age=24 * 3600)

            # It is a LabContact, set up departments.
            elif brain[0].portal_type == 'LabContact':
                lab_con = brain[0].getObject()
                if lab_con.getDefaultDepartment():
                    dep_for_cookie = lab_con.getDefaultDepartment()
                else:
                    departments = lab_con.getSortedDepartments()
                    dep_for_cookie = \
                        departments[0].UID() if len(departments) > 0 else ''

        response.setCookie(
            'filter_by_department_info',
            dep_for_cookie,
            path='/',
            max_age=24 * 3600)
    else:
        response.setCookie(
            'filter_by_department_info', None,  path='/', max_age=0)
        response.setCookie(
            'dep_filter_disabled', None,  path='/', max_age=0)


def ClearDepartmentCookies(event):
    """
    Logout event handler.
    When user explicitly logs out from the Logout menu, clean department
    filtering related cookies.
    """
    if not is_bika_installed():
        logger.warn(
            "Package 'bika.lims' is not installed, skipping event handler "
            "for IUserLoggedOutEvent.")
        return
    request = api.env.getRequest()
    response = request.RESPONSE

    # Voiding our special cookie on logout
    response.setCookie(
        'filter_by_department_info', None,  path='/', max_age=0)
    response.setCookie(
        'dep_filter_disabled', None,  path='/', max_age=0)


def is_bika_installed():
    """Check if Bika LIMS is installed in the Portal
    """
    qi = api.portal.get_tool("portal_quickinstaller")
    return qi.isProductInstalled("bika.lims")
