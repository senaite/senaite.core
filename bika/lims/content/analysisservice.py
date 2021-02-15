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
from bika.lims import PMF
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets.partitionsetupwidget import PartitionSetupWidget
from bika.lims.browser.widgets.recordswidget import RecordsWidget
from bika.lims.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.abstractbaseanalysis import AbstractBaseAnalysis
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IDeactivable
from bika.lims.utils import to_utf8 as _c
from magnitude import mg
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import registerType
from Products.Archetypes.Registry import registerField
from Products.ATExtensions.ateapi import RecordsField
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


def getContainers(instance,
                  minvol=None,
                  allow_blank=True,
                  show_container_types=True,
                  show_containers=True):
    """ Containers vocabulary

    This is a separate class so that it can be called from ajax to filter
    the container list, as well as being used as the AT field vocabulary.

    Returns a tuple of tuples: ((object_uid, object_title), ())

    If the partition is flagged 'Separate', only containers are displayed.
    If the Separate flag is false, displays container types.

    XXX bsc = self.portal.bika_setup_catalog
    XXX obj = bsc(getKeyword='Moist')[0].getObject()
    XXX u'Container Type: Canvas bag' in obj.getContainers().values()
    XXX True

    """

    bsc = getToolByName(instance, 'bika_setup_catalog')

    items = [['', _('Any')]] if allow_blank else []

    containers = []
    for container in bsc(portal_type='Container', sort_on='sortable_title'):
        container = container.getObject()

        # verify container capacity is large enough for required sample volume.
        if minvol is not None:
            capacity = container.getCapacity()
            try:
                capacity = capacity.split(' ', 1)
                capacity = mg(float(capacity[0]), capacity[1])
                if capacity < minvol:
                    continue
            except (ValueError, TypeError):
                # if there's a unit conversion error, allow the container
                # to be displayed.
                pass

        containers.append(container)

    if show_containers:
        # containers with no containertype first
        for container in containers:
            if not container.getContainerType():
                items.append([container.UID(), container.Title()])

    ts = getToolByName(instance, 'translation_service').translate
    cat_str = _c(ts(_('Container Type')))
    containertypes = [c.getContainerType() for c in containers]
    containertypes = dict([(ct.UID(), ct.Title())
                           for ct in containertypes if ct])
    for ctype_uid, ctype_title in containertypes.items():
        ctype_title = _c(ctype_title)
        if show_container_types:
            items.append([ctype_uid, "%s: %s" % (cat_str, ctype_title)])
        if show_containers:
            for container in containers:
                ctype = container.getContainerType()
                if ctype and ctype.UID() == ctype_uid:
                    items.append([container.UID(), container.Title()])

    items = tuple(items)
    return items


