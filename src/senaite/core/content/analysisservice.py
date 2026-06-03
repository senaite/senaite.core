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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveDepartment
from bika.lims.interfaces import IHaveInstrument
from plone.supermodel import model
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IAnalysisService
from senaite.core.interfaces import IHaveAnalysisCategory
from zope import schema
from zope.interface import implementer


class IAnalysisServiceSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            u"title_analysisservice_title",
            default=u"Name"
        ),
        description=_(
            u"description_analysisservice_title",
            default=u"Name of the analysis service"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_analysisservice_description",
            default=u"Description"
        ),
        required=False,
    )

    short_title = schema.Text(
        title=_(
            u"title_analysisservice_short_title",
            default=u"Short title"
        ),
        description=_(
            u"description_analysisservice_short_title",
            default=u"If text is entered here, it is used instead of the "
                    u"title when the service is listed in column headings. "
                    u"HTML formatting is allowed."
        )
    )


@implementer(IAnalysisService, IAnalysisServiceSchema, IHaveDepartment,
             IHaveAnalysisCategory, IHaveInstrument, IDeactivable)
class AnalysisService(Container):
    """AnalysisService
    """
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getShortTitle(self):
        accessor = self.accessor("short_title")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setShortTitle(self, value):
        mutator = self.mutator("short_title")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    DepartmentID = property(getShortTitle, setShortTitle)
