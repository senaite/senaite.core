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
    DateTimeField('SamplingDate',
        widget = DateTimeWidget(
            label = _("Sampling Date"),
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateReceived',
        widget = DateTimeWidget(
            label = _("Date Received"),
            visible = {'edit':'hidden'},
        ),
    ),
    IntegerField('LastARNumber',
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
    ComputedField('DisposalDate',
        expression = 'context.disposal_date()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    DateTimeField('DateExpired',
        widget = DateTimeWidget(
            label = _("Date Expired"),
            visible = {'edit':'hidden'},
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

    def setSampleType(self, value, **kw):
        """ convert SampleType title to UID
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        sampletype = bsc(portal_type = 'SampleType', Title = value)
        value = sampletype[0].UID
        return self.Schema()['SampleType'].set(self, value)

    def setSamplePoint(self, value, **kw):
        """ convert SamplePoint title to UID
        """
        sp_uid = None
        if value:
            bsc = getToolByName(self, 'bika_setup_catalog')
            samplepoints = bsc(portal_type = 'SamplePoint', Title = value)
            if samplepoints:
                sp_uid = samplepoints[0].UID
        return self.Schema()['SamplePoint'].set(self, sp_uid)

    def getDateSampled(self):
        """ Return the dates that our Partitions were sampled.
        """
        props = getToolByName(self, 'portal_properties').site_properties
        localTimeFormat = props.getProperty('localTimeFormat')
        dates = dict(
            [(p.getDateSampled().asdatetime().strftime(localTimeFormat), p.id)
             for p in self.objectValues("SamplePartition")
             if p.getDateSampled()])
        return ", ".join(dates.keys())

    def getSampler(self):
        """ Return the users recorded as sampling our Partitions.
        """
        users = [(pretty_user_name_or_id(self, p.getSampler()), p.id)
                 for p in self.objectValues("SamplePartition")
                 if p.getSampler()]
        users = dict(users)
        return ", ".join(users.keys())

    def getDatePreserved(self):
        """ Return the dates that our Partitions were preserved.
        """
        dates = dict([(p.getDatePreserved(), p.id)
                      for p in self.objectValues("SamplePartition")
                      if p.getDatePreserved()])
        return ", ".join(dates.keys())

    def getPreserver(self):
        """ Return the users recorded as Preserving our Partitions.
        """
        users = [(pretty_user_name_or_id(self, p.getPreserver()), p.id)
                      for p in self.objectValues("SamplePartition")
                      if p.getPreserver()]
        users = dict(users)
        return ", ".join(users.keys())

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
    def getAnalyses(self, full_objects=True):
        """ return list of analyses for all partitions in this sample
        ignore full_objects
        """
        analyses = []
        for part in self.objectValues('SamplePartition'):
            analyses += part.getAnalyses()
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

atapi.registerType(Sample, PROJECTNAME)
