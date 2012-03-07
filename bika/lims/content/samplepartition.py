from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from datetime import timedelta
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt,dt2DT
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
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
        referenceClass=HoldingReference,
        required=1,
        multiValued=0,
    ),
    ReferenceField('Preservation',
        allowed_types=('Preservation',),
        relationship='SamplePartitionPreservation',
        referenceClass=HoldingReference,
        required=0,
        multiValued=0,
    ),
    ReferenceField('Analyses',
        allowed_types=('Analysis',),
        relationship='SamplePartitionAnalysis',
        referenceClass=HoldingReference,
        required=0,
        multiValued=1,
    ),
    DateTimeField('DatePreserved',
    ),
    StringField('PreservedByUser',
        searchable=True
    ),
    DurationField('RetentionPeriod',
    ),
    ComputedField('ExpiryDate',
        expression = 'context.expiry_date()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('DisposalDate',
        expression = 'context.disposal_date()',
        widget = ComputedWidget(
            visible = False,
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
),
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
        return self.getId()

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

        DateSampled = self.aq_parent.getDateSampled()

        # fallback to sampletype retention period
        st_retention = self.aq_parent.getSampleType().getRetentionPeriod()
        pres = self.getPreservation()
        pres_retention = pres and pres.getRetentionPeriod() or None

        #XXX
        part_retention = None

        rp = pres_retention and pres_retention or None
        rp = rp or st_retention


        td = timedelta(
            days = rp['days'] and int(rp['days']) or 0,
            hours = rp['hours'] and int(rp['hours']) or 0,
            minutes = rp['minutes'] and int(rp['minutes']) or 0)
        dis_date = DateSampled and dt2DT(DT2dt(DateSampled) + td) or None
        return dis_date

    security.declarePublic('expiry_date')
    def expiry_date(self):
        """ return expiry date """
        return 0

    security.declarePublic('current_user')
    def current_user(self):
        """ get the current user """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        return user_id

    security.declarePublic('getPreservedByName')
    def getPreservedByName(self):
        """ get the name of the user who preserved this partition """
        uid = self.getPreservedByUser()
        if uid in (None, ''):
            return ' '

        r = self.portal_catalog(portal_type = 'Contact', getUsername = uid)
        if len(r) == 1:
            return r[0].Title

        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getMemberById(uid)
        if member is None:
            return uid
        else:
            fullname = member.getProperty('fullname')
        if fullname in (None, ''):
            return uid
        return fullname

registerType(SamplePartition, PROJECTNAME)
