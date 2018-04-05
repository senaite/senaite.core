# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api

from bika.lims import logger


def set_department_cookies(event):
    """
    Login event handler.
    When user logs in, departments must be selected if filtering by department
    is enabled in Bika Setup.
        - For (Lab)Managers and Client Contacts, all the departments from the
          system must be selected.
        - For regular Lab Contacts, default Department must be selected. If
          the Contact doesn't have any default department assigned, then first
          department in alphabetical order will be selected.
    """
    if not is_bika_installed():
        logger.warn(
            "Package 'bika.lims' is not installed, skipping event handler "
            "for IUserLoggedInEvent.")
        return

    # get the bika_setup object
    portal = api.get_portal()
    bika_setup = portal.get("bika_setup")

    # just to be sure...
    # This should go into the api.py module once it is in place
    if bika_setup is None:
        raise RuntimeError(
            "bika_setup not found in this Bika LIMS installation")

    # Getting request, response and username
    request = api.get_request()
    response = request.RESPONSE
    user = api.get_current_user()
    username = user and user.getUserName() or None
    is_manager = user and (user.has_role('Manager') or
                           user.has_role('LabManager'))
    portal_catalog = api.get_tool("portal_catalog")

    # If department filtering is disabled, disable the cookies
    if not bika_setup.getAllowDepartmentFiltering():
        response.setCookie(
            'filter_by_department_info', None,  path='/', max_age=0)
        response.setCookie(
            'dep_filter_disabled', None,  path='/', max_age=0)
        return

    selected_deps = []

    # Select all Departments for Lab Managers
    if is_manager:
        selected_deps = portal_catalog(
            portal_type='Department',
            sort_on='sortable_title',
            sort_order='ascending',
            inactive_state='active')

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

        # If it is a Client Contact, select all departments no need to filter.
        elif brain[0].portal_type == 'Contact':
            selected_deps = portal_catalog(
                portal_type='Department',
                sort_on='sortable_title',
                sort_order='ascending',
                inactive_state='active')

            response.setCookie(
                'dep_filter_disabled', None, path='/', max_age=24 * 3600)

        # It is a LabContact, select only one department. It must be Default
        # Department of the Lab Contact if possible
        elif brain[0].portal_type == 'LabContact':
            lab_con = brain[0].getObject()
            if lab_con.getDefaultDepartment():
                selected_deps = [lab_con.getDefaultDepartment()]
            else:
                departments = lab_con.getSortedDepartments()
                selected_deps = [departments[0]] if departments else []

            response.setCookie(
                'dep_filter_disabled', None, path='/', max_age=0)

    selected_dep_uids = ','.join([api.get_uid(dep) for dep in selected_deps])
    response.setCookie(
        'filter_by_department_info',
        selected_dep_uids,
        path='/',
        max_age=24 * 3600)

    return

def clear_department_cookies(event):
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
    request = api.get_request()
    response = request.RESPONSE

    # Voiding our special cookie on logout
    response.setCookie(
        'filter_by_department_info', None,  path='/', max_age=0)
    response.setCookie(
        'dep_filter_disabled', None,  path='/', max_age=0)


def is_bika_installed():
    """Check if Bika LIMS is installed in the Portal
    """
    qi = api.get_tool("portal_quickinstaller")
    return qi.isProductInstalled("bika.lims")
