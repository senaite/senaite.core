from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget, RecordsField
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    ComputedField('RequestID',
        expression = 'here.getRequestID()',
        widget = ComputedWidget(
            visible = True,
        ),
    ),
    FileField('AttachmentFile',
        widget = FileWidget(
            label=_("Attachment"),
        ),
    ),
    ReferenceField('AttachmentType',
        required = 0,
        allowed_types = ('AttachmentType',),
        relationship = 'AttachmentAttachmentType',
        widget = ReferenceWidget(
            label=_("Attachment Type"),
        ),
    ),
    StringField('AttachmentKeys',
        searchable = True,
        widget = StringWidget(
            label=_("Attachment Keys"),
        ),
    ),
    DateTimeField('DateLoaded',
        required = 1,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label=_("Date Loaded"),
        ),
    ),
    ComputedField('AttachmentTypeUID',
        expression="context.getAttachmentType().UID() if context.getAttachmentType() else ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientUID',
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
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Id """
        return safe_unicode(self.getId()).encode('utf-8')

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
        workflow = getToolByName(self, 'portal_workflow')
        return workflow.getInfoFor(parent, 'review_state', '')

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()


atapi.registerType(Attachment, PROJECTNAME)
