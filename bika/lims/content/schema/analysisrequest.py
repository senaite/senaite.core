# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxsize

from Products.ATExtensions.field import RecordsField
from Products.Archetypes.Field import BooleanField, ComputedField, \
    FixedPointField, ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    RichWidget, StringWidget, TextAreaWidget
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import ARAnalysesField, UIDReferenceField
from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import DateTimeWidget, DecimalWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.browser.widgets import RejectionWidget
from bika.lims.browser.widgets import SelectionWidget
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.permissions import EditARContact, SampleSample, ScheduleSampling
from bika.lims.content.schema import Storage

Contact = UIDReferenceField(
    'Contact',
    storage=Storage,
    required=1,
    default_method='getContactUIDForUser',
    allowed_types=('Contact',),
    mode="rw",
    read_permission=permissions.View,
    write_permission=EditARContact,
    widget=ReferenceWidget(
        label=_("Contact"),
        render_own_label=True,
        size=20,
        helper_js=("bika_widgets/referencewidget.js",
                   "++resource++bika.lims.js/contact.js"),
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'prominent',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        base_query={'inactive_state': 'active'},
        showOn=True,
        popup_width='400px',
        colModel=[
            {'columnName': 'UID', 'hidden': True},
            {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
            {'columnName': 'EmailAddress', 'width': '50',
             'label': _('Email Address')},
        ]
    ),
)

CCContact = ReferenceField(
    'CCContact',
    storage=Storage,
    multiValued=1,
    vocabulary_display_path_bound=maxsize,
    allowed_types=('Contact',),
    referenceClass=HoldingReference,
    relationship='AnalysisRequestCCContact',
    mode="rw",
    read_permission=permissions.View,
    write_permission=EditARContact,
    widget=ReferenceWidget(
        label=_("CC Contacts"),
        render_own_label=True,
        size=20,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'prominent',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        base_query={'inactive_state': 'active'},
        showOn=True,
        popup_width='400px',
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Fullname', 'width': '50',
                   'label': _('Name')},
                  {'columnName': 'EmailAddress', 'width': '50',
                   'label': _('Email Address')},
                  ]
    ),
)

CCEmails = StringField(
    'CCEmails',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=EditARContact,
    acquire=True,
    acquire_fieldname="CCEmails",
    widget=StringWidget(
        label=_("CC Emails"),
        visible={
            'edit': 'visible',
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

Client = ReferenceField(
    'Client',
    storage=Storage,
    required=1,
    allowed_types=('Client',),
    relationship='AnalysisRequestClient',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Client"),
        description=_("You must assign this request to a client"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'invisible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'invisible', 'edit': 'invisible'},
            'scheduled_sampling':
                {'view': 'invisible', 'edit': 'invisible'},
            'sampled': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
            'sample_received': {'view': 'invisible', 'edit': 'invisible'},
            'attachment_due': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'invisible', 'edit': 'invisible'},
            'verified': {'view': 'invisible', 'edit': 'invisible'},
            'published': {'view': 'invisible', 'edit': 'invisible'},
            'invalid': {'view': 'invisible', 'edit': 'invisible'},
            'rejected': {'view': 'invisible', 'edit': 'invisible'},
        },
        base_query={'inactive_state': 'active'},
        showOn=True,
        add_button={
            'visible': True,
            'url': 'clients/createObject?type_name=Client',
            'return_fields': ['Title'],
            'js_controllers': ['#client-base-edit'],
            'overlay_handler': 'ClientOverlayHandler',
        }
    ),
)

Sample = ReferenceField(
    'Sample',
    storage=Storage,
    vocabulary_display_path_bound=maxsize,
    allowed_types=('Sample',),
    referenceClass=HoldingReference,
    relationship='AnalysisRequestSample',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sample"),
        description=_("Select a sample to create a secondary AR"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_catalog',
        base_query={'cancellation_state': 'active',
                    'review_state': ['sample_due', 'sample_received', ]},
        showOn=True
    ),
)

Batch = ReferenceField(
    'Batch',
    storage=Storage,
    allowed_types=('Batch',),
    relationship='AnalysisRequestBatch',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Batch"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'visible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_catalog',
        base_query={'review_state': 'open',
                    'cancellation_state': 'active'},
        showOn=True
    ),
)

