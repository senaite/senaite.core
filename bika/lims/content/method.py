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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveInstrument
from bika.lims.interfaces import IMethod
from plone.app.blob.field import FileField as BlobFileField
from Products.Archetypes.atapi import InAndOutWidget
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import FileWidget
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import TextField
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import DisplayList
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    # Method ID should be unique, specified on MethodSchemaModifier
    StringField(
        "MethodID",
        searchable=1,
        required=0,
        validators=("uniquefieldvalidator",),
        widget=StringWidget(
            visible={"view": "visible", "edit": "visible"},
            label=_("Method ID"),
            description=_("Define an identifier code for the method. "
                          "It must be unique."),
        ),
    ),

    TextField(
        "Instructions",
        default_content_type="text/plain",
        allowed_content_types=("text/plain", ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            label=_("Instructions"),
            description=_("Technical description and instructions "
                          "intended for analysts"),
        ),
    ),

    BlobFileField(
        "MethodDocument",  # XXX Multiple Method documents please
        widget=FileWidget(
            label=_("Method Document"),
            description=_("Load documents describing the method here"),
        )
    ),

    LinesField(
        "Instruments",
        vocabulary="availableInstrumentsVocabulary",
        accessor="getInstrumentUIDs",
        widget=InAndOutWidget(
            visible=True,
            label=_("Instruments"),
            description=_(
                "Select the supported Instruments for this Method."),
        )
    ),

    # If no instrument selected, always True.
    BooleanField(
        "ManualEntryOfResults",
        schemata="default",
        default=True,
        widget=BooleanWidget(
            label=_("Manual entry of results"),
            description=_("The results for the Analysis Services that use "
                          "this method can be set manually"),
        )
    ),

    # Calculations associated to this method. The analyses services
    # with this method assigned will use the calculation selected here.
    UIDReferenceField(
        "Calculation",
        allowed_types=("Calculation", ),
        widget=ReferenceWidget(
            visible={"edit": "visible", "view": "visible"},
            format="select",
            checkbox_bound=0,
            label=_("Calculation"),
            description=_(
                "If required, select a calculation for the The analysis "
                "services linked to this method. Calculations can be "
                "configured under the calculations item in the LIMS set-up"),
            showOn=True,
            catalog_name="bika_setup_catalog",
            base_query={
                "sort_on": "sortable_title",
                "is_active": True,
                "sort_limit": 50,
            },
        )
    ),
    BooleanField(
        "Accredited",
        schemata="default",
        default=True,
        widget=BooleanWidget(
            label=_("Accredited"),
            description=_("Check if the method has been accredited"))
    ),
))

schema["description"].schemata = "default"
schema["description"].widget.visible = True
schema["description"].widget.label = _("Description")
schema["description"].widget.description = _(
    "Describes the method in layman terms. "
    "This information is made available to lab clients")


class Method(BaseFolder):
    """Method content
    """
    implements(IMethod, IDeactivable, IHaveInstrument)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getInstrument(self):
        """Instruments capable to perform this method.
        Required by IHaveInstrument
        """
        return self.getInstruments()

    def getInstruments(self):
        """Instruments capable to perform this method
        """
        return self.getBackReferences("InstrumentMethods")

    def getRawInstruments(self):
        """List of Instrument UIDs capable to perform this method
        """
        return map(api.get_uid, self.getInstruments())

    def setInstruments(self, value):
        """Set the method on the selected instruments
        """
        # filter out empty value
        value = filter(lambda uid: uid, value)

        # handle removed instruments
        existing = self.getInstrumentUIDs()
        to_remove = filter(lambda uid: uid not in value, existing)

        # handle all Instruments flushed
        if not value:
            self.setManualEntryOfResults(True)

        # remove method from removed instruments
        for uid in to_remove:
            instrument = api.get_object_by_uid(uid)
            methods = instrument.getMethods()
            methods.remove(self)
            instrument.setMethods(methods)

        # add method to new added instruments
        for uid in value:
            instrument = api.get_object_by_uid(uid)
            methods = instrument.getMethods()
            if self in methods:
                continue
            methods.append(self)
            instrument.setMethods(methods)

    def getInstrumentUIDs(self):
        """UIDs of the instruments capable to perform this method
        """
        return map(api.get_uid, self.getInstruments())

    def setManualEntryOfResults(self, value):
        """Allow manual entry of results
        """
        field = self.getField("ManualEntryOfResults")
        if not self.getInstruments():
            # Always true if no instrument is selected
            field.set(self, True)
        else:
            field.set(self, value)

    def availableInstrumentsVocabulary(self):
        """Available instruments registered in the system
        """
        bsc = api.get_tool("bika_setup_catalog")
        query = {
            "portal_type": "Instrument",
            "sort_on": "sortable_title",
            "is_active": True,
        }
        items = [(i.UID, i.Title) for i in bsc(query)]
        return DisplayList(list(items))

    def isManualEntryOfResults(self):
        """BBB
        """
        return self.getManualEntryOfResults()


registerType(Method, PROJECTNAME)
