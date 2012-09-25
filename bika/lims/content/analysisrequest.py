"""The request for analysis by a client. It contains analysis instances.
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import delete_objects
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.ATExtensions.widget.records import RecordsWidget
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import shasattr
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from bika.lims.browser.fields import ARAnalysesField
from bika.lims.config import PROJECTNAME, \
    ManageInvoices
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.utils import sortable_title

from decimal import Decimal
from email.Utils import formataddr
from types import ListType, TupleType
from zope.app.component.hooks import getSite
from zope.interface import implements
import sys
import time
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('RequestID',
        required = 1,
        searchable = True,
        widget = StringWidget(
            label = _('Request ID'),
            description = _("The ID assigned to the client's request by the lab"),
            visible = {'edit':'hidden'},
        ),
    ),
    ReferenceField('Contact',
        required = 1,
        vocabulary = 'getContactsDisplayList',
        default_method = 'getContactUIDForUser',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Contact',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestContact',
    ),
    ReferenceField('Sample',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Sample',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestSample',
    ),
    ARAnalysesField('Analyses',
        required = 1,
    ),
    StringField('ClientOrderNumber',
        searchable = True,
        widget = StringWidget(
            label = _('Client Order'),
        ),
    ),
    ReferenceField('Attachment',
        multiValued = 1,
        allowed_types = ('Attachment',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestAttachment',
    ),
    ReferenceField('CCContact',
        multiValued = 1,
        vocabulary = 'getContactsDisplayList',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Contact',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestCCContact',
    ),
    StringField('CCEmails',
        widget = StringWidget(
            label = _('CC Emails')
        ),
    ),
    ReferenceField('Invoice',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Invoice',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestInvoice',
    ),
    ReferenceField('Profile',
        allowed_types = ('AnalysisProfile',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestAnalysisProfile',
    ),
    ReferenceField('Template',
        allowed_types = ('ARTemplate',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestARTemplate',
    ),
    BooleanField('InvoiceExclude',
        default = False,
        widget = BooleanWidget(
            label = _('Invoice Exclude'),
            description = _('Select if analyses to be excluded from invoice'),
        ),
    ),
    BooleanField('ReportDryMatter',
        default = False,
        widget = BooleanWidget(
            label = _('Report as Dry Matter'),
            description = _('This result can be reported as dry matter'),
        ),
    ),
    DateTimeField('DateReceived',
        widget = DateTimeWidget(
            label = _('Date Received'),
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DatePublished',
        widget = DateTimeWidget(
            label = _('Date Published'),
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
    FixedPointField('MemberDiscount',
        default_method = 'getDefaultMemberDiscount',
        widget = DecimalWidget(
            label = _('Member discount %'),
            description = _('Enter percentage value eg. 33.0'),
        ),
    ),
    ComputedField('ClientUID',
        searchable = True,
        expression = 'here.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientReference',
        searchable = True,
        expression = 'here.getSample() and here.getSample().getClientReference()' ,
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SamplingDate',
        expression = 'here.getSample() and here.getSample().getSamplingDate() or ""',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientSampleID',
        searchable = True,
        expression = 'here.getSample() and here.getSample().getClientSampleID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleTypeTitle',
        searchable = True,
        expression = "here.getSample() and here.getSample().getSampleType() and here.getSample().getSampleType().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SamplePointTitle',
        searchable = True,
        expression = "here.getSample() and here.getSample().getSamplePoint() and here.getSample().getSamplePoint().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleUID',
        expression = 'here.getSample() and here.getSample().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ContactUID',
        expression = 'here.getContact() and here.getContact().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ProfileUID',
        expression = 'here.getProfile( and here.getProfile().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('Invoiced',
        expression = 'here.getInvoice() and True or False',
        default = False,
        widget = ComputedWidget(
            visible = False,
        ),
    ),
)
)

schema['title'].required = False

class AnalysisRequest(BaseFolder):
    implements(IAnalysisRequest)
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
        """ Return the Request ID as title """
        return self.getRequestID()

    def Description(self):
        """ Return searchable data as Description """
        return " ".join((
            self.getRequestID(),
            self.aq_parent.Title()
        ))

    def getDefaultMemberDiscount(self):
        """ compute default member discount if it applies """
        if hasattr(self, 'getMemberDiscountApplies'):
            if self.getMemberDiscountApplies():
                plone = getSite()
                settings = plone.bika_setup
                return settings.getMemberDiscount()
            else:
                return "0.00"

    security.declareProtected(View, 'getResponsible')
    def getResponsible(self):
        """ Return all manager info of responsible departments """
        managers = {}
        departments = []
        for analysis in self.objectValues('Analysis'):
            department = analysis.getService().getDepartment()
            if department is None:
                continue
            department_id = department.getId()
            if department_id in departments:
                continue
            departments.append(department_id)
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if not managers.has_key(manager_id):
                managers[manager_id] = {}
                managers[manager_id]['name'] = manager.getFullname()
                managers[manager_id]['email'] = manager.getEmailAddress()
                managers[manager_id]['phone'] = manager.getBusinessPhone()
                managers[manager_id]['signature'] = '%s/Signature' % manager.absolute_url()
                managers[manager_id]['dept'] = ''
            mngr_dept = managers[manager_id]['dept']
            if mngr_dept:
                mngr_dept += ', '
            mngr_dept += department.Title()
            managers[manager_id]['dept'] = mngr_dept
        mngr_keys = managers.keys()
        mngr_info = {}
        mngr_info['ids'] = mngr_keys
        mngr_info['dict'] = managers

        return mngr_info

    security.declareProtected(View, 'getResponsible')
    def getManagers(self):
        """ Return all managers of responsible departments """
        manager_ids = []
        manager_list = []
        departments = []
        for analysis in self.objectValues('Analysis'):
            department = analysis.getService().getDepartment()
            if department is None:
                continue
            department_id = department.getId()
            if department_id in departments:
                continue
            departments.append(department_id)
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if not manager_id in manager_ids:
                manager_ids.append(manager_id)
                manager_list.append(manager)

        return manager_list

    security.declareProtected(View, 'getLate')
    def getLate(self):
        """ return True if any analyses are late """
        workflow = getToolByName(self, 'portal_workflow')
        review_state = workflow.getInfoFor(self, 'review_state', '')
        if review_state in ['to_be_sampled', 'to_be_preserved',
                            'sample_due', 'published']:
            return False

        now = DateTime()
        for analysis in self.objectValues('Analysis'):
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state == 'published':
                continue
            if analysis.getDueDate() < analysis.getResultCaptureDate():
                return True
        return False

    security.declareProtected(View, 'getBillableItems')
    def getBillableItems(self):
        """ Return all items except those in 'not_requested' state """
        workflow = getToolByName(self, 'portal_workflow')
        items = []
        for analysis in self.objectValues('Analysis'):
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state != 'not_requested':
                items.append(analysis)
        return items

    security.declareProtected(View, 'getSubtotal')
    def getSubtotal(self):
        """ Compute Subtotal
        """
        return sum(
            [Decimal(obj.getService() and obj.getService().getPrice() or 0) \
            for obj in self.getBillableItems()])

    security.declareProtected(View, 'getVAT')
    def getVAT(self):
        """ Compute VAT """
        return Decimal(self.getTotalPrice()) - Decimal(self.getSubtotal())

    security.declareProtected(View, 'getTotalPrice')
    def getTotalPrice(self):
        """ Compute TotalPrice """
        billable = self.getBillableItems()
        TotalPrice = Decimal(0, 2)
        for item in billable:
            service = item.getService()
            if not service:
                return Decimal(0, 2)
            itemPrice = Decimal(service.getPrice() or 0)
            VAT = Decimal(service.getVAT() or 0)
            TotalPrice += Decimal(itemPrice) * (Decimal(1, 2) + VAT)
        return TotalPrice
    getTotal = getTotalPrice

    security.declareProtected(ManageInvoices, 'issueInvoice')
    def issueInvoice(self, REQUEST = None, RESPONSE = None):
        """ issue invoice
        """
        # check for an adhoc invoice batch for this month
        now = DateTime()
        batch_month = now.strftime('%b %Y')
        batch_title = '%s - %s' % (batch_month, 'ad hoc')
        invoice_batch = None
        for b_proxy in self.portal_catalog(portal_type = 'InvoiceBatch',
                                           Title = batch_title):
            invoice_batch = b_proxy.getObject()
        if not invoice_batch:
            first_day = DateTime(now.year(), now.month(), 1)
            start_of_month = first_day.earliestTime()
            last_day = first_day + 31
            while last_day.month() != now.month():
                last_day = last_day - 1
            end_of_month = last_day.latestTime()

            invoices = self.invoices
            batch_id = invoices.generateUniqueId('InvoiceBatch')
            invoices.invokeFactory(id = batch_id, type_name = 'InvoiceBatch')
            invoice_batch = invoices._getOb(batch_id)
            invoice_batch.edit(
                title = batch_title,
                BatchStartDate = start_of_month,
                BatchEndDate = end_of_month,
            )
            invoice_batch.processForm()

        client_uid = self.getClientUID()
        invoice_batch.createInvoice(client_uid, [self, ])

        RESPONSE.redirect(
                '%s/analysisrequest_invoice' % self.absolute_url())

    security.declarePublic('printInvoice')
    def printInvoice(self, REQUEST = None, RESPONSE = None):
        """ print invoice
        """
        invoice = self.getInvoice()
        invoice_url = invoice.absolute_url()
        RESPONSE.redirect('%s/invoice_print' % invoice_url)

    def addARAttachment(self, REQUEST = None, RESPONSE = None):
        """ Add the file as an attachment
        """
        workflow = getToolByName(self, 'portal_workflow')

        this_file = self.REQUEST.form['AttachmentFile_file']
        if self.REQUEST.form.has_key('Analysis'):
            analysis_uid = self.REQUEST.form['Analysis']
        else:
            analysis_uid = None

        attachmentid = self.generateUniqueId('Attachment')
        self.aq_parent.invokeFactory(id = attachmentid, type_name = "Attachment")
        attachment = self.aq_parent._getOb(attachmentid)
        attachment.edit(
            AttachmentFile = this_file,
            AttachmentType = self.REQUEST.form['AttachmentType'],
            AttachmentKeys = self.REQUEST.form['AttachmentKeys'])
        attachment.processForm()
        attachment.reindexObject()

        if analysis_uid:
            tool = getToolByName(self, REFERENCE_CATALOG)
            analysis = tool.lookupObject(analysis_uid)
            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)
            if workflow.getInfoFor(analysis, 'review_state') == 'attachment_due':
                workflow.doActionFor(analysis, 'attach')
        else:
            others = self.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())

            self.setAttachment(attachments)

        RESPONSE.redirect(
                '%s/manage_results' % self.absolute_url())

    def delARAttachment(self, REQUEST = None, RESPONSE = None):
        """ delete the attachment """
        tool = getToolByName(self, REFERENCE_CATALOG)
        if self.REQUEST.form.has_key('ARAttachment'):
            attachment_uid = self.REQUEST.form['ARAttachment']
            attachment = tool.lookupObject(attachment_uid)
            parent = attachment.getRequest()
        elif self.REQUEST.form.has_key('AnalysisAttachment'):
            attachment_uid = self.REQUEST.form['AnalysisAttachment']
            attachment = tool.lookupObject(attachment_uid)
            parent = attachment.getAnalysis()

        others = parent.getAttachment()
        attachments = []
        for other in others:
            if not other.UID() == attachment_uid:
                attachments.append(other.UID())
        parent.setAttachment(attachments)
        client = attachment.aq_parent
        ids = [attachment.getId(), ]
        BaseFolder.manage_delObjects(client, ids, REQUEST)

        RESPONSE.redirect(
                '%s/manage_results' % self.absolute_url())

    security.declarePublic('get_verifier')
    def get_verifier(self):
        wtool = getToolByName(self, 'portal_workflow')
        mtool = getToolByName(self, 'portal_membership')

        verifier = None
        try:
            review_history = wtool.getInfoFor(self, 'review_history')
        except:
            return 'access denied'

        if not review_history:
            return 'no history'
        for items in  review_history:
            action = items.get('action')
            if action != 'verify':
                continue
            actor = items.get('actor')
            member = mtool.getMemberById(actor)
            verifier = member.getProperty('fullname')
            if verifier is None or verifier == '':
                verifier = actor
        return verifier

    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        pc = getToolByName(self, 'portal_catalog')
        r = pc(portal_type = 'Contact',
               getUsername = user_id)
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

atapi.registerType(AnalysisRequest, PROJECTNAME)
