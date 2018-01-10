# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""Sample represents a physical sample submitted for testing
"""
from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims import bikaMessageFactory as _, logger
from bika.lims.api import get_object_by_uid
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.utils import t, getUsers
from Products.ATExtensions.field import RecordsField
from bika.lims import deprecated
from bika.lims.browser.widgets.datetimewidget import DateTimeWidget
from bika.lims.browser.widgets import RejectionWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ISample, ISamplePrepWorkflow
from bika.lims.permissions import SampleSample
from bika.lims.permissions import ScheduleSampling
from bika.lims.workflow import doActionFor
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import isTransitionAllowed
from bika.lims.workflow import skip
from bika.lims.workflow.sample import guards
from bika.lims.workflow.sample import events
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.public import DisplayList
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt, dt2DT
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget

import sys
from bika.lims.utils import to_unicode

schema = BikaSchema.copy() + Schema((
    StringField('SampleID',
        required=1,
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Sample ID"),
            description=_("The ID assigned to the client's sample by the lab"),
            visible={'edit': 'invisible',
                     'view': 'invisible'},
            render_own_label=True,
        ),
    ),
    StringField('ClientReference',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Client Reference"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    StringField('ClientSampleID',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Client SID"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    ReferenceField('LinkedSample',
        vocabulary_display_path_bound=sys.maxsize,
        multiValue=1,
        allowed_types=('Sample',),
        relationship='SampleSample',
        referenceClass=HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Linked Sample"),
        ),
    ),
    ReferenceField('SampleType',
        required=1,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('SampleType',),
        relationship='SampleSampleType',
        referenceClass=HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Sample Type"),
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ComputedField('SampleTypeTitle',
        expression="here.getSampleType() and here.getSampleType().Title() or ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ReferenceField('SamplePoint',
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('SamplePoint',),
        relationship = 'SampleSamplePoint',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Sample Point"),
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ComputedField('SamplePointTitle',
        expression = "here.getSamplePoint() and here.getSamplePoint().Title() or ''",
        widget = ComputedWidget(
            visible=False,
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
            label=_("Storage Location"),
            description=_("Location where sample is kept"),
            size=20,
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'expired':           {'view': 'visible', 'edit': 'visible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    BooleanField('SamplingWorkflowEnabled',
                 default_method='getSamplingWorkflowEnabledDefault'
    ),
    DateTimeField('DateSampled',
        mode="rw",
        read_permission=permissions.View,
        write_permission=SampleSample,
        widget = DateTimeWidget(
            label=_("Date Sampled"),
            show_time=True,
            size=20,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    StringField('Sampler',
        mode="rw",
        read_permission=permissions.View,
        write_permission=SampleSample,
        vocabulary='getSamplers',
        widget=BikaSelectionWidget(
            format='select',
            label=_("Sampler"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'visible'}
                     },
            render_own_label=True,
        ),
    ),
    StringField('ScheduledSamplingSampler',
        mode="rw",
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
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    DateTimeField('SamplingDate',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label=_("Expected Sampling Date"),
            description=_("Define when the sampler has to take the samples"),
            show_time=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    StringField('PreparationWorkflow',
        mode="rw",
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
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    ReferenceField('SamplingDeviation',
        vocabulary_display_path_bound = sys.maxsize,
        allowed_types = ('SamplingDeviation',),
        relationship = 'SampleSamplingDeviation',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Sampling Deviation"),
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),
    ReferenceField('SampleCondition',
        vocabulary_display_path_bound = sys.maxsize,
        allowed_types = ('SampleCondition',),
        relationship = 'SampleSampleCondition',
        referenceClass = HoldingReference,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Sample Condition"),
            render_own_label=True,
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
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
            label=_("Environmental Conditions"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'add': 'edit',
                     'header_table': 'prominent',
                     'sample_registered': {'view': 'visible', 'edit': 'visible', 'add': 'edit'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'attachment_due':    {'view': 'visible', 'edit': 'visible'},
                     'to_be_verified':    {'view': 'visible', 'edit': 'visible'},
                     'verified':          {'view': 'visible', 'edit': 'invisible'},
                     'published':         {'view': 'visible', 'edit': 'invisible'},
                     'invalid':           {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
            size=20,
        ),
    ),
    # Another way to obtain a transition date is using getTransitionDate
    # function. We are using a DateTimeField/Widget here because in some
    # cases the user may want to change the Received Date.
    # AnalysisRequest and Sample's DateReceived fields needn't to have
    # the same value.
    # This field is updated in workflow_script_receive method.
    DateTimeField('DateReceived',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label=_("Date Received"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'invisible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'invisible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    ComputedField('ClientUID',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible=False,
        ),
    ),
    ComputedField('SampleTypeUID',
                  expression='context.getSampleType() and \
                             context.getSampleType().UID() or None',
                  widget=ComputedWidget(
                    visible=False,
                  ),
    ),
    ComputedField('SamplePointUID',
        expression = 'context.getSamplePoint() and context.getSamplePoint().UID() or None',
        widget = ComputedWidget(
            visible=False,
        ),
    ),
    BooleanField('Composite',
        default = False,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = BooleanWidget(
            label=_("Composite"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    DateTimeField('DateExpired',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label=_("Date Expired"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'invisible'},
                     'scheduled_sampling': {'view': 'invisible', 'edit': 'invisible'},
                     'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'invisible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'invisible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'invisible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    ComputedField('DisposalDate',
        expression = 'context.disposal_date()',
        widget=DateTimeWidget(
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'invisible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'invisible'},
                     'sampled':           {'view': 'visible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'visible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'visible', 'edit': 'invisible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'invisible', 'edit': 'invisible'},
                     'rejected':          {'view': 'invisible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    DateTimeField('DateDisposed',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label=_("Date Disposed"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_sampled':     {'view': 'invisible', 'edit': 'invisible'},
                     'scheduled_sampling': {'view': 'invisible', 'edit': 'invisible'},
                     'sampled':           {'view': 'invisible', 'edit': 'invisible'},
                     'to_be_preserved':   {'view': 'invisible', 'edit': 'invisible'},
                     'sample_due':        {'view': 'invisible', 'edit': 'invisible'},
                     'sample_received':   {'view': 'invisible', 'edit': 'invisible'},
                     'expired':           {'view': 'invisible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'invisible', 'edit': 'invisible'},
                     },
            render_own_label=True,
        ),
    ),
    BooleanField('AdHoc',
        default=False,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=BooleanWidget(
            label=_("Ad-Hoc"),
            visible={'edit': 'visible',
                     'view': 'visible',
                     'header_table': 'visible',
                     'sample_registered': {'view': 'visible', 'edit': 'visible'},
                     'to_be_sampled':     {'view': 'visible', 'edit': 'visible'},
                     'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                     'sampled':           {'view': 'visible', 'edit': 'visible'},
                     'to_be_preserved':   {'view': 'visible', 'edit': 'visible'},
                     'sample_due':        {'view': 'visible', 'edit': 'visible'},
                     'sample_received':   {'view': 'visible', 'edit': 'visible'},
                     'expired':           {'view': 'visible', 'edit': 'invisible'},
                     'disposed':          {'view': 'visible', 'edit': 'invisible'},
                     'rejected':          {'view': 'visible', 'edit': 'invisible'},
                     },
           render_own_label=True,
        ),
    ),
    TextField('Remarks',
        default_content_type='text/x-web-intelligent',
        allowable_content_types = ('text/plain', ),
        default_output_type="text/plain",
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Remarks"),
            append_only=True,
        ),
    ),
    RecordsField('RejectionReasons',
        widget = RejectionWidget(
            label=_("Sample Rejection"),
            description = _("Set the Sample Rejection workflow and the reasons"),
            render_own_label=False,
            visible={'edit': 'invisible',
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
                     'published':         {'view': 'visible', 'edit': 'visible'},
                     'invalid':           {'view': 'visible', 'edit': 'visible'},
                     'rejected':          {'view': 'visible', 'edit': 'visible'},
                     },
        ),
    ),
))


schema['title'].required = False


class Sample(BaseFolder, HistoryAwareMixin):
    implements(ISample, ISamplePrepWorkflow)
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

    def getSampleID(self):
        """ Return the Sample ID as title """
        return safe_unicode(self.getId()).encode('utf-8')

    def Title(self):
        """ Return the Sample ID as title """
        return self.getSampleID()

    def getSamplingWorkflowEnabledDefault(self):
        return self.bika_setup.getSamplingWorkflowEnabled()

    def getContactTitle(self):
        return ""

    def getClientTitle(self):
        proxies = self.getAnalysisRequests()
        if not proxies:
            return ""
        value = proxies[0].aq_parent.Title()
        return value

    def getProfilesTitle(self):
        return ""

    def getAnalysisService(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.Title()
            if val not in value:
                value.append(val)
        return value

    def getAnalysts(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    # Forms submit Title Strings which need
    # to be converted to objects somewhere along the way...
    def setSampleType(self, value, **kw):
        """ Accept Object, Title or UID, and convert SampleType title to UID
        before saving.
        """
        if hasattr(value, "portal_type") and value.portal_type == "SampleType":
            pass
        else:
            bsc = getToolByName(self, 'bika_setup_catalog')
            sampletypes = bsc(portal_type='SampleType', title=to_unicode(value))
            if sampletypes:
                value = sampletypes[0].UID
            else:
                sampletypes = bsc(portal_type='SampleType', UID=value)
                if sampletypes:
                    value = sampletypes[0].UID
                else:
                    value = None
        for ar in self.getAnalysisRequests():
            ar.Schema()['SampleType'].set(ar, value)
        return self.Schema()['SampleType'].set(self, value)

    # Forms submit Title Strings which need
    # to be converted to objects somewhere along the way...
    def setSamplePoint(self, value, **kw):
        """ Accept Object, Title or UID, and convert SampleType title to UID
        before saving.
        """
        if hasattr(value, "portal_type") and value.portal_type == "SamplePoint":
            pass
        elif value:
            bsc = getToolByName(self, 'bika_setup_catalog')
            sampletypes = bsc(portal_type='SamplePoint', title=to_unicode(value))
            if sampletypes:
                value = sampletypes[0].UID
            else:
                sampletypes = bsc(portal_type='SamplePoint', UID=value)
                if sampletypes:
                    value = sampletypes[0].UID
                else:
                    value = None
        for ar in self.getAnalysisRequests():
            ar.Schema()['SamplePoint'].set(ar, value)
        return self.Schema()['SamplePoint'].set(self, value)

    def setClientReference(self, value, **kw):
        """ Set the field on Analysis Requests.
        """
        for ar in self.getAnalysisRequests():
            ar.Schema()['ClientReference'].set(ar, value)
        self.Schema()['ClientReference'].set(self, value)

    def setClientSampleID(self, value, **kw):
        """ Set the field on Analysis Requests.
        """
        for ar in self.getAnalysisRequests():
            ar.Schema()['ClientSampleID'].set(ar, value)
        self.Schema()['ClientSampleID'].set(self, value)

    def setAdHoc(self, value, **kw):
        """ Set the field on Analysis Requests.
        """
        for ar in self.getAnalysisRequests():
            ar.Schema()['AdHoc'].set(ar, value)
        self.Schema()['AdHoc'].set(self, value)

    def setComposite(self, value, **kw):
        """ Set the field on Analysis Requests.
        """
        for ar in self.getAnalysisRequests():
            ar.Schema()['Composite'].set(ar, value)
        self.Schema()['Composite'].set(self, value)

    security.declarePublic('getAnalysisRequests')

    def getAnalysisRequests(self):
        backrefs = get_backreferences(self, 'AnalysisRequestSample')
        ars = map(get_object_by_uid, backrefs)
        return ars

    security.declarePublic('getAnalyses')

    def getAnalyses(self, contentFilter):
        """ return list of all analyses against this sample
        """
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += ar.getAnalyses(**contentFilter)
        return analyses

    def getSamplers(self):
        return getUsers(self, ['Sampler', ])

    def disposal_date(self):
        """ Calculate the disposal date by returning the latest
            disposal date in this sample's partitions """

        parts = self.objectValues("SamplePartition")
        dates = []
        for part in parts:
            date = part.getDisposalDate()
            if date:
                dates.append(date)
        if dates:
            dis_date = dt2DT(max([DT2dt(date) for date in dates]))
        else:
            dis_date = None
        return dis_date

    def getLastARNumber(self):
        ARs = self.getBackReferences("AnalysisRequestSample")
        prefix = self.getSampleType().getPrefix()
        ar_ids = sorted([AR.id for AR in ARs if AR.id.startswith(prefix)])
        try:
            last_ar_number = int(ar_ids[-1].split("-R")[-1])
        except:
            return 0
        return last_ar_number

    def getSampleState(self):
        """Returns the sample veiew_state
        """
        workflow = getToolByName(self, 'portal_workflow')
        return workflow.getInfoFor(self, 'review_state')

    def getPreparationWorkflows(self):
        """Return a list of sample preparation workflows.  These are identified
        by scanning all workflow IDs for those beginning with "sampleprep".
        """
        wf = self.portal_workflow
        ids = wf.getWorkflowIds()
        sampleprep_ids = [wid for wid in ids if wid.startswith('sampleprep')]
        prep_workflows = [['', ''],]
        for workflow_id in sampleprep_ids:
            workflow = wf.getWorkflowById(workflow_id)
            prep_workflows.append([workflow_id, workflow.title])
        return DisplayList(prep_workflows)

    def getSamplePartitions(self):
        """Returns the Sample Partitions associated to this Sample
        """
        partitions = self.objectValues('SamplePartition')
        return partitions

    @security.public
    def workflow_script_no_sampling_workflow(self):
        events.after_no_sampling_workflow(self)

    @security.public
    def workflow_script_sampling_workflow(self):
        events.after_sampling_workflow(self)

    @security.public
    def workflow_script_sample(self):
        events.after_sample(self)

    @security.public
    def workflow_script_sample_due(self):
        events.after_sample_due(self)

    @security.public
    def workflow_script_receive(self):
        events.after_receive(self)

    @security.public
    def workflow_script_preserve(self):
        events.after_preserve(self)

    @security.public
    def workflow_script_expire(self):
        events.after_expire(self)

    @security.public
    def workflow_script_dispose(self):
        events.after_dispose(self)

    @security.public
    def workflow_script_to_be_preserved(self):
        events.after_to_be_preserved(self)

    @security.public
    def workflow_script_reinstate(self):
        events.after_reinstate(self)

    @security.public
    def workflow_script_cancel(self):
        events.after_cancel(self)

    @security.public
    def workflow_script_reject(self):
        events.after_reject(self)

    @security.public
    def workflow_script_schedule_sampling(self):
        events.after_schedule_sampling(self)

    @security.public
    def guard_to_be_preserved(self):
        return guards.to_be_preserved(self)

    @security.public
    def guard_receive_transition(self):
        return guards.receive(self)

    @security.public
    def guard_sample_prep_transition(self):
        return guards.sample_prep(self)

    @security.public
    def guard_sample_prep_complete_transition(self):
        return guards.sample_prep_complete(self)

    @security.public
    def guard_schedule_sampling_transition(self):
        return guards.schedule_sampling(self)

atapi.registerType(Sample, PROJECTNAME)
