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

import transaction

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG

from Products.CMFCore.WorkflowCore import WorkflowException


def before_deactivate(analysis_category):
    """Function triggered before a 'deactivate' transition for
    the analysis category passed in is performed.
    """

    # Analysis Category can't be deactivated if it contains services
    query = dict(portal_type="AnalysisService",
                 category_uid=analysis_category.UID())
    brains = api.search(query, SETUP_CATALOG)
    if brains:
        pu = api.get_tool("plone_utils")
        message = _("Category cannot be deactivated because it contains "
                    "Analysis Services")
        pu.addPortalMessage(message, 'error')
        transaction.abort()
        raise WorkflowException
