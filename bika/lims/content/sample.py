"""Sample represents a physical sample submitted for testing
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName, getToolByName
from bika.lims.config import I18N_DOMAIN, ManageBika, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.utils import sortable_title
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
            description = _("The ID assigned to the client''s sample by the lab"),
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
    StringField('SubmittedByUser',
        searchable = True,
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
        expression = "here.getSamplePoint() and here.getSamplePoint().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    DateTimeField('DateSubmitted',
        required = 1,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = _("Date submitted"),
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateSampled',
        with_time = False,
        widget = DateTimeWidget(
            label = _("Date sampled"),
            visible = {'edit':'hidden'},
        ),
    ),
    StringField('SampledByUser',
        index = 'FieldIndex',
        searchable = True,
    ),
    DateTimeField('DateReceived',
        widget = DateTimeWidget(
            label = _("Date received"),
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DisposalDate',
        widget = DateTimeWidget(
            label = _("Disposal date"),
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateExpired',
        widget = DateTimeWidget(
            label = _("Date expired"),
            visible = {'edit':'hidden'},
        ),
    ),
    IntegerField('LastARNumber',
    ),
    TextField('Notes',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = _("Notes")
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
            label = "Composite",
            label_msgid = "label_composite",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))

schema['title'].required = False

class Sample(BaseFolder, HistoryAwareMixin):
    implements(ISample)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def Title(self):
        """ Return the Sample ID as title """
        return self.getSampleID()

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

    # XXX not used anywhere???
    security.declarePublic('getAnalyses')
    def getAnalyses(self):
        """ return list of titles of analyses linked to this sample """
        ars = self.getAnalysisRequests()
        analyses = []
        for ar in ars:
            for analysis in ar.getAnalyses():
                analyses.append(analysis.Title())
        """ sort, and remove duplicates """
        if analyses:
           analyses.sort()
           last = analyses[-1]
           for i in range(len(analyses) - 2, -1, -1):
               if last == analyses[i]: del analyses[i]
               else: last = analyses[i]

        return analyses

##     workflow methods
##
##    def workflow_script_receive(self, state_info):
##        """ receive sample """
##        self.setDateReceived(DateTime())
##        self.reindexObject()
##        self._delegateWorkflowAction('receive')

    def workflow_script_expire(self, state_info):
        """ expire sample """
        self.setDateExpired(DateTime())
        self.reindexObject()

##    def _delegateWorkflowAction(self, action_id):
##        """ Notify the analysisrequests that the sample has been received """
##        if action_id not in ('receive'):
##            return
##        tool = getToolByName(self, REFERENCE_CATALOG)
##        wf_tool = self.portal_workflow
##        uids = [uid for uid in
##                tool.getBackReferences(self, 'AnalysisRequestSample')]
##        for uid in uids:
##            reference = uid
##            ar = tool.lookupObject(reference.sourceUID)
##            review_state = wf_tool.getInfoFor(ar, 'review_state', '')
##            if review_state != 'sample_due':
##                #from zLOG import LOG, WARNING; LOG('bika', WARNING,
##                #'Escalate workflow action sample receive. ',
##                #'Analysis request %s in state: %s' % (self.getId(), review_state))
##                continue
##            try:
##                wf_tool.doActionFor(ar, action_id)
##                ar.reindexObject()
##            except WorkflowException, msg:
##                from zLOG import LOG; LOG('INFO', 0, '', msg)
##                pass
##            # ar._delegateWorkflowAction('receive_sample')

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    security.declarePublic('disposal_date')
    def disposal_date(self):
        """ return disposal date """
        delay = self.getSampleType().getRetentionPeriod()
        dis_date = self.getDateSampled() + int(delay)
        return dis_date

    security.declarePublic('current_user')
    def current_user(self):
        """ get the current user """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        return user_id

    security.declarePublic('getSubmittedByName')
    def getSubmittedByName(self):
        """ get the name of the user who submitted the sample """
        uid = self.getSubmittedByUser()
        if uid is None:
            return ' '

        if uid == '':
            return ' '

        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = uid
        )
        if len(r) == 1:
            return r[0].Title

        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getMemberById(uid)
        if member is None:
            return uid
        else:
            fullname = member.getProperty('fullname')
        if fullname is None:
            return uid
        if fullname == '':
            return uid
        return fullname


atapi.registerType(Sample, PROJECTNAME)

