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
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields import PartitionSetupField
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
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

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

# XXX REMOVE
# Allow/Disallow to set the calculation manually
# Behavior controlled by javascript depending on Instruments field:
# - If no instruments available, hide and uncheck
# - If at least one instrument selected then checked, but not readonly
# See browser/js/bika.lims.analysisservice.edit.js
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
        description=_("Available methods to perform the test"),
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

# Calculation to be used. This field is used in Analysis Service Edit view.
#
# AnalysisService defines a setter to maintain back-references on the
# calculation, so that calculations can easily lookup their dependants based
# on this field's value.
#
#  The default calculation is the one linked to the default method Behavior
# controlled by js depending on UseDefaultCalculation:
# - If UseDefaultCalculation is set to False, show this field
# - If UseDefaultCalculation is set to True, show this field
#  See browser/js/bika.lims.analysisservice.edit.js
Calculation = UIDReferenceField(
    "Calculation",
    schemata="Method",
    required=0,
    vocabulary="_getAvailableCalculationsDisplayList",
    allowed_types=("Calculation",),
    accessor="getCalculationUID",
    widget=SelectionWidget(
        format="select",
        label=_("Calculation"),
        description=_("Calculation to be assigned to this content."),
        catalog_name="bika_setup_catalog",
        base_query={"is_active": True},
    )
)

# InterimFields are defined in Calculations, Services, and Analyses.
# In Analysis Services, the default values are taken from Calculation.
# In Analyses, the default values are taken from the Analysis Service.
# When instrument results are imported, the values in analysis are overridden
# before the calculation is performed.
InterimFields = InterimFieldsField(
    'InterimFields',
    schemata="Result Options",
    widget=RecordsWidget(
        label=_("Result variables"),
        description=_(
            "Variables are displayed as additional input fields on results "
            "entry, next to 'Result' field. If the analysis has a Calculation "
            "assigned, the values set here override those from the Calculation "
        ),
    )
)

schema = schema.copy() + Schema((
    Separate,
    Preservation,
    Container,
    PartitionSetup,
    Methods,
    Instruments,
    UseDefaultCalculation,
    Calculation,
    InterimFields,
))

# Move default method field after available methods field
schema.moveField("Method", after="Methods")
# Move default instrument field after available instruments field
schema.moveField("Instrument", after="Instruments")


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

    @security.public
    def getCalculation(self):
        """Returns the assigned calculation

        :returns: Calculation object
        """
        return self.getField("Calculation").get(self)

    @security.public
    def getCalculationUID(self):
        """Returns the UID of the assigned calculation

        NOTE: This is the default accessor of the `Calculation` schema field
        and needed for the selection widget to render the selected value
        properly in _view_ mode.

        :returns: Calculation UID
        """
        calculation = self.getCalculation()
        if not calculation:
            return None
        return api.get_uid(calculation)

    @security.public
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

    @security.public
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

    @security.public
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

    @security.public
    def getMethods(self):
        """Returns the assigned methods

        If you want to obtain the available methods to assign to the service,
        use getAvailableMethodUIDs.

        :returns: List of method objects
        """
        return self.getField("Methods").get(self)

    @security.public
    def getRawMethods(self):
        """Returns the assigned method UIDs

        :returns: List of method UIDs
        """
        field = self.getField("Methods")
        methods = field.getRaw(self)
        if not methods:
            return []
        return methods

    @security.public
    def getInstruments(self):
        """Returns the assigned instruments

        :returns: List of instrument objects
        """
        return self.getField("Instruments").get(self)

    def getRawInstruments(self):
        """List of assigned Instrument UIDs
        """
        return self.getField("Instruments").getRaw(self)

    @security.public
    def getAvailableInstruments(self):
        """ Returns the instruments available for this service.
            If the service has the getInstrumentEntryOfResults(), returns
            the instruments capable to perform this service. Otherwhise,
            returns an empty list.
        """
        instruments = self.getInstruments() \
            if self.getInstrumentEntryOfResults() is True \
            else None
        return instruments if instruments else []

    @security.private
    def _getAvailableCalculationsDisplayList(self):
        """ Returns a DisplayList with the available Calculations
            registered in Bika-Setup. Only active Calculations are
            fetched. Used to fill the Calculation field
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Calculation',
                              is_active=True)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

    @security.public
    def getServiceDependencies(self):
        """
        This methods returns a list with the analyses services dependencies.
        :return: a list of analysis services objects.
        """
        calc = self.getCalculation()
        if calc:
            return calc.getCalculationDependencies(flat=True)
        return []

    @security.public
    def getServiceDependenciesUIDs(self):
        """
        This methods returns a list with the service dependencies UIDs
        :return: a list of uids
        """
        deps = self.getServiceDependencies()
        deps_uids = [service.UID() for service in deps]
        return deps_uids

    @security.public
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

    @security.public
    def getServiceDependantsUIDs(self):
        deps = self.getServiceDependants()
        deps_uids = [service.UID() for service in deps]
        return deps_uids

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


registerType(AnalysisService, PROJECTNAME)
