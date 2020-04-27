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

import transaction
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import FloatField
from Products.Archetypes.Field import ReferenceField
from Products.Archetypes.Field import TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import DecimalWidget
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.interface import implements

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisCategory
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveDepartment

Comments = TextField(
    "Comments",
    default_output_type="text/plain",
    allowable_content_types=("text/plain",),
    widget=TextAreaWidget(
        description=_(
            "To be displayed below each Analysis Category section on results "
            "reports."),
        label=_("Comments")),
)

Department = ReferenceField(
    "Department",
    required=1,
    allowed_types=("Department",),
    relationship="AnalysisCategoryDepartment",
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        label=_("Department"),
        description=_("The laboratory department"),
        showOn=True,
        catalog_name=SETUP_CATALOG,
        base_query={
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        },
    )
)

SortKey = FloatField(
    "SortKey",
    validators=("SortKeyValidator",),
    widget=DecimalWidget(
        label=_("Sort Key"),
        description=_(
            "Float value from 0.0 - 1000.0 indicating the sort order. "
            "Duplicate values are ordered alphabetically."),
    ),
)

schema = BikaSchema.copy() + Schema((
    Comments,
    Department,
    SortKey,
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class AnalysisCategory(BaseContent):
    implements(IAnalysisCategory, IHaveDepartment, IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def workflow_script_deactivate(self):
        # A instance cannot be deactivated if it contains services
        query = dict(portal_type="AnalysisService", category_uid=self.UID())
        brains = api.search(query, SETUP_CATALOG)
        if brains:
            pu = api.get_tool("plone_utils")
            message = _("Category cannot be deactivated because it contains "
                        "Analysis Services")
            pu.addPortalMessage(message, 'error')
            transaction.abort()
            raise WorkflowException


registerType(AnalysisCategory, PROJECTNAME)
