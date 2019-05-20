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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

"""Sample represents a physical sample submitted for testing
"""

from datetime import timedelta
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.api import get_object_by_uid
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.utils import t, getUsers
from Products.ATExtensions.field import RecordsField
from bika.lims.browser.widgets.datetimewidget import DateTimeWidget
from bika.lims.browser.widgets import RejectionWidget
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ISample
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt, dt2DT
from Products.CMFCore import permissions
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

from bika.lims.browser.fields import DateTimeField
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget

import sys
from bika.lims.utils import to_unicode
from bika.lims.interfaces import IDoNotSupportSnapshots

schema = BikaSchema.copy() + Schema((
    # TODO This field is only for v1.3.0 migration purposes
    # bika_catalog contains an "isValid" index. We will take advantage of this
    # index to keep track of the Samples that have been migrated already in
    # order to prevent an unnecessary reimport when v1.3.0 is rerun.
    # This field is used by `isValid` function
    BooleanField('Migrated',
        default = False,
    ),
    StringField('SampleID',
        required=1,
        searchable=True,
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Sample ID"),
            description=_("The ID assigned to the client's sample by the lab"),
            visible=False,
            render_own_label=True,
        ),
    ),
    StringField('ClientReference',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Client Reference"),
            visible=False,
            render_own_label=True,
        ),
    ),
    StringField('ClientSampleID',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget=StringWidget(
            label=_("Client SID"),
            visible=False,
            render_own_label=True,
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
            visible=False,
            catalog_name='bika_setup_catalog',
            base_query={'is_active': True},
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
            visible=False,
            catalog_name='bika_setup_catalog',
            base_query={'is_active': True},
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
            visible=False,
            catalog_name='bika_setup_catalog',
            base_query={'is_active': True},
            showOn=True,
        ),
    ),
    BooleanField('SamplingWorkflowEnabled',
                 default_method='getSamplingWorkflowEnabledDefault'
    ),
    DateTimeField('DateSampled',
        mode="rw",
        read_permission=permissions.View,
        widget = DateTimeWidget(
            label=_("Date Sampled"),
            show_time=True,
            size=20,
            visible=False,
            render_own_label=True,
        ),
    ),
    StringField('Sampler',
        mode="rw",
        read_permission=permissions.View,
        vocabulary='getSamplers',
        widget=BikaSelectionWidget(
            format='select',
            label=_("Sampler"),
            visible=False,
            render_own_label=True,
        ),
    ),
    StringField('ScheduledSamplingSampler',
        mode="rw",
        read_permission=permissions.View,
        vocabulary='getSamplers',
        widget=BikaSelectionWidget(
            description=_("Define the sampler supposed to do the sample in "
                          "the scheduled date"),
            format='select',
            label=_("Sampler for scheduled sampling"),
            visible=False,
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
            visible=False,
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
            visible=False,
            catalog_name='bika_setup_catalog',
            base_query={'is_active': True},
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
            visible=False,
            catalog_name='bika_setup_catalog',
            base_query={'is_active': True},
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
            visible=False,
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
            show_time=True,
            datepicker_nofuture=1,
            visible=False,
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
            visible=False,
            render_own_label=True,
        ),
    ),
    DateTimeField('DateExpired',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label=_("Date Expired"),
            visible=False,
            render_own_label=True,
        ),
    ),
    ComputedField('DisposalDate',
        expression = 'context.disposal_date()',
        widget=DateTimeWidget(
            visible=False,
            render_own_label=True,
        ),
    ),
    DateTimeField('DateDisposed',
        mode="rw",
        read_permission=permissions.View,
        write_permission=permissions.ModifyPortalContent,
        widget = DateTimeWidget(
            label=_("Date Disposed"),
            visible=False,
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
            visible=False,
           render_own_label=True,
        ),
    ),
    RemarksField(
        'Remarks',
        searchable=True,
        widget=RemarksWidget(
            label=_("Remarks"),
        ),
    ),
    RecordsField(
        'RejectionReasons',
        widget = RejectionWidget(
            label=_("Sample Rejection"),
            description = _("Set the Sample Rejection workflow and the reasons"),
            render_own_label=False,
            visible=False,
        ),
    ),
))


schema['title'].required = False


class Sample(BaseFolder, HistoryAwareMixin):
    implements(ISample, IDoNotSupportSnapshots)
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

    security.declarePublic('getAnalysisRequests')

    def getAnalysisRequests(self):
        backrefs = get_backreferences(self, 'AnalysisRequestSample')
        ars = map(get_object_by_uid, backrefs)
        return ars

    security.declarePublic('getAnalyses')

    def getAnalyses(self, contentFilter=None, **kwargs):
        """ return list of all analyses against this sample
        """
        # contentFilter and kwargs are combined.  They both exist for
        # compatibility between the two signatures; kwargs has been added
        # to be compatible with how getAnalyses() is used everywhere else.
        cf = contentFilter if contentFilter else {}
        cf.update(kwargs)
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses.extend(ar.getAnalyses(**cf))
        return analyses

    def getSamplers(self):
        return getUsers(self, ['Sampler', ])

    def disposal_date(self):
        """Returns the date the retention period ends for this sample based on
        the retention period from the Sample Type. If the sample hasn't been
        collected yet, returns None
        """
        date_sampled = self.getDateSampled()
        if not date_sampled:
            return None

        # TODO Preservation - preservation's retention period has priority over
        # sample type's preservation period

        retention_period = self.getSampleType().getRetentionPeriod() or {}
        retention_period_delta = timedelta(
            days=int(retention_period.get("days", 0)),
            hours=int(retention_period.get("hours", 0)),
            minutes=int(retention_period.get("minutes", 0))
        )
        return dt2DT(DT2dt(date_sampled) + retention_period_delta)


    # TODO This method is only for v1.3.0 migration purposes
    # bika_catalog contains an "isValid" index. We will take advantage of this
    # index to keep track of the Samples that have been migrated already in
    # order to prevent an unnecessary reimport when v1.3.0 is rerun.
    def isValid(self):
        return self.getMigrated()


atapi.registerType(Sample, PROJECTNAME)
