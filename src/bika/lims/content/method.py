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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveInstrument
from bika.lims.interfaces import IMethod
from plone.app.blob.field import FileField as BlobFileField
from Products.Archetypes.atapi import PicklistWidget
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import FileWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import TextField
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.Widget import RichWidget
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    # Method ID should be unique, specified on MethodSchemaModifier
    StringField(
        "MethodID",
        required=0,
        validators=("uniquefieldvalidator",),
        widget=StringWidget(
            label=_("Method ID"),
            description=_("Define an identifier code for the method. "
                          "It must be unique."),
        ),
    ),

    BooleanField(
        "Accredited",
        required=0,
        widget=BooleanWidget(
            label=_("Accredited"),
            description=_("Check if the method has been accredited"))
    ),

    TextField(
        "Instructions",
        required=0,
        default_content_type="text/html",
        allowed_content_types=("text/plain", "text/html"),
        default_output_type="text/x-html-safe",
        widget=RichWidget(
            label=_("Instructions"),
            description=_("Technical description and instructions "
                          "intended for analysts"),
            allow_file_upload=False,
        ),
    ),

    BlobFileField(
        "MethodDocument",  # XXX Multiple Method documents please
        required=0,
        widget=FileWidget(
            label=_("Method Document"),
            description=_("Load documents describing the method here"),
        )
    ),

    # NOTE: `Instruments` is a computed field and checks the supported methods
    #        of all global instruments.
    UIDReferenceField(
        "Instruments",
        required=0,
        vocabulary="_instruments_vocabulary",
        multiValued=1,
        accessor="getRawInstruments",
        widget=PicklistWidget(
            label=_("Instruments"),
            description=_("Instruments supporting this method"),
        )
    ),

    UIDReferenceField(
        "Calculations",
        required=0,
        vocabulary="_calculations_vocabulary",
        allowed_types=("Calculation", ),
        multiValued=1,
        accessor="getRawCalculations",
        widget=PicklistWidget(
            label=_("Calculations"),
            description=_("Supported calculations of this method"),
        )
    ),

    # XXX: HIDDEN -> TO BE REMOVED
    UIDReferenceField(
        "Calculation",
        allowed_types=("Calculation", ),
        widget=ReferenceWidget(
            visible=False,
            format="select",
            checkbox_bound=0,
            label=_("Calculation"),
            description=_(
                "If required, select a calculation for the The analysis "
                "services linked to this method. Calculations can be "
                "configured under the calculations item in the LIMS set-up"),
            showOn=True,
            catalog_name="senaite_catalog_setup",
            base_query={
                "sort_on": "sortable_title",
                "is_active": True,
                "sort_limit": 50,
            },
        )
    ),

    # XXX: HIDDEN -> TO BE REMOVED
    BooleanField(
        "ManualEntryOfResults",
        schemata="default",
        default=True,
        widget=BooleanWidget(
            visible=False,
            label=_("Manual entry of results"),
            description=_("The results for the Analysis Services that use "
                          "this method can be set manually"),
        )
    ),
))


# Show the description field after MethodID
schema["description"].schemata = "default"
schema["description"].widget.visible = True
schema["description"].widget.label = _("Description")
schema["description"].widget.description = _("Short method description")
schema.moveField("description", after="MethodID")


class Method(BaseFolder):
    """A method describes how an analysis is performed

    Methods can be assigned to analysis services and define which instruments
    and calculations are possible.
    """
    implements(IMethod, IDeactivable, IHaveInstrument)

    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

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
        existing = self.getRawInstruments()
        to_remove = filter(lambda uid: uid not in value, existing)

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

    def getCalculations(self):
        """List of Calculation UIDs
        """
        field = self.getField("Calculations")
        return field.get(self)

    def getRawCalculations(self):
        """List of Calculation UIDs
        """
        field = self.getField("Calculations")
        calculations = field.getRaw(self)
        if not calculations:
            return []
        return map(api.get_uid, calculations)

    def setCalculations(self, value):
        """Set the available calculations for the method
        """
        if not value:
            value = []
        value = filter(api.is_uid, value)
        field = self.getField("Calculations")
        field.set(self, value)

    def query_available_instruments(self):
        """Return all available Instruments
        """
        catalog = api.get_tool(SETUP_CATALOG)
        query = {
            "portal_type": "Instrument",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        return catalog(query)

    def _instruments_vocabulary(self):
        """Vocabulary used for instruments field
        """
        instruments = self.query_available_instruments()
        items = [(ins.UID, ins.Title) for ins in instruments]
        dlist = DisplayList(items)
        return dlist

    def query_available_calculations(self):
        """Return all available calculations
        """
        catalog = api.get_tool(SETUP_CATALOG)
        query = {
            "portal_type": "Calculation",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        return catalog(query)

    def _calculations_vocabulary(self):
        """Vocabulary used for calculations field
        """
        calculations = self.query_available_calculations()
        items = [(api.get_uid(c), api.get_title(c)) for c in calculations]
        dlist = DisplayList(items)
        return dlist


registerType(Method, PROJECTNAME)
