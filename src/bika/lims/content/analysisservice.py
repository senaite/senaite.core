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

import itertools

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import PartitionSetupField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.partitionsetupfield import getContainers
from bika.lims.browser.widgets.partitionsetupwidget import PartitionSetupWidget
from bika.lims.browser.widgets.recordswidget import RecordsWidget
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractbaseanalysis import AbstractBaseAnalysis
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IDeactivable
from Products.Archetypes.atapi import PicklistWidget
from Products.Archetypes.Field import StringField
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import registerType
from Products.Archetypes.Widget import StringWidget
from senaite.core.browser.fields.records import RecordsField
from zope.interface import implements

Methods = UIDReferenceField(
    "Methods",
    schemata="Method",
    required=0,
    multiValued=1,
    vocabulary="_methods_vocabulary",
    allowed_types=("Method", ),
    accessor="getRawMethods",
    widget=PicklistWidget(
        label=_("Methods"),
        description=_(
            "Available methods to perform the test"),
    )
)

Instruments = UIDReferenceField(
    "Instruments",
    schemata="Method",
    required=0,
    multiValued=1,
    vocabulary="_instruments_vocabulary",
    allowed_types=("Instrument", ),
    accessor="getRawInstruments",
    widget=PicklistWidget(
        label=_("Instruments"),
        description=_("Available instruments based on the selected methods."),
    )
)

# XXX: HIDDEN -> TO BE REMOVED
UseDefaultCalculation = BooleanField(
    "UseDefaultCalculation",
    schemata="Method",
    default=True,
    widget=BooleanWidget(
        visible=False,
        label=_("Use the Default Calculation of Method"),
        description=_(
            "Select if the calculation to be used is the calculation set by "
            "default in the default method. If unselected, the calculation "
            "can be selected manually"),
    )
)

Calculation = UIDReferenceField(
    "Calculation",
    schemata="Method",
    required=0,
    relationship="AnalysisServiceCalculation",
    vocabulary="_default_calculation_vocabulary",
    allowed_types=("Calculation", ),
    accessor="getRawCalculation",
    widget=SelectionWidget(
        format="select",
        label=_("Calculation"),
        description=_("Calculation to be assigned to this content."),
        catalog_name=SETUP_CATALOG,
        base_query={"is_active": True},
    )
)

InterimFields = InterimFieldsField(
    "InterimFields",
    schemata="Result Options",
    widget=RecordsWidget(
        label=_("Result variables"),
        description=_("Additional result values"),
    )
)

# XXX: HIDDEN -> TO BE REMOVED
Separate = BooleanField(
    "Separate",
    schemata="Container and Preservation",
    default=False,
    required=0,
    widget=BooleanWidget(
        visible=False,
        label=_("Separate Container"),
        description=_("Check this box to ensure a separate sample container "
                      "is used for this analysis service"),
    )
)

# XXX: HIDDEN -> TO BE REMOVED
Preservation = UIDReferenceField(
    "Preservation",
    schemata="Container and Preservation",
    allowed_types=("SamplePreservation",),
    vocabulary="getPreservations",
    required=0,
    multiValued=0,
    widget=ReferenceWidget(
        visible=False,
        label=_("Default Preservation"),
        description=_(
            "Select a default preservation for this analysis service. If the "
            "preservation depends on the sample type combination, specify a "
            "preservation per sample type in the table below"),
        catalog_name=SETUP_CATALOG,
        base_query={"is_active": True},
    )
)

# XXX: HIDDEN -> TO BE REMOVED
Container = UIDReferenceField(
    "Container",
    schemata="Container and Preservation",
    allowed_types=("Container", "ContainerType"),
    vocabulary="getContainers",
    required=0,
    multiValued=0,
    widget=ReferenceWidget(
        visible=False,
        label=_("Default Container"),
        description=_(
            "Select the default container to be used for this analysis "
            "service. If the container to be used depends on the sample type "
            "and preservation combination, specify the container in the "
            "sample type table below"),
        catalog_name=SETUP_CATALOG,
        base_query={"is_active": True},
    )
)

# XXX: HIDDEN -> TO BE REMOVED
PartitionSetup = PartitionSetupField(
    "PartitionSetup",
    schemata="Container and Preservation",
    widget=PartitionSetupWidget(
        visible=False,
        label=_("Preservation per sample type"),
        description=_(
            "Please specify preservations that differ from the analysis "
            "service's default preservation per sample type here."),
    )
)

# Allow/disallow the capture of text as the result of the analysis
DefaultResult = StringField(
    "DefaultResult",
    schemata="Result Options",
    validators=('service_defaultresult_validator',),
    widget=StringWidget(
        label=_("Default result"),
        description=_(
            "Default result to display on result entry"
        )
    )
)

