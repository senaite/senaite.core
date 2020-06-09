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

import base64
import re
import sys
from decimal import Decimal
from urlparse import urljoin

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.api.security import check_permission
from bika.lims.browser.fields import ARAnalysesField
from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.fields import DurationField
from bika.lims.browser.fields import EmailsField
from bika.lims.browser.fields import ResultsRangesField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import DecimalWidget
from bika.lims.browser.widgets import PrioritySelectionWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.browser.widgets import RejectionWidget
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget
from bika.lims.browser.widgets.durationwidget import DurationWidget
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.catalog.bika_catalog import BIKA_CATALOG
from bika.lims.config import PRIORITIES
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.clientawaremixin import ClientAwareMixin
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IAnalysisRequestPartition
from bika.lims.interfaces import IAnalysisRequestWithPartitions
from bika.lims.interfaces import IBatch
from bika.lims.interfaces import ICancellable
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IDynamicResultsRange
from bika.lims.interfaces import ISubmitted
from bika.lims.permissions import FieldEditBatch
from bika.lims.permissions import FieldEditClient
from bika.lims.permissions import FieldEditClientOrderNumber
from bika.lims.permissions import FieldEditClientReference
from bika.lims.permissions import FieldEditClientSampleID
from bika.lims.permissions import FieldEditComposite
from bika.lims.permissions import FieldEditContact
from bika.lims.permissions import FieldEditContainer
from bika.lims.permissions import FieldEditDatePreserved
from bika.lims.permissions import FieldEditDateReceived
from bika.lims.permissions import FieldEditDateSampled
from bika.lims.permissions import FieldEditEnvironmentalConditions
from bika.lims.permissions import FieldEditInternalUse
from bika.lims.permissions import FieldEditInvoiceExclude
from bika.lims.permissions import FieldEditMemberDiscount
from bika.lims.permissions import FieldEditPreservation
from bika.lims.permissions import FieldEditPreserver
from bika.lims.permissions import FieldEditPriority
from bika.lims.permissions import FieldEditProfiles
from bika.lims.permissions import FieldEditPublicationSpecifications
from bika.lims.permissions import FieldEditRejectionReasons
from bika.lims.permissions import FieldEditRemarks
from bika.lims.permissions import FieldEditResultsInterpretation
from bika.lims.permissions import FieldEditSampleCondition
from bika.lims.permissions import FieldEditSamplePoint
from bika.lims.permissions import FieldEditSampler
from bika.lims.permissions import FieldEditSampleType
from bika.lims.permissions import FieldEditSamplingDate
from bika.lims.permissions import FieldEditSamplingDeviation
from bika.lims.permissions import FieldEditScheduledSampler
from bika.lims.permissions import FieldEditSpecification
from bika.lims.permissions import FieldEditStorageLocation
from bika.lims.permissions import FieldEditTemplate
from bika.lims.permissions import ManageInvoices
from bika.lims.utils import getUsers
from bika.lims.utils import tmpID
from bika.lims.utils import user_email
from bika.lims.utils import user_fullname
from bika.lims.workflow import getTransitionDate
from bika.lims.workflow import getTransitionUsers
from DateTime import DateTime
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import ComputedField
from Products.Archetypes.atapi import ComputedWidget
from Products.Archetypes.atapi import FileField
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import FixedPointField
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import registerType
from Products.Archetypes.public import Schema
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.Widget import RichWidget
from Products.ATExtensions.field import RecordsField
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides

IMG_SRC_RX = re.compile(r'<img.*?src="(.*?)"')
IMG_DATA_SRC_RX = re.compile(r'<img.*?src="(data:image/.*?;base64,)(.*?)"')
FINAL_STATES = ["published", "retracted", "rejected", "cancelled"]


