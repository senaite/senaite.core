# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxsize

from Products.ATExtensions.field import RecordsField
from Products.Archetypes.Field import BooleanField, ComputedField, \
    ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    SelectionWidget, StringWidget, TextAreaWidget
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.browser.widgets import RejectionWidget
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget
from bika.lims.browser.widgets.datetimewidget import DateTimeWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.permissions import SampleSample
from bika.lims.permissions import ScheduleSampling

SampleID = StringField(
    'SampleID',
    storage=Storage(),
    required=1,
    searchable=True,
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_('Sample ID'),
        description=_(
            "The ID assigned to the client's sample by the lab"),
        visible={'edit': 'invisible',
                 'view': 'invisible'},
        render_own_label=True
    ),
)

ClientReference = StringField(
    'ClientReference',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Client Reference"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

ClientSampleID = StringField(
    'ClientSampleID',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Client SID"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

LinkedSample = ReferenceField(
    'LinkedSample',
    storage=Storage(),
    vocabulary_display_path_bound=maxsize,
    multiValue=1,
    allowed_types=('Sample',),
    relationship='SampleSample',
    referenceClass=HoldingReference,
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Linked Sample")
    ),
)

SampleType = ReferenceField(
    'SampleType',
    storage=Storage(),
    required=1,
    vocabulary_display_path_bound=maxsize,
    allowed_types=('SampleType',),
    relationship='SampleSampleType',
    referenceClass=HoldingReference,
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sample Type"),
        render_own_label=True,
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                 'sample_due': {'view': 'visible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

SampleTypeTitle = ComputedField(
    'SampleTypeTitle',
    expression="context.getSampleType().Title() "
               "if context.getSampleType() else None",
    widget=ComputedWidget(
        visible=False
    ),
)

SamplePoint = ReferenceField(
    'SamplePoint',
    storage=Storage(),
    vocabulary_display_path_bound=maxsize,
    allowed_types=('SamplePoint',),
    relationship='SampleSamplePoint',
    referenceClass=HoldingReference,
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sample Point"),
        render_own_label=True,
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
                 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                 'sample_due': {'view': 'visible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

SamplePointTitle = ComputedField(
    'SamplePointTitle',
    expression="context.getSamplePoint().Title() "
               "if context.getSamplePoint() else None",
    widget=ComputedWidget(
        visible=False
    ),
)

StorageLocation = ReferenceField(
    'StorageLocation',
    storage=Storage(),
    allowed_types='StorageLocation',
    relationship='AnalysisRequestStorageLocation',
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Storage Location"),
        description=_("Location where sample is kept"),
        size=20,
        render_own_label=True,
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 'expired': {'view': 'visible', 'edit': 'visible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

SamplingWorkflowEnabled = BooleanField(
    'SamplingWorkflowEnabled',
    storage=Storage(),
    default_method='getSamplingWorkflowEnabledDefault'
)
DateSampled = DateTimeField(
    'DateSampled',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=SampleSample,
    widget=DateTimeWidget(
        label=_("Date Sampled"),
        show_time=True,
        size=20,
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'invisible',
                                       'edit': 'invisible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                 'sample_due': {'view': 'visible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

Sampler = StringField(
    'Sampler',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=SampleSample,
    vocabulary='getSamplers',
    widget=BikaSelectionWidget(
        format='select',
        label=_("Sampler"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'invisible',
                                       'edit': 'invisible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                 'sample_due': {'view': 'visible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'visible'}
                 },
        render_own_label=True
    ),
)

ScheduledSamplingSampler = StringField(
    'ScheduledSamplingSampler',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=ScheduleSampling,
    vocabulary='getSamplers',
    widget=BikaSelectionWidget(
        description=_("Define the sampler supposed to do the sample in "
                      "the scheduled date"),
        format='select',
        label=_("Sampler for scheduled sampling"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                 'sample_due': {'view': 'visible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

SamplingDate = DateTimeField(
    'SamplingDate',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Sampling Date"),
        description=_(
            "Define when the sampler has to take the samples"),
        show_time=True,
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                 'sample_due': {'view': 'visible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

PreparationWorkflow = StringField(
    'PreparationWorkflow',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getPreparationWorkflows',
    acquire=True,
    widget=SelectionWidget(
        format="select",
        label=_("Preparation Workflow"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
                 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                 'sample_due': {'view': 'visible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

SamplingDeviation = ReferenceField(
    'SamplingDeviation',
    storage=Storage(),
    vocabulary_display_path_bound=maxsize,
    allowed_types=('SamplingDeviation',),
    relationship='SampleSamplingDeviation',
    referenceClass=HoldingReference,
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sampling Deviation"),
        render_own_label=True,
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

SampleCondition = ReferenceField(
    'SampleCondition',
    storage=Storage(),
    vocabulary_display_path_bound=maxsize,
    allowed_types=('SampleCondition',),
    relationship='SampleSampleCondition',
    referenceClass=HoldingReference,
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sample Condition"),
        render_own_label=True,
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

EnvironmentalConditions = StringField(
    'EnvironmentalConditions',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Environmental Conditions"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'add': 'edit',
                 'header_table': 'prominent',
                 'sample_registered':
                     {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 'attachment_due': {'view': 'visible', 'edit': 'visible'},
                 'to_be_verified': {'view': 'visible', 'edit': 'visible'},
                 'verified': {'view': 'visible', 'edit': 'invisible'},
                 'published': {'view': 'visible', 'edit': 'invisible'},
                 'invalid': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True,
        size=20
    ),
)

# Another way to obtain a transition date is using getTransitionDate
# function. We are using a DateTimeField/Widget here because in some
# cases the user may want to change the Received Date.
# AnalysisRequest and Sample's DateReceived fields needn't to have
# the same value.
# This field is updated in workflow_script_receive method.
DateReceived = DateTimeField(
    'DateReceived',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Received"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered':
                     {'view': 'invisible', 'edit': 'invisible'},
                 'to_be_sampled': {'view': 'invisible', 'edit': 'invisible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'invisible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
                 'sample_due': {'view': 'invisible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

ClientUID = ComputedField(
    'ClientUID',
    expression='context.aq_parent.UID()',
    widget=ComputedWidget(
        visible=False
    ),
)

SampleTypeUID = ComputedField(
    'SampleTypeUID',
    expression='context.getSampleType().UID()',
    widget=ComputedWidget(
        visible=False
    ),
)

SamplePointUID = ComputedField(
    'SamplePointUID',
    expression='context.getSamplePoint().UID() '
               'if context.getSamplePoint() else None',
    widget=ComputedWidget(
        visible=False
    ),
)

Composite = BooleanField(
    'Composite',
    storage=Storage(),
    default=False,
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=BooleanWidget(
        label=_("Composite"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

DateExpired = DateTimeField(
    'DateExpired',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Expired"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered':
                     {'view': 'invisible', 'edit': 'invisible'},
                 'to_be_sampled': {'view': 'invisible', 'edit': 'invisible'},
                 'scheduled_sampling':
                     {'view': 'invisible', 'edit': 'invisible'},
                 'sampled': {'view': 'invisible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
                 'sample_due': {'view': 'invisible', 'edit': 'invisible'},
                 'sample_received': {'view': 'invisible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'invisible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

DisposalDate = ComputedField(
    'DisposalDate',
    expression='context.disposal_date()',
    widget=DateTimeWidget(
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'invisible',
                                       'edit': 'invisible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
                 'sampled': {'view': 'visible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                 'sample_due': {'view': 'visible', 'edit': 'invisible'},
                 'sample_received': {'view': 'visible', 'edit': 'invisible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'invisible', 'edit': 'invisible'},
                 'rejected': {'view': 'invisible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

DateDisposed = DateTimeField(
    'DateDisposed',
    storage=Storage(),
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Disposed"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'invisible',
                                       'edit': 'invisible'},
                 'to_be_sampled': {'view': 'invisible', 'edit': 'invisible'},
                 'scheduled_sampling': {'view': 'invisible',
                                        'edit': 'invisible'},
                 'sampled': {'view': 'invisible', 'edit': 'invisible'},
                 'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
                 'sample_due': {'view': 'invisible', 'edit': 'invisible'},
                 'sample_received': {'view': 'invisible', 'edit': 'invisible'},
                 'expired': {'view': 'invisible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'invisible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

AdHoc = BooleanField(
    'AdHoc',
    storage=Storage(),
    default=False,
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=BooleanWidget(
        label=_("Ad-Hoc"),
        visible={'edit': 'visible',
                 'view': 'visible',
                 'header_table': 'visible',
                 'sample_registered': {'view': 'visible', 'edit': 'visible'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 'expired': {'view': 'visible', 'edit': 'invisible'},
                 'disposed': {'view': 'visible', 'edit': 'invisible'},
                 'rejected': {'view': 'visible', 'edit': 'invisible'},
                 },
        render_own_label=True
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage(),
    default_content_type='text/x-web-intelligent',
    allowable_content_types=('text/plain',),
    default_output_type="text/plain",
    mode='rw',
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True
    ),
)

RejectionReasons = RecordsField(
    'RejectionReasons',
    # XXX RejectionReasons should not be stored as a List of Dictionaries.
    # It should simply be LinesField, and store a list of strings, the
    # rejection reasons themselves.  When this is done, un-comment the
    # Storage() line below.  See analysisrequest.py for the same comment.
    # storage=Storage(),
    widget=RejectionWidget(
        label=_("Sample Rejection"),
        description=_(
            "Set the Sample Rejection workflow and the reasons"),
        render_own_label=False,
        visible={'edit': 'invisible',
                 'view': 'visible',
                 'add': 'edit',
                 'secondary': 'disabled',
                 'header_table': 'visible',
                 'sample_registered':
                     {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                 'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
                 'sampled': {'view': 'visible', 'edit': 'visible'},
                 'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
                 'sample_due': {'view': 'visible', 'edit': 'visible'},
                 'sample_received': {'view': 'visible', 'edit': 'visible'},
                 'attachment_due': {'view': 'visible', 'edit': 'visible'},
                 'to_be_verified': {'view': 'visible', 'edit': 'visible'},
                 'verified': {'view': 'visible', 'edit': 'visible'},
                 'published': {'view': 'visible', 'edit': 'visible'},
                 'invalid': {'view': 'visible', 'edit': 'visible'},
                 'rejected': {'view': 'visible', 'edit': 'visible'},
                 }
    ),
)

schema = BikaSchema.copy() + Schema((
    SampleID,
    ClientReference,
    ClientSampleID,
    LinkedSample,
    SampleType,
    SampleTypeTitle,
    SamplePoint,
    SamplePointTitle,
    StorageLocation,
    SamplingWorkflowEnabled,
    DateSampled,
    Sampler,
    ScheduledSamplingSampler,
    SamplingDate,
    PreparationWorkflow,
    SamplingDeviation,
    SampleCondition,
    EnvironmentalConditions,
    DateReceived,
    ClientUID,
    SampleTypeUID,
    SamplePointUID,
    Composite,
    DateExpired,
    DisposalDate,
    DateDisposed,
    AdHoc,
    Remarks,
    RejectionReasons
))

schema['title'].required = False
