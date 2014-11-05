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

from bika.lims.browser.widgets import ReferenceWidget as BikaReferenceWidget

schema = BikaSchema.copy() + Schema((
#     ComputedField('RequestID',
#         expression = 'here.getRequestID()',
#         widget = ComputedWidget(
#             visible = True,
#         ),
#     ),
    FileField('AttachmentFile',
        required = 1,
        widget = FileWidget(
            label=_("Attachment"),
        ),
    ),
    ReferenceField('AttachmentType',
        required = 0,
        allowed_types = ('AttachmentType',),
        relationship = 'AttachmentAttachmentType',
        widget = BikaReferenceWidget(
            label=_("Attachment Type"),
            catalog_name = "bika_setup_catalog",
            base_query={'inactive_state': 'active'},
            showOn=True,
            popup_width='300px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Title', 'width': '100', 'label': _('Title')},
                     ],
        ),
    ),
    StringField('AttachmentKeys',
        searchable = True,
        widget = StringWidget(
            label=_("Attachment Keys"),
        ),
    ),
    ComputedField('AttachmentTypeUID',
        expression="context.getAttachmentType().UID() if context.getAttachmentType() else ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientUID',
        expression = 'context.get_client_uid',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

schema['id'].required = False
schema['title'].widget.visible = False
schema['title'].required = False

class Attachment(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Id """
        try:
            file = self.getAttachmentFile()
            if not file:
                return ''
        except:
            return ''
        
        fn = file.getFilename()
        if fn:
            return safe_unicode(fn).encode('utf-8')
        return ''

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

    def get_client_uid(self):
        if IAnalysisRequest.providedBy(self):
            return self.aq_parent.UID()
        elif IBatch.providedBy(self):
            client = self.aq_parent.getClient()
            if client:
                return client.UID()

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

atapi.registerType(Attachment, PROJECTNAME)
