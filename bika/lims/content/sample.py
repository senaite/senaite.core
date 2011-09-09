"""Sample represents a physical sample submitted for testing
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
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
        index = 'FieldIndex:brains',
        searchable = True,
        widget = StringWidget(
            label = 'Sample ID',
            label_msgid = 'label_sampleid',
            description = 'The ID assigned to the client''s sample by the lab',
            description_msgid = 'help_sampleid',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden'},
        ),
    ),
    StringField('ClientReference',
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Client Reference',
            label_msgid = 'label_clientreference',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('ClientSampleID',
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Client Sample ID',
            label_msgid = 'label_clientsampleid',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('SubmittedByUser',
        index = 'FieldIndex',
        searchable = True,
    ),
    ReferenceField('LinkedSample',
        vocabulary_display_path_bound = sys.maxint,
        multiValue = 1,
        allowed_types = ('Sample',),
        relationship = 'SampleSample',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = 'Linked Sample',
            label_msgid = 'label_linkedsample',
            i18n_domain = I18N_DOMAIN,
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
            label = 'Sample Type',
            label_msgid = 'label_type',
            i18n_domain = I18N_DOMAIN,
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
            label = 'Sample Point',
            label_msgid = 'label_type',
            i18n_domain = I18N_DOMAIN,
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
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date submitted',
            label_msgid = 'label_datesubmitted',
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateSampled',
        index = 'DateIndex',
        with_time = False,
        widget = DateTimeWidget(
            label = 'Date sampled',
            label_msgid = 'label_datesampled',
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateReceived',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date received',
            label_msgid = 'label_datereceived',
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DisposalDate',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Disposal date',
            label_msgid = 'label_disposal_date',
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateExpired',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date expired',
            label_msgid = 'label_dateexpired',
            visible = {'edit':'hidden'},
        ),
    ),
    IntegerField('LastARNumber',
        index = 'FieldIndex',
    ),
    TextField('Notes',
        widget = TextAreaWidget(
            label = 'Notes'
        ),
    ),
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleTypeUID',
        index = 'FieldIndex',
        expression = 'context.getSampleType().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SamplePointUID',
        index = 'FieldIndex',
        expression = 'context.getSamplePoint() and context.getSamplePoint().UID() or None',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))

schema['title'].required = False

class Sample(BaseFolder):
    implements(ISample)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    def Title(self):
        """ Return the Sample ID as title """
        return self.getSampleID()

    def setSampleType(self, value, **kw):
        """ convert SampleType title to UID
        """
        portal = self.portal_url.getPortalObject()
        rs = self.portal_catalog(
            portal_type = 'SampleType',
            Title = value
        )
        value = rs[0].UID

        return self.Schema()['SampleType'].set(self, value)

    def setSamplePoint(self, value, **kw):
        """ convert SamplePoint title to UID
        """
        sp_uid = None
        if value:
            portal = self.portal_url.getPortalObject()
            sps = self.portal_catalog(
                portal_type = 'SamplePoint',
                sortable_title = sortable_title(portal, value)
            )
            if sps:
                sp_uid = sps[0].UID
            else:
                # add the SamplePoint
                folder = portal.bika_samplepoints
                sp_id = folder.generateUniqueId('SamplePoint')
                folder.invokeFactory(id = sp_id, type_name = 'SamplePoint')
                sp = folder[sp_id]
                sp.processForm()
                sp.edit(
                    title = value)
                sp_uid = sp.UID()
                sp.reindexObject()

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
        dis_date = self.getDateSubmitted() + int(delay)
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