Conditions = RecordsField(
    "Conditions",
    schemata="Advanced",
    type="conditions",
    subfields=(
        "title",
        "description",
        "type",
        "choices",
        "default",
        "required",
    ),
    required_subfields=(
        "title",
        "type",
    ),
    subfield_labels={
        "title": _("Title"),
        "description": _("Description"),
        "type": _("Control type"),
        "choices": _("Choices"),
        "default": _("Default value"),
        "required": _("Required"),
    },
    subfield_descriptions={
        "choices": _("Please use the following format for select options: "
                     "key1:value1|key2:value2|...|keyN:valueN"),
    },
    subfield_types={
        "title": "string",
        "description": "string",
        "type": "string",
        "default": "string",
        "choices": "string",
        "required": "boolean",
    },
    subfield_sizes={
        "title": 20,
        "description": 50,
        "type": 1,
        "choices": 30,
        "default": 20,
    },
    subfield_validators={
        "title": "service_conditions_validator",
    },
    subfield_maxlength={
        "title": 50,
        "description": 200,
    },
    subfield_vocabularies={
        "type": DisplayList((
            ('', ''),
            ('text', _('Text')),
            ('number', _('Number')),
            ('checkbox', _('Checkbox')),
            ('select', _('Select')),
            ('file', _('File upload')),
        )),
    },
    widget=RecordsWidget(
        label=_("Analysis conditions"),
        description=_(
            "Conditions to ask for this analysis on sample registration. For "
            "instance, laboratory may want the user to input the temperature, "
            "the ramp and flow when a thermogravimetric (TGA) analysis is "
            "selected on sample registration. The information provided will be "
            "later considered by the laboratory personnel when performing the "
            "test."
        ),
    )
)


schema = schema.copy() + Schema((
    Methods,
    Instruments,
    UseDefaultCalculation,
    Calculation,
    InterimFields,
    Separate,
    Preservation,
    Container,
    PartitionSetup,
    DefaultResult,
    Conditions,
))

# Move default method field after available methods field
schema.moveField("Method", after="Methods")
# Move default instrument field after available instruments field
schema.moveField("Instrument", after="Instruments")
# Move default result field after Result Options
schema.moveField("DefaultResult", after="ResultOptions")


