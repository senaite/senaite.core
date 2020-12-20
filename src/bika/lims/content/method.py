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
from Products.Archetypes.public import SelectionWidget
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
        required=0,
        validators=("uniquefieldvalidator",),
        widget=StringWidget(
            label=_("Method ID"),
            description=_("Define an identifier code for the method. "
                          "It must be unique."),
        ),
    ),

    TextField(
        "Instructions",
        required=0,
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
        required=0,
        widget=FileWidget(
            label=_("Method Document"),
            description=_("Load documents describing the method here"),
        )
    ),

    BooleanField(
        "Accredited",
        required=0,
        widget=BooleanWidget(
            label=_("Accredited"),
            description=_("Check if the method has been accredited"))
    ),

    # N.B. Always true when no instrument selected
    BooleanField(
        "ManualEntryOfResults",
        required=0,
        default=True,
        widget=BooleanWidget(
            label=_("Manual entry of results"),
            description=_("Allow to introduce analysis results manually"),
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
        "Instrument",
        required=0,
        allowed_types=("Instrument", ),
        vocabulary="_default_instrument_vocabulary",
        default="",
        accessor="getRawInstrument",
        widget=SelectionWidget(
            format="select",
            label=_("Default Instrument"),
            description=_("Default selected instrument for analyses"),
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

    UIDReferenceField(
        "Calculation",
        required=0,
        allowed_types=("Calculation", ),
        vocabulary="_default_calculation_vocabulary",
        accessor="getRawCalculation",
        widget=SelectionWidget(
            format="select",
            label=_("Default Calculation"),
            description=_("Default selected calculation for analyses"),
        )
    ),
))


class Method(BaseFolder):
    """Analysis method
    """
    implements(IMethod, IDeactivable, IHaveInstrument)

    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def setManualEntryOfResults(self, value):
        """Allow manual entry of results
        """
        field = self.getField("ManualEntryOfResults")
        if not self.getInstruments():
            # Always true if no instrument is selected
            field.set(self, True)
        else:
            field.set(self, value)

    def isManualEntryOfResults(self):
        """BBB: Remove when not used anymore!
        """
        return self.getManualEntryOfResults()

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

    def getInstrument(self):
        """Return the default instrument
        """
        field = self.getField("Instrument")
        instrument = field.get(self)
        if not instrument:
            return None
        # check if the instrument is in the selected instruments
        instruments = self.getRawInstruments()
        if instrument not in instruments:
            return None
        return api.get_object(instrument)

    def getRawInstrument(self):
        """Return the UID of the default instrument
        """
        field = self.getField("Instrument")
        instrument = field.getRaw(self)
        if not instrument:
            return None
        # check if the instrument is in the selected instruments
        instruments = self.getRawInstruments()
        if instrument not in instruments:
            return None
        return instrument

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

    def getCalculation(self):
        """Get the default calculation
        """
        field = self.getField("Calculation")
        calculation = field.get(self)
        if not calculation:
            return None
        # check if the calculation is in the selected calculations
        calculations = self.getRawCalculations()
        if calculation not in calculations:
            return None
        return api.get_object(calculation)

    def getRawCalculation(self):
        """Returns the UID of the assigned calculation

        NOTE: This is the default accessor of the `Calculation` schema field
        and needed for the selection widget to render the selected value
        properly in _view_ mode.

        :returns: Calculation UID
        """
        field = self.getField("Calculation")
        calculation = field.getRaw(self)
        if not calculation:
            return None
        # check if the calculation is in the selected calculations
        calculations = self.getRawCalculations()
        if calculation not in calculations:
            return None
        return calculation

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

    def _default_instrument_vocabulary(self):
        """Vocabulary used for default instrument field
        """
        # check if we selected instruments
        instruments = self.getInstruments()
        if not instruments:
            # query all available instruments
            instruments = self.query_available_instruments()
        items = [(api.get_uid(i), api.get_title(i)) for i in instruments]
        dlist = DisplayList(items)
        # allow to leave this field empty
        dlist.add("", _("None"))
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

    def _default_calculation_vocabulary(self):
        """Vocabulary used for the default calculation field
        """
        # check selected calculations
        calculations = self.getCalculations()
        if not calculations:
            # query all available calculations
            calculations = self.query_available_calculations()
        items = [(api.get_uid(c), api.get_title(c)) for c in calculations]
        # allow to leave this field empty
        dlist = DisplayList(items)
        dlist.add("", _("None"))
        return dlist


registerType(Method, PROJECTNAME)
