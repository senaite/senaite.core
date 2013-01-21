from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from datetime import timedelta
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt,dt2DT
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ISamplePartition
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    ReferenceField('Container',
        allowed_types=('Container',),
        relationship='SamplePartitionContainer',
        #referenceClass=HoldingReference,
        required=1,
        multiValued=0,
    ),
    ReferenceField('Preservation',
        allowed_types=('Preservation',),
        relationship='SamplePartitionPreservation',
        #referenceClass=HoldingReference,
        required=0,
        multiValued=0,
    ),
    BooleanField('Separate',
        default=False
    ),
    ReferenceField('Analyses',
        allowed_types=('Analysis',),
        relationship='SamplePartitionAnalysis',
        #referenceClass=HoldingReference,
        required=0,
        multiValued=1,
    ),
    DateTimeField('DatePreserved',
    ),
    StringField('Preserver',
        searchable=True
    ),
    DurationField('RetentionPeriod',
    ),
    ComputedField('DisposalDate',
        expression = 'context.disposal_date()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
)
)

schema['title'].required = False

class SamplePartition(BaseContent, HistoryAwareMixin):
    implements(ISamplePartition)
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
        return safe_unicode(self.getId()).encode('utf-8')

    security.declarePublic('getAnalyses')
    def getAnalyses(self):
        """ return list of titles of analyses linked to this sample Partition """
        analyses = self.getBackReferences("AnalysisSamplePartition")
        analyses.sort()
        return analyses

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    security.declarePublic('disposal_date')
    def disposal_date(self):
        """ return disposal date """

        DateSampled = self.getDateSampled()

        # fallback to sampletype retention period
        st_retention = self.aq_parent.getSampleType().getRetentionPeriod()

        # but prefer retention period from preservation
        pres = self.getPreservation()
        pres_retention = pres and pres.getRetentionPeriod() or None

        rp = pres_retention and pres_retention or None
        rp = rp or st_retention

        td = timedelta(
            days = 'days' in rp and int(rp['days']) or 0,
            hours = 'hours' in rp and int(rp['hours']) or 0,
            minutes = 'minutes' in rp and int(rp['minutes']) or 0)

        dis_date = DateSampled and dt2DT(DT2dt(DateSampled) + td) or None
        return dis_date

registerType(SamplePartition, PROJECTNAME)
