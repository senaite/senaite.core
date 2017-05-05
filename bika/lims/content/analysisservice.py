# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


import sys
import transaction

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import DisplayList, ReferenceField, \
    BooleanField, BooleanWidget, Schema, registerType, SelectionWidget, \
    MultiSelectionWidget
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets.partitionsetupwidget import PartitionSetupWidget
from bika.lims.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.baseanalysis import schema as BaseAnalysisSchema, \
    BaseAnalysis
from bika.lims.interfaces import IAnalysisService, IHaveIdentifiers
from bika.lims.utils import to_utf8 as _c
from magnitude import mg
from plone.indexer import indexer
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

    items = allow_blank and [['', _('Any')]] or []

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
                items.append((container.UID(), container.Title()))

    ts = getToolByName(instance, 'translation_service').translate
    cat_str = _c(ts(_('Container Type')))
    containertypes = [c.getContainerType() for c in containers]
    containertypes = dict([(ct.UID(), ct.Title())
                           for ct in containertypes if ct])
    for ctype_uid, ctype_title in containertypes.items():
        ctype_title = _c(ctype_title)
        if show_container_types:
            items.append((ctype_uid, "%s: %s" % (cat_str, ctype_title)))
        if show_containers:
            for container in containers:
                ctype = container.getContainerType()
                if ctype and ctype.UID() == ctype_uid:
                    items.append((container.UID(), container.Title()))

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
                      inactive_state='active',
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
        items = [(c.UID, c.title) for c in
                 bsc(portal_type='Preservation',
                     inactive_state='active',
                     sort_on='sortable_title')]
        items = [['', _('Any')]] + list(items)
        return DisplayList(items)

    security.declarePublic('Containers')

    def Containers(self, instance=None):
        instance = instance or self
        items = getContainers(instance, allow_blank=True)
        return DisplayList(items)


registerField(PartitionSetupField, title="", description="")


@indexer(IAnalysisService)
def sortable_title_with_sort_key(instance):
    sort_key = instance.getSortKey()
    if sort_key:
        return "{:010.3f}{}".format(sort_key, instance.Title())
    return instance.Title()


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
        base_query={'inactive_state': 'active'},
    )
)

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
        base_query={'inactive_state': 'active'},
    )
)

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