BatchUID = ComputedField(
    'BatchUID',
    storage=Storage,
    expression='here.getBatch().UID() if here.getBatch() else ""',
    widget=ComputedWidget(
        visible=False
    ),
)

SamplingRound = ReferenceField(
    'SamplingRound',
    storage=Storage,
    allowed_types=('SamplingRound',),
    relationship='AnalysisRequestSamplingRound',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sampling Round"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'visible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='portal_catalog',
        base_query={},
        showOn=True
    ),
)

SubGroup = ReferenceField(
    'SubGroup',
    storage=Storage,
    required=False,
    allowed_types=('SubGroup',),
    referenceClass=HoldingReference,
    relationship='AnalysisRequestSubGroup',
    widget=ReferenceWidget(
        label=_("Sub-group"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'visible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        colModel=[
            {'columnName': 'Title', 'width': '30',
             'label': _('Title'), 'align': 'left'},
            {'columnName': 'Description', 'width': '70',
             'label': _('Description'), 'align': 'left'},
            {'columnName': 'SortKey', 'hidden': True},
            {'columnName': 'UID', 'hidden': True},
        ],
        base_query={'inactive_state': 'active'},
        sidx='SortKey',
        sord='asc',
        showOn=True
    ),
)

Template = ReferenceField(
    'Template',
    storage=Storage,
    allowed_types=('ARTemplate',),
    referenceClass=HoldingReference,
    relationship='AnalysisRequestARTemplate',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Template"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

# TODO: Profile'll be delated
Profile = ReferenceField(
    'Profile',
    storage=Storage,
    allowed_types=('AnalysisProfile',),
    referenceClass=HoldingReference,
    relationship='AnalysisRequestAnalysisProfile',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Analysis Profile"),
        size=20,
        render_own_label=True,
        visible=False,
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=False
    ),
)

