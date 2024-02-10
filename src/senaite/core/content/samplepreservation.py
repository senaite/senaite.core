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

from AccessControl import ClassSecurityInfo
from bika.lims import _
from bika.lims import api
from bika.lims.interfaces import IDeactivable
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import ISamplePreservation
from senaite.core.schema.durationfield import DurationField
from senaite.core.z3cform.widgets.duration.widget import DurationWidgetFactory
from zope import schema
from zope.interface import implementer


class ISamplePreservationSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=u"Title",
        required=False,
    )

    description = schema.Text(
        title=u"Description",
        required=False,
    )

    category = schema.Choice(
        title=_(
            u"label_samplepreservation_category",
            default=u"Category"
        ),
        source="senaite.core.vocabularies.samplepreservation.categories",
        default="lab",
        required=True,
    )

    directives.widget("duration", DurationWidgetFactory)
    retention_period = DurationField(
        title=_(
            u"label_samplepreservation_retention_period",
            default=u"Once preserved, the sample must be disposed of within "
                    u"this time period. If not specified, the sample type "
                    u"retention period will be used."
        ),
        required=False,
    )


@implementer(ISamplePreservation, ISamplePreservationSchema, IDeactivable)
class SamplePreservation(Container):
    """Sample preservation
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getCategory(self):
        accessor = self.accessor("category")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setCategory(self, value):
        mutator = self.mutator("category")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getRetentionPeriod(self):
        accessor = self.accessor("retention_period")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setRetentionPeriod(self, value):
        mutator = self.mutator("retention_period")
        mutator(self, value)
