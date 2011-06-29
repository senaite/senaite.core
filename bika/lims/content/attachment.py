from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget, RecordsField
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME, ManageBika, ManageAnalysisRequests

schema = BikaSchema.copy() + Schema((
    ComputedField('RequestID',
        index = 'FieldIndex',
        expression = 'here.getRequestID()',
        widget = ComputedWidget(
            visible = True,
        ),
    ),
    FileField('AttachmentFile',
        widget = FileWidget(
            label = 'Attachment',
            label_msgid = 'label_attachment',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('AttachmentType',
        required = 1,
        allowed_types = ('AttachmentType',),
        relationship = 'AttachmentAttachmentType',
        widget = ReferenceWidget(
            label = 'Attachment Type',
            label_msgid = 'label_attachment_type',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('AttachmentKeys',
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Attachment Keys',
            label_msgid = 'label_attachment_keys',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    DateTimeField('DateLoaded',
        required = 1,
        default_method = 'current_date',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date loaded',
            label_msgid = 'label_dateloaded',
            visible = {'edit':'hidden'},
        ),
    ),
    ComputedField('AttachmentTypeUID',
        index = 'FieldIndex',
        expression = 'context.getAttachmentType().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'here.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

schema['id'].required = False
schema['title'].required = False

class Attachment(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    def Title(self):
        """ Return the Id """
        return self.getId()

    def getTextTitle(self):
        """ Return the request and possibly analayis title as title """
        requestid = self.getRequestID()
        if requestid:
            analysis = self.getAnalysis()
            if analysis:
                return '%s - %s' % (requestid, analysis.Title())
            else:
                return requestid
        else:
            return None

    def getRequest(self):
        """ Return the AR to which this is linked """
        """ there is a short time between creation and linking """
        """ when it is not linked """
        tool = getToolByName(self, REFERENCE_CATALOG)
        uids = [uid for uid in
                tool.getBackReferences(self, 'AnalysisRequestAttachment')]
        if len(uids) == 1:
            reference = uids[0]
            ar = tool.lookupObject(reference.sourceUID)
            return ar
        else:
            uids = [uid for uid in
                    tool.getBackReferences(self, 'AnalysisAttachment')]
            if len(uids) == 1:
                reference = uids[0]
                analysis = tool.lookupObject(reference.sourceUID)
                ar = analysis.aq_parent
                return ar
        return None

    def getRequestID(self):
        """ Return the ID of the request to which this is linked """
        ar = self.getRequest()
        if ar:
            return ar.getRequestID()
        else:
            return None

    def getAnalysis(self):
        """ Return the analysis to which this is linked """
        """  it may not be linked to an analysis """
        tool = getToolByName(self, REFERENCE_CATALOG)
        uids = [uid for uid in
                tool.getBackReferences(self, 'AnalysisAttachment')]
        if len(uids) == 1:
            reference = uids[0]
            analysis = tool.lookupObject(reference.sourceUID)
            return analysis
        return None

    def getParentState(self):
        """ Return the review state of the object - analysis or AR """
        """ to which this is linked """
        tool = getToolByName(self, REFERENCE_CATALOG)
        uids = [uid for uid in
                tool.getBackReferences(self, 'AnalysisAttachment')]
        if len(uids) == 1:
            reference = uids[0]
            parent = tool.lookupObject(reference.sourceUID)
        else:
            uids = [uid for uid in
                    tool.getBackReferences(self, 'AnalysisRequestAttachment')]
            if len(uids) == 1:
                reference = uids[0]
                parent = tool.lookupObject(reference.sourceUID)
        wf_tool = getToolByName(self, 'portal_workflow')
        return wf_tool.getInfoFor(parent, 'review_state', '')

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()


atapi.registerType(Attachment, PROJECTNAME)
