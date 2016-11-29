# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

def ClearDepartmentCookies(event):
    """
    Logout event handler.

    When user explicitly logs out from the Logout menu, clean department filtering related cookies.
    """
    # Which cookie we want to clear
    request = event.object.REQUEST
    # YES CAPS LOCK WAS MUST WHEN ZOPE 2 WAS INVENTED
    # SOMEWHERE AROUND NINETIES. THEN IT WAS THE CRUISE
    # CONTROL FOR COOLNESS AND ZOPE IS SOO COOOOOL.
    response = request.RESPONSE
    # Voiding our special cookie on logout
    response.setCookie('filter_by_department_info',None,  path = '/', max_age = 0)
    response.setCookie('dep_filter_disabled',None,  path = '/', max_age = 0)
