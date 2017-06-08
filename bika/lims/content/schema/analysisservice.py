# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.


from Products.Archetypes.public import BooleanField, BooleanWidget, \
    MultiSelectionWidget, Schema, SelectionWidget
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.partitionsetupfield import PartitionSetupField
from bika.lims.browser.widgets.partitionsetupwidget import PartitionSetupWidget
from bika.lims.browser.widgets.referencewidget import ReferenceWidget
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.content.schema import Storage

# If this flag is true, then analyses created from this service will be linked
# to their own Sample Partition, and no other analyses will be linked to that
# partition.
Separate = BooleanField(
    'Separate',
    storage=Storage(),
    schemata='Container and Preservation',
    default=False,
    required=0,
    widget=BooleanWidget(
        label=_("Separate Container"),
        description=_("Check this box to ensure a separate sample container is "
                      "used for this analysis service"),
    ),
)

# The preservation for this service; If multiple services share the same
# preservation, then it's possible that they can be performed on the same
# sample partition.
Preservation = UIDReferenceField(
    'Preservation',
    storage=Storage(),
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
    ),
)

# The container or containertype for this service's analyses can be specified.
# If multiple services share the same container or containertype, then it's
# possible that their analyses can be performed on the same partitions
Container = UIDReferenceField(
    'Container',
    storage=Storage(),
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
    ),
)

# This is a list of dictionaries which contains the PartitionSetupWidget
# settings.  This is used to decide how many distinct physical partitions
# will be created, which containers/preservations they will use, and which
# analyases can be performed on each partition.
PartitionSetup = PartitionSetupField(
    'PartitionSetup',
    storage=Storage(),
    schemata='Container and Preservation',
    widget=PartitionSetupWidget(
        label=PMF("Preservation per sample type"),
        description=_(
            "Please specify preservations that differ from the analysis "
            "service's default preservation per sample type here."),
    ),
)

# Manually configured calculation to be used for analyses derived from this
# service.  This field is used if UseDefaultCalculation is set to false.
# The default calculation is the one linked to the default method
# Behavior controlled by js depending on UseDefaultCalculation:
# - If UseDefaultCalculation is set to False, show this field
# - If UseDefaultCalculation is set to True, show this field
# See browser/js/bika.lims.analysisservice.edit.js
Calculation = UIDReferenceField(
    'Calculation',
    storage=Storage(),
    schemata="Method",
    required=0,
    vocabulary='_getAvailableCalculationsDisplayList',
    allowed_types=('Calculation',),
    widget=SelectionWidget(
        format='select',
        label=_("Default Calculation"),
        description=_("Default calculation to be used from the "
                      "default Method selected. The Calculation "
                      "for a method can be assigned in the Method "
                      "edit view."),
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'}
    ),
)

# Allow/Disallow to set the calculation manually
# Behavior controlled by javascript depending on Instruments field:
# - If no instruments available, hide and uncheck
# - If at least one instrument selected then checked, but not readonly
# See browser/js/bika.lims.analysisservice.edit.js
UseDefaultCalculation = BooleanField(
    'UseDefaultCalculation',
    storage=Storage(),
    schemata="Method",
    default=True,
    widget=BooleanWidget(
        label=_("Use default calculation"),
        description=_(
            "Select if the calculation to be used is the calculation set by "
            "default in the default method. If unselected, the calculation "
            "can be selected manually"),
    ),
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
    storage=Storage(),
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
    ),
)

# Instruments associated to the AS
# List of instruments capable to perform the Analysis Service. The
# Instruments selected here are displayed in the Analysis Request
# Add view, closer to this Analysis Service if selected.
# - If InstrumentEntry not checked, hide and unset
# - If InstrumentEntry checked, set the first selected and show
Instruments = UIDReferenceField(
    'Instruments',
    storage=Storage(),
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
    ),
)

schema = schema.copy() + Schema((
    Separate,
    Preservation,
    Container,
    PartitionSetup,
    UseDefaultCalculation,
    Calculation,
    Methods,
    Instruments,
))
