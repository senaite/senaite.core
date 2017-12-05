# This file is part of Senaite
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from plone import api

from bika.lims import logger
from bika.lims.browser.dashboard.dashboard import DASHBOARD_FILTER_COOKIE
from bika.lims.utils import is_bika_installed


def ClearDashboardCookies(event):
    """
    Logout event handler.
    When user explicitly logs out from the Logout menu, clean dashboard
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
    response.setCookie(DASHBOARD_FILTER_COOKIE, None,  path='/', max_age=0)