Profiles = ReferenceField(
    'Profiles',
    storage=Storage,
    multiValued=1,
    allowed_types=('AnalysisProfile',),
    referenceClass=HoldingReference,
    vocabulary_display_path_bound=maxsize,
    relationship='AnalysisRequestAnalysisProfiles',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Analysis Profiles"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

# This field is a mirror of a field in Sample with the same name
DateSampled = DateTimeField(
    'DateSampled',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=SampleSample,
    widget=DateTimeWidget(
        label=_("Date Sampled"),
        size=20,
        show_time=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'secondary': 'disabled',
            'header_table': 'prominent',
            'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_sampled': {'view': 'invisible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'invisible', 'edit': 'visible'},
            'sampled': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
            'sample_due': {'view': 'invisible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'invisible', 'edit': 'invisible'},
            'attachment_due': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'invisible', 'edit': 'invisible'},
            'verified': {'view': 'invisible', 'edit': 'invisible'},
            'published': {'view': 'invisible', 'edit': 'invisible'},
            'invalid': {'view': 'invisible', 'edit': 'invisible'},
            'rejected': {'view': 'invisible', 'edit': 'invisible'},
        },
        render_own_label=True
    ),
)

# This field is a mirror of a field in Sample with the same name
Sampler = StringField(
    'Sampler',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=SampleSample,
    vocabulary='getSamplers',
    widget=BikaSelectionWidget(
        format='select',
        label=_("Sampler"),
        # see SamplingWOrkflowWidgetVisibility
        visible={
            'edit': 'visible',
            'view': 'visible',
            'header_table': 'prominent',
            'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_sampled': {'view': 'invisible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'invisible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
        },
        render_own_label=True,
    ),
)

ScheduledSamplingSampler = StringField(
    'ScheduledSamplingSampler',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=ScheduleSampling,
    vocabulary='getSamplers',
    widget=BikaSelectionWidget(
        description=_("Define the sampler supposed to do the sample in "
                      "the scheduled date"),
        format='select',
        label=_("Sampler for scheduled sampling"),
        visible={
            'edit': 'visible',
            'view': 'visible',
            'header_table': 'visible',
            'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
            'sample_due': {'view': 'invisible', 'edit': 'invisible'},
            'sample_received': {'view': 'invisible', 'edit': 'invisible'},
            'expired': {'view': 'invisible', 'edit': 'invisible'},
            'disposed': {'view': 'invisible', 'edit': 'invisible'},
        },
        render_own_label=True,
    ),
)

# This field is a mirror of a Sample field with the same name
SamplingDate = DateTimeField(
    'SamplingDate',
    storage=Storage,
    required=1,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Sampling Date"),
        size=20,
        show_time=True,
        render_own_label=True,
        # see SamplingWOrkflowWidgetVisibility
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'secondary': 'disabled',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

SampleType = ReferenceField(
    'SampleType',
    storage=Storage,
    required=1,
    allowed_types='SampleType',
    relationship='AnalysisRequestSampleType',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sample Type"),
        description=_("Create a new sample of this type"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
            'scheduled_sampling':
                {'view': 'invisible', 'edit': 'invisible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

RejectionReasons = RecordsField(
    'RejectionReasons',
    storage=Storage,
    widget=RejectionWidget(
        label=_("Sample Rejection"),
        description=_("Set the Sample Rejection workflow and the reasons"),
        render_own_label=False,
        visible={
            'edit': 'visible',
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
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

Specification = ReferenceField(
    'Specification',
    storage=Storage,
    required=0,
    allowed_types='AnalysisSpec',
    relationship='AnalysisRequestAnalysisSpec',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Analysis Specification"),
        description=_("Choose default AR specification values"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        colModel=[
            {'columnName': 'contextual_title',
             'width': '30',
             'label': _('Title'),
             'align': 'left'},
            {'columnName': 'SampleTypeTitle',
             'width': '70',
             'label': _('SampleType'),
             'align': 'left'},
            # UID is required in colModel
            {'columnName': 'UID', 'hidden': True},
        ],
        showOn=True,
    ),
)

# see setResultsRange below.
ResultsRange = RecordsField(
    'ResultsRange',
    storage=Storage,
    required=0,
    type='resultsrange',
    subfields=('keyword', 'min', 'max', 'error', 'hidemin', 'hidemax',
               'rangecomment'),
    widget=ComputedWidget(visible=False)
)

PublicationSpecification = ReferenceField(
    'PublicationSpecification',
    storage=Storage,
    required=0,
    allowed_types='AnalysisSpec',
    relationship='AnalysisRequestPublicationSpec',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.View,
    widget=ReferenceWidget(
        label=_("Publication Specification"),
        description=_(
            "Set the specification to be used before publishing an AR."),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'header_table': 'visible',
            'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_sampled': {'view': 'invisible', 'edit': 'invisible'},
            'scheduled_sampling':
                {'view': 'invisible', 'edit': 'invisible'},
            'sampled': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
            'sample_due': {'view': 'invisible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'invisible', 'edit': 'invisible'},
            'attachment_due': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'invisible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'visible'},
            'published': {'view': 'visible', 'edit': 'visible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

SamplePoint = ReferenceField(
    'SamplePoint',
    storage=Storage,
    allowed_types='SamplePoint',
    relationship='AnalysisRequestSamplePoint',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sample Point"),
        description=_("Location where sample was taken"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            # LIMS-1159
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

StorageLocation = ReferenceField(
    'StorageLocation',
    storage=Storage,
    allowed_types='StorageLocation',
    relationship='AnalysisRequestStorageLocation',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Storage Location"),
        description=_("Location where sample is kept"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'visible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

ClientOrderNumber = StringField(
    'ClientOrderNumber',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Client Order Number"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'visible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

# Sample field
ClientReference = StringField(
    'ClientReference',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Client Reference"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'visible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

# Sample field
ClientSampleID = StringField(
    'ClientSampleID',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Client Sample ID"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered': {'view': 'visible', 'edit': 'visible'},
            'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

# Sample field
SamplingDeviation = ReferenceField(
    'SamplingDeviation',
    storage=Storage,
    allowed_types=('SamplingDeviation',),
    relationship='AnalysisRequestSamplingDeviation',
    referenceClass=HoldingReference,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sampling Deviation"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

# Sample field
SampleCondition = ReferenceField(
    'SampleCondition',
    storage=Storage,
    allowed_types=('SampleCondition',),
    relationship='AnalysisRequestSampleCondition',
    referenceClass=HoldingReference,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Sample condition"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

EnvironmentalConditions = StringField(
    'EnvironmentalConditions',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=StringWidget(
        label=_("Environmental conditions"),
        visible={
            'edit': 'visible',
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
        size=20,
    ),
)

DefaultContainerType = ReferenceField(
    'DefaultContainerType',
    storage=Storage,
    allowed_types=('ContainerType',),
    relationship='AnalysisRequestContainerType',
    referenceClass=HoldingReference,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        label=_("Default Container"),
        description=_("Default container for new sample partitions"),
        size=20,
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        },
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

# Sample field
AdHoc = BooleanField(
    'AdHoc',
    storage=Storage,
    default=False,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=BooleanWidget(
        label=_("Ad-Hoc"),
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
            'sampled': {'view': 'visible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
            'sample_due': {'view': 'visible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

# Sample field
Composite = BooleanField(
    'Composite',
    storage=Storage,
    default=False,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=BooleanWidget(
        label=_("Composite"),
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

ReportDryMatter = BooleanField(
    'ReportDryMatter',
    storage=Storage,
    default=False,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=BooleanWidget(
        label=_("Report as Dry Matter"),
        render_own_label=True,
        description=_("These results can be reported as dry matter"),
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'visible'},
            'attachment_due': {'view': 'visible', 'edit': 'visible'},
            'to_be_verified': {'view': 'visible', 'edit': 'visible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

InvoiceExclude = BooleanField(
    'InvoiceExclude',
    storage=Storage,
    default=False,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=BooleanWidget(
        label=_("Invoice Exclude"),
        description=_("Select if analyses to be excluded from invoice"),
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

Analyses = ARAnalysesField(
    'Analyses',
    storage=Storage,
    required=1,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ComputedWidget(
        visible={
            'edit': 'invisible',
            'view': 'invisible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'invisible'},
        }
    ),
)

Attachment = ReferenceField(
    'Attachment',
    storage=Storage,
    multiValued=1,
    allowed_types=('Attachment',),
    referenceClass=HoldingReference,
    relationship='AnalysisRequestAttachment',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ComputedWidget(
        visible={
            'edit': 'invisible',
            'view': 'invisible',
        }
    ),
)

Invoice = ReferenceField(
    'Invoice',
    storage=Storage,
    vocabulary_display_path_bound=maxsize,
    allowed_types=('Invoice',),
    referenceClass=HoldingReference,
    relationship='AnalysisRequestInvoice',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ComputedWidget(
        visible={
            'edit': 'invisible',
            'view': 'invisible',
        }
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
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DateTimeWidget(
        label=_("Date Received"),
        visible={
            'edit': 'visible',
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
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'visible', 'edit': 'invisible'},
        }
    ),
)

DatePublished = DateTimeField(
    'DatePublished',
    storage=Storage,
    mode="r",
    read_permission=permissions.View,
    widget=DateTimeWidget(
        label=_("Date Published"),
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'invisible',
            'secondary': 'invisible',
            'header_table': 'visible',
            'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_sampled': {'view': 'invisible', 'edit': 'invisible'},
            'scheduled_sampling':
                {'view': 'invisible', 'edit': 'invisible'},
            'sampled': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_preserved': {'view': 'invisible', 'edit': 'invisible'},
            'sample_due': {'view': 'invisible', 'edit': 'invisible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'invisible', 'edit': 'invisible'},
            'attachment_due': {'view': 'invisible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'invisible', 'edit': 'invisible'},
            'verified': {'view': 'invisible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
            'rejected': {'view': 'invisible', 'edit': 'invisible'},
        }
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage,
    default_content_type='text/x-web-intelligent',
    allowable_content_types=('text/plain',),
    default_output_type="text/plain",
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'invisible',
            'sample_registered':
                {'view': 'invisible', 'edit': 'invisible'},
        }
    ),
)

MemberDiscount = FixedPointField(
    'MemberDiscount',
    storage=Storage,
    default_method='getDefaultMemberDiscount',
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=DecimalWidget(
        label=_("Member discount %"),
        description=_("Enter percentage value eg. 33.0"),
        render_own_label=True,
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'invisible',
            'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
        }
    ),
)

SampleTypeTitle = ComputedField(
    'SampleTypeTitle',
    storage=Storage,
    expression="here.getSampleType().Title() if here.getSampleType() "
               "else ''",
    widget=ComputedWidget(
        visible=False,
    ),
)

SamplePointTitle = ComputedField(
    'SamplePointTitle',
    storage=Storage,
    expression="here.getSamplePoint().Title() if here.getSamplePoint() "
               "else ''",
    widget=ComputedWidget(
        visible=False,
    ),
)

SampleUID = ComputedField(
    'SampleUID',
    storage=Storage,
    expression="here.getSample() and here.getSample().UID() or ''",
    widget=ComputedWidget(
        visible=False,
    ),
)

SampleID = ComputedField(
    'SampleID',
    storage=Storage,
    expression="here.getSample() and here.getSample().getId() or ''",
    widget=ComputedWidget(
        visible=False,
    ),
)

ContactUID = ComputedField(
    'ContactUID',
    storage=Storage,
    expression="here.getContact() and here.getContact().UID() or ''",
    widget=ComputedWidget(
        visible=False,
    ),
)

ProfilesUID = ComputedField(
    'ProfilesUID',
    storage=Storage,
    expression="[p.UID() for p in here.getProfiles()] if here.getProfiles() "
               "else []",
    widget=ComputedWidget(
        visible=False,
    ),
)

Invoiced = ComputedField(
    'Invoiced',
    storage=Storage,
    expression='here.getInvoice() and True or False',
    default=False,
    widget=ComputedWidget(
        visible=False,
    ),
)

ReceivedBy = ComputedField(
    'ReceivedBy',
    storage=Storage,
    expression='here.getReceivedBy()',
    default='',
    widget=ComputedWidget(visible=False, )
)

CreatorFullName = ComputedField(
    'CreatorFullName',
    storage=Storage,
    expression="here._getCreatorFullName()",
    widget=ComputedWidget(visible=False)
)

CreatorEmail = ComputedField(
    'CreatorEmail',
    storage=Storage,
    expression="here._getCreatorEmail()",
    widget=ComputedWidget(visible=False)
)

SamplingRoundUID = ComputedField(
    'SamplingRoundUID',
    storage=Storage,
    expression="here.getSamplingRound().UID() if here.getSamplingRound() else"
               " ''",
    widget=ComputedWidget(visible=False)
)

SampleURL = ComputedField(
    'SampleURL',
    storage=Storage,
    expression="here.getSample().absolute_url_path() if here.getSample() else"
               " ''",
    widget=ComputedWidget(visible=False)
)

SamplerFullName = ComputedField(
    'SamplerFullName',
    storage=Storage,
    expression="here._getSamplerFullName()",
    widget=ComputedWidget(visible=False)
)

SamplerEmail = ComputedField(
    'SamplerEmail',
    storage=Storage,
    expression="here._getSamplerEmail()",
    widget=ComputedWidget(visible=False)
)

BatchID = ComputedField(
    'BatchID',
    storage=Storage,
    expression="here.getBatch().getId() if here.getBatch() else ''",
    widget=ComputedWidget(visible=False)
)

BatchURL = ComputedField(
    'BatchURL',
    storage=Storage,
    expression="here.getBatch().absolute_url_path() if here.getBatch() else ''",
    widget=ComputedWidget(visible=False)
)

# TODO-catalog: move all these computed fields to methods
ClientUID = ComputedField(
    'ClientUID',
    storage=Storage,
    expression="here.getClient().UID() if here.getClient() else ''",
    widget=ComputedWidget(visible=False)
)

ClientTitle = ComputedField(
    'ClientTitle',
    storage=Storage,
    expression="here.getClient().Title() if here.getClient() else ''",
    widget=ComputedWidget(visible=False)
)

ClientURL = ComputedField(
    'ClientURL',
    storage=Storage,
    expression="here.getClient().absolute_url_path() if here.getClient() else"
               " ''",
    widget=ComputedWidget(visible=False)
)

ContactUsername = ComputedField(
    'ContactUsername',
    storage=Storage,
    expression="here.getContact().getUsername() if here.getContact() else ''",
    widget=ComputedWidget(visible=False)
)

ContactFullName = ComputedField(
    'ContactFullName',
    storage=Storage,
    expression="here.getContact().getFullname() if here.getContact() else ''",
    widget=ComputedWidget(visible=False)
)

ContactEmail = ComputedField(
    'ContactEmail',
    storage=Storage,
    expression="here.getContact().getEmailAddress() if here.getContact() else"
               " ''",
    widget=ComputedWidget(visible=False)
)

SampleTypeUID = ComputedField(
    'SampleTypeUID',
    storage=Storage,
    expression="here.getSampleType().UID() if here.getSampleType() else ''",
    widget=ComputedWidget(visible=False)
)

SamplePointUID = ComputedField(
    'SamplePointUID',
    storage=Storage,
    expression="here.getSamplePoint().UID() if here.getSamplePoint() else ''",
    widget=ComputedWidget(visible=False)
)

StorageLocationUID = ComputedField(
    'StorageLocationUID',
    storage=Storage,
    expression="here.getStorageLocation().UID() if here.getStorageLocation() "
               "else ''",
    widget=ComputedWidget(visible=False)
)

ProfilesURL = ComputedField(
    'ProfilesURL',
    storage=Storage,
    expression="[p.absolute_url_path() for p in here.getProfiles()] if "
               "here.getProfiles() else []",
    widget=ComputedWidget(visible=False)
)

ProfilesTitle = ComputedField(
    'ProfilesTitle',
    storage=Storage,
    expression="[p.Title() for p in here.getProfiles()] if here.getProfiles()"
               " else []",
    widget=ComputedWidget(visible=False)
)

ProfilesTitleStr = ComputedField(
    'ProfilesTitleStr',
    storage=Storage,
    expression="' '.join([p.Title() for p in here.getProfiles()]) if "
               "here.getProfiles() else []",
    widget=ComputedWidget(visible=False)
)

TemplateUID = ComputedField(
    'TemplateUID',
    storage=Storage,
    expression="here.getTemplate().UID() if here.getTemplate() else ''",
    widget=ComputedWidget(visible=False)
)

TemplateURL = ComputedField(
    'TemplateURL',
    storage=Storage,
    expression="here.getTemplate().absolute_url_path() if here.getTemplate() "
               "else ''",
    widget=ComputedWidget(visible=False)
)

TemplateTitle = ComputedField(
    'TemplateTitle',
    storage=Storage,
    expression="here.getTemplate().Title() if here.getTemplate() else ''",
    widget=ComputedWidget(visible=False)
)

AnalysesNum = ComputedField(
    'AnalysesNum',
    storage=Storage,
    expression="here._getAnalysesNum()",
    widget=ComputedWidget(visible=False)
)

ChildAnalysisRequest = ReferenceField(
    'ChildAnalysisRequest',
    storage=Storage,
    allowed_types=('AnalysisRequest',),
    relationship='AnalysisRequestChildAnalysisRequest',
    referenceClass=HoldingReference,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        visible=False,
    ),
)

ParentAnalysisRequest = ReferenceField(
    'ParentAnalysisRequest',
    storage=Storage,
    allowed_types=('AnalysisRequest',),
    relationship='AnalysisRequestParentAnalysisRequest',
    referenceClass=HoldingReference,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=ReferenceWidget(
        visible=False,
    ),
)

PreparationWorkflow = StringField(
    'PreparationWorkflow',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    vocabulary='getPreparationWorkflows',
    acquire=True,
    widget=SelectionWidget(
        format="select",
        label=_("Preparation Workflow"),
        visible={
            'edit': 'visible',
            'view': 'visible',
            'add': 'edit',
            'header_table': 'visible',
            'sample_registered':
                {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
            'to_be_sampled': {'view': 'visible', 'edit': 'visible'},
            'sampled': {'view': 'visible', 'edit': 'visible'},
            'to_be_preserved': {'view': 'visible', 'edit': 'visible'},
            'sample_due': {'view': 'visible', 'edit': 'visible'},
            'sample_prep': {'view': 'visible', 'edit': 'invisible'},
            'sample_received': {'view': 'visible', 'edit': 'invisible'},
            'attachment_due': {'view': 'visible', 'edit': 'invisible'},
            'to_be_verified': {'view': 'visible', 'edit': 'invisible'},
            'verified': {'view': 'visible', 'edit': 'invisible'},
            'published': {'view': 'visible', 'edit': 'invisible'},
            'invalid': {'view': 'visible', 'edit': 'invisible'},
        },
        render_own_label=True
    ),
)

# For comments or results interpretation
# Old one, to be removed because of the incorporation of
# ResultsInterpretationDepts (due to LIMS-1628)
ResultsInterpretation = TextField(
    'ResultsInterpretation',
    storage=Storage,
    mode="rw",
    default_content_type='text/html',
    # Input content type for the textfield
    default_output_type='text/x-html-safe',
    # getResultsInterpretation returns a str with html tags
    # to conserve the txt format in the report.
    read_permission=permissions.View,
    write_permission=permissions.ModifyPortalContent,
    widget=RichWidget(
        description=_("Comments or results interpretation"),
        label=_("Results Interpretation"),
        size=10,
        allow_file_upload=False,
        default_mime_type='text/x-rst',
        output_mime_type='text/x-html',
        rows=3,
        visible=False
    ),
)

ResultsInterpretationDepts = RecordsField(
    'ResultsInterpretationDepts',
    storage=Storage,
    subfields=('uid', 'richtext'),
    subfield_labels={'uid': _('Department'),
                     'richtext': _('Results Interpreation')},
    widget=RichWidget(visible=False)
)

# Custom settings for the assigned analysis services
# https://jira.bikalabs.com/browse/LIMS-1324
# Fields:
#   - uid: Analysis Service UID
#   - hidden: True/False. Hide/Display in results reports

AnalysisServicesSettings = RecordsField(
    'AnalysisServicesSettings',
    storage=Storage,
    required=0,
    subfields=('uid', 'hidden',),
    widget=ComputedWidget(visible=False)
)

Printed = StringField(
    'Printed',
    storage=Storage,
    mode="rw",
    read_permission=permissions.View,
    widget=StringWidget(
        label=_("Printed"),
        description=_("Indicates if the last ARReport is printed,"),
        visible={'view': 'invisible',
                 'edit': 'invisible'},
    ),
)

# Here is stored pre-digested data used during publication.
# It is updated when the object is verified or when changes
# are made to verified objects.
Digest = StringField(
    'Digest',
    storage=Storage,
)

schema = BikaSchema.copy() + Schema((
    Contact,
    CCContact,
    CCEmails,
    Client,
    Sample,
    Batch,
    BatchUID,
    SamplingRound,
    SubGroup,
    Template,
    Profile,
    Profiles,
    DateSampled,
    Sampler,
    ScheduledSamplingSampler,
    SamplingDate,
    SampleType,
    RejectionReasons,
    Specification,
    ResultsRange,
    PublicationSpecification,
    SamplePoint,
    StorageLocation,
    ClientOrderNumber,
    ClientReference,
    ClientSampleID,
    SamplingDeviation,
    SampleCondition,
    EnvironmentalConditions,
    DefaultContainerType,
    AdHoc,
    Composite,
    ReportDryMatter,
    InvoiceExclude,
    Analyses,
    Attachment,
    Invoice,
    DateReceived,
    DatePublished,
    Remarks,
    MemberDiscount,
    ClientUID,
    SampleTypeTitle,
    SamplePointTitle,
    SampleUID,
    SampleID,
    ContactUID,
    ProfilesUID,
    Invoiced,
    ReceivedBy,
    CreatorFullName,
    CreatorEmail,
    SamplingRoundUID,
    SampleURL,
    SamplerFullName,
    SamplerEmail,
    BatchID,
    BatchURL,
    ClientTitle,
    ClientURL,
    ContactUsername,
    ContactFullName,
    ContactEmail,
    SampleTypeUID,
    SamplePointUID,
    StorageLocationUID,
    ProfilesURL,
    ProfilesTitle,
    ProfilesTitleStr,
    TemplateUID,
    TemplateURL,
    TemplateTitle,
    AnalysesNum,
    ChildAnalysisRequest,
    ParentAnalysisRequest,
    PreparationWorkflow,
    ResultsInterpretation,
    ResultsInterpretationDepts,
    AnalysisServicesSettings,
    Printed,
    Digest
))

schema['title'].required = False

schema['id'].widget.visible = {
    'edit': 'invisible',
    'view': 'invisible',
}

schema['title'].widget.visible = {
    'edit': 'invisible',
    'view': 'invisible',
}

schema.moveField('Client', before='Contact')
schema.moveField('ResultsInterpretation', pos='bottom')
schema.moveField('ResultsInterpretationDepts', pos='bottom')
