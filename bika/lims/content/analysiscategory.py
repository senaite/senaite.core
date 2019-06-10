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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

"""Analysis Category - the category of the analysis service
"""

import transaction
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisCategory, IDeactivable
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    TextField(
        'Comments',
        default_output_type='text/plain',
        allowable_content_types=('text/plain',),
        widget=TextAreaWidget(
            description=_(
                "To be displayed below each Analysis Category section on "
                "results reports."),
            label=_("Comments")),
    ),
    ReferenceField(
        'Department',
        required=1,
        vocabulary='getDepartments',
        allowed_types=('Department',),
        relationship='AnalysisCategoryDepartment',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Department"),
            description=_("The laboratory department"),
        ),
    ),
    FloatField(
        'SortKey',
        validators=('SortKeyValidator',),
        widget=DecimalWidget(
            label=_("Sort Key"),
            description=_(
                "Float value from 0.0 - 1000.0 indicating the sort "
                "order. Duplicate values are ordered alphabetically."),
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class AnalysisCategory(BaseContent):
    implements(IAnalysisCategory, IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getDepartments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        deps = []
        for d in bsc(portal_type='Department',
                     is_active=True):
            deps.append((d.UID, d.Title))
        return DisplayList(deps)

    def getDepartmentTitle(self):
        field = self.Schema().getField('Department')
        dept = field.get(self)
        return dept.Title() if dept else ''

    def workflow_script_deactivate(self):
        # A instance cannot be deactivated if it contains services
        pu = getToolByName(self, 'plone_utils')
        bsc = getToolByName(self, 'bika_setup_catalog')
        ars = bsc(portal_type='AnalysisService', getCategoryUID=self.UID())
        if ars:
            message = _("Category cannot be deactivated because it contains "
                        "Analysis Services")
            pu.addPortalMessage(message, 'error')
            transaction.abort()
            raise WorkflowException


registerType(AnalysisCategory, PROJECTNAME)
