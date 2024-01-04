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
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import ReferenceResultsField
from bika.lims.browser.widgets import ReferenceResultsWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import registerType
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    ReferenceResultsField(
        "ReferenceResults",
        schemata="Reference Values",
        required=1,
        subfield_validators={
            "result": "analysisspecs_validator",
            "min": "analysisspecs_validator",
            "max": "analysisspecs_validator",
        },
        widget=ReferenceResultsWidget(
            label=_("label_referencedefinition_referencevalues",
                    default=u"Reference Values"),
            description=_(
                "description_referencedefinition_referencevalues",
                default=u"Click on Analysis Categories "
                "to see Analysis Services in each category. Enter minimum "
                "and maximum values to indicate a valid results range. "
                "Any result outside this range will raise an alert. "
                "The % Error field allows for an % uncertainty to be "
                "considered when evaluating results against minimum and "
                "maximum values. A result out of range but still in range "
                "if the % error is taken into consideration, will raise a "
                "less severe alert."
            ),
        ),
    ),

    BooleanField(
        "Blank",
        schemata="Description",
        default=False,
        widget=BooleanWidget(
            label=_("label_referencedefinition_blank",
                    default=u"Blank"),
            description=_(
                "description_referencedefinition_blank",
                default=u"Reference sample values are zero or 'blank'"
            ),
        ),
    ),

    BooleanField(
        "Hazardous",
        schemata="Description",
        default=False,
        widget=BooleanWidget(
            label=_("label_referencedefinition_hazardous",
                    default=u"Hazardous"),
            description=_(
                "description_referencedefinition_hazardous",
                default=u"Samples of this type should be treated as hazardous"
            ),
        ),
    ),
))

schema["title"].schemata = "Description"
schema["title"].widget.visible = True
schema["description"].schemata = "Description"
schema["description"].widget.visible = True


class ReferenceDefinition(BaseContent):
    implements(IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(ReferenceDefinition, PROJECTNAME)
