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
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import PartitionSetupField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.partitionsetupfield import getContainers
from bika.lims.browser.widgets.partitionsetupwidget import PartitionSetupWidget
from bika.lims.browser.widgets.recordswidget import RecordsWidget
from bika.lims.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractbaseanalysis import AbstractBaseAnalysis
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IDeactivable
from Products.Archetypes.atapi import PicklistWidget
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import getToolByName
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
            "Available methods to perform the test depending if they "
            "allow or deny the manual entry of results."),
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

# XXX REMOVE
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

Calculations = UIDReferenceField(
    "Calculations",
    schemata="Method",
    required=0,
    vocabulary="_calculations_vocabulary",
    allowed_types=("Calculation", ),
    multiValued=1,
    accessor="getRawCalculations",
    widget=PicklistWidget(
        label=_("Calculations"),
        description=_("Supported calculations of this service"),
    )
)

Calculation = UIDReferenceField(
    "Calculation",
    schemata="Method",
    required=0,
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

# If this flag is true, then analyses created from this service will be linked
# to their own Sample Partition, and no other analyses will be linked to that
# partition.
Separate = BooleanField(
    "Separate",
    schemata="Container and Preservation",
    default=False,
    required=0,
    widget=BooleanWidget(
        label=_("Separate Container"),
        description=_("Check this box to ensure a separate sample container "
                      "is used for this analysis service"),
    )
)

# The preservation for this service; If multiple services share the same
# preservation, then it's possible that they can be performed on the same
# sample partition.
Preservation = UIDReferenceField(
    "Preservation",
    schemata="Container and Preservation",
    allowed_types=("Preservation",),
    vocabulary="getPreservations",
    required=0,
    multiValued=0,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Default Preservation"),
        description=_(
            "Select a default preservation for this analysis service. If the "
            "preservation depends on the sample type combination, specify a "
            "preservation per sample type in the table below"),
        catalog_name=SETUP_CATALOG,
        base_query={"is_active": True},
    )
)

# The container or containertype for this service's analyses can be specified.
# If multiple services share the same container or containertype, then it's
# possible that their analyses can be performed on the same partitions
Container = UIDReferenceField(
    "Container",
    schemata="Container and Preservation",
    allowed_types=("Container", "ContainerType"),
    vocabulary="getContainers",
    required=0,
    multiValued=0,
    widget=ReferenceWidget(
        checkbox_bound=0,
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

# This is a list of dictionaries which contains the PartitionSetupWidget
# settings.  This is used to decide how many distinct physical partitions
# will be created, which containers/preservations they will use, and which
# analyases can be performed on each partition.
PartitionSetup = PartitionSetupField(
    "PartitionSetup",
    schemata="Container and Preservation",
    widget=PartitionSetupWidget(
        label=_("Preservation per sample type"),
        description=_(
            "Please specify preservations that differ from the analysis "
            "service's default preservation per sample type here."),
    )
)


schema = schema.copy() + Schema((
    Methods,
    Instruments,
    UseDefaultCalculation,
    Calculations,
    Calculation,
    InterimFields,
    Separate,
    Preservation,
    Container,
    PartitionSetup,
))

# Move manual entry of results field before available methods field
schema.moveField("ManualEntryOfResults", before="Methods")
# Move default method field after available methods field
schema.moveField("Method", after="Methods")
# Move default instrument field after available instruments field
schema.moveField("Instrument", after="Instruments")
# Move default calculation field after available calculations field
schema.moveField("Calculation", after="Calculations")


class AnalysisService(AbstractBaseAnalysis):
    """Analysis Service Content Holder
    """
    implements(IAnalysisService, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation

        return renameAfterCreation(self)

    def setManualEntryOfResults(self, value):
        """Allow manual entry of results

        Always enabled when no instrument is selected
        """
        field = self.getField("ManualEntryOfResults")
        if not self.getInstruments():
            field.set(self, True)
        else:
            field.set(self, value)

    def getMethods(self):
        """Returns the assigned methods

        :returns: List of method objects
        """
        field = self.getField("Methods")
        methods = field.get(self)

        # filter out methods based on manaul entry setting of the service
        if self.getManualEntryOfResults():
            # filter out methods that do not allow manual entry of results
            methods = filter(
                lambda m: not m.getManualEntryOfResults(), methods)
        else:
            # filter out methods w/o instruments assigned
            methods = filter(lambda m: not m.getInstrument(), methods)

        return methods

    def getRawMethods(self):
        """Returns the assigned method UIDs

        :returns: List of method UIDs
        """
        methods = self.getMethods()
        return map(api.get_uid, methods)

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
        """Returns the assigned calculations

        :returns: List of calculation objects
        """
        return self.getField("Calculations").get(self)

    def getRawCalculations(self):
        """Returns the assigned calculation UIDs

        :returns: List of calculation UIDs
        """
        field = self.getField("Calculations")
        methods = field.getRaw(self)
        if not methods:
            return []
        return methods

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
        dlist = DisplayList(items)
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

    def after_deactivate_transition_event(self):
        """Method triggered after a 'deactivate' transition

        Removes this service from all assigned Profiles and Templates.
        """
        # Remove the service from profiles to which is assigned
        profiles = self.getBackReferences("AnalysisProfileAnalysisService")
        for profile in profiles:
            profile.remove_service(self)

        # Remove the service from templates to which is assigned
        catalog = api.get_tool(SETUP_CATALOG)
        templates = catalog(portal_type="ARTemplate")
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
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(o.UID, o.Title) for o in
                 bsc(portal_type='Preservation', is_active=True)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getServiceDependencies(self):
        """
        This methods returns a list with the analyses services dependencies.
        :return: a list of analysis services objects.
        """
        calc = self.getCalculation()
        if calc:
            return calc.getCalculationDependencies(flat=True)
        return []

    def getServiceDependenciesUIDs(self):
        """
        This methods returns a list with the service dependencies UIDs
        :return: a list of uids
        """
        deps = self.getServiceDependencies()
        deps_uids = [service.UID() for service in deps]
        return deps_uids

    def getServiceDependants(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        active_calcs = bsc(portal_type='Calculation', is_active=True)
        calculations = [c.getObject() for c in active_calcs]
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
        deps = self.getServiceDependants()
        deps_uids = [service.UID() for service in deps]
        return deps_uids

    def getAvailableMethods(self):
        """ Returns the methods available for this analysis.
            If the service has the getInstrumentEntryOfResults(), returns
            the methods available from the instruments capable to perform
            the service, as well as the methods set manually for the
            analysis on its edit view. If getInstrumentEntryOfResults()
            is unset, only the methods assigned manually to that service
            are returned.
        """
        if not self.getInstrumentEntryOfResults():
            # No need to go further, just return the manually assigned methods
            return self.getMethods()

        # Return the manually assigned methods plus those from instruments
        method_uids = self.getAvailableMethodUIDs()
        query = dict(portal_type="Method", UID=method_uids)
        brains = api.search(query, "bika_setup_catalog")
        return map(api.get_object_by_uid, brains)

    def getAvailableMethodUIDs(self):
        """
        Returns the UIDs of the available methods. it is used as a
        vocabulary to fill the selection list of 'Methods' field.
        """
        # N.B. we return a copy of the list to avoid accidental writes
        method_uids = self.getRawMethods()[:]
        if self.getInstrumentEntryOfResults():
            for instrument in self.getInstruments():
                method_uids.extend(instrument.getRawMethods())
            method_uids = filter(None, method_uids)
            method_uids = list(set(method_uids))
        return method_uids


registerType(AnalysisService, PROJECTNAME)
