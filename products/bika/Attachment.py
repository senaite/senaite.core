from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget, RecordsField
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME, ManageBika, ManageAnalysisRequest
from Products.bika.fixedpoint import FixedPoint

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

IdField = schema['id']
IdField.required = 0
IdField.widget.visible = False
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}

class Attachment(BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    archetype_name = 'Attachment'
    schema = schema
    allowed_content_types = ()
    default_view = 'attachment_edit'
    content_icon = 'attachment.png'
    global_allow = 0
    filter_content_types = 1
    use_folder_tabs = 0

    actions = (
        {'id': 'edit',
         'name': 'Edit',
         'action': 'string:${object_url}/attachment_edit',
         'permissions': (ManageAnalysisRequest,),
        },
        {'id': 'view',
         'name': 'View',
         'action': 'string:${object_url}/attachment_view',
         'permissions': (View,),
        },
        {'id': 'log',
         'name': 'Log',
         'action': 'string:${object_url}/status_log',
         'permissions': (ManageBika,),
        },

    )

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

        return wf_tool.getInfoFor(parent, 'review_state', '')

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

registerType(Attachment, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
