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
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.browser.widgets import WorksheetTemplateLayoutWidget
from bika.lims.config import ANALYSIS_TYPES
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveInstrument
from bika.lims.interfaces import IWorksheetTemplate
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import registerType
from senaite.core import logger
from senaite.core.browser.fields.records import RecordsField
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.catalog import SETUP_CATALOG
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    RecordsField(
        "Layout",
        schemata="Layout",
        required=1,
        type="templateposition",
        subfields=("pos", "type", "blank_ref", "control_ref", "dup"),
        required_subfields=("pos", "type"),
        subfield_labels={
            "pos": _("Position"),
            "type": _("Analysis Type"),
            "blank_ref": _("Reference"),
            "control_ref": _("Reference"),
            "dup": _("Duplicate Of")
        },
        widget=WorksheetTemplateLayoutWidget(
            label=_("Worksheet Layout"),
            description=_(
                "Specify the size of the Worksheet, e.g. corresponding to a "
                "specific instrument's tray size. "
                "Then select an Analysis 'type' per Worksheet position."
                "Where QC samples are selected, also select which Reference "
                "Sample should be used."
                "If a duplicate analysis is selected, indicate which sample "
                "position it should be a duplicate of"),
        )
    ),

    UIDReferenceField(
        "Service",
        schemata="Analyses",
        required=0,
        multiValued=1,
        allowed_types=("AnalysisService",),
        widget=ServicesWidget(
            label=_("Analysis Service"),
            description=_(
                "Select which Analyses should be included on the Worksheet"
            ),
        )
    ),

    UIDReferenceField(
        "RestrictToMethod",
        allowed_types=("Method",),
        widget=ReferenceWidget(
            label=_(
                "label_worksheettemplate_restrict_to_method",
                default="Restrict to Method"),
            description=_(
                "description_worksheettemplate_restrict_to_method",
                default="Restrict the available analysis services and "
                "instruments to those with the selected method. <br/>"
                "In order to apply this change to the services list, you "
                "should save the change first."
            ),
            catalog=SETUP_CATALOG,
            query={
                "portal_type": "Method",
                "is_active": True,
                "sort_limit": 5,
                "sort_on": "sortable_title",
                "sort_order": "ascending",
            },
        ),
    ),

    UIDReferenceField(
        "Instrument",
        allowed_types=("Instrument",),
        widget=ReferenceWidget(
            label=_(
                "label_worksheettemplate_instrument",
                default="Preferred instrument"),
            description=_(
                "description_worksheettemplate_instrument",
                default="Select the preferred instrument"
            ),
            catalog=SETUP_CATALOG,
            query="get_widget_instrument_query",
        ),
    ),

    StringField(
        "InstrumentTitle",
        widget=StringWidget(
            visible=False
        )
    ),

    BooleanField(
        "EnableMultipleUseOfInstrument",
        default=True,
        widget=BooleanWidget(
            label=_("Enable Multiple Use of Instrument in Worksheets."),
            description=_(
                "If unchecked, Lab Managers won't be able to assign the same "
                "Instrument more than one Analyses while creating a Worksheet."
            )
        )
    ),

))

schema["title"].widget.visible = True
schema["description"].widget.visible = True
schema["description"].widget.description = ""


# TODO: Migrated to DX - https://github.com/senaite/senaite.core/pull/2599
class WorksheetTemplate(BaseContent):
    """Worksheet Templates
    """
    implements(IWorksheetTemplate, IHaveInstrument, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    @security.public
    def getAnalysisTypes(self):
        """Return Analysis type displaylist
        """
        return ANALYSIS_TYPES

    def get_widget_instrument_query(self, **kw):
        """Return the preferred instruments
        """
        query = {
            "portal_type": "Instrument",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        # Restrict available instruments to those with the selected method
        method_uid = self.getRawRestrictToMethod()
        if method_uid:
            # prepare subquery
            uids = []
            brains = api.search(query, SETUP_CATALOG)
            for brain in brains:
                uid = api.get_uid(brain)
                instrument = api.get_object(brain)
                if method_uid in instrument.getRawMethods():
                    uids.append(uid)
            # create a simple UID query
            query = {"UID": uids}

        logger.info("get_widget_contact_query: %r" % query)
        return query

    def getMethodUID(self):
        """Return method UID
        """
        return self.getRawRestrictToMethod()


registerType(WorksheetTemplate, PROJECTNAME)
