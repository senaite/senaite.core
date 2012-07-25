"""Sample represents a physical sample submitted for testing
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from datetime import timedelta
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt,dt2DT
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims.config import ManageBika, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.utils import sortable_title, pretty_user_name_or_id
import sys
import time
from zope.interface import implements
from bika.lims.interfaces import ISample
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('SampleID',
        required = 1,
        searchable = True,
        widget = StringWidget(
            label = _("Sample ID"),
            description = _("The ID assigned to the client's sample by the lab"),
            visible = {'edit':'hidden'},
        ),
    ),
    StringField('ClientReference',
        searchable = True,
        widget = StringWidget(
            label = _("Client Reference"),
        ),
    ),
    StringField('ClientSampleID',
        searchable = True,
        widget = StringWidget(
            label = _("Client SID"),
        ),
    ),
    ReferenceField('LinkedSample',
        vocabulary_display_path_bound = sys.maxint,
        multiValue = 1,
        allowed_types = ('Sample',),
        relationship = 'SampleSample',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = _("Linked Sample"),
        ),
    ),
    ReferenceField('SampleType',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'SampleSampleType',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Sample Type"),
        ),
    ),
    ComputedField('SampleTypeTitle',
        searchable = True,
        expression = "here.getSampleType() and here.getSampleType().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ReferenceField('SamplePoint',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SamplePoint',),
        relationship = 'SampleSamplePoint',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Sample Point"),
        ),
    ),
    ComputedField('SamplePointTitle',
        searchable = True,
        expression = "here.getSamplePoint() and here.getSamplePoint().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    BooleanField('SamplingWorkflowEnabled',
    ),
    DateTimeField('DateSampled',
    ),
    StringField('Sampler',
        searchable=True
    ),
    DateTimeField('SamplingDate',
        widget = DateTimeWidget(
            label = _("Sampling Date"),
            visible = {'edit':'hidden'},
        ),
    ),
    ReferenceField('SamplingDeviation',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SamplingDeviation',),
        relationship = 'SampleSamplingDeviation',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _('Sampling Deviation'),
        ),
    ),
    DateTimeField('DateReceived',
        widget = DateTimeWidget(
            label = _("Date Received"),
            visible = {'edit':'hidden'},
        ),
    ),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/html",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _('Remarks'),
            append_only = True,
        ),
    ),
    ComputedField('ClientUID',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleTypeUID',
        expression = 'context.getSampleType().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SamplePointUID',
        expression = 'context.getSamplePoint() and context.getSamplePoint().UID() or None',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    BooleanField('Composite',
        default = False,
        widget = BooleanWidget(
            label = _("Composite"),
        ),
    ),
    DateTimeField('DateExpired',
        widget = DateTimeWidget(
            label = _("Date Expired"),
            visible = {'edit':'hidden'},
        ),
    ),
    ComputedField('DisposalDate',
        expression = 'context.disposal_date()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    DateTimeField('DateDisposed',
        widget = DateTimeWidget(
            label = _("Date Disposed"),
            visible = {'edit':'hidden'},
        ),
    ),
    BooleanField('AdHoc',
        default=False,
        widget=BooleanWidget(
            label=_("Ad-Hoc"),
        ),
    ),
))

schema['title'].required = False

class Sample(BaseFolder, HistoryAwareMixin):
    implements(ISample)
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

    def Title(self):
        """ Return the Sample ID as title """
        return self.getId()

    # Forms submit Title Strings which need
    # to be converted to objects somewhere along the way...
    def setSampleType(self, value, **kw):
        """ convert SampleType title to UID
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        sampletype = bsc(portal_type = 'SampleType', title = value)
        value = sampletype[0].UID
        return self.Schema()['SampleType'].set(self, value)

    # Forms submit Title Strings which need
    # to be converted to objects somewhere along the way...
    def setSamplePoint(self, value, **kw):
        """ convert SamplePoint title to UID
        """
        sp_uid = None
        if value:
            bsc = getToolByName(self, 'bika_setup_catalog')
            samplepoints = bsc(portal_type = 'SamplePoint', title = value)
            if samplepoints:
                sp_uid = samplepoints[0].UID
        return self.Schema()['SamplePoint'].set(self, sp_uid)

    security.declarePublic('getAnalysisRequests')
    def getAnalysisRequests(self):
        tool = getToolByName(self, REFERENCE_CATALOG)
        ar = ''
        ars = []
        uids = [uid for uid in
                tool.getBackReferences(self, 'AnalysisRequestSample')]
        for uid in uids:
            reference = uid
            ar = tool.lookupObject(reference.sourceUID)
            ars.append(ar)
        return ars

    security.declarePublic('getAnalyses')
    def getAnalyses(self, contentFilter):
        """ return list of all analyses against this sample
        """
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += ar.getAnalyses(**contentFilter)
        return analyses

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
        ar_ids = [AR.id for AR in ARs]
        ar_ids.sort()
        try:
            last_ar_number = int(ar_ids[-1].split("-")[-1])
        except ValueError:
            return 0
        return last_ar_number

atapi.registerType(Sample, PROJECTNAME)
