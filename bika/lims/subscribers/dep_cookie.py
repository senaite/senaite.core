# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.CMFCore.utils import getToolByName

def SetDepartmentCookies(event):
    """
    Login event handler.
    When user logs in for the first time, we are setting department filtering cookie values.
    """

    #Getting request,response and username
    request = event.object.REQUEST
    response = request.RESPONSE
    context=find_context(request)
    mtool = getToolByName(context,'portal_membership')
    username = mtool.getAuthenticatedMember().getUserName()
    dep_for_cookie=''

    if context.bika_setup.getAllowDepartmentFiltering():
        if username=='admin':
            deps=context.portal_catalog(portal_type='Department',sort_on='sortable_title', sort_order='ascending',
                    inactive_state='active')
            for dep in deps:
                dep_for_cookie+=dep.UID+','
            response.setCookie('dep_filter_disabled','true',  path = '/', max_age = 24 * 3600)
        else:
            lab_con=context.portal_catalog(portal_type='LabContact',
                                getUsername=username)[0].getObject()
            if lab_con.getDefaultDepartment():
                dep_for_cookie=lab_con.getDefaultDepartment()
            else:
                deps=lab_con.getSortedDepartments()
                dep_for_cookie=deps[0].UID() if len(deps)>0 else ''
        response.setCookie('filter_by_department_info',dep_for_cookie,  path = '/', max_age = 24 * 3600)
    else:
        response.setCookie('filter_by_department_info',None,  path = '/', max_age = 0)
        response.setCookie('dep_filter_disabled',None,  path = '/', max_age = 0)


def ClearDepartmentCookies(event):
    """
    Logout event handler.
    When user explicitly logs out from the Logout menu, clean department filtering related cookies.
    """
    request = event.object.REQUEST
    response = request.RESPONSE
    # Voiding our special cookie on logout
    response.setCookie('filter_by_department_info',None,  path = '/', max_age = 0)
    response.setCookie('dep_filter_disabled',None,  path = '/', max_age = 0)

def find_context(request):
    """
    Find the context from the request
    """
    published = request.get('PUBLISHED', None)
    context = getattr(published, '__parent__', None)
    if context is None:
        context = request.PARENTS[0]
    return context