# SCHEMA DEFINITION
schema = BikaSchema.copy() + Schema((

    UIDReferenceField(
        'Contact',
        required=1,
        default_method='getContactUIDForUser',
        allowed_types=('Contact',),
        mode="rw",
        read_permission=View,
        write_permission=FieldEditContact,
        widget=ReferenceWidget(
            label=_("Contact"),
            render_own_label=True,
            size=20,
            helper_js=("bika_widgets/referencewidget.js",
                       "++resource++bika.lims.js/contact.js"),
            description=_("The primary contact of this sample, "
                          "who will receive notifications and publications "
                          "via email"),
            visible={
                'add': 'edit',
                'header_table': 'prominent',
            },
            catalog_name="portal_catalog",
            base_query={"is_active": True,
                        "sort_limit": 50,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
            popup_width='400px',
            colModel=[
                {'columnName': 'Fullname', 'width': '50',
                 'label': _('Name')},
                {'columnName': 'EmailAddress', 'width': '50',
                 'label': _('Email Address')},
            ],
            ui_item='Fullname',
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
        read_permission=View,
        write_permission=FieldEditContact,
        widget=ReferenceWidget(
            label=_("CC Contacts"),
            description=_("The contacts used in CC for email notifications"),
            render_own_label=True,
            size=20,
            visible={
                'add': 'edit',
                'header_table': 'prominent',
            },
            catalog_name="portal_catalog",
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
            popup_width='400px',
            colModel=[
                {'columnName': 'Fullname', 'width': '50',
                 'label': _('Name')},
                {'columnName': 'EmailAddress', 'width': '50',
                 'label': _('Email Address')},
            ],
            ui_item='Fullname',
        ),
    ),

    EmailsField(
        'CCEmails',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditContact,
        widget=StringWidget(
            label=_("CC Emails"),
            description=_("Additional email addresses to be notified"),
            visible={
                'add': 'edit',
                'header_table': 'prominent',
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
        read_permission=View,
        write_permission=FieldEditClient,
        widget=ReferenceWidget(
            label=_("Client"),
            description=_("The assigned client of this request"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'header_table': 'prominent',
            },
            catalog_name="portal_catalog",
            base_query={"is_active": True,
                        "sort_limit": 30,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    # Field for the creation of Secondary Analysis Requests.
    # This field is meant to be displayed in AR Add form only. A viewlet exists
    # to inform the user this Analysis Request is secondary
    ReferenceField(
        "PrimaryAnalysisRequest",
        allowed_types=("AnalysisRequest",),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestPrimaryAnalysisRequest',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditClient,
        widget=ReferenceWidget(
            label=_("Primary Sample"),
            description=_("Select a sample to create a secondary Sample"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'header_table': 'prominent',
            },
            catalog_name=CATALOG_ANALYSIS_REQUEST_LISTING,
            search_fields=('listing_searchable_text',),
            base_query={'is_active': True,
                        'is_received': True,
                        'sort_limit': 30,
                        'sort_on': 'getId',
                        'sort_order': 'descending'},
            colModel=[
                {'columnName': 'getId', 'width': '20',
                 'label': _('Sample ID'), 'align': 'left'},
                {'columnName': 'getClientSampleID', 'width': '20',
                 'label': _('Client SID'), 'align': 'left'},
                {'columnName': 'getSampleTypeTitle', 'width': '30',
                 'label': _('Sample Type'), 'align': 'left'},
                {'columnName': 'getClientTitle', 'width': '30',
                 'label': _('Client'), 'align': 'left'},
                {'columnName': 'UID', 'hidden': True},
            ],
            ui_item='getId',
            showOn=True,
        )
    ),

    ReferenceField(
        'Batch',
        allowed_types=('Batch',),
        relationship='AnalysisRequestBatch',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditBatch,
        widget=ReferenceWidget(
            label=_("Batch"),
            size=20,
            description=_("The assigned batch of this request"),
            render_own_label=True,
            visible={
                'add': 'edit',
            },
            catalog_name=BIKA_CATALOG,
            search_fields=('listing_searchable_text',),
            base_query={"is_active": True,
                        "sort_limit": 50,
                        "sort_on": "sortable_title",
                        "sort_order": "descending"},
            colModel=[
                {'columnName': 'getId', 'width': '20',
                 'label': _('Batch ID'), 'align': 'left'},
                {'columnName': 'Title', 'width': '20',
                 'label': _('Title'), 'align': 'left'},
                {'columnName': 'getClientBatchID', 'width': '20',
                 'label': _('CBID'), 'align': 'left'},
                {'columnName': 'getClientTitle', 'width': '30',
                 'label': _('Client'), 'align': 'left'},
            ],
            force_all = False,
            ui_item="getId",
            showOn=True,
        ),
    ),

    ReferenceField(
        'SubGroup',
        required=False,
        allowed_types=('SubGroup',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestSubGroup',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditBatch,
        widget=ReferenceWidget(
            label=_("Batch Sub-group"),
            description=_("The assigned batch sub group of this request"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
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
            base_query={'is_active': True},
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
        read_permission=View,
        write_permission=FieldEditTemplate,
        widget=ReferenceWidget(
            label=_("Sample Template"),
            description=_("The predefined values of the Sample template are set "
                          "in the request"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    # TODO Remove Profile field (in singular)
    ReferenceField(
        'Profile',
        allowed_types=('AnalysisProfile',),
        referenceClass=HoldingReference,
        relationship='AnalysisRequestAnalysisProfile',
        mode="rw",
        read_permission=View,
        write_permission=ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Analysis Profile"),
            description=_("Analysis profiles apply a certain set of analyses"),
            size=20,
            render_own_label=True,
            visible=False,
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
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
        read_permission=View,
        write_permission=FieldEditProfiles,
        widget=ReferenceWidget(
            label=_("Analysis Profiles"),
            description=_("Analysis profiles apply a certain set of analyses"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),
    # TODO Workflow - Request - Fix DateSampled inconsistencies. At the moment,
    # one can create an AR (using code) with DateSampled set when sampling_wf at
    # the same time sampling workflow is active. This might cause
    # inconsistencies: AR still in `to_be_sampled`, but getDateSampled returns
    # a valid date!
    DateTimeField(
        'DateSampled',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditDateSampled,
        widget=DateTimeWidget(
            label=_("Date Sampled"),
            description=_("The date when the sample was taken"),
            size=20,
            show_time=True,
            datepicker_nofuture=1,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
                'header_table': 'prominent',
            },
            render_own_label=True,
        ),
    ),
    StringField(
        'Sampler',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditSampler,
        vocabulary='getSamplers',
        widget=BikaSelectionWidget(
            format='select',
            label=_("Sampler"),
            description=_("The person who took the sample"),
            # see SamplingWOrkflowWidgetVisibility
            visible={
                'add': 'edit',
                'header_table': 'prominent',
            },
            render_own_label=True,
        ),
    ),

    StringField(
        'ScheduledSamplingSampler',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditScheduledSampler,
        vocabulary='getSamplers',
        widget=BikaSelectionWidget(
            description=_("Define the sampler supposed to do the sample in "
                          "the scheduled date"),
            format='select',
            label=_("Sampler for scheduled sampling"),
            visible={
                'add': 'edit',
            },
            render_own_label=True,
        ),
    ),

    DateTimeField(
        'SamplingDate',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditSamplingDate,
        widget=DateTimeWidget(
            label=_("Expected Sampling Date"),
            description=_("The date when the sample will be taken"),
            size=20,
            show_time=True,
            datepicker_nopast=1,
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
        ),
    ),

    UIDReferenceField(
        'SampleType',
        required=1,
        allowed_types='SampleType',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditSampleType,
        widget=ReferenceWidget(
            label=_("Sample Type"),
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    UIDReferenceField(
        'Container',
        required=0,
        allowed_types='Container',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditContainer,
        widget=ReferenceWidget(
            label=_("Container"),
            render_own_label=True,
            visible={
                'add': 'edit',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    UIDReferenceField(
        'Preservation',
        required=0,
        allowed_types='Preservation',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditPreservation,
        widget=ReferenceWidget(
            label=_("Preservation"),
            render_own_label=True,
            visible={
                'add': 'edit',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    DateTimeField('DatePreserved',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditDatePreserved,
        widget=DateTimeWidget(
            label=_("Date Preserved"),
            description=_("The date when the sample was preserved"),
            size=20,
            show_time=True,
            render_own_label=True,
            visible={
                'add': 'edit',
                'header_table': 'prominent',
            },
        ),
    ),
    StringField('Preserver',
        required=0,
        mode="rw",
        read_permission=View,
        write_permission=FieldEditPreserver,
        vocabulary='getPreservers',
        widget=BikaSelectionWidget(
            format='select',
            label=_("Preserver"),
            description=_("The person who preserved the sample"),
            visible={
                'add': 'edit',
                'header_table': 'prominent',
            },
            render_own_label=True,
        ),
    ),
    # TODO Sample cleanup - This comes from partition
    DurationField('RetentionPeriod',
        required=0,
        mode="r",
        read_permission=View,
        widget=DurationWidget(
            label=_("Retention Period"),
            visible=False,
        ),
    ),
    RecordsField(
        'RejectionReasons',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditRejectionReasons,
        widget=RejectionWidget(
            label=_("Sample Rejection"),
            description=_("Set the Sample Rejection workflow and the reasons"),
            render_own_label=False,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
        ),
    ),

    ReferenceField(
        'Specification',
        required=0,
        primary_bound=True,  # field changes propagate to partitions
        allowed_types='AnalysisSpec',
        relationship='AnalysisRequestAnalysisSpec',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditSpecification,
        widget=ReferenceWidget(
            label=_("Analysis Specification"),
            description=_("Choose default Sample specification values"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            search_fields=('listing_searchable_text',),
            colModel=[
                {'columnName': 'contextual_title',
                 'width': '30',
                 'label': _('Title'),
                 'align': 'left'},
                {'columnName': 'getSampleTypeTitle',
                 'width': '70',
                 'label': _('SampleType'),
                 'align': 'left'},
                # UID is required in colModel
                {'columnName': 'UID', 'hidden': True},
            ],
            ui_item="contextual_title",
            showOn=True,
        ),
    ),

    # Field to keep the result ranges from the specification initially set
    # through "Specifications" field. This guarantees that the result ranges
    # set by default to this Sample won't change even if the Specifications
    # object referenced gets modified thereafter.
    # This field does not consider result ranges manually set to analyses.
    # Therefore, is also used to "detect" changes between the result ranges
    # specifically set to analyses and the results ranges set to the sample
    ResultsRangesField(
        "ResultsRange",
        write_permission=FieldEditSpecification,
        widget=ComputedWidget(visible=False),
    ),

    ReferenceField(
        'PublicationSpecification',
        required=0,
        allowed_types='AnalysisSpec',
        relationship='AnalysisRequestPublicationSpec',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditPublicationSpecifications,
        widget=ReferenceWidget(
            label=_("Publication Specification"),
            description=_(
                "Set the specification to be used before publishing a Sample."),
            size=20,
            render_own_label=True,
            visible={
                "add": "invisible",
                'secondary': 'disabled',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    # Sample field
    UIDReferenceField(
        'SamplePoint',
        allowed_types='SamplePoint',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditSamplePoint,
        widget=ReferenceWidget(
            label=_("Sample Point"),
            description=_("Location where sample was taken"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    UIDReferenceField(
        'StorageLocation',
        allowed_types='StorageLocation',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditStorageLocation,
        widget=ReferenceWidget(
            label=_("Storage Location"),
            description=_("Location where sample is kept"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    StringField(
        'ClientOrderNumber',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditClientOrderNumber,
        widget=StringWidget(
            label=_("Client Order Number"),
            description=_("The client side order number for this request"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
        ),
    ),

    StringField(
        'ClientReference',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditClientReference,
        widget=StringWidget(
            label=_("Client Reference"),
            description=_("The client side reference for this request"),
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
        ),
    ),

    StringField(
        'ClientSampleID',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditClientSampleID,
        widget=StringWidget(
            label=_("Client Sample ID"),
            description=_("The client side identifier of the sample"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
        ),
    ),

    UIDReferenceField(
        'SamplingDeviation',
        allowed_types='SamplingDeviation',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditSamplingDeviation,
        widget=ReferenceWidget(
            label=_("Sampling Deviation"),
            description=_("Deviation between the sample and how it "
                          "was sampled"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    UIDReferenceField(
        'SampleCondition',
        allowed_types='SampleCondition',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditSampleCondition,
        widget=ReferenceWidget(
            label=_("Sample condition"),
            description=_("The condition of the sample"),
            size=20,
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    StringField(
        'Priority',
        default='3',
        vocabulary=PRIORITIES,
        mode='rw',
        read_permission=View,
        write_permission=FieldEditPriority,
        widget=PrioritySelectionWidget(
            label=_('Priority'),
            format='select',
            visible={
                'add': 'edit',
            },
        ),
    ),
    StringField(
        'EnvironmentalConditions',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditEnvironmentalConditions,
        widget=StringWidget(
            label=_("Environmental conditions"),
            description=_("The environmental condition during sampling"),
            visible={
                'add': 'edit',
                'header_table': 'prominent',
            },
            render_own_label=True,
            size=20,
        ),
    ),

    # TODO Remove - Is this still necessary?
    ReferenceField(
        'DefaultContainerType',
        allowed_types=('ContainerType',),
        relationship='AnalysisRequestContainerType',
        referenceClass=HoldingReference,
        mode="rw",
        read_permission=View,
        write_permission=ModifyPortalContent,
        widget=ReferenceWidget(
            label=_("Default Container"),
            description=_("Default container for new sample partitions"),
            size=20,
            render_own_label=True,
            visible=False,
            catalog_name='bika_setup_catalog',
            base_query={"is_active": True,
                        "sort_on": "sortable_title",
                        "sort_order": "ascending"},
            showOn=True,
        ),
    ),

    BooleanField(
        'Composite',
        default=False,
        mode="rw",
        read_permission=View,
        write_permission=FieldEditComposite,
        widget=BooleanWidget(
            label=_("Composite"),
            render_own_label=True,
            visible={
                'add': 'edit',
                'secondary': 'disabled',
            },
        ),
    ),

    BooleanField(
        'InvoiceExclude',
        default=False,
        mode="rw",
        read_permission=View,
        write_permission=FieldEditInvoiceExclude,
        widget=BooleanWidget(
            label=_("Invoice Exclude"),
            description=_("Should the analyses be excluded from the invoice?"),
            render_own_label=True,
            visible={
                'add': 'edit',
                'header_table': 'visible',
            },
        ),
    ),

    # TODO Review permission for this field Analyses
    ARAnalysesField(
        'Analyses',
        required=1,
        mode="rw",
        read_permission=View,
        write_permission=ModifyPortalContent,
        widget=ComputedWidget(
            visible={
                'edit': 'invisible',
                'view': 'invisible',
                'sample_registered': {
                    'view': 'visible', 'edit': 'visible', 'add': 'invisible'},
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
        read_permission=View,
        write_permission=ModifyPortalContent,
        widget=ComputedWidget(
            visible={
                'edit': 'invisible',
                'view': 'invisible',
            },
        )
    ),

    # This is a virtual field and handled only by AR Add View to allow multi
    # attachment upload in AR Add. It should never contain an own value!
    FileField(
        '_ARAttachment',
        widget=FileWidget(
            label=_("Attachment"),
            description=_("Add one or more attachments to describe the "
                          "sample in this sample, or to specify "
                          "your request."),
            render_own_label=True,
            visible={
                'view': 'invisible',
                'add': 'edit',
                'header_table': 'invisible',
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
        read_permission=View,
        write_permission=ModifyPortalContent,
        widget=ComputedWidget(
            visible={
                'edit': 'invisible',
                'view': 'visible',
            },
        )
    ),

    DateTimeField(
        'DateReceived',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditDateReceived,
        widget=DateTimeWidget(
            label=_("Date Sample Received"),
            show_time=True,
            datepicker_nofuture=1,
            description=_("The date when the sample was received"),
            render_own_label=True,
        ),
    ),
    ComputedField(
        'DatePublished',
        mode="r",
        read_permission=View,
        expression="here.getDatePublished().strftime('%Y-%m-%d %H:%M %p') if here.getDatePublished() else ''",
        widget=DateTimeWidget(
            label=_("Date Published"),
            visible={
                'edit': 'invisible',
                'add': 'invisible',
                'secondary': 'invisible',
            },
        ),
    ),

    RemarksField(
        'Remarks',
        read_permission=View,
        write_permission=FieldEditRemarks,
        widget=RemarksWidget(
            label=_("Remarks"),
            description=_("Remarks and comments for this request"),
            render_own_label=True,
            visible={
                'add': 'edit',
                'header_table': 'invisible',
            },
        ),
    ),

    FixedPointField(
        'MemberDiscount',
        default_method='getDefaultMemberDiscount',
        mode="rw",
        read_permission=View,
        write_permission=FieldEditMemberDiscount,
        widget=DecimalWidget(
            label=_("Member discount %"),
            description=_("Enter percentage value eg. 33.0"),
            render_own_label=True,
            visible={
                'add': 'invisible',
            },
        ),
    ),

    ComputedField(
        'SampleTypeTitle',
        expression="here.getSampleType().Title() if here.getSampleType() "
                   "else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),

    ComputedField(
        'SamplePointTitle',
        expression="here.getSamplePoint().Title() if here.getSamplePoint() "
                   "else ''",
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
        expression="[p.UID() for p in here.getProfiles()] " \
                   "if here.getProfiles() else []",
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
    ComputedField(
        'ReceivedBy',
        expression='here.getReceivedBy()',
        default='',
        widget=ComputedWidget(visible=False,),
    ),
    ComputedField(
        'CreatorFullName',
        expression="here._getCreatorFullName()",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'CreatorEmail',
        expression="here._getCreatorEmail()",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'SamplerFullName',
        expression="here._getSamplerFullName()",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'SamplerEmail',
        expression="here._getSamplerEmail()",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'BatchID',
        expression="here.getBatch().getId() if here.getBatch() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'BatchURL',
        expression="here.getBatch().absolute_url_path() " \
                   "if here.getBatch() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'ContactUsername',
        expression="here.getContact().getUsername() " \
                   "if here.getContact() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'ContactFullName',
        expression="here.getContact().getFullname() " \
                   "if here.getContact() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'ContactEmail',
        expression="here.getContact().getEmailAddress() " \
                   "if here.getContact() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'SampleTypeUID',
        expression="here.getSampleType().UID() " \
                   "if here.getSampleType() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'SamplePointUID',
        expression="here.getSamplePoint().UID() " \
                   "if here.getSamplePoint() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'StorageLocationUID',
        expression="here.getStorageLocation().UID() " \
                   "if here.getStorageLocation() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'ProfilesURL',
        expression="[p.absolute_url_path() for p in here.getProfiles()] " \
                   "if here.getProfiles() else []",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'ProfilesTitle',
        expression="[p.Title() for p in here.getProfiles()] " \
                   "if here.getProfiles() else []",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'ProfilesTitleStr',
        expression="', '.join([p.Title() for p in here.getProfiles()]) " \
                   "if here.getProfiles() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'TemplateUID',
        expression="here.getTemplate().UID() if here.getTemplate() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'TemplateURL',
        expression="here.getTemplate().absolute_url_path() " \
                   "if here.getTemplate() else ''",
        widget=ComputedWidget(visible=False),
    ),
    ComputedField(
        'TemplateTitle',
        expression="here.getTemplate().Title() if here.getTemplate() else ''",
        widget=ComputedWidget(visible=False),
    ),

    ReferenceField(
        'ParentAnalysisRequest',
        allowed_types=('AnalysisRequest',),
        relationship='AnalysisRequestParentAnalysisRequest',
        referenceClass=HoldingReference,
        mode="rw",
        read_permission=View,
        write_permission=ModifyPortalContent,
        widget=ReferenceWidget(
            visible=False,
        ),
    ),

    # The Primary Sample the current sample was detached from
    ReferenceField(
        "DetachedFrom",
        allowed_types=("AnalysisRequest",),
        relationship="AnalysisRequestDetachedFrom",
        referenceClass=HoldingReference,
        mode="rw",
        read_permission=View,
        write_permission=ModifyPortalContent,
        widget=ReferenceWidget(
            visible=False,
        )
    ),

    # The Analysis Request the current Analysis Request comes from because of
    # an invalidation of the former
    ReferenceField(
        'Invalidated',
        allowed_types=('AnalysisRequest',),
        relationship='AnalysisRequestRetracted',
        referenceClass=HoldingReference,
        mode="rw",
        read_permission=View,
        write_permission=ModifyPortalContent,
        widget=ReferenceWidget(
            visible=False,
        ),
    ),

    # The Analysis Request that was automatically generated due to the
    # invalidation of the current Analysis Request
    ComputedField(
        'Retest',
        expression="here.get_retest()",
        widget=ComputedWidget(visible=False)
    ),

    # For comments or results interpretation
    # Old one, to be removed because of the incorporation of
    # ResultsInterpretationDepts (due to LIMS-1628)
    TextField(
        'ResultsInterpretation',
        mode="rw",
        default_content_type='text/html',
        # Input content type for the textfield
        default_output_type='text/x-html-safe',
        # getResultsInterpretation returns a str with html tags
        # to conserve the txt format in the report.
        read_permission=View,
        write_permission=FieldEditResultsInterpretation,
        widget=RichWidget(
            description=_("Comments or results interpretation"),
            label=_("Results Interpretation"),
            size=10,
            allow_file_upload=False,
            default_mime_type='text/x-rst',
            output_mime_type='text/x-html',
            rows=3,
            visible=False),
    ),

    RecordsField(
        'ResultsInterpretationDepts',
        read_permission=View,
        write_permission=FieldEditResultsInterpretation,
        subfields=('uid', 'richtext'),
        subfield_labels={
            'uid': _('Department'),
            'richtext': _('Results Interpretation')},
        widget=RichWidget(visible=False),
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
    StringField(
        'Printed',
        mode="rw",
        read_permission=View,
        widget=StringWidget(
            label=_("Printed"),
            description=_("Indicates if the last SampleReport is printed,"),
            visible=False,
        ),
    ),
    BooleanField(
        "InternalUse",
        mode="rw",
        required=0,
        default=False,
        read_permission=View,
        write_permission=FieldEditInternalUse,
        widget=BooleanWidget(
            label=_("Internal use"),
            description=_("Mark the sample for internal use only. This means "
                          "it is only accessible to lab personnel and not to "
                          "clients."),
            format="radio",
            render_own_label=True,
            visible={'add': 'edit',}
        ),
    ),
)
)


# Some schema rearrangement
schema['title'].required = False
schema['id'].widget.visible = False
schema['title'].widget.visible = False
schema.moveField('Client', before='Contact')
schema.moveField('ResultsInterpretation', pos='bottom')
schema.moveField('ResultsInterpretationDepts', pos='bottom')
schema.moveField("PrimaryAnalysisRequest", before="Client")


class AnalysisRequest(BaseFolder, ClientAwareMixin):
    implements(IAnalysisRequest, ICancellable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        """Rename hook called by processForm
        """
        # https://github.com/senaite/senaite.core/issues/1327
        primary = self.getPrimaryAnalysisRequest()
        if primary:
            logger.info("Secondary sample detected: Skipping ID generation")
            return False
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def Title(self):
        """ Return the Request ID as title """
        return self.getId()

    def sortable_title(self):
        """
        Some lists expects this index
        """
        return self.getId()

    def Description(self):
        """Returns searchable data as Description"""
        descr = " ".join((self.getId(), self.aq_parent.Title()))
        return safe_unicode(descr).encode('utf-8')

    def setSpecification(self, value):
        """Sets the Specifications and ResultRange values
        """
        current_spec = self.getRawSpecification()
        if value and current_spec == api.get_uid(value):
            # Specification has not changed, preserve the current value to
            # prevent result ranges (both from Sample and from analyses) from
            # being overriden
            return

        self.getField("Specification").set(self, value)

        # Set the value for field ResultsRange, cause Specification is only
        # used as a template: all the results range logic relies on
        # ResultsRange field, so changes in setup's Specification object won't
        # have effect to already created samples
        spec = self.getSpecification()
        if spec:
            # Update only results ranges if specs is not None, so results
            # ranges manually set previously (e.g. via ManageAnalyses view) are
            # preserved unless a new Specification overrides them
            self.setResultsRange(spec.getResultsRange(), recursive=False)

        # Cascade the changes to partitions, but only to those that are in a
        # status in which the specification can be updated. This prevents the
        # re-assignment of Specifications to already verified or published
        # samples
        permission = self.getField("Specification").write_permission
        for descendant in self.getDescendants():
            if check_permission(permission, descendant):
                descendant.setSpecification(spec)

    def setResultsRange(self, value, recursive=True):
        """Sets the results range for this Sample and analyses it contains.
        If recursive is True, then applies the results ranges to descendants
        (partitions) as well as their analyses too
        """
        # Set Results Range to the Sample
        field = self.getField("ResultsRange")
        field.set(self, value)

        # Set Results Range to analyses
        for analysis in self.objectValues("Analysis"):
            if not ISubmitted.providedBy(analysis):
                service_uid = analysis.getRawAnalysisService()
                # get the default results range from the spec
                result_range = field.get(self, search_by=service_uid)
                # check if we have an dynamic results range adapter
                adapter = IDynamicResultsRange(analysis, None)
                if adapter:
                    # update the result range with the dynamic values
                    result_range.update(adapter())
                analysis.setResultsRange(result_range)
                analysis.reindexObject()

        if recursive:
            # Cascade the changes to partitions
            permission = self.getField("Specification").write_permission
            for descendant in self.getDescendants():
                if check_permission(permission, descendant):
                    descendant.setResultsRange(value)

    def getClient(self):
        """Returns the client this object is bound to. We override getClient
        from ClientAwareMixin because the "Client" schema field is only used to
        allow the user to set the client while creating the Sample through
        Sample Add form, but cannot be changed afterwards. The Sample is
        created directly inside the selected client folder on submit
        """
        if IClient.providedBy(self.aq_parent):
            return self.aq_parent
        if IBatch.providedBy(self.aq_parent):
            return self.aq_parent.getClient()
        return None

    def getProfilesTitle(self):
        return [profile.Title() for profile in self.getProfiles()]

    def getAnalysisService(self):
        proxies = self.getAnalyses(full_objects=False)
        value = set()
        for proxy in proxies:
            value.add(proxy.Title)
        return list(value)

    def getAnalysts(self):
        proxies = self.getAnalyses(full_objects=True)
        value = []
        for proxy in proxies:
            val = proxy.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    def getDistrict(self):
        client = self.aq_parent
        return client.getDistrict()

    def getProvince(self):
        client = self.aq_parent
        return client.getProvince()

    @security.public
    def getBatch(self):
        # The parent type may be "Batch" during ar_add.
        # This function fills the hidden field in ar_add.pt
        if self.aq_parent.portal_type == 'Batch':
            return self.aq_parent
        else:
            return self.Schema()['Batch'].get(self)

    @security.public
    def getBatchUID(self):
        batch = self.getBatch()
        if batch:
            return batch.UID()

    @security.public
    def setBatch(self, value=None):
        original_value = self.Schema().getField('Batch').get(self)
        if original_value != value:
            self.Schema().getField('Batch').set(self, value)

    def getDefaultMemberDiscount(self):
        """Compute default member discount if it applies
        """
        if hasattr(self, 'getMemberDiscountApplies'):
            if self.getMemberDiscountApplies():
                settings = self.bika_setup
                return settings.getMemberDiscount()
            else:
                return "0.00"

    @security.public
    def getAnalysesNum(self):
        """ Returns an array with the number of analyses for the current AR in
            different statuses, like follows:
                [verified, total, not_submitted, to_be_verified]
        """
        an_nums = [0, 0, 0, 0]
        for analysis in self.getAnalyses():
            review_state = analysis.review_state
            if review_state in ['retracted', 'rejected', 'cancelled']:
                continue
            if review_state == 'to_be_verified':
                an_nums[3] += 1
            elif review_state in ['published', 'verified']:
                an_nums[0] += 1
            else:
                an_nums[2] += 1
            an_nums[1] += 1
        return an_nums

    @security.public
    def getResponsible(self):
        """Return all manager info of responsible departments
        """
        managers = {}
        for department in self.getDepartments():
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if manager_id not in managers:
                managers[manager_id] = {}
                managers[manager_id]['salutation'] = safe_unicode(
                    manager.getSalutation())
                managers[manager_id]['name'] = safe_unicode(
                    manager.getFullname())
                managers[manager_id]['email'] = safe_unicode(
                    manager.getEmailAddress())
                managers[manager_id]['phone'] = safe_unicode(
                    manager.getBusinessPhone())
                managers[manager_id]['job_title'] = safe_unicode(
                    manager.getJobTitle())
                if manager.getSignature():
                    managers[manager_id]['signature'] = \
                        '{}/Signature'.format(manager.absolute_url())
                else:
                    managers[manager_id]['signature'] = False
                managers[manager_id]['departments'] = ''
            mngr_dept = managers[manager_id]['departments']
            if mngr_dept:
                mngr_dept += ', '
            mngr_dept += safe_unicode(department.Title())
            managers[manager_id]['departments'] = mngr_dept
        mngr_keys = managers.keys()
        mngr_info = {'ids': mngr_keys, 'dict': managers}

        return mngr_info

    @security.public
    def getManagers(self):
        """Return all managers of responsible departments
        """
        manager_ids = []
        manager_list = []
        for department in self.getDepartments():
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if manager_id not in manager_ids:
                manager_ids.append(manager_id)
                manager_list.append(manager)
        return manager_list

    def getDueDate(self):
        """Returns the earliest due date of the analyses this Analysis Request
        contains."""
        due_dates = map(lambda an: an.getDueDate, self.getAnalyses())
        return due_dates and min(due_dates) or None

    security.declareProtected(View, 'getLate')

    def getLate(self):
        """Return True if there is at least one late analysis in this Request
        """
        for analysis in self.getAnalyses():
            if analysis.review_state == "retracted":
                continue
            analysis_obj = api.get_object(analysis)
            if analysis_obj.isLateAnalysis():
                return True
        return False

    def getPrinted(self):
        """ returns "0", "1" or "2" to indicate Printed state.
            0 -> Never printed.
            1 -> Printed after last publish
            2 -> Printed but republished afterwards.
        """
        workflow = getToolByName(self, 'portal_workflow')
        review_state = workflow.getInfoFor(self, 'review_state', '')
        if review_state not in ['published']:
            return "0"
        report_list = sorted(self.objectValues('ARReport'),
                             key=lambda report: report.getDatePublished())
        if not report_list:
            return "0"
        last_report = report_list[-1]
        if last_report.getDatePrinted():
            return "1"
        else:
            for report in report_list:
                if report.getDatePrinted():
                    return "2"
        return "0"

    @security.protected(View)
    def getBillableItems(self):
        """Returns the items to be billed
        """
        # Assigned profiles
        profiles = self.getProfiles()
        # Billable profiles which have a fixed price set
        billable_profiles = filter(
            lambda pr: pr.getUseAnalysisProfilePrice(), profiles)
        # All services contained in the billable profiles
        billable_profile_services = reduce(lambda a, b: a+b, map(
            lambda profile: profile.getService(), billable_profiles), [])
        # Keywords of the contained services
        billable_service_keys = map(
            lambda s: s.getKeyword(), set(billable_profile_services))
        # The billable items contain billable profiles and single selected analyses
        billable_items = billable_profiles
        # Get the analyses to be billed
        exclude_rs = ["retracted", "rejected"]
        for analysis in self.getAnalyses(is_active=True):
            if analysis.review_state in exclude_rs:
                continue
            if analysis.getKeyword in billable_service_keys:
                continue
            billable_items.append(api.get_object(analysis))
        return billable_items

    @security.protected(View)
    def getSubtotal(self):
        """Compute Subtotal (without member discount and without vat)
        """
        return sum([Decimal(obj.getPrice()) for obj in self.getBillableItems()])

    @security.protected(View)
    def getSubtotalVATAmount(self):
        """Compute VAT amount without member discount
        """
        return sum([Decimal(o.getVATAmount()) for o in self.getBillableItems()])

    @security.protected(View)
    def getSubtotalTotalPrice(self):
        """Compute the price with VAT but no member discount
        """
        return self.getSubtotal() + self.getSubtotalVATAmount()

    @security.protected(View)
    def getDiscountAmount(self):
        """It computes and returns the analysis service's discount amount
        without VAT
        """
        has_client_discount = self.aq_parent.getMemberDiscountApplies()
        if has_client_discount:
            discount = Decimal(self.getDefaultMemberDiscount())
            return Decimal(self.getSubtotal() * discount / 100)
        else:
            return 0

    @security.protected(View)
    def getVATAmount(self):
        """It computes the VAT amount from (subtotal-discount.)*VAT/100, but
        each analysis has its own VAT!

        :returns: the analysis request VAT amount with the discount
        """
        has_client_discount = self.aq_parent.getMemberDiscountApplies()
        VATAmount = self.getSubtotalVATAmount()
        if has_client_discount:
            discount = Decimal(self.getDefaultMemberDiscount())
            return Decimal((1 - discount / 100) * VATAmount)
        else:
            return VATAmount

    @security.protected(View)
    def getTotalPrice(self):
        """It gets the discounted price from analyses and profiles to obtain the
        total value with the VAT and the discount applied

        :returns: analysis request's total price including VATs and discounts
        """
        price = (self.getSubtotal() - self.getDiscountAmount() +
                 self.getVATAmount())
        return price

    getTotal = getTotalPrice

    @security.protected(ManageInvoices)
    def createInvoice(self, pdf):
        """Issue invoice
        """
        client = self.getClient()
        invoice = self.getInvoice()
        if not invoice:
            invoice = _createObjectByType("Invoice", client, tmpID())
        invoice.edit(
            AnalysisRequest=self,
            Client=client,
            InvoiceDate=DateTime(),
            InvoicePDF=pdf
        )
        invoice.processForm()
        self.setInvoice(invoice)
        return invoice

    @security.public
    def printInvoice(self, REQUEST=None, RESPONSE=None):
        """Print invoice
        """
        invoice = self.getInvoice()
        invoice_url = invoice.absolute_url()
        RESPONSE.redirect('{}/invoice_print'.format(invoice_url))

    @deprecated("Use getVerifiers instead")
    @security.public
    def getVerifier(self):
        """Returns the user that verified the whole Analysis Request. Since the
        verification is done automatically as soon as all the analyses it
        contains are verified, this function returns the user that verified the
        last analysis pending.
        """
        wtool = getToolByName(self, 'portal_workflow')
        mtool = getToolByName(self, 'portal_membership')

        verifier = None
        # noinspection PyBroadException
        try:
            review_history = wtool.getInfoFor(self, 'review_history')
        except:  # noqa FIXME: remove blind except!
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

    @security.public
    def getVerifiersIDs(self):
        """Returns the ids from users that have verified at least one analysis
        from this Analysis Request
        """
        verifiers_ids = list()
        for brain in self.getAnalyses():
            verifiers_ids += brain.getVerificators
        return list(set(verifiers_ids))

    @security.public
    def getVerifiers(self):
        """Returns the list of lab contacts that have verified at least one
        analysis from this Analysis Request
        """
        contacts = list()
        for verifier in self.getVerifiersIDs():
            user = api.get_user(verifier)
            contact = api.get_user_contact(user, ["LabContact"])
            if contact:
                contacts.append(contact)
        return contacts

    security.declarePublic('getContactUIDForUser')

    def getContactUIDForUser(self):
        """get the UID of the contact associated with the authenticated user
        """
        mt = getToolByName(self, 'portal_membership')
        user = mt.getAuthenticatedMember()
        user_id = user.getUserName()
        pc = getToolByName(self, 'portal_catalog')
        r = pc(portal_type='Contact',
               getUsername=user_id)
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('current_date')

    def current_date(self):
        """return current date
        """
        # noinspection PyCallingNonCallable
        return DateTime()

    def getWorksheets(self, full_objects=False):
        """Returns the worksheets that contains analyses from this Sample
        """
        # Get the Analyses UIDs of this Sample
        analyses_uids = map(api.get_uid, self.getAnalyses())
        if not analyses_uids:
            return []

        # Get the worksheets that contain any of these analyses
        query = dict(getAnalysesUIDs=analyses_uids)
        worksheets = api.search(query, CATALOG_WORKSHEET_LISTING)
        if full_objects:
            worksheets = map(api.get_object, worksheets)
        return worksheets

    def getQCAnalyses(self, review_state=None):
        """Returns the Quality Control analyses assigned to worksheets that
        contains analyses from this Sample
        """
        # Get the worksheet uids
        worksheet_uids = map(api.get_uid, self.getWorksheets())
        if not worksheet_uids:
            return []

        # Get reference qc analyses from these worksheets
        query = dict(portal_type="ReferenceAnalysis",
                     getWorksheetUID=worksheet_uids)
        qc_analyses = api.search(query, CATALOG_ANALYSIS_LISTING)

        # Extend with duplicate qc analyses from these worksheets and Sample
        query = dict(portal_type="DuplicateAnalysis",
                     getWorksheetUID=worksheet_uids,
                     getAncestorsUIDs=[api.get_uid(self)])
        qc_analyses += api.search(query, CATALOG_ANALYSIS_LISTING)

        # Bail out analyses with a different review_state
        if review_state:
            qc_analyses = filter(
                lambda an: api.get_review_status(an) in review_state,
                qc_analyses
            )

        # Return the objects
        return map(api.get_object, qc_analyses)

    def isInvalid(self):
        """return if the Analysis Request has been invalidated
        """
        workflow = getToolByName(self, 'portal_workflow')
        return workflow.getInfoFor(self, 'review_state') == 'invalid'

    def getStorageLocationTitle(self):
        """ A method for AR listing catalog metadata
        :return: Title of Storage Location
        """
        sl = self.getStorageLocation()
        if sl:
            return sl.Title()
        return ''

    def getDatePublished(self):
        """
        Returns the transition date from the Analysis Request object
        """
        return getTransitionDate(self, 'publish', return_as_datetime=True)

    @security.public
    def getSamplingDeviationTitle(self):
        """
        It works as a metacolumn.
        """
        sd = self.getSamplingDeviation()
        if sd:
            return sd.Title()
        return ''

    @security.public
    def getSampleConditionTitle(self):
        """Helper method to access the title of the sample condition
        """
        obj = self.getSampleCondition()
        if not obj:
            return ""
        return api.get_title(obj)

    @security.public
    def getHazardous(self):
        """
        It works as a metacolumn.
        """
        sample_type = self.getSampleType()
        if sample_type:
            return sample_type.getHazardous()
        return False

    @security.public
    def getContactURL(self):
        """
        It works as a metacolumn.
        """
        contact = self.getContact()
        if contact:
            return contact.absolute_url_path()
        return ''

    @security.public
    def getSamplingWorkflowEnabled(self):
        """Returns True if the sample of this Analysis Request has to be
        collected by the laboratory personnel
        """
        template = self.getTemplate()
        if template:
            return template.getSamplingRequired()
        return self.bika_setup.getSamplingWorkflowEnabled()

    def getSamplers(self):
        return getUsers(self, ['Sampler', ])

    def getPreservers(self):
        return getUsers(self, ['Preserver', 'Sampler'])

    def getDepartments(self):
        """Returns a list of the departments assigned to the Analyses
        from this Analysis Request
        """
        departments = list()
        for analysis in self.getAnalyses(full_objects=True):
            department = analysis.getDepartment()
            if department and department not in departments:
                departments.append(department)
        return departments

    def getResultsInterpretationByDepartment(self, department=None):
        """Returns the results interpretation for this Analysis Request
           and department. If department not set, returns the results
           interpretation tagged as 'General'.

        :returns: a dict with the following keys:
            {'uid': <department_uid> or 'general', 'richtext': <text/plain>}
        """
        uid = department.UID() if department else 'general'
        rows = self.Schema()['ResultsInterpretationDepts'].get(self)
        row = [row for row in rows if row.get('uid') == uid]
        if len(row) > 0:
            row = row[0]
        elif uid == 'general' \
                and hasattr(self, 'getResultsInterpretation') \
                and self.getResultsInterpretation():
            row = {'uid': uid, 'richtext': self.getResultsInterpretation()}
        else:
            row = {'uid': uid, 'richtext': ''}
        return row

    def getAnalysisServiceSettings(self, uid):
        """Returns a dictionary with the settings for the analysis service that
        match with the uid provided.

        If there are no settings for the analysis service and
        analysis requests:

        1. looks for settings in AR's ARTemplate. If found, returns the
           settings for the AnalysisService set in the Template
        2. If no settings found, looks in AR's ARProfile. If found, returns the
           settings for the AnalysisService from the AR Profile. Otherwise,
           returns a one entry dictionary with only the key 'uid'
        """
        sets = [s for s in self.getAnalysisServicesSettings()
                if s.get('uid', '') == uid]

        # Created by using an ARTemplate?
        if not sets and self.getTemplate():
            adv = self.getTemplate().getAnalysisServiceSettings(uid)
            sets = [adv] if 'hidden' in adv else []

        # Created by using an AR Profile?
        if not sets and self.getProfiles():
            adv = []
            adv += [profile.getAnalysisServiceSettings(uid) for profile in
                    self.getProfiles()]
            sets = adv if 'hidden' in adv[0] else []

        return sets[0] if sets else {'uid': uid}

    # TODO Sample Cleanup - Remove (Use getContainer instead)
    def getContainers(self):
        """This functions returns the containers from the analysis request's
        analyses

        :returns: a list with the full partition objects
        """
        return self.getContainer() and [self.getContainer] or []

    def isAnalysisServiceHidden(self, uid):
        """Checks if the analysis service that match with the uid provided must
        be hidden in results. If no hidden assignment has been set for the
        analysis in this request, returns the visibility set to the analysis
        itself.

        Raise a TypeError if the uid is empty or None

        Raise a ValueError if there is no hidden assignment in this request or
        no analysis service found for this uid.
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
                raise ValueError('{} is not valid'.format(uid))
        return sets.get('hidden', False)

    def getRejecter(self):
        """If the Analysis Request has been rejected, returns the user who did the
        rejection. If it was not rejected or the current user has not enough
        privileges to access to this information, returns None.
        """
        wtool = getToolByName(self, 'portal_workflow')
        mtool = getToolByName(self, 'portal_membership')
        # noinspection PyBroadException
        try:
            review_history = wtool.getInfoFor(self, 'review_history')
        except:  # noqa FIXME: remove blind except!
            return None
        for items in review_history:
            action = items.get('action')
            if action != 'reject':
                continue
            actor = items.get('actor')
            return mtool.getMemberById(actor)
        return None

    def getReceivedBy(self):
        """
        Returns the User who received the analysis request.
        :returns: the user id
        """
        user = getTransitionUsers(self, 'receive', last_user=True)
        return user[0] if user else ''

    def getDateVerified(self):
        """
        Returns the date of verification as a DateTime object.
        """
        return getTransitionDate(self, 'verify', return_as_datetime=True)

    @security.public
    def getPrioritySortkey(self):
        """Returns the key that will be used to sort the current Analysis
        Request based on both its priority and creation date. On ASC sorting,
        the oldest item with highest priority will be displayed.
        :return: string used for sorting
        """
        priority = self.getPriority()
        created_date = self.created().ISO8601()
        return '%s.%s' % (priority, created_date)

    @security.public
    def setPriority(self, value):
        if not value:
            value = self.Schema().getField('Priority').getDefault(self)
        original_value = self.Schema().getField('Priority').get(self)
        if original_value != value:
            self.Schema().getField('Priority').set(self, value)
            self._reindexAnalyses(['getPrioritySortkey'], True)

    @security.private
    def _reindexAnalyses(self, idxs=None, update_metadata=False):
        if not idxs and not update_metadata:
            return
        if not idxs:
            idxs = []
        analyses = self.getAnalyses()
        catalog = getToolByName(self, CATALOG_ANALYSIS_LISTING)
        for analysis in analyses:
            analysis_obj = analysis.getObject()
            catalog.reindexObject(analysis_obj, idxs=idxs, update_metadata=1)

    def _getCreatorFullName(self):
        """
        Returns the full name of this analysis request's creator.
        """
        return user_fullname(self, self.Creator())

    def _getCreatorEmail(self):
        """
        Returns the email of this analysis request's creator.
        """
        return user_email(self, self.Creator())

    def _getSamplerFullName(self):
        """
        Returns the full name's defined sampler.
        """
        return user_fullname(self, self.getSampler())

    def _getSamplerEmail(self):
        """
        Returns the email of this analysis request's sampler.
        """
        return user_email(self, self.Creator())

    def getPriorityText(self):
        """
        This function looks up the priority text from priorities vocab
        :returns: the priority text or ''
        """
        if self.getPriority():
            return PRIORITIES.getValue(self.getPriority())
        return ''

    def get_ARAttachment(self):
        logger.warn("_ARAttachment is a virtual field used in AR Add. "
                    "It can not hold an own value!")
        return None

    def set_ARAttachment(self, value):
        logger.warn("_ARAttachment is a virtual field used in AR Add. "
                    "It can not hold an own value!")
        return None

    def get_retest(self):
        """Returns the Analysis Request automatically generated because of the
        retraction of the current analysis request
        """
        relationship = "AnalysisRequestRetracted"
        retest = self.getBackReferences(relationship=relationship)
        if retest and len(retest) > 1:
            logger.warn("More than one retest for {0}".format(self.getId()))
        return retest and retest[0] or None

    def getAncestors(self, all_ancestors=True):
        """Returns the ancestor(s) of this Analysis Request
        param all_ancestors: include all ancestors, not only the parent
        """
        parent = self.getParentAnalysisRequest()
        if not parent:
            return list()
        if not all_ancestors:
            return [parent]
        return [parent] + parent.getAncestors(all_ancestors=True)

    def isRootAncestor(self):
        """Returns True if the AR is the root ancestor

        :returns: True if the AR has no more parents
        """
        parent = self.getParentAnalysisRequest()
        if parent:
            return False
        return True

    def getDescendants(self, all_descendants=False):
        """Returns the descendant Analysis Requests

        :param all_descendants: recursively include all descendants
        """

        # N.B. full objects returned here from
        #      `Products.Archetypes.Referenceable.getBRefs`
        #      -> don't add this method into Metadata
        children = self.getBackReferences(
            "AnalysisRequestParentAnalysisRequest")

        descendants = []

        # recursively include all children
        if all_descendants:
            for child in children:
                descendants.append(child)
                descendants += child.getDescendants(all_descendants=True)
        else:
            descendants = children

        return descendants

    def getDescendantsUIDs(self, all_descendants=False):
        """Returns the UIDs of the descendant Analysis Requests

        This method is used as metadata
        """
        descendants = self.getDescendants(all_descendants=all_descendants)
        return map(api.get_uid, descendants)

    def isPartition(self):
        """Returns true if this Analysis Request is a partition
        """
        return not self.isRootAncestor()

    # TODO Remove in favour of getSamplingWorkflowEnabled
    def getSamplingRequired(self):
        """Returns True if the sample of this Analysis Request has to be
        collected by the laboratory personnel
        """
        return self.getSamplingWorkflowEnabled()

    def isOpen(self):
        """Returns whether all analyses from this Analysis Request haven't been
        submitted yet (are in a open status)
        """
        for analysis in self.getAnalyses():
            if ISubmitted.providedBy(api.get_object(analysis)):
                return False
        return True

    def setParentAnalysisRequest(self, value):
        """Sets a parent analysis request, making the current a partition
        """
        parent = self.getParentAnalysisRequest()
        self.Schema().getField("ParentAnalysisRequest").set(self, value)
        if not value:
            noLongerProvides(self, IAnalysisRequestPartition)
            if parent and not parent.getDescendants(all_descendants=False):
                noLongerProvides(self, IAnalysisRequestWithPartitions)
        else:
            alsoProvides(self, IAnalysisRequestPartition)
            parent = self.getParentAnalysisRequest()
            alsoProvides(parent, IAnalysisRequestWithPartitions)

    def getSecondaryAnalysisRequests(self):
        """Returns the secondary analysis requests from this analysis request
        """
        relationship = "AnalysisRequestPrimaryAnalysisRequest"
        return self.getBackReferences(relationship=relationship)

    def setDateReceived(self, value):
        """Sets the date received to this analysis request and to secondary
        analysis requests
        """
        self.Schema().getField('DateReceived').set(self, value)
        for secondary in self.getSecondaryAnalysisRequests():
            secondary.setDateReceived(value)
            secondary.reindexObject(idxs=["getDateReceived", "is_received"])

    def setDateSampled(self, value):
        """Sets the date sampled to this analysis request and to secondary
        analysis requests
        """
        self.Schema().getField('DateSampled').set(self, value)
        for secondary in self.getSecondaryAnalysisRequests():
            secondary.setDateSampled(value)
            secondary.reindexObject(idxs="getDateSampled")

    def setSamplingDate(self, value):
        """Sets the sampling date to this analysis request and to secondary
        analysis requests
        """
        self.Schema().getField('SamplingDate').set(self, value)
        for secondary in self.getSecondaryAnalysisRequests():
            secondary.setSamplingDate(value)
            secondary.reindexObject(idxs="getSamplingDate")

    def getSelectedRejectionReasons(self):
        """Returns a list with the selected rejection reasons, if any
        """
        reasons = self.getRejectionReasons()
        if not reasons:
            return []
        return reasons[0].get("selected", [])

    def getOtherRejectionReasons(self):
        """Returns other rejection reasons custom text, if any
        """
        reasons = self.getRejectionReasons()
        if not reasons:
            return ""
        return reasons[0].get("other", "")

    def createAttachment(self, filedata, filename="", **kw):
        """Add a new attachment to the sample

        :param filedata: Raw filedata of the attachment (not base64)
        :param filename: Filename + extension, e.g. `image.png`
        :param kw: Additional keywords set to the attachment
        :returns: New created and added attachment
        """
        # Add a new Attachment
        attachment = api.create(self.getClient(), "Attachment")
        attachment.setAttachmentFile(filedata)
        fileobj = attachment.getAttachmentFile()
        fileobj.filename = filename
        attachment.edit(**kw)
        attachment.processForm()
        self.addAttachment(attachment)
        return attachment

    def addAttachment(self, attachment):
        """Adds an attachment or a list of attachments to the Analysis Request
        """
        if not isinstance(attachment, (list, tuple)):
            attachment = [attachment]

        original = self.getAttachment() or []

        # Function addAttachment can accept brain, objects or uids
        original = map(api.get_uid, original)
        attachment = map(api.get_uid, attachment)

        # Boil out attachments already assigned to this Analysis Request
        attachment = filter(lambda at: at not in original, attachment)
        if attachment:
            original.extend(attachment)
            self.setAttachment(original)

    def setResultsInterpretationDepts(self, value):
        """Custom setter which converts inline images to attachments

        https://github.com/senaite/senaite.core/pull/1344

        :param value: list of dictionary records
        """
        if not isinstance(value, list):
            raise TypeError("Expected list, got {}".format(type(value)))

        # Convert inline images -> attachment files
        records = []
        for record in value:
            # N.B. we might here a ZPublisher record. Converting to dict
            #      ensures we can set values as well.
            record = dict(record)
            # Handle inline images in the HTML
            html = record.get("richtext", "")
            # Process inline images to attachments
            record["richtext"] = self.process_inline_images(html)
            # append the processed record for storage
            records.append(record)

        # set the field
        self.getField("ResultsInterpretationDepts").set(self, records)

    def process_inline_images(self, html):
        """Convert inline images in the HTML to attachments

        https://github.com/senaite/senaite.core/pull/1344

        :param html: The richtext HTML
        :returns: HTML with converted images
        """
        # Check for inline images
        inline_images = re.findall(IMG_DATA_SRC_RX, html)

        # convert to inline images -> attachments
        for data_type, data in inline_images:
            # decode the base64 data to filedata
            filedata = base64.decodestring(data)
            # extract the file extension from the data type
            extension = data_type.lstrip("data:image/").rstrip(";base64,")
            # generate filename + extension
            filename = "attachment.{}".format(extension or "png")
            # create a new attachment
            attachment = self.createAttachment(filedata, filename)
            # ignore the attachment in report
            attachment.setReportOption("i")
            # remove the image data base64 prefix
            html = html.replace(data_type, "")
            # remove the base64 image data with the attachment URL
            html = html.replace(data, "{}/AttachmentFile".format(
                attachment.absolute_url()))
            size = attachment.getAttachmentFile().get_size()
            logger.info("Converted {:.2f} Kb inline image for {}"
                        .format(size/1024, api.get_url(self)))

        # convert relative URLs to absolute URLs
        # N.B. This is actually a TinyMCE issue, but hardcoded in Plone:
        #      https://www.tiny.cloud/docs/configure/url-handling/#relative_urls
        image_sources = re.findall(IMG_SRC_RX, html)

        # we need a trailing slash so that urljoin does not remove the last segment
        base_url = "{}/".format(api.get_url(self))

        for src in image_sources:
            if re.match("(http|https|data)", src):
                continue
            obj = self.restrictedTraverse(src, None)
            if obj is None:
                continue
            # ensure we have an absolute URL
            html = html.replace(src, urljoin(base_url, src))

        return html

    def getProgress(self):
        """Returns the progress in percent of all analyses
        """
        review_state = api.get_review_status(self)

        # Consider final states as 100%
        # https://github.com/senaite/senaite.core/pull/1544#discussion_r379821841
        if review_state in FINAL_STATES:
            return 100

        numbers = self.getAnalysesNum()

        num_analyses = numbers[1] or 0
        if not num_analyses:
            return 0

        # [verified, total, not_submitted, to_be_verified]
        num_to_be_verified = numbers[3] or 0
        num_verified = numbers[0] or 0

        # 2 steps per analysis (submit, verify) plus one step for publish
        max_num_steps = (num_analyses * 2) + 1
        num_steps = num_to_be_verified + (num_verified * 2)
        if not num_steps:
            return 0
        if num_steps > max_num_steps:
            return 100
        return (num_steps * 100) / max_num_steps


registerType(AnalysisRequest, PROJECTNAME)