class PartitionSetupField(RecordsField):
    _properties = RecordsField._properties.copy()
    _properties.update({
        'subfields': (
            'sampletype',
            'separate',
            'preservation',
            'container',
            'vol',
            # 'retentionperiod',
        ),
        'subfield_labels': {
            'sampletype': _('Sample Type'),
            'separate': _('Separate Container'),
            'preservation': _('Preservation'),
            'container': _('Container'),
            'vol': _('Required Volume'),
            # 'retentionperiod': _('Retention Period'),
        },
        'subfield_types': {
            'separate': 'boolean',
            'vol': 'string',
            'container': 'selection',
            'preservation': 'selection',
        },
        'subfield_vocabularies': {
            'sampletype': 'SampleTypes',
            'preservation': 'Preservations',
            'container': 'Containers',
        },
        'subfield_sizes': {
            'sampletype': 1,
            'preservation': 6,
            'vol': 8,
            'container': 6,
            # 'retentionperiod':10,
        }
    })
    security = ClassSecurityInfo()

    security.declarePublic('SampleTypes')

    def SampleTypes(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = []
        for st in bsc(portal_type='SampleType',
                      is_active=True,
                      sort_on='sortable_title'):
            st = st.getObject()
            title = st.Title()
            items.append((st.UID(), title))
        items = [['', '']] + list(items)
        return DisplayList(items)

    security.declarePublic('Preservations')

    def Preservations(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = [[c.UID, c.title] for c in
                 bsc(portal_type='Preservation',
                     is_active=True,
                     sort_on='sortable_title')]
        items = [['', _('Any')]] + list(items)
        return DisplayList(items)

    security.declarePublic('Containers')

    def Containers(self, instance=None):
        instance = instance or self
        items = getContainers(instance, allow_blank=True)
        return DisplayList(items)


registerField(PartitionSetupField, title="", description="")


# If this flag is true, then analyses created from this service will be linked
# to their own Sample Partition, and no other analyses will be linked to that
# partition.
Separate = BooleanField(
    'Separate',
    schemata='Container and Preservation',
    default=False,
    required=0,
    widget=BooleanWidget(
        label=_("Separate Container"),
        description=_("Check this box to ensure a separate sample container is "
                      "used for this analysis service"),
    )
)

# The preservation for this service; If multiple services share the same
# preservation, then it's possible that they can be performed on the same
# sample partition.
Preservation = UIDReferenceField(
    'Preservation',
    schemata='Container and Preservation',
    allowed_types=('Preservation',),
    vocabulary='getPreservations',
    required=0,
    multiValued=0,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Default Preservation"),
        description=_(
            "Select a default preservation for this analysis service. If the "
            "preservation depends on the sample type combination, specify a "
            "preservation per sample type in the table below"),
        catalog_name='bika_setup_catalog',
        base_query={'is_active': True},
    )
)

# The container or containertype for this service's analyses can be specified.
# If multiple services share the same container or containertype, then it's
# possible that their analyses can be performed on the same partitions
Container = UIDReferenceField(
    'Container',
    schemata='Container and Preservation',
    allowed_types=('Container', 'ContainerType'),
    vocabulary='getContainers',
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
        catalog_name='bika_setup_catalog',
        base_query={'is_active': True},
    )
)

# This is a list of dictionaries which contains the PartitionSetupWidget
# settings.  This is used to decide how many distinct physical partitions
# will be created, which containers/preservations they will use, and which
# analyases can be performed on each partition.
PartitionSetup = PartitionSetupField(
    'PartitionSetup',
    schemata='Container and Preservation',
    widget=PartitionSetupWidget(
        label=PMF("Preservation per sample type"),
        description=_(
            "Please specify preservations that differ from the analysis "
            "service's default preservation per sample type here."),
    )
)

# Allow/Disallow to set the calculation manually
# Behavior controlled by javascript depending on Instruments field:
# - If no instruments available, hide and uncheck
# - If at least one instrument selected then checked, but not readonly
# See browser/js/bika.lims.analysisservice.edit.js
UseDefaultCalculation = BooleanField(
    'UseDefaultCalculation',
    schemata="Method",
    default=True,
    widget=BooleanWidget(
        label=_("Use the Default Calculation of Method"),
        description=_(
            "Select if the calculation to be used is the calculation set by "
            "default in the default method. If unselected, the calculation "
            "can be selected manually"),
    )
)

# Manual methods associated to the AS
# List of methods capable to perform the Analysis Service. The
# Methods selected here are displayed in the Analysis Request
# Add view, closer to this Analysis Service if selected.
# Use getAvailableMethods() to retrieve the list with methods both
# from selected instruments and manually entered.
# Behavior controlled by js depending on ManualEntry/Instrument:
# - If InstrumentEntry not checked, show
# See browser/js/bika.lims.analysisservice.edit.js
Methods = UIDReferenceField(
    'Methods',
    schemata="Method",
    required=0,
    multiValued=1,
    vocabulary='_getAvailableMethodsDisplayList',
    allowed_types=('Method',),
    accessor="getMethodUIDs",
    widget=MultiSelectionWidget(
        label=_("Methods"),
        description=_(
            "The tests of this type of analysis can be performed by using "
            "more than one method with the 'Manual entry of results' option "
            "enabled. A selection list with the methods selected here is "
            "populated in the manage results view for each test of this type "
            "of analysis. Note that only methods with 'Allow manual entry' "
            "option enabled are displayed here; if you want the user to be "
            "able to assign a method that requires instrument entry, enable "
            "the 'Instrument assignment is allowed' option."),
    )
)