# Manual methods associated to the AS
# List of methods capable to perform the Analysis Service. The
# Methods selected here are displayed in the Analysis Request
# Add view, closer to this Analysis Service if selected.
# Use getAvailableMethods() to retrieve the list with methods both
# from selected instruments and manually entered.
# Behavior controlled by js depending on ManualEntry/Instrument:
# - If InsrtumentEntry not checked, show
# See browser/js/bika.lims.analysisservice.edit.js
Methods = UIDReferenceField(
    'Methods',
    schemata="Method",
    required=0,
    multiValued=1,
    vocabulary='_getAvailableMethodsDisplayList',
    allowed_types=('Method',),
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

# Default method to be used. This field is used in Analysis Service
# Edit view, use getMethod() to retrieve the Method to be used in
# this Analysis Service.
# Gets populated with the methods selected in the multiselection
# box above or with the default instrument's method.
# Behavior controlled by js depending on ManualEntry/Instrument/Methods:
# - If InstrumentEntry checked, set instrument's default method, and readonly
# - If InstrumentEntry not checked, populate dynamically with
#   selected Methods, set the first method selected and non-readonly
# See browser/js/bika.lims.analysisservice.edit.js
_Method = UIDReferenceField(
    '_Method',
    schemata="Method",
    required=0,
    searchable=True,
    vocabulary_display_path_bound=sys.maxint,
    allowed_types=('Method',),
    vocabulary='_getAvailableMethodsDisplayList',
    widget=SelectionWidget(
        format='select',
        label=_("Default Method"),
        description=_(
            "If 'Allow instrument entry of results' is selected, the method "
            "from the default instrument will be used. Otherwise, only the "
            "methods selected above will be displayed.")
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
        label=_("Use default calculation"),
        description=_(
            "Select if the calculation to be used is the calculation set by "
            "default in the default method. If unselected, the calculation "
            "can be selected manually"),
    )
)

# Default calculation to be used. This field is used in Analysis Service
# Edit view, use getCalculation() to retrieve the Calculation to be used in
# this Analysis Service.
# The default calculation is the one linked to the default method
# Behavior controlled by js depending on UseDefaultCalculation:
# - If UseDefaultCalculation is set to False, show this field
# - If UseDefaultCalculation is set to True, show this field
# See browser/js/bika.lims.analysisservice.edit.js
_Calculation = UIDReferenceField(
    '_Calculation',
    schemata="Method",
    required=0,
    vocabulary_display_path_bound=sys.maxint,
    vocabulary='_getAvailableCalculationsDisplayList',
    allowed_types=('Calculation',),
    widget=SelectionWidget(
        format='select',
        label=_("Default Calculation"),
        description=_(
            "Default calculation to be used from the default Method selected. "
            "The Calculation for a method can be assigned in the Method edit "
            "view."),
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
    )
)

# Default calculation is not longer linked directly to the AS: it
# currently uses the calculation linked to the default Method.
# Use getCalculation() to retrieve the Calculation to be used.
# Old ASes (before 3008 upgrade) can be linked to the same Method,
# but to different Calculation objects. In that case, the Calculation
# is saved as DeferredCalculation and UseDefaultCalculation is set to
# False in the upgrade.
# Behavior controlled by js depending on UseDefaultCalculation:
# - If UseDefaultCalculation is set to False, show this field
# - If UseDefaultCalculation is set to True, show this field
# See browser/js/bika.lims.analysisservice.edit.js
#     bika/lims/upgrade/to3008.py
DeferredCalculation = UIDReferenceField(
    'DeferredCalculation',
    schemata="Method",
    required=0,
    vocabulary_display_path_bound=sys.maxint,
    vocabulary='_getAvailableCalculationsDisplayList',
    allowed_types=('Calculation',),
    widget=SelectionWidget(
        format='select',
        label=_("Alternative Calculation"),
        description=_(
            "If required, select a calculation for the analysis here. "
            "Calculations can be configured under the calculations item in "
            "the LIMS set-up"),
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
    )
)

## XXX Keep synced to service duplication code in bika_analysisservices.py
schema = BaseAnalysisSchema.copy() + Schema((
    Separate,
    Preservation,
    Container,
    PartitionSetup,
    Methods,
    _Method,
    Instruments,
    UseDefaultCalculation,
    _Calculation,
    DeferredCalculation,
))


class AnalysisService(BaseAnalysis):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IAnalysisService, IHaveIdentifiers)

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation

        return renameAfterCreation(self)

    security.declarePublic('getContainers')

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
                 bsc(portal_type='Preservation', inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

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
                              inactive_state='active')
                 if i.getObject().isManualEntryOfResults()]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        return DisplayList(list(items))

    @security.private
    def _getAvailableCalculationsDisplayList(self):
        """ Returns a DisplayList with the available Calculations
            registered in Bika-Setup. Only active Calculations are
            fetched. Used to fill the _Calculation and DeferredCalculation
            List fields
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Calculation',
                              inactive_state='active')]
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
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def workflow_script_activate(self):
        workflow = getToolByName(self, 'portal_workflow')
        pu = getToolByName(self, 'plone_utils')
        # A service cannot be activated if it's calculation is inactive
        calc = self.getCalculation()
        inactive_state = workflow.getInfoFor(calc, "inactive_state")
        if calc and inactive_state == "inactive":
            message = _(
                "This Analysis Service cannot be activated because it's "
                "calculation is inactive.")
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException

    def workflow_scipt_deactivate(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        pu = getToolByName(self, 'plone_utils')
        # A service cannot be deactivated if "active" calculations list it
        # as a dependency.
        active_calcs = bsc(portal_type='Calculation', inactive_state="active")
        calculations = (c.getObject() for c in active_calcs)
        for calc in calculations:
            deps = [dep.UID() for dep in calc.getDependentServices()]
            if self.UID() in deps:
                message = _(
                    "This Analysis Service cannot be deactivated because one "
                    "or more active calculations list it as a dependency")
                pu.addPortalMessage(message, 'error')
                transaction.get().abort()
                raise WorkflowException


registerType(AnalysisService, PROJECTNAME)
