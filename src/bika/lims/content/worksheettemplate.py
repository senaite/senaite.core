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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import sys
from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
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
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import ReferenceWidget
from Products.Archetypes.public import registerType
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.references import HoldingReference
from senaite.core.browser.fields.records import RecordsField
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.p3compat import cmp
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

    ReferenceField(
        "Service",
        schemata="Analyses",
        required=0,
        multiValued=1,
        allowed_types=("AnalysisService",),
        relationship="WorksheetTemplateAnalysisService",
        referenceClass=HoldingReference,
        widget=ServicesWidget(
            label=_("Analysis Service"),
            description=_(
                "Select which Analyses should be included on the Worksheet"
            ),
        )
    ),

    ReferenceField(
        "RestrictToMethod",
        schemata="Description",
        required=0,
        vocabulary_display_path_bound=sys.maxint,
        vocabulary="_getMethodsVoc",
        allowed_types=("Method",),
        relationship="WorksheetTemplateMethod",
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Method"),
            description=_(
                "Restrict the available analysis services and instruments"
                "to those with the selected method."
                " In order to apply this change to the services list, you "
                "should save the change first."
            ),
        ),
    ),

    ReferenceField(
        "Instrument",
        schemata="Description",
        required=0,
        vocabulary_display_path_bound=sys.maxint,
        vocabulary="getInstrumentsDisplayList",
        allowed_types=("Instrument",),
        relationship="WorksheetTemplateInstrument",
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Instrument"),
            description=_(
                "Select the preferred instrument"
            ),
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
        schemata="Description",
        widget=BooleanWidget(
            label=_("Enable Multiple Use of Instrument in Worksheets."),
            description=_(
                "If unchecked, Lab Managers won't be able to assign the same "
                "Instrument more than one Analyses while creating a Worksheet."
            )
        )
    ),

))

schema["title"].schemata = "Description"
schema["title"].widget.visible = True

schema["description"].schemata = "Description"
schema["description"].widget.visible = True


class WorksheetTemplate(BaseContent):
    """Worksheet Templates
    """
    implements(IWorksheetTemplate, IHaveInstrument, IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    @security.public
    def getAnalysisTypes(self):
        """Return Analysis type displaylist
        """
        return ANALYSIS_TYPES

    @security.public
    def getInstrumentsDisplayList(self):
        """Returns a display list with the instruments that are allowed for
        this worksheet template based on the method selected, sorted by title
        ascending. It also includes "No instrument" as the first option
        """
        items = []
        for instrument in self.getInstruments():
            uid = api.get_uid(instrument)
            title = api.get_title(instrument)
            items.append((uid, title))

        # Sort them alphabetically by title
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ("", _("No instrument")))
        return DisplayList(items)

    def getInstruments(self):
        """Returns the list of active Instrument objects that are allowed for
        this worksheet template based on the method selected
        """
        uids = self.getRawInstruments()
        return [api.get_object_by_uid(uid) for uid in uids]

    def getRawInstruments(self):
        """Returns the list of UIDs from active instruments that are allowed
        for this worksheet template based on the method selected, if any
        """
        uids = []
        method_uid = self.getRawRestrictToMethod()
        query = {
            "portal_type": "Instrument",
            "is_active": True,
        }
        brains = api.search(query, SETUP_CATALOG)
        for brain in brains:
            uid = api.get_uid(brain)
            if not method_uid:
                uids.append(uid)
                continue

            # Restrict available instruments to those with the selected method
            instrument = api.get_object(brain)
            if method_uid in instrument.getRawMethods():
                uids.append(uid)

        return uids

    def getMethodUID(self):
        """Return method UID
        """
        method = self.getRestrictToMethod()
        if method:
            return method.UID()
        return ""

    def _getMethodsVoc(self):
        """Return the registered methods as DisplayList
        """
        methods = api.search({
            "portal_type": "Method",
            "is_active": True
        }, "senaite_catalog_setup")

        items = map(lambda m: (api.get_uid(m), api.get_title(m)), methods)
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ("", _("Not specified")))

        return DisplayList(list(items))


registerType(WorksheetTemplate, PROJECTNAME)