# Instruments associated to the AS
# List of instruments capable to perform the Analysis Service. The
# Instruments selected here are displayed in the Analysis Request
# Add view, closer to this Analysis Service if selected.
# - If InstrumentEntry not checked, hide and unset
# - If InstrumentEntry checked, set the first selected and show
Instruments = UIDReferenceField(
    'Instruments',
    schemata="Method",
    required=0,
    multiValued=1,
    vocabulary='_getAvailableInstrumentsDisplayList',
    allowed_types=('Instrument',),
    accessor="getInstrumentUIDs",
    widget=MultiSelectionWidget(
        label=_("Instruments"),
        description=_(
            "More than one instrument can be used in a test of this type of "
            "analysis. A selection list with the instruments selected here is "
            "populated in the results manage view for each test of this type "
            "of analysis. The available instruments in the selection list "
            "will change in accordance with the method selected by the user "
            "for that test in the manage results view. Although a method can "
            "have more than one instrument assigned, the selection list is "
            "only populated with the instruments that are both set here and "
            "allowed for the selected method."),
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
    schemata='Method',
    widget=RecordsWidget(
        label=_("Additional Values"),
        description=_(
            "Values can be entered here which will override the defaults "
            "specified in the Calculation Interim Fields."),
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

# Re-order some fields from AbstractBaseAnalysis schema.
# Adding them to the Schema(()) above does not work.
schema.moveField('ManualEntryOfResults', after='PartitionSetup')
schema.moveField('Methods', after='ManualEntryOfResults')
schema.moveField('InstrumentEntryOfResults', after='Methods')
schema.moveField('Instruments', after='InstrumentEntryOfResults')
schema.moveField('Instrument', after='Instruments')
schema.moveField('Method', after='Instrument')
schema.moveField('Calculation', after='UseDefaultCalculation')
schema.moveField('DuplicateVariation', after='Calculation')
schema.moveField('Accredited', after='Calculation')
schema.moveField('InterimFields', after='Calculation')


class AnalysisService(AbstractBaseAnalysis):
    implements(IAnalysisService, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
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
    def getMethodUIDs(self):
        """Returns the UIDs of the assigned methods

        NOTE: This is the default accessor of the `Methods` schema field
        and needed for the multiselection widget to render the selected values
        properly in _view_ mode.

        :returns: List of method UIDs
        """
        return self.getRawMethods()

    @security.public
    def getInstruments(self):
        """Returns the assigned instruments

        :returns: List of instrument objects
        """
        return self.getField("Instruments").get(self)

    @security.public
    def getInstrumentUIDs(self):
        """Returns the UIDs of the assigned instruments

        NOTE: This is the default accessor of the `Instruments` schema field
        and needed for the multiselection widget to render the selected values
        properly in _view_ mode.

        :returns: List of instrument UIDs
        """
        return self.getRawInstruments()

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
    def _getAvailableMethodsDisplayList(self):
        """ Returns a DisplayList with the available Methods
            registered in Bika-Setup. Only active Methods and those
            with Manual Entry field active are fetched.
            Used to fill the Methods MultiSelectionWidget when 'Allow
            Instrument Entry of Results is not selected'.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method',
                              is_active=True)
                 if i.getObject().isManualEntryOfResults()]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

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

    @security.private
    def _getAvailableInstrumentsDisplayList(self):
        """ Returns a DisplayList with the available Instruments
            registered in Bika-Setup. Only active Instruments are
            fetched. Used to fill the Instruments MultiSelectionWidget
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Instrument',
                              is_active=True)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
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

    @security.public
    def after_deactivate_transition_event(self):
        """Method triggered after a 'deactivate' transition for the current
        AnalysisService is performed. Removes this service from the Analysis
        Profiles or Analysis Request Templates where is assigned.
        This function is called automatically by
        bika.lims.workflow.AfterTransitionEventHandler
        """
        # Remove the service from profiles to which is assigned
        profiles = self.getBackReferences('AnalysisProfileAnalysisService')
        for profile in profiles:
            profile.remove_service(self)

        # Remove the service from templates to which is assigned
        bsc = api.get_tool('bika_setup_catalog')
        templates = bsc(portal_type='ARTemplate')
        for template in templates:
            template = api.get_object(template)
            template.remove_service(self)


registerType(AnalysisService, PROJECTNAME)