class AnalysisService(AbstractBaseAnalysis):
    """Analysis Service Content Holder
    """
    implements(IAnalysisService, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation

        return renameAfterCreation(self)

    def getMethods(self):
        """Returns the assigned methods

        :returns: List of method objects
        """
        return self.getField("Methods").get(self)

    def getRawMethods(self):
        """Returns the assigned method UIDs

        :returns: List of method UIDs
        """
        return self.getField("Methods").getRaw(self)

    def getMethod(self):
        """Get the default method
        """
        field = self.getField("Method")
        method = field.get(self)
        if not method:
            return None
        # check if the method is in the selected methods
        methods = self.getMethods()
        if method not in methods:
            return None
        return method

    def getRawMethod(self):
        """Returns the UID of the default method

        :returns: method UID
        """
        field = self.getField("Method")
        method = field.getRaw(self)
        if not method:
            return None
        # check if the method is in the selected methods
        methods = self.getRawMethods()
        if method not in methods:
            return None
        return method

    def getInstruments(self):
        """Returns the assigned instruments

        :returns: List of instrument objects
        """
        return self.getField("Instruments").get(self)

    def getRawInstruments(self):
        """List of assigned Instrument UIDs
        """
        return self.getField("Instruments").getRaw(self)

    def getInstrument(self):
        """Return the default instrument
        """
        field = self.getField("Instrument")
        instrument = field.get(self)
        if not instrument:
            return None
        # check if the instrument is in the selected instruments
        instruments = self.getInstruments()
        if instrument not in instruments:
            return None
        return instrument

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

    def getCalculation(self):
        """Get the default calculation
        """
        field = self.getField("Calculation")
        calculation = field.get(self)
        if not calculation:
            return None
        return calculation

    def getRawCalculation(self):
        """Returns the UID of the assigned calculation

        :returns: Calculation UID
        """
        field = self.getField("Calculation")
        calculation = field.getRaw(self)
        if not calculation:
            return None
        return calculation

    def getServiceDependencies(self):
        """Return calculation dependencies of the service

        :return: a list of analysis services objects.
        """
        calc = self.getCalculation()
        if calc:
            return calc.getCalculationDependencies(flat=True)
        return []

    def getServiceDependenciesUIDs(self):
        """Return calculation dependency UIDs of the service

        :return: a list of uids
        """
        return map(api.get_uid, self.getServiceDependencies())

    def getServiceDependants(self):
        """Return services depending on us
        """
        catalog = api.get_tool(SETUP_CATALOG)
        active_calcs = catalog(portal_type="Calculation", is_active=True)
        calculations = map(api.get_object, active_calcs)
        dependants = []
        for calc in calculations:
            calc_dependants = calc.getDependentServices()
            if self in calc_dependants:
                calc_dependencies = calc.getCalculationDependants()
                dependants = dependants + calc_dependencies
        dependants = list(set(dependants))
        if self in dependants:
            dependants.remove(self)
        return dependants

    def getServiceDependantsUIDs(self):
        """Return service UIDs depending on us
        """
        return map(api.get_uid, self.getServiceDependants())

    def query_available_methods(self):
        """Return all available methods
        """
        catalog = api.get_tool(SETUP_CATALOG)
        query = {
            "portal_type": "Method",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        return catalog(query)

    def _methods_vocabulary(self):
        """Vocabulary used for methods field
        """
        methods = self.query_available_methods()
        items = [(api.get_uid(m), api.get_title(m)) for m in methods]
        dlist = DisplayList(items)
        return dlist

    def _default_method_vocabulary(self):
        """Vocabulary used for default method field
        """
        # check if we selected methods
        methods = self.getMethods()
        if not methods:
            # query all available methods
            methods = self.query_available_methods()
        items = [(api.get_uid(m), api.get_title(m)) for m in methods]
        dlist = DisplayList(items).sortedByValue()
        # allow to leave this field empty
        dlist.add("", _("None"))
        return dlist

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
        instruments = []
        # When methods are selected, display only instruments from the methods
        methods = self.getMethods()
        for method in methods:
            for instrument in method.getInstruments():
                if instrument in instruments:
                    continue
                instruments.append(instrument)

        if not methods:
            # query all available instruments when no methods are selected
            instruments = self.query_available_instruments()

        items = [(api.get_uid(i), api.get_title(i)) for i in instruments]
        dlist = DisplayList(items)
        return dlist

    def _default_instrument_vocabulary(self):
        """Vocabulary used for default instrument field
        """
        # check if we selected instruments
        instruments = self.getInstruments()
        items = [(api.get_uid(i), api.get_title(i)) for i in instruments]
        dlist = DisplayList(items).sortedByValue()
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

    def get_methods_calculations(self):
        """Return calculations assigned to the selected methods
        """
        methods = self.getMethods()
        if not methods:
            return None
        methods_calcs = map(lambda m: m.getCalculations(), methods)
        return list(itertools.chain(*methods_calcs))

    def _default_calculation_vocabulary(self):
        """Vocabulary used for the default calculation field
        """
        calculations = self.get_methods_calculations()
        if calculations is None:
            # query all available calculations
            calculations = self.query_available_calculations()
        items = [(api.get_uid(c), api.get_title(c)) for c in calculations]
        # allow to leave this field empty
        dlist = DisplayList(items).sortedByValue()
        dlist.add("", _("None"))
        return dlist

    def after_deactivate_transition_event(self):
        """Method triggered after a 'deactivate' transition

        Removes this service from all assigned Profiles and Templates.
        """
        catalog = api.get_tool(SETUP_CATALOG)

        # Remove the service from profiles to which is assigned
        profiles = catalog(portal_type="AnalysisProfile")
        for profile in profiles:
            profile = api.get_object(profile)
            profile.remove_service(self)

        # Remove the service from templates to which is assigned
        templates = catalog(portal_type="SampleTemplate")
        for template in templates:
            template = api.get_object(template)
            template.remove_service(self)

    # XXX DECIDE IF NEEDED
    # --------------------

    def getContainers(self, instance=None):
        # On first render, the containers must be filtered
        instance = instance or self
        separate = self.getSeparate()
        containers = getContainers(instance,
                                   allow_blank=True,
                                   show_container_types=not separate,
                                   show_containers=separate)
        return DisplayList(containers)

    def getPreservations(self):
        query = {
            "portal_type": "SamplePreservation",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        brains = api.search(query, SETUP_CATALOG)
        items = [(brain.UID, brain.Title) for brain in brains]
        return DisplayList(items)

    def getAvailableMethods(self):
        """Returns the methods available for this analysis.
        """
        return self.getMethods()

    def getAvailableMethodUIDs(self):
        """Returns the UIDs of the available methods

        Used here:
        bika.lims.catalog.indexers.bikasetup.method_available_uid
        """
        # N.B. we return a copy of the list to avoid accidental writes
        return self.getRawMethods()[:]


registerType(AnalysisService, PROJECTNAME)
