"""The request for analysis by a client. It contains analysis instances.
"""
import logging
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.field import RecordsField
from plone.indexer import indexer
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.Widget import RichWidget
from Products.CMFCore import permissions
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.browser.fields import ARAnalysesField
from bika.lims.config import PROJECTNAME
from bika.lims.permissions import *
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.widgets import DateTimeWidget, DecimalWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.browser.widgets import SelectionWidget
from bika.lims.workflow import skip, isBasicTransitionAllowed
from bika.lims.workflow import doActionFor
from decimal import Decimal
from zope.interface import implements
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, getUsers, dicts_to_dict

from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget

import sys

try:
    from zope.component.hooks import getSite
except:
    # Plone < 4.3
    from zope.app.component.hooks import getSite


@indexer(IAnalysisRequest)
def Priority(instance):
    priority = instance.getPriority()
    if priority:
        return priority.getSortKey()

@indexer(IAnalysisRequest)
def BatchUID(instance):
    batch = instance.getBatch()
    if batch:
        return batch.UID()

@indexer(IAnalysisRequest)
def SamplingRoundUID(instance):
    sr = instance.getSamplingRound()
    if sr:
        return sr.UID()

schema = BikaSchema.copy() + Schema((
    StringField(
        'RequestID',
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label = _("Request ID"),
            description=_("The ID assigned to the client's request by the lab"),
            visible={'view': 'invisible',
                     'edit': 'invisible'},
        ),
    ),
    ReferenceField(
        'Contact',
        required=1,
        default_method='getContactUIDForUser',
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Contact',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestContact',
        mode="rw",
        read_permission=permissions.View,
        write_permission=EditARContact,
        widget=ReferenceWidget(
            label = _("Contact"),
            render_own_label=True,
            size=20,
            helper_js=("bika_widgets/referencewidget.js", "++resource++bika.lims.js/contact.js"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'prominent',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            base_query={'inactive_state': 'active'},
            showOn=True,
            popup_width='400px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
                      {'columnName': 'EmailAddress', 'width': '50', 'label': _('Email Address')},
                     ],
        ),
    ),
    ReferenceField(
        'CCContact',
        multiValued=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Contact',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestCCContact',
        mode="rw",
        read_permission=permissions.View,
        write_permission=EditARContact,
        widget=ReferenceWidget(
            label = _("CC Contacts"),
            render_own_label=True,
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'prominent',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            base_query={'inactive_state': 'active'},
            showOn=True,
            popup_width='400px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
                      {'columnName': 'EmailAddress', 'width': '50', 'label': _('Email Address')},
                     ],
        ),
    ),
    StringField(
        'CCEmails',
        mode="rw",
        read_permission=permissions.View,
        write_permission=EditARContact,
        widget=StringWidget(
            label = _("CC Emails"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'prominent',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
            size=20,
        ),
    ),
    ReferenceField(
        'Client',
        required=1,
        allowed_types=('Client',),
        relationship='AnalysisRequestClient',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Client"),
            description = _("You must assign this request to a client"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'invisible'},
                     'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'invisible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'invisible', 'edit': 'invisible'},
                     'verified':          {'view': 'invisible', 'edit': 'invisible'},
                     'published':         {'view': 'invisible', 'edit': 'invisible'},
                     'invalid':           {'view': 'invisible', 'edit': 'invisible'},
                     },
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'Sample',
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Sample',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestSample',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Sample"),
            description = _("Select a sample to create a secondary AR"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_catalog',
            base_query={'cancellation_state': 'active',
                        'review_state': ['sample_due', 'sample_received', ]},
            showOn=True,
        ),
    ),
    ReferenceField(
        'Batch',
        allowed_types=('Batch',),
        relationship='AnalysisRequestBatch',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Batch"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'visible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_catalog',
            base_query={'review_state': 'open',
                        'cancellation_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'SamplingRound',
        allowed_types=('SamplingRound',),
        relationship='AnalysisRequestSamplingRound',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Sampling Round"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'visible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='portal_catalog',
            base_query={},
            showOn=True,
        ),
    ),
    ReferenceField(
        'SubGroup',
        required=False,
        allowed_types=('SubGroup',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestSubGroup',
        widget=ReferenceWidget(
            label = _("Sub-group"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'visible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
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
            showOn=True,
        ),
    ),
    ReferenceField(
        'Template',
        allowed_types=('ARTemplate',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestARTemplate',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Template"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    # TODO: Profile'll be delated
    ReferenceField(
        'Profile',
        allowed_types=('AnalysisProfile',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestAnalysisProfile',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Analysis Profile"),
            size=20,
            render_own_label=True,
            visible=False,
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=False,
        ),
    ),

    ReferenceField(
        'Profiles',
        multiValued=1,
        allowed_types=('AnalysisProfile',),
        referenceClass=HoldingReference,
        vocabulary_display_path_bound=sys.maxsize,
        relationship='AnalysisRequestAnalysisProfiles',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Analysis Profiles"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    # Sample field
    DateTimeField('DateSampled',
        mode="rw",
        read_permission=permissions.View,
        write_permission=SampleSample,
        widget = DateTimeWidget(
            label = _("Date Sampled"),
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'secondary': 'disabled',
                     'header_table': 'prominent',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'visible'},
                     'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'invisible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'invisible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'invisible', 'edit': 'invisible'},
                     'verified':          {'view': 'invisible', 'edit': 'invisible'},
                     'published':         {'view': 'invisible', 'edit': 'invisible'},
                     'invalid':           {'view': 'invisible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    # Sample field
    StringField('Sampler',
        mode="rw",
        read_permission=permissions.View,
        write_permission=SampleSample,
        vocabulary='getSamplers',
        widget=BikaSelectionWidget(
            format='select',
            label = _("Sampler"),
            # see SamplingWOrkflowWidgetVisibility
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'prominent',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    DateTimeField(
        'SamplingDate',
        required=1,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label = _("Sampling Date"),
            size=20,
            render_own_label=True,
            # see SamplingWOrkflowWidgetVisibility
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'secondary': 'disabled',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    ReferenceField(
        'SampleType',
        required=1,
        allowed_types='SampleType',
        relationship='AnalysisRequestSampleType',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Sample Type"),
            description = _("Create a new sample of this type"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'Specification',
        required=0,
        allowed_types='AnalysisSpec',
        relationship='AnalysisRequestAnalysisSpec',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Analysis Specification"),
            description = _("Choose default AR specification values"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
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
    ),
    # see setResultsRange below.
    RecordsField('ResultsRange',
         required=0,
         type='analysisspec',
         subfields=('keyword', 'min', 'max', 'error', 'hidemin', 'hidemax', 'rangecomment'),
         widget=ComputedWidget(visible=False),
    ),
    ReferenceField(
        'PublicationSpecification',
        required=0,
        allowed_types='AnalysisSpec',
        relationship='AnalysisRequestPublicationSpec',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.View,
        widget=ReferenceWidget(
            label = _("Publication Specification"),
            description = _("Set the specification to be used before publishing an AR."),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'invisible'},
                     'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'invisible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'invisible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'invisible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'visible'},
                     'published':         {'view': 'visible', 'edit': 'visible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'SamplePoint',
        allowed_types='SamplePoint',
        relationship='AnalysisRequestSamplePoint',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Sample Point"),
            description = _("Location where sample was taken"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'}, # LIMS-1159
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField(
        'StorageLocation',
        allowed_types='StorageLocation',
        relationship='AnalysisRequestStorageLocation',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Storage Location"),
            description = _("Location where sample is kept"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'visible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    StringField(
        'ClientOrderNumber',
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label = _("Client Order Number"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'visible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    # Sample field
    StringField(
        'ClientReference',
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label = _("Client Reference"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'visible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    # Sample field
    StringField(
        'ClientSampleID',
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label = _("Client Sample ID"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    # Sample field
    ReferenceField('SamplingDeviation',
        allowed_types = ('SamplingDeviation',),
        relationship = 'AnalysisRequestSamplingDeviation',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Sampling Deviation"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    # Sample field
    ReferenceField(
        'SampleCondition',
        allowed_types = ('SampleCondition',),
        relationship = 'AnalysisRequestSampleCondition',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Sample condition"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    StringField(
        'EnvironmentalConditions',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Environmental conditions"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'prominent',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
            size=20,
        ),
    ),
    ReferenceField(
        'DefaultContainerType',
        allowed_types = ('ContainerType',),
        relationship = 'AnalysisRequestContainerType',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Default Container"),
            description = _("Default container for new sample partitions"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    # Sample field
    BooleanField(
        'AdHoc',
        default=False,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=BooleanWidget(
            label = _("Ad-Hoc"),
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    # Sample field
    BooleanField(
        'Composite',
        default=False,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=BooleanWidget(
            label = _("Composite"),
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'secondary': 'disabled',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    BooleanField(
        'ReportDryMatter',
        default=False,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=BooleanWidget(
            label = _("Report as Dry Matter"),
            render_own_label=True,
            description = _("These results can be reported as dry matter"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    BooleanField(
        'InvoiceExclude',
        default=False,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=BooleanWidget(
            label = _("Invoice Exclude"),
            description = _("Select if analyses to be excluded from invoice"),
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    ARAnalysesField(
        'Analyses',
        required=1,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ComputedWidget(
            visible={'edit': 'invisible',
                     'view': 'invisible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'invisible'},
                     }
        ),
    ),
    ReferenceField(
        'Attachment',
        multiValued=1,
        allowed_types=('Attachment',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestAttachment',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ComputedWidget(
            visible={'edit': 'invisible',
                     'view': 'invisible',
                     },
        )
    ),
    ReferenceField(
        'Invoice',
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Invoice',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestInvoice',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ComputedWidget(
            visible={'edit': 'invisible',
                     'view': 'invisible',
                     },
        )
    ),
    DateTimeField(
        'DateReceived',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=DateTimeWidget(
            label = _("Date Received"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible', 'add': 'invisible'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'invisible'},
                     'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'invisible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'invisible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    DateTimeField(
        'DatePublished',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=DateTimeWidget(
            label = _("Date Published"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'invisible',
                     'secondary': 'invisible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible', 'add': 'invisible'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'invisible'},
                     'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'invisible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'invisible', 'edit': 'invisible'},
                     'attachment_due':    {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_verified':    {'view': 'invisible', 'edit': 'invisible'},
                     'verified':          {'view': 'invisible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
        ),
    ),
    TextField(
        'Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label = _("Remarks"),
            append_only=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'invisible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible', 'add': 'invisible'},
                     },
        ),
    ),
    FixedPointField(
        'MemberDiscount',
        default_method='getDefaultMemberDiscount',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=DecimalWidget(
            label = _("Member discount %"),
            description = _("Enter percentage value eg. 33.0"),
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'invisible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible', 'add': 'invisible'},
                     },
        ),
    ),
    ComputedField(
        'ClientUID',
        searchable=True,
        expression='here.aq_parent.UID()',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField(
        'SampleTypeTitle',
        searchable=True,
        expression="here.getSampleType().Title() if here.getSampleType() else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField(
        'SamplePointTitle',
        searchable=True,
        expression="here.getSamplePoint().Title() if here.getSamplePoint() else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField(
        'SampleUID',
        expression="here.getSample() and here.getSample().UID() or ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField(
        'SampleID',
        expression="here.getSample() and here.getSample().getId() or ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField(
        'ContactUID',
        expression="here.getContact() and here.getContact().UID() or ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField(
        'ProfilesUID',
        expression="here.getProfiles() and [profile.UID() for profile in here.getProfiles()] or []",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField(
        'Invoiced',
        expression='here.getInvoice() and True or False',
        default=False,
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ReferenceField(
        'ChildAnalysisRequest',
        allowed_types = ('AnalysisRequest',),
        relationship = 'AnalysisRequestChildAnalysisRequest',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            visible=False,
        ),
    ),
    ReferenceField(
        'ParentAnalysisRequest',
        allowed_types = ('AnalysisRequest',),
        relationship = 'AnalysisRequestParentAnalysisRequest',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            visible=False,
        ),
    ),
    HistoryAwareReferenceField(
        'Priority',
        allowed_types=('ARPriority',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestPriority',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label = _("Priority"),
            size=10,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'visible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            colModel=[
                {'columnName': 'Title', 'width': '30',
                 'label': _('Title'), 'align': 'left'},
                {'columnName': 'Description', 'width': '70',
                 'label': _('Description'), 'align': 'left'},
                {'columnName': 'sortKey', 'hidden': True},
                {'columnName': 'UID', 'hidden': True},
            ],
            sidx='sortKey',
            sord='asc',
            showOn=True,
        ),
    ),

    # For comments or results interpretation
    # Old one, to be removed because of the incorporation of
    # ResultsInterpretationDepts (due to LIMS-1628)
    TextField(
        'ResultsInterpretation',
        searchable=True,
        mode="rw",
        default_content_type = 'text/html',  # Input content type for the textfield
        default_output_type = 'text/x-html-safe',  # getResultsInterpretation returns a str with html tags
                                                   # to conserve the txt format in the report.
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=RichWidget (
            description = _("Comments or results interpretation"),
            label = _("Results Interpretation"),
            size=10,
            allow_file_upload=False,
            default_mime_type='text/x-rst',
            output_mime_type='text/x-html',
            rows=3,
            visible=False),
    ),
    RecordsField('ResultsInterpretationDepts',
        subfields = ('uid',
                     'richtext'),
        subfield_labels = {'uid': _('Department'),
                           'richtext': _('Results Interpreation'),},
        widget = RichWidget(visible=False),
    ),
    # Custom settings for the assigned analysis services
    # https://jira.bikalabs.com/browse/LIMS-1324
    # Fields:
    #   - uid: Analysis Service UID
    #   - hidden: True/False. Hide/Display in results reports
    RecordsField('AnalysisServicesSettings',
         required=0,
         subfields=('uid', 'hidden',),
         widget=ComputedWidget(visible=False),
    ),
)
)


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

class AnalysisRequest(BaseFolder):
    implements(IAnalysisRequest)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def getRequestID(self):
        """ Return the id as RequestID
        """
        return safe_unicode(self.getId()).encode('utf-8')

    def Title(self):
        """ Return the Request ID as title """
        return self.getRequestID()

    def Description(self):
        """ Return searchable data as Description """
        descr = " ".join((self.getRequestID(), self.aq_parent.Title()))
        return safe_unicode(descr).encode('utf-8')

    def getClient(self):
        if self.aq_parent.portal_type == 'Client':
            return self.aq_parent
        if self.aq_parent.portal_type == 'Batch':
            return self.aq_parent.getClient()

    def getClientPath(self):
        return "/".join(self.aq_parent.getPhysicalPath())

    def getClientTitle(self):
        return self.getClient().Title() if self.getClient() else ''

    def getContactTitle(self):
        return self.getContact().Title() if self.getContact() else ''

    def getProfilesTitle(self):
        return [profile.Title() for profile in self.getProfiles()]

    def getTemplateTitle(self):
        return self.getTemplate().Title() if self.getTemplate() else ''

    def setPublicationSpecification(self, value):
        "Never contains a value; this field is here for the UI."
        return None

    def getAnalysisCategory(self):
        proxies = self.getAnalyses(full_objects=True)
        value = []
        for proxy in proxies:
            val = proxy.getCategoryTitle()
            if val not in value:
                value.append(val)
        return value

    def getAnalysisService(self):
        proxies = self.getAnalyses(full_objects=True)
        value = []
        for proxy in proxies:
            val = proxy.getServiceTitle()
            if val not in value:
                value.append(val)
        return value

    def getAnalysts(self):
        proxies = self.getAnalyses(full_objects=True)
        value = []
        for proxy in proxies:
            val = proxy.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    def getBatch(self):
        # The parent type may be "Batch" during ar_add.
        # This function fills the hidden field in ar_add.pt
        if self.aq_parent.portal_type == 'Batch':
            return self.aq_parent
        else:
            return self.Schema()['Batch'].get(self)

    def getDefaultMemberDiscount(self):
        """ compute default member discount if it applies """
        if hasattr(self, 'getMemberDiscountApplies'):
            if self.getMemberDiscountApplies():
                plone = getSite()
                settings = plone.bika_setup
                return settings.getMemberDiscount()
            else:
                return "0.00"

    def setDefaultPriority(self):
        """ compute default priority """
        bsc = getToolByName(self, 'bika_setup_catalog')
        priorities = bsc(
            portal_type='ARPriority',
            )
        for brain in priorities:
            obj = brain.getObject()
            if obj.getIsDefault():
                self.setPriority(obj)
                return

        # priority is not a required field.  No default means...
        logging.info('Priority: no default priority found')
        return

    security.declareProtected(View, 'getResponsible')

    def getAnalysesNum(self):
        """ Return the amount of analyses verified/total in the current AR """
        verified = 0
        total = 0
        for analysis in self.getAnalyses():
            review_state = analysis.review_state
            if review_state in ['verified' ,'published']:
                verified += 1
            if review_state not in 'retracted':
                total += 1
        return verified,total

    def getResponsible(self):
        """ Return all manager info of responsible departments """
        managers = {}
        departments = []
        for analysis in self.objectValues('Analysis'):
            department = analysis.getService().getDepartment()
            if department is None:
                continue
            department_id = department.getId()
            if department_id in departments:
                continue
            departments.append(department_id)
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if manager_id not in managers:
                managers[manager_id] = {}
                managers[manager_id]['salutation'] = safe_unicode(manager.getSalutation())
                managers[manager_id]['name'] = safe_unicode(manager.getFullname())
                managers[manager_id]['email'] = safe_unicode(manager.getEmailAddress())
                managers[manager_id]['phone'] = safe_unicode(manager.getBusinessPhone())
                managers[manager_id]['job_title'] = safe_unicode(manager.getJobTitle())
                if manager.getSignature():
                    managers[manager_id]['signature'] = '%s/Signature' % manager.absolute_url()
                else:
                    managers[manager_id]['signature'] = False
                managers[manager_id]['departments'] = ''
            mngr_dept = managers[manager_id]['departments']
            if mngr_dept:
                mngr_dept += ', '
            mngr_dept += safe_unicode(department.Title())
            managers[manager_id]['departments'] = mngr_dept
        mngr_keys = managers.keys()
        mngr_info = {}
        mngr_info['ids'] = mngr_keys
        mngr_info['dict'] = managers

        return mngr_info

    security.declareProtected(View, 'getResponsible')

    def getManagers(self):
        """ Return all managers of responsible departments """
        manager_ids = []
        manager_list = []
        departments = []
        for analysis in self.objectValues('Analysis'):
            department = analysis.getService().getDepartment()
            if department is None:
                continue
            department_id = department.getId()
            if department_id in departments:
                continue
            departments.append(department_id)
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if not manager_id in manager_ids:
                manager_ids.append(manager_id)
                manager_list.append(manager)

        return manager_list

    security.declareProtected(View, 'getLate')

    def getLate(self):
        """ return True if any analyses are late """
        workflow = getToolByName(self, 'portal_workflow')
        review_state = workflow.getInfoFor(self, 'review_state', '')
        if review_state in ['to_be_sampled', 'to_be_preserved',
                            'sample_due', 'published']:
            return False

        for analysis in self.objectValues('Analysis'):
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state == 'published':
                continue
            calculation = analysis.getService().getCalculation()
            if not calculation \
                or (calculation and not calculation.getDependentServices()):
                resultdate = analysis.getResultCaptureDate()
                duedate = analysis.getDueDate()
                if (resultdate and resultdate > duedate) \
                    or (not resultdate and DateTime() > duedate):
                    return True
        return False

    security.declareProtected(View, 'getBillableItems')

    def getBillableItems(self):
        """
        The main purpose of this function is to obtain the analysis services and profiles from the analysis request
        whose prices are needed to quote the analysis request.
        If an analysis belongs to a profile, this analysis will only be included in the analyses list if the profile
        has disabled "Use Analysis Profile Price".
        :return: a tuple of two lists. The first one only contains analysis services not belonging to a profile
                 with active "Use Analysis Profile Price".
                 The second list contains the profiles with activated "Use Analysis Profile Price".
        """
        workflow = getToolByName(self, 'portal_workflow')
        # REMEMBER: Analysis != Analysis services
        analyses = []
        analysis_profiles = []
        to_be_billed = []
        # Getting all analysis request analyses
        for analysis in self.objectValues('Analysis'):
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state != 'not_requested':
                analyses.append(analysis)
        # Getting analysis request profiles
        for profile in self.getProfiles():
            # Getting the analysis profiles which has "Use Analysis Profile Price" enabled
            if profile.getUseAnalysisProfilePrice():
                analysis_profiles.append(profile)
            else:
                # we only need the analysis service keywords from these profiles
                to_be_billed += [service.getKeyword() for service in profile.getService()]
        # So far we have three arrays:
        #   - analyses: has all analyses (even if they are included inside a profile or not)
        #   - analysis_profiles: has the profiles with "Use Analysis Profile Price" enabled
        #   - to_be_quoted: has analysis services keywords from analysis profiles with "Use Analysis Profile Price"
        #     disabled
        # If a profile has its own price, we don't need their analises' prices, so we have to quit all
        # analysis belonging to that profile. But if another profile has the same analysis service but has
        # "Use Analysis Profile Price" disabled, the service must be included as billable.
        for profile in analysis_profiles:
            for analysis_service in profile.getService():
                for analysis in analyses:
                    if analysis_service.getKeyword() == analysis.getService().getKeyword() and \
                       analysis.getService().getKeyword() not in to_be_billed:
                        analyses.remove(analysis)
        return analyses, analysis_profiles

    def getServicesAndProfiles(self):
        """
        This function gets all analysis services and all profiles and removes the services belonging to a profile.
        :return: a tuple of three lists, where the first list contains the analyses and the second list the profiles.
                 The third contains the analyses objects used by the profiles.
        """
        # Getting requested analyses
        workflow = getToolByName(self, 'portal_workflow')
        analyses = []
        # profile_analyses contains the profile's analyses (analysis != service") objects to obtain
        # the correct price later
        profile_analyses = []
        for analysis in self.objectValues('Analysis'):
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state != 'not_requested':
                analyses.append(analysis)
        # Getting all profiles
        analysis_profiles = self.getProfiles() if len(self.getProfiles()) > 0 else []
        # Cleaning services included in profiles
        for profile in analysis_profiles:
            for analysis_service in profile.getService():
                for analysis in analyses:
                    if analysis_service.getKeyword() == analysis.getService().getKeyword():
                        analyses.remove(analysis)
                        profile_analyses.append(analysis)
        return analyses, analysis_profiles, profile_analyses

    security.declareProtected(View, 'getSubtotal')

    def getSubtotal(self):
        """ Compute Subtotal (without member discount and without vat)
        """
        analyses, a_profiles = self.getBillableItems()
        return sum(
            [Decimal(obj.getPrice()) for obj in analyses] +
            [Decimal(obj.getAnalysisProfilePrice()) for obj in a_profiles]
        )

    security.declareProtected(View, 'getSubtotalVATAmount')

    def getSubtotalVATAmount(self):
        """ Compute VAT amount without member discount"""
        analyses, a_profiles = self.getBillableItems()
        if len(analyses) > 0 or len(a_profiles) > 0:
            return sum(
                [Decimal(o.getVATAmount()) for o in analyses] +
                [Decimal(o.getVATAmount()) for o in a_profiles]
            )
        return 0

    security.declareProtected(View, 'getSubtotalTotalPrice')

    def getSubtotalTotalPrice(self):
        """ Compute the price with VAT but no member discount"""
        return self.getSubtotal() + self.getSubtotalVATAmount()

    security.declareProtected(View, 'getDiscountAmount')

    def getDiscountAmount(self):
        """
        It computes and returns the analysis service's discount amount without VAT
        """
        has_client_discount = self.aq_parent.getMemberDiscountApplies()
        if has_client_discount:
            discount = Decimal(self.getDefaultMemberDiscount())
            return Decimal(self.getSubtotal() * discount / 100)
        else:
            return 0

    def getVATAmount(self):
        """
        It computes the VAT amount from (subtotal-discount.)*VAT/100, but each analysis has its
        own VAT!
        :return: the analysis request VAT amount with the discount
        """
        has_client_discount = self.aq_parent.getMemberDiscountApplies()
        VATAmount = self.getSubtotalVATAmount()
        if has_client_discount:
            discount = Decimal(self.getDefaultMemberDiscount())
            return Decimal((1 - discount/100) * VATAmount)
        else:
            return VATAmount

    security.declareProtected(View, 'getTotalPrice')

    def getTotalPrice(self):
        """
        It gets the discounted price from analyses and profiles to obtain the total value with the VAT
        and the discount applied
        :return: the analysis request's total price including the VATs and discounts
        """
        return self.getSubtotal() - self.getDiscountAmount() + self.getVATAmount()
    getTotal = getTotalPrice

    security.declareProtected(ManageInvoices, 'issueInvoice')

    def issueInvoice(self, REQUEST=None, RESPONSE=None):
        """ issue invoice
        """
        # check for an adhoc invoice batch for this month
        now = DateTime()
        batch_month = now.strftime('%b %Y')
        batch_title = '%s - %s' % (batch_month, 'ad hoc')
        invoice_batch = None
        for b_proxy in self.portal_catalog(portal_type='InvoiceBatch',
                                           Title=batch_title):
            invoice_batch = b_proxy.getObject()
        if not invoice_batch:
            first_day = DateTime(now.year(), now.month(), 1)
            start_of_month = first_day.earliestTime()
            last_day = first_day + 31
            while last_day.month() != now.month():
                last_day = last_day - 1
            end_of_month = last_day.latestTime()

            invoices = self.invoices
            batch_id = invoices.generateUniqueId('InvoiceBatch')
            invoice_batch = _createObjectByType("InvoiceBatch", invoices, batch_id)
            invoice_batch.edit(
                title=batch_title,
                BatchStartDate=start_of_month,
                BatchEndDate=end_of_month,
            )
            invoice_batch.processForm()

        client_uid = self.getClientUID()
        # Get the created invoice
        invoice = invoice_batch.createInvoice(client_uid, [self, ])
        invoice.setAnalysisRequest(self)
        # Set the created invoice in the schema
        self.Schema()['Invoice'].set(self, invoice)

    security.declarePublic('printInvoice')
    def printInvoice(self, REQUEST=None, RESPONSE=None):
        """ print invoice
        """
        invoice = self.getInvoice()
        invoice_url = invoice.absolute_url()
        RESPONSE.redirect('%s/invoice_print' % invoice_url)

    def addARAttachment(self, REQUEST=None, RESPONSE=None):
        """ Add the file as an attachment
        """
        workflow = getToolByName(self, 'portal_workflow')

        this_file = self.REQUEST.form['AttachmentFile_file']
        if 'Analysis' in self.REQUEST.form:
            analysis_uid = self.REQUEST.form['Analysis']
        else:
            analysis_uid = None

        attachmentid = self.generateUniqueId('Attachment')
        attachment = _createObjectByType("Attachment", self.aq_parent,
                                         attachmentid)
        attachment.edit(
            AttachmentFile=this_file,
            AttachmentType=self.REQUEST.form.get('AttachmentType', ''),
            AttachmentKeys=self.REQUEST.form['AttachmentKeys'])
        attachment.processForm()
        attachment.reindexObject()

        if analysis_uid:
            tool = getToolByName(self, REFERENCE_CATALOG)
            analysis = tool.lookupObject(analysis_uid)
            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)
            if workflow.getInfoFor(analysis, 'review_state') == 'attachment_due':
                workflow.doActionFor(analysis, 'attach')
        else:
            others = self.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())

            self.setAttachment(attachments)

        if REQUEST['HTTP_REFERER'].endswith('manage_results'):
            RESPONSE.redirect('%s/manage_results' % self.absolute_url())
        else:
            RESPONSE.redirect(self.absolute_url())

    def delARAttachment(self, REQUEST=None, RESPONSE=None):
        """ delete the attachment """
        tool = getToolByName(self, REFERENCE_CATALOG)
        if 'Attachment' in self.REQUEST.form:
            attachment_uid = self.REQUEST.form['Attachment']
            attachment = tool.lookupObject(attachment_uid)
            parent_r = attachment.getRequest()
            parent_a = attachment.getAnalysis()

        parent = parent_a if parent_a else parent_r
        others = parent.getAttachment()
        attachments = []
        for other in others:
            if not other.UID() == attachment_uid:
                attachments.append(other.UID())
        parent.setAttachment(attachments)
        client = attachment.aq_parent
        ids = [attachment.getId(), ]
        BaseFolder.manage_delObjects(client, ids, REQUEST)

        RESPONSE.redirect(self.REQUEST.get_header('referer'))

    security.declarePublic('getVerifier')

    def getVerifier(self):
        wtool = getToolByName(self, 'portal_workflow')
        mtool = getToolByName(self, 'portal_membership')

        verifier = None
        try:
            review_history = wtool.getInfoFor(self, 'review_history')
        except:
            return 'access denied'

        if not review_history:
            return 'no history'
        for items in review_history:
            action = items.get('action')
            if action != 'verify':
                continue
            actor = items.get('actor')
            member = mtool.getMemberById(actor)
            verifier = member.getProperty('fullname')
            if verifier is None or verifier == '':
                verifier = actor
        return verifier

    security.declarePublic('getContactUIDForUser')

    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        pc = getToolByName(self, 'portal_catalog')
        r = pc(portal_type='Contact',
               getUsername=user_id)
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    def getQCAnalyses(self, qctype=None, review_state=None):
        """ return the QC analyses performed in the worksheet in which, at
            least, one sample of this AR is present.
            Depending on qctype value, returns the analyses of:
            - 'b': all Blank Reference Samples used in related worksheet/s
            - 'c': all Control Reference Samples used in related worksheet/s
            - 'd': duplicates only for samples contained in this AR
            If qctype==None, returns all type of qc analyses mentioned above
        """
        qcanalyses = []
        suids = []
        ans = self.getAnalyses()
        wf = getToolByName(self, 'portal_workflow')
        for an in ans:
            an = an.getObject()
            if an.getServiceUID() not in suids:
                suids.append(an.getServiceUID())

        for an in ans:
            an = an.getObject()
            br = an.getBackReferences('WorksheetAnalysis')
            if (len(br) > 0):
                ws = br[0]
                was = ws.getAnalyses()
                for wa in was:
                    if wa.portal_type == 'DuplicateAnalysis' \
                        and wa.getRequestID() == self.id \
                        and wa not in qcanalyses \
                            and (qctype is None or wa.getReferenceType() == qctype) \
                            and (review_state is None or wf.getInfoFor(wa, 'review_state') in review_state):
                        qcanalyses.append(wa)

                    elif wa.portal_type == 'ReferenceAnalysis' \
                        and wa.getServiceUID() in suids \
                        and wa not in qcanalyses \
                            and (qctype is None or wa.getReferenceType() == qctype) \
                            and (review_state is None or wf.getInfoFor(wa, 'review_state') in review_state):
                        qcanalyses.append(wa)

        return qcanalyses

    def isInvalid(self):
        """ return if the Analysis Request has been invalidated
        """
        workflow = getToolByName(self, 'portal_workflow')
        return workflow.getInfoFor(self, 'review_state') == 'invalid'

    def getLastChild(self):
        """ return the last child Request due to invalidation
        """
        child = self.getChildAnalysisRequest()
        while (child and child.getChildAnalysisRequest()):
            child = child.getChildAnalysisRequest()
        return child

    def getRequestedAnalyses(self):
        """
        It returns all requested analyses, even if they belong to an analysis profile or not.
        """
        #
        # title=Get requested analyses
        #
        result = []
        cats = {}
        workflow = getToolByName(self, 'portal_workflow')
        for analysis in self.getAnalyses(full_objects=True):
            review_state = workflow.getInfoFor(analysis, 'review_state')
            if review_state == 'not_requested':
                continue
            service = analysis.getService()
            category_name = service.getCategoryTitle()
            if not category_name in cats:
                cats[category_name] = {}
            cats[category_name][analysis.Title()] = analysis
        cat_keys = cats.keys()
        cat_keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
        for cat_key in cat_keys:
            analyses = cats[cat_key]
            analysis_keys = analyses.keys()
            analysis_keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
            for analysis_key in analysis_keys:
                result.append(analyses[analysis_key])
        return result

    def getSamplingRoundUID(self):
        """
        Obtains the sampling round UID
        :return: a UID
        """
        if self.getSamplingRound():
            return self.getSamplingRound().UID()
        else:
            return ''

    def setResultsRange(self, value=None):
        """Sets the spec values for this AR.
        1 - Client specs where (spec.Title) matches (ar.SampleType.Title)
        2 - Lab specs where (spec.Title) matches (ar.SampleType.Title)
        3 - Take override values from instance.Specification
        4 - Take override values from the form (passed here as parameter 'value').

        The underlying field value is a list of dictionaries.

        The value parameter may be a list of dictionaries, or a dictionary (of
        dictionaries).  In the last case, the keys are irrelevant, but in both
        cases the specs must contain, at minimum, the "keyword", "min", "max",
        and "error" fields.

        Value will be stored in ResultsRange field as list of dictionaries
        """
        rr = {}
        sample = self.getSample()
        if not sample:
            # portal_factory
            return []
        stt = self.getSample().getSampleType().Title()
        bsc = getToolByName(self, 'bika_setup_catalog')
        # 1 or 2: rr = Client specs where (spec.Title) matches (ar.SampleType.Title)
        for folder in self.aq_parent, self.bika_setup.bika_analysisspecs:
            proxies = bsc(portal_type='AnalysisSpec',
                          getSampleTypeTitle=stt,
                          ClientUID=folder.UID())
            if proxies:
                rr = dicts_to_dict(proxies[0].getObject().getResultsRange(), 'keyword')
                break
        # 3: rr += override values from instance.Specification
        ar_spec = self.getSpecification()
        if ar_spec:
            ar_spec_rr = ar_spec.getResultsRange()
            rr.update(dicts_to_dict(ar_spec_rr, 'keyword'))
        # 4: rr += override values from the form (value=dict key=service_uid)
        if value:
            if type(value) in (list, tuple):
                value = dicts_to_dict(value, "keyword")
            elif type(value) == dict:
                value = dicts_to_dict(value.values(), "keyword")
            rr.update(value)
        return self.Schema()['ResultsRange'].set(self, rr.values())

    # Then a string of fields which are defined on the AR, but need to be set
    # and read from the sample

    security.declarePublic('setSamplingDate')

    def setSamplingDate(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSamplingDate(value)

    security.declarePublic('getSamplingDate')

    def getSamplingDate(self):
        sample = self.getSample()
        if sample:
            return sample.getSamplingDate()

    security.declarePublic('setSampler')

    def setSampler(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSampler(value)
        self.Schema()['Sampler'].set(self, value)

    security.declarePublic('getSampler')

    def getSampler(self):
        sample = self.getSample()
        if sample:
            return sample.getSampler()
        return self.Schema().getField('Sampler').get(self)

    security.declarePublic('setDateSampled')

    def setDateSampled(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setDateSampled(value)
        self.Schema()['DateSampled'].set(self, value)

    security.declarePublic('getDateSampled')

    def getDateSampled(self):
        sample = self.getSample()
        if sample:
            return sample.getDateSampled()
        return self.Schema().getField('DateSampled').get(self)

    security.declarePublic('setSamplePoint')

    def setSamplePoint(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSamplePoint(value)
        self.Schema()['SamplePoint'].set(self, value)

    security.declarePublic('getSamplepoint')

    def getSamplePoint(self):
        sample = self.getSample()
        if sample:
            return sample.getSamplePoint()
        return self.Schema().getField('SamplePoint').get(self)

    security.declarePublic('setSampleType')

    def setSampleType(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSampleType(value)
        self.Schema()['SampleType'].set(self, value)

    security.declarePublic('getSampleType')

    def getSampleType(self):
        sample = self.getSample()
        if sample:
            return sample.getSampleType()
        return self.Schema().getField('SampleType').get(self)

    security.declarePublic('setClientReference')

    def setClientReference(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setClientReference(value)
        self.Schema()['ClientReference'].set(self, value)

    security.declarePublic('getClientReference')

    def getClientReference(self):
        sample = self.getSample()
        if sample:
            return sample.getClientReference()
        return self.Schema().getField('ClientReference').get(self)

    security.declarePublic('setClientSampleID')

    def setClientSampleID(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setClientSampleID(value)
        self.Schema()['ClientSampleID'].set(self, value)

    security.declarePublic('getClientSampleID')

    def getClientSampleID(self):
        sample = self.getSample()
        if sample:
            return sample.getClientSampleID()
        return self.Schema().getField('ClientSampleID').get(self)

    security.declarePublic('setSamplingDeviation')

    def setSamplingDeviation(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSamplingDeviation(value)
        self.Schema()['SamplingDeviation'].set(self, value)

    security.declarePublic('getSamplingDeviation')

    def getSamplingDeviation(self):
        sample = self.getSample()
        if sample:
            return sample.getSamplingDeviation()
        return self.Schema().getField('SamplingDeviation').get(self)

    security.declarePublic('setSampleCondition')

    def setSampleCondition(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setSampleCondition(value)
        self.Schema()['SampleCondition'].set(self, value)

    security.declarePublic('getSampleCondition')

    def getSampleCondition(self):
        sample = self.getSample()
        if sample:
            return sample.getSampleCondition()
        return self.Schema().getField('SampleCondition').get(self)

    security.declarePublic('setEnvironmentalConditions')

    def setEnvironmentalConditions(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setEnvironmentalConditions(value)
        self.Schema()['EnvironmentalConditions'].set(self, value)

    security.declarePublic('getEnvironmentalConditions')

    def getEnvironmentalConditions(self):
        sample = self.getSample()
        if sample:
            return sample.getEnvironmentalConditions()
        return self.Schema().getField('EnvironmentalConditions').get(self)

    security.declarePublic('setComposite')

    def setComposite(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setComposite(value)
        self.Schema()['Composite'].set(self, value)

    security.declarePublic('getComposite')

    def getComposite(self):
        sample = self.getSample()
        if sample:
            return sample.getComposite()
        return self.Schema().getField('Composite').get(self)

    security.declarePublic('setStorageLocation')

    def setStorageLocation(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setStorageLocation(value)
        self.Schema()['StorageLocation'].set(self, value)

    security.declarePublic('getStorageLocation')

    def getStorageLocation(self):
        sample = self.getSample()
        if sample:
            return sample.getStorageLocation()
        return self.Schema().getField('StorageLocation').get(self)

    security.declarePublic('setAdHoc')

    def setAdHoc(self, value):
        sample = self.getSample()
        if sample and value:
            sample.setAdHoc(value)
        self.Schema()['AdHoc'].set(self, value)

    security.declarePublic('getAdHoc')

    def getAdHoc(self):
        sample = self.getSample()
        if sample:
            return sample.getAdHoc()
        return self.Schema().getField('AdHoc').get(self)

    def getSamplers(self):
        return getUsers(self, ['LabManager', 'Sampler'])

    def getDepartments(self):
        """ Returns a set with the departments assigned to the Analyses
            from this Analysis Request
        """
        ans = [an.getObject() for an in self.getAnalyses()]
        depts = [an.getService().getDepartment() for an in ans if an.getService().getDepartment()]
        return set(depts)

    def getResultsInterpretationByDepartment(self, department=None):
        """ Returns the results interpretation for this Analysis Request
            and department. If department not set, returns the results
            interpretation tagged as 'General'.

            Returns a dict with the following keys:
            {'uid': <department_uid> or 'general',
             'richtext': <text/plain>}
        """
        uid = department.UID() if department else 'general'
        rows = self.Schema()['ResultsInterpretationDepts'].get(self)
        row = [row for row in rows if row.get('uid') == uid]
        if len(row) > 0:
            row = row[0]
        elif uid=='general' \
            and hasattr(self, 'getResultsInterpretation') \
            and self.getResultsInterpretation():
            row = {'uid': uid, 'richtext': self.getResultsInterpretation()}
        else:
            row = {'uid': uid, 'richtext': ''};
        return row

    def getAnalysisServiceSettings(self, uid):
        """ Returns a dictionary with the settings for the analysis
            service that match with the uid provided.
            If there are no settings for the analysis service and
            analysis requests:
            1. looks for settings in AR's ARTemplate. If found, returns
                the settings for the AnalysisService set in the Template
            2. If no settings found, looks in AR's ARProfile. If found,
                returns the settings for the AnalysisService from the
                AR Profile. Otherwise, returns a one entry dictionary
                with only the key 'uid'
        """
        sets = [s for s in self.getAnalysisServicesSettings() \
                if s.get('uid','') == uid]

        # Created by using an ARTemplate?
        if not sets and self.getTemplate():
            adv = self.getTemplate().getAnalysisServiceSettings(uid)
            sets = [adv] if 'hidden' in adv else []

        # Created by using an AR Profile?
        if not sets and self.getProfiles():
            adv = []
            adv += [profile.getAnalysisServiceSettings(uid) for profile in self.getProfiles()]
            sets = adv if 'hidden' in adv[0] else []

        return sets[0] if sets else {'uid': uid}

    def getPartitions(self):
        """
        This functions returns the partitions from the analysis request's analyses.
        :return: a list with the full partition objects
        """
        analyses = self.getRequestedAnalyses()
        partitions = []
        for analysis in analyses:
            if analysis.getSamplePartition() not in partitions:
                partitions.append(analysis.getSamplePartition())
        return partitions

    def getContainers(self):
        """
        This functions returns the containers from the analysis request's analyses
        :return: a list with the full partition objects
        """
        partitions = self.getPartitions()
        containers = []
        for partition in partitions:
            if partition.getContainer():
                containers.append(partition.getContainer())
        return containers

    def isAnalysisServiceHidden(self, uid):
        """ Checks if the analysis service that match with the uid
            provided must be hidden in results.
            If no hidden assignment has been set for the analysis in
            this request, returns the visibility set to the analysis
            itself.
            Raise a TypeError if the uid is empty or None
            Raise a ValueError if there is no hidden assignment in this
                request or no analysis service found for this uid.
        """
        if not uid:
            raise TypeError('None type or empty uid')
        sets = self.getAnalysisServiceSettings(uid)
        if 'hidden' not in sets:
            uc = getToolByName(self, 'uid_catalog')
            serv = uc(UID=uid)
            if serv and len(serv) == 1:
                return serv[0].getObject().getRawHidden()
            else:
                raise ValueError('%s is not valid' % uid)
        return sets.get('hidden', False)

    def guard_unassign_transition(self):
        """Allow or disallow transition depending on our children's states
        """
        if not isBasicTransitionAllowed(self):
            return False
        if self.getAnalyses(worksheetanalysis_review_state='unassigned'):
            return True
        if not self.getAnalyses(worksheetanalysis_review_state='assigned'):
            return True
        return False

    def guard_assign_transition(self):
        """Allow or disallow transition depending on our children's states
        """
        if not isBasicTransitionAllowed(self):
            return False
        if not self.getAnalyses(worksheetanalysis_review_state='assigned'):
            return False
        if self.getAnalyses(worksheetanalysis_review_state='unassigned'):
            return False
        return True

    def guard_receive_transition(self):
        """Prevent the receive transition from being available:
        - if object is cancelled
        - if any related ARs have field analyses with no result.
        """
        if not isBasicTransitionAllowed(self):
            return False
        # check if any related ARs have field analyses with no result.
        for ar in self.getSample().getAnalysisRequests():
            field_analyses = ar.getAnalyses(getPointOfCapture='field',
                                            full_objects=True)
            no_results = [a for a in field_analyses if a.getResult() == '']
            if no_results:
                return False
        return True

    def workflow_script_receive(self):
        if skip(self, "receive"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.setDateReceived(DateTime())
        self.reindexObject(idxs=["review_state", "getDateReceived", ])
        # receive the AR's sample
        sample = self.getSample()
        if not skip(sample, 'receive', peek=True):
            # unless this is a secondary AR
            if workflow.getInfoFor(sample, 'review_state') == 'sample_due':
                workflow.doActionFor(sample, 'receive')
        # receive all analyses in this AR.
        analyses = self.getAnalyses(review_state='sample_due')
        for analysis in analyses:
            if not skip(analysis, 'receive'):
                workflow.doActionFor(analysis.getObject(), 'receive')

    def workflow_script_preserve(self):
        if skip(self, "preserve"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        # transition our sample
        sample = self.getSample()
        if not skip(sample, "preserve", peek=True):
            workflow.doActionFor(sample, "preserve")

    def workflow_script_submit(self):
        if skip(self, "submit"):
            return
        self.reindexObject(idxs=["review_state", ])

    def workflow_script_sampling_workflow(self):
        if skip(self, "sampling_workflow"):
            return
        sample = self.getSample()
        if sample.getSamplingDate() > DateTime():
            sample.future_dated = True

    def workflow_script_no_sampling_workflow(self):
        if skip(self, "no_sampling_workflow"):
            return
        sample = self.getSample()
        if sample.getSamplingDate() > DateTime():
            sample.future_dated = True

    def workflow_script_attach(self):
        if skip(self, "attach"):
            return
        self.reindexObject(idxs=["review_state", ])
        # Don't cascade. Shouldn't be attaching ARs for now (if ever).
        return

    def workflow_script_sample(self):
        # no skip check here: the sampling workflow UI is odd
        # if skip(self, "sample"):
        #     return
        # transition our sample
        workflow = getToolByName(self, 'portal_workflow')
        sample = self.getSample()
        if not skip(sample, "sample", peek=True):
            workflow.doActionFor(sample, "sample")

    # def workflow_script_to_be_preserved(self):
    #     if skip(self, "to_be_preserved"):
    #         return
    #     pass

    # def workflow_script_sample_due(self):
    #     if skip(self, "sample_due"):
    #         return
    #     pass

    # def workflow_script_retract(self):
    #     if skip(self, "retract"):
    #         return
    #     pass

    def workflow_script_verify(self):
        if skip(self, "verify"):
            return
        self.reindexObject(idxs=["review_state", ])
        if not "verify all analyses" in self.REQUEST['workflow_skiplist']:
            # verify all analyses in this AR.
            analyses = self.getAnalyses(review_state='to_be_verified')
            for analysis in analyses:
                doActionFor(analysis.getObject(), "verify")

    def workflow_script_publish(self):
        if skip(self, "publish"):
            return
        self.reindexObject(idxs=["review_state", "getDatePublished", ])
        if not "publish all analyses" in self.REQUEST['workflow_skiplist']:
            # publish all analyses in this AR. (except not requested ones)
            analyses = self.getAnalyses(review_state='verified')
            for analysis in analyses:
                doActionFor(analysis.getObject(), "publish")

    def workflow_script_reinstate(self):
        if skip(self, "reinstate"):
            return
        self.reindexObject(idxs=["cancellation_state", ])
        # activate all analyses in this AR.
        analyses = self.getAnalyses(cancellation_state='cancelled')
        for analysis in analyses:
            doActionFor(analysis.getObject(), 'reinstate')

    def workflow_script_cancel(self):
        if skip(self, "cancel"):
            return
        self.reindexObject(idxs=["cancellation_state", ])
        # deactivate all analyses in this AR.
        analyses = self.getAnalyses(cancellation_state='active')
        for analysis in analyses:
            doActionFor(analysis.getObject(), 'cancel')


atapi.registerType(AnalysisRequest, PROJECTNAME)

