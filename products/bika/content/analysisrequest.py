"""The request for analysis by a client. It contains analysis instances.

$Id: AnalysisRequest.py 2567 2010-09-27 14:51:15Z anneline $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import delete_objects
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import shasattr
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone.utils import transaction_note
from Products.bika.browser.fields import AnalysesField
from Products.bika.browser.widgets import AnalysesWidget
from Products.bika.config import I18N_DOMAIN, SubmitResults, PROJECTNAME, \
    ManageInvoices
from Products.bika.content.bikaschema import BikaSchema
from Products.bika.utils import sortable_title
from email.Utils import formataddr
from types import ListType, TupleType
from zope.app.component.hooks import getSite
import sys
import time

schema = BikaSchema.copy() + Schema((
    StringField('RequestID',
        required = 1,
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Request ID',
            label_msgid = 'label_requestid',
            description = 'The ID assigned to the client''s request by the lab',
            description_msgid = 'help_requestid',
            i18n_domain = I18N_DOMAIN,
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
    ReferenceField('CCContact',
        multiValued = 1,
        vocabulary = 'getContactsDisplayList',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Contact',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestCCContact',
    ),
    ReferenceField('Attachment',
        multiValued = 1,
        allowed_types = ('Attachment',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestAttachment',
    ),
    StringField('CCEmails',
        widget = StringWidget(
            label = 'CC Emails',
            label_msgid = 'label_ccemails',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Sample',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Sample',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestSample',
    ),
    StringField('ClientOrderNumber',
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Client Order ID',
            label_msgid = 'label_client_order_id',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Invoice',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Invoice',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestInvoice',
    ),
    ReferenceField('Profile',
        allowed_types = ('ARProfile', 'LabARProfile',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestProfile',
    ),
    BooleanField('InvoiceExclude',
        default = False,
        index = 'FieldIndex',
        widget = BooleanWidget(
            label = "Invoice Exclude",
            label_msgid = "label_invoice_exclude",
            description = "Select if analyses to be excluded from invoice",
            description_msgid = 'help_invoiceexclude',
        ),
    ),
    BooleanField('ReportDryMatter',
        default = False,
        index = 'FieldIndex',
        widget = BooleanWidget(
            label = "Report as dry matter",
            label_msgid = "label_report_dry_matter",
            description = "Select if result is to be reported as dry matter",
            description_msgid = 'help_report_dry_matter',
        ),
    ),
    DateTimeField('DateRequested',
        required = 1,
        default_method = 'current_date',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date requested',
            label_msgid = 'label_daterequested',
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
    DateTimeField('DatePublished',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date published',
            label_msgid = 'label_datepublished',
            visible = {'edit':'hidden'},
        ),
    ),
    TextField('Notes',
        widget = TextAreaWidget(
            label = 'Notes'
        ),
    ),
    AnalysesField('Analyses',
        required = 1,
        widget = AnalysesWidget(
            label = 'Analyses',
            label_msgid = 'label_analyses',
        ),
    ),
    FixedPointField('MemberDiscount',
        default_method = 'getDefaultMemberDiscount',
        widget = DecimalWidget(
            label = 'Member discount %',
            label_msgid = 'label_memberdiscount_percentage',
            description = 'Enter percentage value eg. 33.0',
            description_msgid = 'help_memberdiscount_percentage',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'here.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleUID',
        index = 'FieldIndex',
        expression = 'here.getSample().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ContactUID',
        index = 'FieldIndex',
        expression = 'here.getContact().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ProfileUID',
        index = 'FieldIndex',
        expression = 'here.getProfile().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

schema['title'].required = False

class AnalysisRequest(VariableSchemaSupport, BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _assigned_to_worksheet = False
    _has_dependant_calcs = False

    def hasBeenInvoiced(self):
        if self.getInvoice():
            return True
        else:
            return False

    def Title(self):
        """ Return the Request ID as title """
        return self.getRequestID()

    def getDefaultMemberDiscount(self):
        """ compute default member discount if it applies """
        if hasattr(self, 'getMemberDiscountApplies'):
            if self.getMemberDiscountApplies():
                plone = getSite()
                settings = plone.bika_settings
                return settings.getMemberDiscount()
            else:
                return 0

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
        wf_tool = getToolByName(self, 'portal_workflow')
        review_state = wf_tool.getInfoFor(self, 'review_state', '')
        if review_state in ['sample_due', 'published']:
            return False

        now = DateTime()
        for analysis in self.objectValues('Analysis'):
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            if review_state == 'published':
                continue
            if analysis.getDueDate() < now:
                return True
        return False


    security.declareProtected(View, 'getBillableItems')
    def getBillableItems(self):
        """ Return all items except those in 'not_requested' state """
        wf_tool = getToolByName(self, 'portal_workflow')
        items = []
        for analysis in self.objectValues('Analysis'):
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            if review_state != 'not_requested':
                items.append(analysis)
        return items

    security.declareProtected(View, 'getSubtotal')
    def getSubtotal(self):
        """ Compute Subtotal """
        return sum(
            [obj.getPrice() \
            for obj in self.getBillableItems()])

    security.declareProtected(View, 'getVAT')
    def getVAT(self):
        """ Compute VAT """
        return self.getTotalPrice() - self.getSubtotal()

    security.declareProtected(View, 'getTotalPrice')
    def getTotalPrice(self):
        """ Compute TotalPrice """
        return sum(
            [obj.getTotalPrice() \
            for obj in self.getBillableItems()])
    getTotal = getTotalPrice

    security.declareProtected(View, 'getCatAnalyses')
    def getCatAnalyses(self):
        """ return analyses in category sequence """
        cats = {}
        results = []
        for analysis in self.getAnalyses():
            if cats.has_key(analysis.getCategoryName()):
                analyses = cats[analysis.getCategoryName()]
            else:
                analyses = []
            analyses.append(analysis)
            cats[analysis.getCategoryName()] = analyses
        cat_keys = cats.keys()
        cat_keys.sort()
        for cat_key in cat_keys():
            analyses = cats[cat_key]
            analyses.sort(lambda x, y:cmp(x.Title().lower(), y.Title().lower()))
            for analysis in analyses:
                results.append(analysis)
        return results

    security.declareProtected(View, 'getPublishedAnalyses')
    def getPublishedAnalyses(self):
        """ return published analyses """
        wf_tool = getToolByName(self, 'portal_workflow')
        r = []
        for analysis in self.getAnalyses():
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            if review_state == 'published':
                r.append(analysis)
        return r

    def setDryMatterResults(self):
        """ get results of analysis requiring DryMatter reporting """
        analyses = []
        DryMatter = None
        settings = getToolByName(self, 'bika_settings').settings
        dry_service = settings.getDryMatterService()
        for analysis in self.getAnalyses():
            if analysis.getReportDryMatter():
                analyses.append(analysis)
            if analysis.getServiceUID() == dry_service.UID():
                try:
                    DryMatter = float(analysis.getResult())
                except:
                    DryMatter = None

        for analysis in analyses:
            if DryMatter:
                try:
                    wet_result = float(analysis.getResult())
                except:
                    wet_result = None
            if DryMatter and wet_result:
                dry_result = '%.2f' % ((wet_result / DryMatter) * 100)
            else:
                dry_result = None
            analysis.setResultDM(dry_result)

        return

    security.declareProtected(ManageInvoices, 'issueInvoice')
    def issueInvoice(self, REQUEST = None, RESPONSE = None):
        """ issue invoice
        """
        # check for an adhoc invoice batch for this month
        now = DateTime()
        batch_month = now.strftime('%b %Y')
        batch_title = '%s - %s' % (batch_month, 'ad hoc')
        invoice_batch = None
        for b_proxy in  self.portal_catalog(portal_type = 'InvoiceBatch',
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
        else:
            others = self.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())

            self.setAttachment(attachments)

        RESPONSE.redirect(
                '%s/analysisrequest_analyses' % self.absolute_url())

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
                '%s/analysisrequest_analyses' % self.absolute_url())

    security.declareProtected(SubmitResults, 'submitResults')
    def submitResults(self, results = {}, REQUEST = None, RESPONSE = None):
        """ Submit results
        """
        wf_tool = getToolByName(self, 'portal_workflow')

        for key, value in self.REQUEST.form.items():
            if key.startswith('results'):
                id = key.split('.')[-1]
                analysis = self._getOb(id)
                if analysis.getCalcType() == 'dep':
                    continue
                result = value.get('Result')
                if result:
                    if result.strip() == '':
                        result = None
                else:
                    result = None

                retested = value.get('Retested')

                uncertainty = None
                service = analysis.getService()

                if result:
                    precision = service.getPrecision()
                    if precision:
                        result = self.get_precise_result(result, precision)

                    uncertainty = self.get_uncertainty(result, service)

                titrationvolume = value.get('TitrationVolume')
                if titrationvolume:
                    if titrationvolume.strip() == '':
                        titrationvolume = None
                else:
                    titrationvolume = None

                titrationfactor = value.get('TitrationFactor')
                if titrationfactor:
                    if titrationfactor.strip() == '':
                        titrationfactor = None
                else:
                    titrationfactor = None

                grossmass = value.get('GrossMass')
                if grossmass:
                    if grossmass.strip() == '':
                        grossmass = None
                else:
                    grossmass = None

                netmass = value.get('NetMass')
                if netmass:
                    if netmass.strip() == '':
                        netmass = None
                else:
                    netmass = None

                vesselmass = value.get('VesselMass')
                if vesselmass:
                    if vesselmass.strip() == '':
                        vesselmass = None
                else:
                    vesselmass = None

                samplemass = value.get('SampleMass')
                if samplemass:
                    if samplemass.strip() == '':
                        samplemass = None
                else:
                    samplemass = None

                analysis.setTitrationVolume(titrationvolume)
                analysis.setTitrationFactor(titrationfactor)
                analysis.setGrossMass(grossmass)
                analysis.setNetMass(netmass)
                analysis.setVesselMass(vesselmass)
                analysis.setSampleMass(samplemass)

                analysis.edit(
                    Result = result,
                    Retested = retested,
                    Uncertainty = uncertainty,
                    Unit = service.getUnit()
                )

                if analysis._affects_other_analysis:
                    self.get_dependant_results(analysis)
                if result is None:
                    continue

                wf_tool.doActionFor(analysis, 'submit')
                transaction_note('Changed status of %s at %s' % (
                    analysis.title_or_id(), analysis.absolute_url()))

        if self.getReportDryMatter():
            self.setDryMatterResults()

        review_state = wf_tool.getInfoFor(self, 'review_state', '')
        if review_state == 'to_be_verified':
            RESPONSE.redirect(self.absolute_url())
        else:
            RESPONSE.redirect(
                '%s/analysisrequest_analyses' % self.absolute_url())


    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = user_id
        )
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('getCCDisplays')
    def getCCDisplays(self):
        """ get a string of titles of the contacts
        """
        cc_uids = ''
        cc_titles = ''
        for cc in self.getCCContact():
            if cc_uids:
                cc_uids = cc_uids + ', ' + cc.UID()
                cc_titles = cc_titles + ', ' + cc.Title()
            else:
                cc_uids = cc.UID()
                cc_titles = cc.Title()
        return [cc_uids, cc_titles]

    security.declareProtected(delete_objects, 'manage_delObjects')
    def manage_delObjects(self, ids = [], REQUEST = None):
        """ recalculate state from remaining analyses """
        BaseFolder.manage_delObjects(self, ids, REQUEST)
        self._escalateWorkflowAction()


    # workflow methods
    #
    def workflow_script_receive(self, state_info):
        """ receive sample """
        self.setDateReceived(DateTime())
        self.reindexObject()
        self._delegateWorkflowAction('receive')

    def workflow_script_assign(self, state_info):
        """ submit sample """
        self._delegateWorkflowAction('assign')
        # we need to record that we passed through the 'assigned' state
        self._assigned_to_worksheet = True

    def workflow_script_submit(self, state_info):
        """ submit sample """
        self._delegateWorkflowAction('submit')

    def workflow_script_verify(self, state_info):
        """ verify sample """
        self._delegateWorkflowAction('verify')

    def workflow_script_retract(self, state_info):
        """ retract sample """
        self._delegateWorkflowAction('retract')
        self._escalateWorkflowAction()
        #wf_tool = self.portal_workflow
        #for analysis in self.getAnalyses():
        #    review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
        #    if review_state == 'assigned':
        #        continue
        #    if analysis._assigned_to_worksheet:
        #        wf_tool.doActionFor(analysis, 'assign')
        #        analysis.reindexObject()

    def workflow_script_publish(self, state_info):
        """ publish analysis request """
        self.setDatePublished(DateTime())
        self.reindexObject()
        self._delegateWorkflowAction('publish')
        #get_transaction().commit()
        if self.REQUEST.has_key('PUBLISH_BATCH'):
            return

        contact = self.getContact()
        analysis_requests = [self]
        self.publish_analysis_requests(contact, analysis_requests, None)

        # cc contacts
        for cc_contact in self.getCCContact():
            self.publish_analysis_requests(cc_contact, analysis_requests, None)
        # cc emails
        cc_emails = self.getCCEmails()
        if cc_emails:
            self.publish_analysis_requests(None, analysis_requests, cc_emails)

        # AVS print the published ar
        #if 'print' in contact.getPublicationPreference():
        #    self.REQUEST.SESSION.set('uids', [self.UID(),])
        #    self.REQUEST.RESPONSE.redirect('%s/print_analysisrequests'%self.absolute_url())

    def workflow_script_prepublish(self, state_info):
        """ prepublish analysis request """
        """ publish verified analyses linked to this request """
        self._delegateWorkflowAction('publish')
        #get_transaction().commit()
        if self.REQUEST.has_key('PUBLISH_BATCH'):
            return

        contact = self.getContact()
        analysis_requests = [self]
        self.publish_analysis_requests(contact, analysis_requests, None)

        # cc contacts
        for cc_contact in self.getCCContact():
            self.publish_analysis_requests(cc_contact, analysis_requests, None)
        # cc emails
        cc_emails = self.getCCEmails()
        if cc_emails:
            self.publish_analysis_requests(None, analysis_requests, cc_emails)

    def workflow_script_republish(self, state_info):
        """ republish analysis request """
        if self.REQUEST.has_key('PUBLISH_BATCH'):
            return

        contact = self.getContact()
        analysis_requests = [self]
        self.publish_analysis_requests(contact, analysis_requests, None)

        # cc contacts
        for cc_contact in self.getCCContact():
            self.publish_analysis_requests(cc_contact, analysis_requests, None)
        # cc emails
        cc_emails = self.getCCEmails()
        if cc_emails:
            self.publish_analysis_requests(None, analysis_requests, cc_emails)

    def _delegateWorkflowAction(self, action_id):
        """ if analysisrequest is 'received', that actually means that
            the sample is received. Delegate received status to sample, 
            which will delegate it to all other linked analysisrequests
        """
        if getattr(self, '_escalating_workflow_action', None):
            return
        if action_id == 'receive_sample':
            receive_sample = True
            action_id = 'receive'
        else:
            receive_sample = False

        self._delegating_workflow_action = 1
        wf_tool = self.portal_workflow
        for analysis in self.getAnalyses():
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            # 'not requested' analyses stay unaffected until
            # individually verified
            if review_state == 'not_requested':
                continue
            try:
                wf_tool.doActionFor(analysis, action_id)
                analysis.reindexObject()
            except WorkflowException, msg:
                from zLOG import LOG; LOG('INFO', 0, '', msg)
                pass

        if receive_sample:
            # this is an escalation from the sample, do not escalate sample
            pass
        elif action_id in ('receive'):
            # analysisrequest was received, and must delegate to sample
            sample = self.getSample()
            review_state = wf_tool.getInfoFor(sample, 'review_state', '')
            if review_state != 'due':
                from zLOG import LOG, WARNING; LOG('bika', WARNING,
                'Escalate workflow action sample receive. ',
                'sample %s in state: %s' % (self.getId(), review_state))
                return
            try:
                wf_tool.doActionFor(sample, action_id)
                sample.reindexObject()
            except WorkflowException, msg:
                from zLOG import LOG; LOG('INFO', 0, '', msg)
                pass

            # sample._delegateWorkflowAction('receive')

        del self._delegating_workflow_action

    def _escalateWorkflowAction(self):
        """ if all analyses have transitioned to next state then our
            state must change too
        """
        if getattr(self, '_delegating_workflow_action', None):
            return


        self._escalating_workflow_action = 1
        wf_tool = self.portal_workflow
        analyses_states = {}
        for analysis in self.getAnalyses():
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            analyses_states[review_state] = 1

        # build a state to transition map
        transitions = wf_tool.getTransitionsFor(self)
        wf = wf_tool.getWorkflowById('bika_analysis_workflow')
        # make a map of transitions
        transition_map = {}
        for t in transitions:
            # 'import' is not a transition made by users
            if t['id'] == 'import':
                continue
            transition = wf.transitions.get(t['id'])
            transition_map[transition.new_state_id] = transition.id

        ar_state = wf_tool.getInfoFor(self, 'review_state', '')
        # change the AR to the lowest possible state
        for state_id in ('sample_due', 'sample_received', 'assigned',
             'to_be_verified', 'verified', 'published'):
            if analyses_states.has_key(state_id):
                if ar_state == state_id:
                    break
                elif transition_map.has_key(state_id):
                    wf_tool.doActionFor(self, transition_map.get(state_id))
                    break

        if getattr(self, '_escalating_workflow_action', None):
            del self._escalating_workflow_action
        else:
            from zLOG import LOG, WARNING; LOG('bika', WARNING,
            'Escalate workflow action',
            'No _escalateWorkflowAction found on %s' % self.getId())

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

atapi.registerType(AnalysisRequest, PROJECTNAME)
