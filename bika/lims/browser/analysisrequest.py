from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.publish import doPublish
from bika.lims.browser.sample import SamplePartitionsView
from bika.lims.adapters.widgetvisibility import WidgetVisibility as _WV
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IAnalysisRequestAddView
from bika.lims.interfaces import IDisplayListVocabulary
from bika.lims.permissions import *
from bika.lims.subscribers import doActionFor
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import getUsers
from bika.lims.utils import isActive
from bika.lims.utils import to_unicode as _u
from bika.lims.utils import tmpID
from bika.lims.utils import encode_header
from bika.lims.vocabularies import CatalogVocabulary
from bika.lims.browser.analyses import QCAnalysesView
from DateTime import DateTime
from email.Utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from magnitude import mg
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getAdapter
import zope.event
from zope.i18n.locales import locales
from zope.interface import implements

import json
import plone
import urllib
from bika.lims.browser.log import LogView

class AnalysisRequestWorkflowAction(WorkflowAction):
    """Workflow actions taken in AnalysisRequest context.

        Sample context workflow actions also redirect here
        Applies to
            Analysis objects
            SamplePartition objects
    """
    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        action, came_from = WorkflowAction._get_form_workflow_action(self)
        checkPermission = self.context.portal_membership.checkPermission

        # calcs.js has kept item_data and form input interim values synced,
        # so the json strings from item_data will be the same as the form values
        item_data = {}
        if 'item_data' in form:
            if type(form['item_data']) == list:
                for i_d in form['item_data']:
                    for i, d in json.loads(i_d).items():
                        item_data[i] = d
            else:
                item_data = json.loads(form['item_data'])

        ## Sample Partitions or AR Manage Analyses: save Partition Table
        if action == "save_partitions_button":
            sample = self.context.portal_type == 'Sample' and self.context or\
                self.context.getSample()
            part_prefix = sample.getId() + "-P"

            nr_existing = len(sample.objectIds())
            nr_parts = len(form['PartTitle'][0])
            # add missing parts
            if nr_parts > nr_existing:
                for i in range(nr_parts - nr_existing):
                    _id = sample.invokeFactory('SamplePartition', id = 'tmp')
                    part = sample[_id]
                    part.setDateReceived = DateTime()
                    part.processForm()
            # remove excess parts
            if nr_existing > nr_parts:
                for i in range(nr_existing - nr_parts):
                    part = sample['%s%s'%(part_prefix, nr_existing - i)]
                    for a in part.getBackReferences("AnalysisSamplePartition"):
                        a.setSamplePartition(None)
                    sample.manage_delObjects(['%s%s'%(part_prefix, nr_existing - i),])
            # modify part container/preservation
            for part_uid, part_id in form['PartTitle'][0].items():
                part = sample["%s%s"%(part_prefix, part_id.split(part_prefix)[1])]
                part.edit(
                    Container = form['getContainer'][0][part_uid],
                    Preservation = form['getPreservation'][0][part_uid],
                )
                part.reindexObject()


            objects = WorkflowAction._get_selected_items(self)
            if not objects:
                message = self.context.translate(
                    _("No items have been selected"))
                self.context.plone_utils.addPortalMessage(message, 'info')
                if self.context.portal_type == 'Sample':
                    # in samples his table is on 'Partitions' tab
                    self.destination_url = self.context.absolute_url() +\
                        "/partitions"
                else:
                    # in ar context this table is on 'ManageAnalyses' tab
                    self.destination_url = self.context.absolute_url() +\
                        "/analyses"
                self.request.response.redirect(self.destination_url)
                return

        ## AR Manage Analyses: save Analyses
        if action == "save_analyses_button":
            ar = self.context
            sample = ar.getSample()

            objects = WorkflowAction._get_selected_items(self)
            if not objects:
                message = self.context.translate(
                    _("No analyses have been selected"))
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.destination_url = self.context.absolute_url() + "/analyses"
                self.request.response.redirect(self.destination_url)
                return

            prices = form.get('Price', [None])[0]
            new = ar.setAnalyses(objects.keys(), prices = prices)

            # link analyses and partitions
            for service_uid, service in objects.items():
                part_id = form['Partition'][0][service_uid]
                part = sample[part_id]
                analysis = ar[service.getKeyword()]
                analysis.setSamplePartition(part)
                analysis.reindexObject()

            if new:
                ar_state = workflow.getInfoFor(ar, 'review_state')
                for analysis in new:
                    analysis.updateDueDate()
                    changeWorkflowState(analysis, 'bika_analysis_workflow', ar_state)

            message = self.context.translate(PMF("Changes saved."))
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)
            return

        ## Partition Preservation
        # the partition table shown in AR and Sample views sends it's
        # action button submits here.
        elif action == "preserve":
            objects = WorkflowAction._get_selected_items(self)
            transitioned = []
            for obj_uid, obj in objects.items():
                part = obj
                # can't transition inactive items
                if workflow.getInfoFor(part, 'inactive_state', '') == 'inactive':
                    continue
                if not checkPermission(PreserveSample, part):
                    continue

                # grab this object's Preserver and DatePreserved from the form
                Preserver = form['getPreserver'][0][obj_uid].strip()
                Preserver = Preserver and Preserver or ''
                DatePreserved = form['getDatePreserved'][0][obj_uid].strip()
                DatePreserved = DatePreserved and DateTime(DatePreserved) or ''

                # write them to the sample
                part.setPreserver(Preserver)
                part.setDatePreserved(DatePreserved)

                # transition the object if both values are present
                if Preserver and DatePreserved:
                    workflow.doActionFor(part, action)
                    transitioned.append(part.id)

                part.reindexObject()
                part.aq_parent.reindexObject()

            message = None
            if len(transitioned) > 1:
                message = _('${items} are waiting to be received.',
                            mapping = {'items': ', '.join(transitioned)})
                message = self.context.translate(message)
                self.context.plone_utils.addPortalMessage(message, 'info')
            elif len(transitioned) == 1:
                message = _('${item} is waiting to be received.',
                            mapping = {'item': ', '.join(transitioned)})
                message = self.context.translate(message)
                self.context.plone_utils.addPortalMessage(message, 'info')
            if not message:
                message = _('No changes made.')
                message = self.context.translate(message)
                self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        elif action == "sample":
            # This action happens only for a single context.
            # Context can be a sample or an AR.
            #
            # Once the Sampler/DateSampled values are completed on the
            # Sample or AR form, the user has two choices.
            #
            # 1) Use the normal Plone UI actions dropdown, (invokes this code).
            # 2) Click the save button, which invokes code in SampleEdit or
            #    AnalysisRequestEdit __call__ methods.
            #
            # Both these methods do pretty much the same thing, but now, it's
            # done in three places.

            if self.context.portal_type == "AnalysisRequest":
                sample = self.context.getSample()
            else:
                sample = self.context
            # can't transition inactive items
            if workflow.getInfoFor(sample, 'inactive_state', '') == 'inactive' \
               or not checkPermission(SampleSample, sample):
                message = _('No changes made.')
                message = self.context.translate(message)
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.destination_url = self.request.get_header("referer",
                                       self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return
            # grab this object's Sampler and DateSampled from the form
            Sampler = form['getSampler'][0][sample_uid].strip()
            Sampler = Sampler and Sampler or ''
            DateSampled = form['getDateSampled'][0][obj_uid].strip()
            DateSampled = DateSampled and DateTime(DateSampled) or ''
            # write them to the sample
            sample.setSampler(Sampler)
            sample.setDateSampled(DateSampled)
            # transition the object if both values are present
            if Sampler and DateSampled:
                workflow.doActionFor(sample, action)
                sample.reindexObject()
                message = "Changes saved."
                message = self.context.translate(message)
                self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)
            return

        elif action == "receive":
            # default bika_listing.py/WorkflowAction, but then
            # print automatic labels.
            if 'receive' in self.context.bika_setup.getAutoPrintLabels():
                size = self.context.bika_setup.getAutoLabelSize()
                q = "/sticker?size=%s&items=%s" % (size, self.context.getId())
                self.destination_url = self.context.absolute_url() + q
            WorkflowAction.__call__(self)

        ## submit
        elif action == 'submit' and self.request.form.has_key("Result"):
            if not isActive(self.context):
                message = self.context.translate(_('Item is inactive.'))
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(self.context.absolute_url())
                return

            selected_analyses = WorkflowAction._get_selected_items(self)
            results = {}
            hasInterims = {}

            # check that the form values match the database
            # save them if not.
            for uid, result in self.request.form['Result'][0].items():
                # if the AR has ReportDryMatter set, get dry_result from form.
                dry_result = ''
                if hasattr(self.context, 'getReportDryMatter') \
                   and self.context.getReportDryMatter():
                    for k, v in self.request.form['ResultDM'][0].items():
                        if uid == k:
                            dry_result = v
                            break
                if uid in selected_analyses:
                    analysis = selected_analyses[uid]
                else:
                    analysis = rc.lookupObject(uid)
                if not analysis:
                    # ignore result if analysis object no longer exists
                    continue
                results[uid] = result
                service = analysis.getService()
                interimFields = item_data[uid]
                if len(interimFields) > 0:
                    hasInterims[uid] = True
                else:
                    hasInterims[uid] = False
                service_unit = service.getUnit() and service.getUnit() or ''
                retested = form.has_key('retested') and form['retested'].has_key(uid)
                remarks = form.get('Remarks', [{},])[0].get(uid, '')
                # Don't save uneccessary things
                # https://github.com/bikalabs/Bika-LIMS/issues/766:
                #    Somehow, using analysis.edit() fails silently when
                #    logged in as Analyst.
                if analysis.getInterimFields() != interimFields or \
                   analysis.getRetested() != retested or \
                   analysis.getRemarks() != remarks:
                    analysis.setInterimFields(interimFields)
                    analysis.setRetested(retested)
                    analysis.setRemarks(remarks)
                # save results separately, otherwise capture date is rewritten
                if analysis.getResult() != result or \
                   analysis.getResultDM() != dry_result:
                    analysis.setResultDM(dry_result)
                    analysis.setResult(result)

            # discover which items may be submitted
            # guard_submit does a lot of the same stuff, too.
            submissable = []
            for uid, analysis in selected_analyses.items():
                if uid not in results or not results[uid]:
                    continue
                can_submit = True
                for dependency in analysis.getDependencies():
                    dep_state = workflow.getInfoFor(dependency, 'review_state')
                    if hasInterims[uid]:
                        if dep_state in ('to_be_sampled', 'to_be_preserved',
                                         'sample_due', 'sample_received',
                                         'attachment_due', 'to_be_verified',):
                            can_submit = False
                            break
                    else:
                        if dep_state in ('to_be_sampled', 'to_be_preserved',
                                         'sample_due', 'sample_received',):
                            can_submit = False
                            break
                if can_submit and analysis not in submissable:
                    submissable.append(analysis)

            # and then submit them.
            for analysis in submissable:
                doActionFor(analysis, 'submit')

            message = self.context.translate(PMF("Changes saved."))
            self.context.plone_utils.addPortalMessage(message, 'info')
            if checkPermission(EditResults, self.context):
                self.destination_url = self.context.absolute_url() + "/manage_results"
            else:
                self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)

        ## publish
        elif action in ('prepublish', 'publish', 'republish'):
            if not isActive(self.context):
                message = self.context.translate(_('Item is inactive.'))
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(self.context.absolute_url())
                return

            # publish entire AR.
            self.context.setDatePublished(DateTime())
            transitioned = self.doPublish(self.context,
                                   self.request,
                                   action,
                                   [self.context, ])()
            if len(transitioned) == 1:
                message = self.context.translate('${items} published.',
                                    mapping = {'items': ', '.join(transitioned)})
            else:
                message = self.context.translate(_("No items were published"))
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        ## verify
        elif action == 'verify':
            # default bika_listing.py/WorkflowAction, but then go to view screen.
            self.destination_url = self.context.absolute_url()
            WorkflowAction.__call__(self)

        elif action == 'retract_ar':
            # AR should be retracted
            # Can't transition inactive ARs
            if not isActive(self.context):
                message = self.context.translate(_('Item is inactive.'))
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(self.context.absolute_url())
                return

            # 1. Copies the AR linking the original one and viceversa
            ar = self.context
            newar = self.cloneAR(ar)

            # 2. The old AR gets a status of 'invalid'
            workflow.doActionFor(ar, 'retract_ar')

            # 3. The new AR copy opens in status 'to be verified'
            changeWorkflowState(newar, 'bika_ar_workflow', 'to_be_verified')

            # 4. The system immediately alerts the client contacts who ordered
            # the results, per email and SMS, that a possible mistake has been
            # picked up and is under investigation.
            # A much possible information is provided in the email, linking
            # to the AR online.
            laboratory = self.context.bika_setup.laboratory
            lab_address = "<br/>".join(laboratory.getPrintAddress())
            mime_msg = MIMEMultipart('related')
            mime_msg['Subject'] = _("Erroneus result publication from %s") % \
                                    ar.getRequestID()
            mime_msg['From'] = formataddr(
                (encode_header(laboratory.getName()),
                 laboratory.getEmailAddress()))
            to = []
            contact = ar.getContact()
            if contact:
                to.append(formataddr((encode_header(contact.Title()),
                                       contact.getEmailAddress())))
            for cc in ar.getCCContact():
                formatted = formataddr((encode_header(cc.Title()),
                                       cc.getEmailAddress()))
                if formatted not in to:
                    to.append(formatted)

            managers = self.context.portal_groups.getGroupMembers('LabManagers')
            for bcc in managers:
                user = self.portal.acl_users.getUser(bcc)
                uemail = user.getProperty('email')
                ufull = user.getProperty('fullname')
                formatted = formataddr((encode_header(ufull), uemail))
                if formatted not in to:
                    to.append(formatted)
            mime_msg['To'] = ','.join(to)
            aranchor = "<a href='%s'>%s</a>" % (ar.absolute_url(),
                                                ar.getRequestID())
            naranchor = "<a href='%s'>%s</a>" % (newar.absolute_url(),
                                                 newar.getRequestID())
            addremarks = ('addremarks' in self.request \
                          and ar.getRemarks()) \
                        and ("<br/><br/>"
                             + _("Additional remarks:")
                             + "<br/>"
                             + ar.getRemarks().split("===")[1].strip()
                             + "<br/><br/>") \
                        or ''

            body = _("Some errors have been detected in the results report "
                     "published from the Analysis Request %s. The Analysis "
                     "Request %s has been created automatically and the "
                     "previous has been invalidated.<br/>The possible mistake "
                     "has been picked up and is under investigation.<br/><br/>"
                     "%s%s"
                     ) % (aranchor, naranchor, addremarks, lab_address)
            msg_txt = MIMEText(safe_unicode(body).encode('utf-8'),
                               _subtype='html')
            mime_msg.preamble = 'This is a multi-part MIME message.'
            mime_msg.attach(msg_txt)
            try:
                host = getToolByName(self.context, 'MailHost')
                host.send(mime_msg.as_string(), immediate=True)
            except Exception, msg:
                message = self.context.translate(
                        _('Unable to send an email to alert lab '
                          'client contacts that the Analysis Request has been '
                          'retracted: %s')) % msg
                self.context.plone_utils.addPortalMessage(message, 'warning')

            message = self.context.translate('${items} invalidated.',
                                mapping={'items': ar.getRequestID()})
            self.context.plone_utils.addPortalMessage(message, 'warning')
            self.request.response.redirect(newar.absolute_url())

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

    def doPublish(self, context, request, action, analysis_requests):
        return doPublish(context, request, action, analysis_requests)

    def cloneAR(self, ar):
        _id = ar.aq_parent.invokeFactory('AnalysisRequest', id=tmpID())
        newar = ar.aq_parent[_id]
        newar.edit(
            title=ar.title,
            description=ar.description,
            RequestID=newar.getId(),
            Contact=ar.getContact(),
            CCContact=ar.getCCContact(),
            CCEmails=ar.getCCEmails(),
            Batch=ar.getBatch(),
            Template=ar.getTemplate(),
            Profile=ar.getProfile(),
            Sample=ar.getSample(),
            SamplingDate=ar.getSamplingDate(),
            SampleType=ar.getSampleType(),
            SamplePoint=ar.getSamplePoint(),
            ClientOrderNumber=ar.getClientOrderNumber(),
            ClientReference=ar.getClientReference(),
            ClientSampleID=ar.getClientSampleID(),
            SamplingDeviation=ar.getSamplingDeviation(),
            SampleCondition=ar.getSampleCondition(),
            DefaultContainerType=ar.getDefaultContainerType(),
            AdHoc=ar.getAdHoc(),
            Composite=ar.getComposite(),
            ReportDryMatter=ar.getReportDryMatter(),
            InvoiceExclude=ar.getInvoiceExclude(),
            Attachment=ar.getAttachment(),
            Invoice=ar.getInvoice(),
            DateReceived=ar.getDateReceived(),
            MemberDiscount=ar.getMemberDiscount()
        )

        # Set the results for each AR analysis
        ans = ar.getAnalyses(full_objects=True)
        for an in ans:
            newar.invokeFactory("Analysis", id=an.getKeyword())
            nan = newar[an.getKeyword()]
            nan.edit(
                Service=an.getService(),
                Calculation=an.getCalculation(),
                InterimFields=an.getInterimFields(),
                Result=an.getResult(),
                ResultDM=an.getResultDM(),
                Retested=False,
                MaxTimeAllowed=an.getMaxTimeAllowed(),
                DueDate=an.getDueDate(),
                Duration=an.getDuration(),
                ReportDryMatter=an.getReportDryMatter(),
                Analyst=an.getAnalyst(),
                Instrument=an.getInstrument(),
                SamplePartition=an.getSamplePartition())
            nan.unmarkCreationFlag()
            zope.event.notify(ObjectInitializedEvent(nan))
            changeWorkflowState(nan, 'bika_analysis_workflow',
                                'to_be_verified')
            nan.reindexObject()

        newar.reindexObject()
        newar.aq_parent.reindexObject()
        renameAfterCreation(newar)
        newar.edit(RequestID=newar.getId())

        if hasattr(ar, 'setChildAnalysisRequest'):
            ar.setChildAnalysisRequest(newar)
        newar.setParentAnalysisRequest(ar)
        return newar

class AnalysisRequestViewView(BrowserView):
    """ AR View form
        The AR fields are printed in a table, using analysisrequest_view.py
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")
    header_table = ViewPageTemplateFile("templates/header_table.pt")
    messages = []

    def __init__(self, context, request):
        super(AnalysisRequestViewView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisrequest_big.png"
        self.messages = []

    def __call__(self):
        form = self.request.form
        ar = self.context
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        checkPermission = self.context.portal_membership.checkPermission
        getAuthenticatedMember = self.context.portal_membership.getAuthenticatedMember
        workflow = getToolByName(self.context, 'portal_workflow')

        ## Create header_table data rows
        sample = self.context.getSample()
        sp = sample.getSamplePoint()
        st = sample.getSampleType()

        contact = self.context.getContact()
        contacts = []
        for cc in self.context.getCCContact():
            contacts.append(cc)
        if contact in contacts:
            contacts.remove(contact)
        ccemails = []
        for cc in contacts:
            ccemails.append("%s &lt;<a href='mailto:%s'>%s</a>&gt;" \
                % (cc.Title(), cc.getEmailAddress(), cc.getEmailAddress()))
        cc_uids = [c.UID() for c in contacts]
        cc_titles = [c.Title() for c in contacts]
        emails = self.context.getCCEmails()
        if type(emails) == str:
            emails = emails and [emails,] or []
        cc_emails = []
        cc_hrefs = []
        for cc in emails:
            cc_emails.append(cc)
            cc_hrefs.append("<a href='mailto:%s'>%s</a>"%(cc, cc))

        # Some sample fields are editable here
        if workflow.getInfoFor(sample, 'cancellation_state') == "cancelled":
            allow_sample_edit = False
            allow_ar_edit = False
        else:
            edit_states = ['to_be_sampled', 'to_be_preserved', 'sample_due']
            ar_edit_states = ['sample_registered', 'to_be_sampled', 'sampled',
                              'to_be_preserved', 'sample_due', 'attachment_due',
                              'sample_received', 'to_be_verified']
            allow_sample_edit = checkPermission(EditSample, sample) \
                and workflow.getInfoFor(sample, 'review_state') in edit_states
            allow_ar_edit = checkPermission(EditAR, self.context) \
                and workflow.getInfoFor(self.context, 'review_state') in ar_edit_states \
                and workflow.getInfoFor(self.context, 'cancellation_state') == 'active'

        SamplingWorkflowEnabled =\
            self.context.bika_setup.getSamplingWorkflowEnabled()
        samplers = getUsers(sample, ['Sampler', 'LabManager', 'Manager'])

        samplingdeviations = DisplayList(
            [(sd.UID, sd.title) for sd \
             in bsc(portal_type = 'SamplingDeviation',
                    inactive_state = 'active')])

        sampleconditions = DisplayList(
            [(sc.UID, sc.title) for sc \
             in bsc(portal_type = 'SampleCondition',
                    inactive_state = 'active')])

        batch = self.context.getBatch()
        if allow_ar_edit:
            contactlabel = "<a href='#' id='open_cc_browser'>%s</a>" % \
                          (self.context.translate(_('Contact Person')))
        else:
            contactlabel = self.context.translate(_('Contact Person'))

        self.header_columns = 3
        self.header_rows = [
            {'id': 'SampleID',
             'title': _('Sample ID'),
             'allow_edit': False,
             'value': "<a href='%s'>%s</a>"%(sample.absolute_url(), sample.id),
             'condition':True,
             'type': 'text'},
            {'id': 'BatchID',
             'title': _('Batch ID'),
             'allow_edit': False,
             'value': batch and batch.getBatchID() or '',
             'condition':True,
             'type': 'text'},
            {'id': 'Contact',
             'title': contactlabel,
             'allow_edit': False,
             'value': "<input name='cc_uids' type='hidden' id='cc_uids' value='%s'/>\
                       <a href='%s'><span name='primary_contact' id='primary_contact' value='%s'>%s</span></a>\
                       &lt;<a href='mailto:%s'>%s</a>&gt;<br/>\
                       <span name='cc_titles' id='cc_titles' value='%s'>%s</span>"\
                       %(",".join(cc_uids),
                         contact.absolute_url(),
                         contact.UID(),
                         contact.Title(),
                         contact.getEmailAddress(),
                         contact.getEmailAddress(),
                         "; ".join(cc_titles),
                         "<br/> ".join(ccemails)),
             'condition':True,
             'type': 'text'},
            {'id': 'ClientSampleID',
             'title': _('Client SID'),
             'allow_edit': allow_ar_edit,
             'value': sample.getClientSampleID(),
             'condition':True,
             'type': 'text'},
            {'id': 'ClientReference',
             'title': _('Client Reference'),
             'allow_edit': allow_ar_edit,
             'value': sample.getClientReference(),
             'condition':True,
             'type': 'text'},
            {'id': 'ClientOrderNumber',
             'title': _('Client Order'),
             'allow_edit': allow_ar_edit,
             'value': self.context.getClientOrderNumber(),
             'condition':True,
             'type': 'text'},
            {'id': 'SampleType',
             'title': _('Sample Type'),
             'allow_edit': allow_sample_edit,
             'value': st and st.Title() or '',
             'condition':True,
             'type': 'text',
             'required': True},
            {'id': 'SampleMatrix',
             'title': _('Sample Matrix'),
             'allow_edit': False,
             'value': st.getSampleMatrix() and st.getSampleMatrix().Title() or '',
             'condition':True,
             'type': 'text'},
            {'id': 'SamplePoint',
             'title': _('Sample Point'),
             'allow_edit': allow_sample_edit,
             'value': sp and sp.Title() or '',
             'condition':True,
             'type': 'text'},
            {'id': 'Creator',
             'title': PMF('Creator'),
             'allow_edit': False,
             'value': self.user_fullname(self.context.Creator()),
             'condition':True,
             'type': 'text'},
            {'id': 'DateCreated',
             'title': PMF('Date Created'),
             'allow_edit': False,
             'value': self.context.created(),
             'condition':True,
             'formatted_value': self.ulocalized_time(self.context.created()),
             'type': 'text'},
            {'id': 'SamplingDate',
             'title': _('Sampling Date'),
             'allow_edit': allow_sample_edit,
             'value': self.ulocalized_time(
                sample.getSamplingDate(), long_format=1),
             'formatted_value': self.ulocalized_time(
                self.context.getSamplingDate()),
             'condition':True,
             'class': 'datepicker',
             'type': 'text'},
            {'id': 'DateSampled',
             'title': _('Date Sampled'),
             'allow_edit': allow_sample_edit,
             'value': sample.getDateSampled() and self.ulocalized_time(
                sample.getDateSampled()) or '',
             'formatted_value': sample.getDateSampled() and self.ulocalized_time(
                sample.getDateSampled()) or '',
             'condition':SamplingWorkflowEnabled,
             'class': 'datepicker',
             'type': 'text',
             'required': True},
            {'id': 'Sampler',
             'title': _('Sampler'),
             'allow_edit': allow_sample_edit,
             'value': sample.getSampler(),
             'formatted_value': sample.getSampler(),
             'condition':SamplingWorkflowEnabled,
             'vocabulary': samplers,
             'type': 'choices',
             'required': True},
            {'id': 'SamplingDeviation',
             'title': _('Sampling Deviation'),
             'allow_edit': allow_sample_edit,
             'value': sample.getSamplingDeviation() and sample.getSamplingDeviation().UID() or '',
             'formatted_value': sample.getSamplingDeviation() and sample.getSamplingDeviation().Title() or '',
             'condition':True,
             'vocabulary': samplingdeviations,
             'type': 'choices'},
            {'id': 'SampleCondition',
             'title': _('Sample Condition'),
             'allow_edit': allow_sample_edit,
             'value': sample.getSampleCondition() and sample.getSampleCondition().UID() or '',
             'formatted_value': sample.getSampleCondition() and sample.getSampleCondition().Title() or '',
             'condition':True,
             'vocabulary': sampleconditions,
             'type': 'choices'},
            {'id': 'DateReceived',
             'title': _('Date Received'),
             'allow_edit': False,
             'value': self.context.getDateReceived(),
             'formatted_value': self.ulocalized_time(self.context.getDateReceived()),
             'condition':True,
             'type': 'text'},
            {'id': 'Composite',
             'title': _('Composite'),
             'allow_edit': allow_sample_edit,
             'value': sample.getComposite(),
             'condition':True,
             'type': 'boolean'},
            {'id': 'AdHoc',
             'title': _('Ad-Hoc'),
             'allow_edit': allow_sample_edit,
             'value': sample.getAdHoc(),
             'condition':True,
             'type': 'boolean'},
            {'id': 'InvoiceExclude',
             'title': _('Invoice Exclude'),
             'allow_edit': allow_ar_edit,
             'value': self.context.getInvoiceExclude(),
             'condition':True,
             'type': 'boolean'},
            {'id': 'ReportDryMatter',
             'title': _('Report as Dry Matter'),
             'allow_edit': allow_sample_edit,
             'value': self.context.getReportDryMatter(),
             'condition':self.context.bika_setup.getDryMatterService(),
             'type': 'boolean'},
        ]
        if allow_sample_edit or allow_ar_edit:
            self.header_buttons = [{'name':'save_button', 'title':_('Save')}]

        ## handle_header table submit
        if form.get('header_submitted', None):
            plone.protect.CheckAuthenticator(form)
            message = None
            values = {
                'CCContact':form.get('cc_uids','').split(",")
            }
            for row in [r for r in self.header_rows if r['allow_edit']]:
                value = _u(urllib.unquote_plus(form.get(row['id'], '')))
                if row['id'] == 'SampleType':
                    if not value:
                        message = PMF(
                            u'error_required',
                            default=u'${name} is required, please correct.',
                            mapping={'name': _('Sample Type')})
                        break
                    st = bsc(portal_type='SampleType', title=value)
                    if st and len(st) == 1:
                        value = st[0].UID
                    else:
                        message = _("${sampletype} is not a valid sample type",
                                    mapping={'sampletype':value})
                        break

                elif row['id'] == 'SamplePoint':
                    value = value.replace("%s: " % _("Lab"), '')
                    if value:
                        sp = bsc(portal_type='SamplePoint', title=value)
                        if sp and len(sp) == 1:
                            value = sp[0].UID
                        else:
                            message = _("${samplepoint} is not a valid sample point",
                                        mapping={'samplepoint': value})
                            break

                elif row['id'] == 'SamplingDeviation':
                    if value:
                        sd = bsc(portal_type='SamplingDeviation', title=value)
                        if sd and len(sd) == 1:
                            value = sd[0].UID
                        else:
                            message = _("${samplingdeviation} is not a valid sample point",
                                        mapping={'samplingdeviation': value})
                            break

                values[row['id']] = value

            # boolean - checkboxes are 'true'/'on' or 'false'/missing in form.
            for row in [r for r in self.header_rows if r.get('type', '') == 'boolean']:
                value = form.get(row['id'], 'false')
                values[row['id']] = value == 'true' and True or value == 'on' and True or False

            if not message:
                self.context.edit(**values)
                self.context.reindexObject()
                sample.edit(**values)
                sample.reindexObject()
                ars = sample.getAnalysisRequests()
                # Analyses and AnalysisRequets have calculated fields
                # that are indexed; re-index all these objects.
                for ar in ars:
                    ar.reindexObject()
                    analyses = sample.getAnalyses({'review_state':'to_be_sampled'})
                    for a in analyses:
                        a.getObject().reindexObject()
                message = PMF("Changes saved.")

            # If this sample was "To Be Sampled", and the
            # Sampler and DateSampled fields were completed,
            # do the Sampled transition.
            if workflow.getInfoFor(sample, "review_state") == "to_be_sampled" \
               and form.get("Sampler", None) \
               and form.get("DateSampled", None):
                # This transition does not invoke the regular WorkflowAction
                # in analysisrequest.py
                workflow.doActionFor(sample, "sample")
                sample.reindexObject()

            self.context.plone_utils.addPortalMessage(message, 'info')
            url = self.context.absolute_url().split("?")[0]
            if len(url) > 1:
                self.request.RESPONSE.redirect(url)

        ## Create Partitions View for this ARs sample
        p = SamplePartitionsView(self.context.getSample(), self.request)
        p.show_column_toggles = False
        self.parts = p.contents_table()

        ## Create Field and Lab Analyses tables
        self.tables = {}
        for poc in POINTS_OF_CAPTURE:
            if self.context.getAnalyses(getPointOfCapture = poc):
                t = self.createAnalysesView(ar,
                                 self.request,
                                 getPointOfCapture = poc,
                                 show_categories=self.context.bika_setup.getCategoriseAnalysisServices())
                t.allow_edit = True
                t.form_id = "%s_analyses" % poc
                t.review_states[0]['transitions'] = [{'id':'submit'},
                                                     {'id':'retract'},
                                                     {'id':'verify'}]
                t.show_workflow_action_buttons = True
                t.show_select_column = True
                if getSecurityManager().checkPermission(EditFieldResults, self.context) \
                   and poc == 'field':
                    t.review_states[0]['columns'].remove('DueDate')
                self.tables[POINTS_OF_CAPTURE.getValue(poc)] = t.contents_table()

        # Un-captured field analyses may cause confusion
        if ar.getAnalyses(getPointOfCapture='field',
                          review_state=['sampled','sample_due']):
            message = _("There are field analyses without submitted results.")
            self.addMessage(message, 'info')

        ## Create QC Analyses View for this AR
        qcview = self.createQCAnalyesView(ar,
                                self.request,
                                show_categories=self.context.bika_setup.getCategoriseAnalysisServices())
        qcview.allow_edit = False
        qcview.show_select_column = False
        qcview.show_workflow_action_buttons = False
        qcview.form_id = "%s_qcanalyses"
        qcview.review_states[0]['transitions'] = [{'id':'submit'},
                                                  {'id':'retract'},
                                                  {'id':'verify'}]
        self.qctable = qcview.contents_table()

        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            anchor = childar and ("<a href='%s'>%s</a>"%(childar.absolute_url(),childar.getRequestID())) or None
            message = _('These results have been withdrawn and are '
                        'listed here for trace-ability purposes. Please follow '
                        'the link to the retest')
            if anchor:
                self.header_rows.append(
                        {'id': 'ChildAR',
                         'title': 'AR for retested results',
                         'allow_edit': False,
                         'value': anchor,
                         'condition': True,
                         'type': 'text'})
                message = (message + " %s.") % childar.getRequestID()
            else:
                message = message + "."

            self.addMessage(message, 'warning')

        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            anchor = "<a href='%s'>%s</a>" % (par.absolute_url(), par.getRequestID())
            self.header_rows.append(
                        {'id': 'ParentAR',
                         'title': 'Invalid AR retested',
                         'allow_edit': False,
                         'value': anchor,
                         'condition': True,
                         'type': 'text'})
            message = _('This Analysis Request has been '
                        'generated automatically due to '
                        'the retraction of the Analysis '
                        'Request %s.') % par.getRequestID()
            self.addMessage(message, 'info')

        self.renderMessages()
        return self.template()

    def addMessage(self, message, msgtype='info'):
        self.messages.append({'message': message, 'msgtype': msgtype})

    def renderMessages(self):
        for message in self.messages:
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message['message']), message['msgtype'])

    def createAnalysesView(self, context, request, **kwargs):
        return AnalysesView(context, request, **kwargs)

    def createQCAnalyesView(self, context, request, **kwargs):
        return QCAnalysesView(context, request, **kwargs)

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def now(self):
        return DateTime()

    def getMemberDiscountApplies(self):
        client = self.context.portal_type == 'Client' and self.context or self.context.aq_parent
        return client and client.portal_type == 'Client' and client.getMemberDiscountApplies() or False

    def analysisprofiles(self):
        """ Return applicable client and Lab AnalysisProfile records
        """
        res = []
        profiles = []
        client = self.context.portal_type == 'AnalysisRequest' \
            and self.context.aq_parent or self.context
        for profile in client.objectValues("AnalysisProfile"):
            if isActive(profile):
                profiles.append((profile.Title(), profile))
        profiles.sort(lambda x,y:cmp(x[0], y[0]))
        res += profiles
        profiles = []
        for profile in self.context.bika_setup.bika_analysisprofiles.objectValues("AnalysisProfile"):
            if isActive(profile):
                profiles.append(("%s: %s" % (self.context.translate(_('Lab')), profile.Title().decode('utf-8')),
                                  profile))
        profiles.sort(lambda x,y:cmp(x[0], y[0]))
        res += profiles
        return res

    def artemplates(self):
        """ Return applicable client and Lab ARTemplate records
        """
        res = []
        templates = []
        client = self.context.portal_type == 'AnalysisRequest' \
            and self.context.aq_parent or self.context
        for template in client.objectValues("ARTemplate"):
            if isActive(template):
                templates.append((template.Title(), template))
        templates.sort(lambda x,y:cmp(x[0], y[0]))
        res += templates
        templates = []
        for template in self.context.bika_setup.bika_artemplates.objectValues("ARTemplate"):
            if isActive(template):
                templates.append(("%s: %s" % (self.context.translate(_('Lab')), template.Title().decode('utf-8')),
                                  template))
        templates.sort(lambda x,y:cmp(x[0], y[0]))
        res += templates
        return res

    def samplingdeviations(self):
        """ SamplingDeviation vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(sd.getObject().Title(), sd.getObject()) \
               for sd in bsc(portal_type = 'SamplingDeviation',
                             inactive_state = 'active')]
        res.sort(lambda x,y:cmp(x[0], y[0]))
        return res

    def sampleconditions(self):
        """ SampleConditions vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(sd.getObject().Title(), sd.getObject()) \
               for sd in bsc(portal_type = 'SampleConditions',
                             inactive_state = 'active')]
        res.sort(lambda x,y:cmp(x[0], y[0]))
        return res

    def containertypes(self):
        """ DefaultContainerType vocabulary for AR Add
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        res = [(o.getObject().Title(), o.getObject()) \
               for o in bsc(portal_type = 'ContainerType')]
        res.sort(lambda x,y:cmp(x[0], y[0]))
        return res

    def SelectedServices(self):
        """ return information about services currently selected in the
            context AR.
            [[PointOfCapture, category uid, service uid],
             [PointOfCapture, category uid, service uid], ...]
        """
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        res = []
        for analysis in bac(portal_type = "Analysis",
                           getRequestID = self.context.RequestID):
            analysis = analysis.getObject()
            service = analysis.getService()
            res.append([service.getPointOfCapture(),
                        service.getCategoryUID(),
                        service.UID()])
        return res

    def getRestrictedCategories(self):
        if self.context.portal_type == 'Client':
            return self.context.getRestrictedCategories()
        return []

    def Categories(self):
        """ Dictionary keys: poc
            Dictionary values: (Category UID,category Title)
        """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        cats = {}
        restricted = [u.UID() for u in self.getRestrictedCategories()]
        for service in bsc(portal_type = "AnalysisService",
                           inactive_state = 'active'):
            cat = (service.getCategoryUID, service.getCategoryTitle)
            if restricted and cat[0] not in restricted:
                continue
            poc = service.getPointOfCapture
            if not cats.has_key(poc): cats[poc] = []
            if cat not in cats[poc]:
                cats[poc].append(cat)
        return cats

    def getDefaultCategories(self):
        if self.context.portal_type == 'Client':
            return self.context.getDefaultCategories()
        return []

    def DefaultCategories(self):
        """ Used in AR add context, to return list of UIDs for
        automatically-expanded categories.
        """
        cats = self.getDefaultCategories()
        return [cat.UID() for cat in cats]

    def getDefaultSpec(self):
        """ Returns 'lab' or 'client' to set the initial value of the
            specification radios
        """
        mt = getToolByName(self.context, 'portal_membership')
        pg = getToolByName(self.context, 'portal_groups')
        member = mt.getAuthenticatedMember()
        member_groups = [pg.getGroupById(group.id).getGroupName() \
                         for group in pg.getGroupsByUserId(member.id)]
        default_spec = ('Clients' in member_groups) and 'client' or 'lab'
        return default_spec

    def getAnalysisProfileTitle(self):
        """Grab the context's current AnalysisProfile Title if any
        """
        return self.context.getProfile() and \
               self.context.getProfile().Title() or ''

    def getARTemplateTitle(self):
        """Grab the context's current ARTemplate Title if any
        """
        return self.context.getTemplate() and \
               self.context.getTemplate().Title() or ''

    def get_requested_analyses(self):
        ##
        ##title=Get requested analyses
        ##
        result = []
        cats = {}
        for analysis in self.context.getAnalyses(full_objects = True):
            if analysis.review_state == 'not_requested':
                continue
            service = analysis.getService()
            category_name = service.getCategoryTitle()
            if not category_name in cats:
                cats[category_name] = {}
            cats[category_name][analysis.Title()] = analysis

        cat_keys = cats.keys()
        cat_keys.sort(lambda x, y:cmp(x.lower(), y.lower()))
        for cat_key in cat_keys:
            analyses = cats[cat_key]
            analysis_keys = analyses.keys()
            analysis_keys.sort(lambda x, y:cmp(x.lower(), y.lower()))
            for analysis_key in analysis_keys:
                result.append(analyses[analysis_key])
        return result

    def get_analyses_not_requested(self):
        ##
        ##title=Get analyses which have not been requested by the client
        ##

        result = []
        for analysis in self.context.getAnalyses():
            if analysis.review_state == 'not_requested':
                result.append(analysis)

        return result

    def get_analysisrequest_verifier(self, analysisrequest):
        ## Script (Python) "get_analysisrequest_verifier"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=analysisrequest
        ##title=Get analysis workflow states
        ##

        ## get the name of the member who last verified this AR
        ##  (better to reverse list and get first!)

        wtool = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')

        verifier = None
        try:
            review_history = wtool.getInfoFor(analysisrequest, 'review_history')
        except:
            return 'access denied'

        review_history = [review for review in review_history if review.get('action', '')]
        if not review_history:
            return 'no history'
        for items in  review_history:
            action = items.get('action')
            if action != 'verify':
                continue
            actor = items.get('actor')
            member = mtool.getMemberById(actor)
            if not member:
                verifier = actor
                continue
            verifier = member.getProperty('fullname')
            if verifier is None or verifier == '':
                verifier = actor
        return verifier


class AnalysisRequestAddView(AnalysisRequestViewView):
    """ The main AR Add form
    """
    implements(IViewView, IAnalysisRequestAddView)
    template = ViewPageTemplateFile("templates/ar_add.pt")

    def __init__(self, context, request):
        AnalysisRequestViewView.__init__(self, context, request)
        self.came_from = "add"
        self.can_edit_sample = True
        self.can_edit_ar = True
        self.DryMatterService = self.context.bika_setup.getDryMatterService()
        request.set('disable_plone.rightcolumn', 1)
        self.col_count = self.request.get('col_count', 6)
        try:
            self.col_count = int(self.col_count)
        except:
            self.col_count == 6

    def __call__(self):
        self.request.set('disable_border', 1)
        return self.template()

    def getContacts(self):
        adapter = getAdapter(self.context.aq_parent, name='getContacts')
        return adapter()

    def getCCsForContact(self, contact_uid, **kwargs):
        """Get the default CCs for a particular client contact.  Used
        once in form creation. #XXX search and destroy: cc_titles, cc_uids
        """
        uc = getToolByName(self.context, 'uid_catalog')
        contact = uc(UID=contact_uid)
        contacts = []
        if contact:
            contact = contact and contact[0].getObject() or None
            contacts = [{'title': x.Title(), 'uid': x.UID()} for x in
                        contact.getCCContact()]
        if kwargs.get('json', ''):
            return json.dumps(contacts)
        else:
            return contacts

    def getWidgetVisibility(self):
        adapter = getAdapter(self.context, name='getWidgetVisibility')
        return adapter()

    def partitioned_services(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        ps = []
        for service in bsc(portal_type='AnalysisService'):
            service = service.getObject()
            if service.getPartitionSetup() \
               or service.getSeparate():
                ps.append(service.UID())
        return json.dumps(ps)

    def listProfiles(self):
        ## List of selected services for each AnalysisProfile
        profiles = {}
        client = self.context.portal_type == 'AnalysisRequest' \
            and self.context.aq_parent or self.context
        for context in (client, self.context.bika_setup.bika_analysisprofiles):
            for profile in [p for p in context.objectValues("AnalysisProfile")
                            if isActive(p)]:
                slist = {}
                profile_services = profile.getService()
                if type(profile_services) not in (list, tuple):
                    profile_services = [profile_services, ]
                for p_service in profile_services:
                    key = "%s_%s" % (p_service.getPointOfCapture(),
                                     p_service.getCategoryUID())
                    if key in slist:
                        slist[key].append(p_service.UID())
                    else:
                        slist[key] = [p_service.UID(), ]

                title = context == self.context.bika_setup.bika_analysisprofiles \
                    and "%s: %s" % (self.context.translate(_('Lab')), profile.Title().decode('utf-8')) \
                    or profile.Title()

                p_dict = {
                    'UID':profile.UID(),
                    'Title':title,
                    'Services':slist,
                }
                profiles[profile.UID()] = p_dict
        return json.dumps(profiles)

    def listTemplates(self):
        ## parameters for all ARTemplates
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        templates = {}
        client = self.context.portal_type == 'AnalysisRequest' \
            and self.context.aq_parent or self.context
        for context in (client, self.context.bika_setup.bika_artemplates):
            for template in [t for t in context.objectValues("ARTemplate")
                             if isActive(t)]:
                title = context == self.context.bika_setup.bika_artemplates \
                    and "%s: %s" % (self.context.translate(_('Lab')), template.Title().decode('utf-8')) \
                    or template.Title()
                sp_title = template.getSamplePoint().Title() \
                    if template.getSamplePoint() else ''
                st_title = template.getSampleType().Title() \
                    if template.getSampleType() else ''
                sp_uid = template.getSamplePoint().UID() \
                    if template.getSamplePoint() else ''
                st_uid = template.getSampleType().UID() \
                    if template.getSampleType() else ''
                profile = template.getAnalysisProfile()
                Analyses = [{
                    'service_poc':bsc(UID=x['service_uid'])[0].getObject().getPointOfCapture(),
                    'category_uid':bsc(UID=x['service_uid'])[0].getObject().getCategoryUID(),
                    'partition':x['partition'],
                    'service_uid':x['service_uid']}
                            for x in template.getAnalyses()]
                t_dict = {
                    'UID':template.UID(),
                    'Title':template.Title(),
                    'Profile':profile and profile.Title() or '',
                    'Profile_uid':profile and profile.UID() or '',
                    'SamplePoint':sp_title,
                    'SamplePoint_uid':sp_uid,
                    'SampleType':st_title,
                    'SampleType_uid':st_uid,
                    'Partitions':template.getPartitions(),
                    'Analyses':Analyses,
                    'ReportDryMatter':template.getReportDryMatter(),
                }
                templates[template.UID()] = t_dict
        return json.dumps(templates)


class SecondaryARSampleInfo(BrowserView):
    """Return fieldnames and pre-digested values for Sample fields which
    javascript must disable/display while adding secondary ARs
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        uid = self.request.get('Sample_uid')
        uc = getToolByName(self.context, "uid_catalog")
        sample = uc(UID=uid)[0].getObject()
        sample_schema = sample.Schema()
        adapter = getAdapter(self.context, name='getWidgetVisibility')
        wv = adapter()
        fieldnames = wv.get('secondary', {}).get('invisible', [])
        ret = []
        for fieldname in fieldnames:
            if fieldname in sample_schema:
                fieldvalue = sample_schema[fieldname].getAccessor(sample)()
                if fieldvalue is None:
                    fieldvalue = ''
                if hasattr(fieldvalue, 'Title'):
                    fieldvalue = fieldvalue.Title()
                if hasattr(fieldvalue, 'year'):
                    fieldvalue = fieldvalue.strftime(self.date_format_short)
            else:
                fieldvalue = ''
            ret.append([fieldname, fieldvalue])
        return json.dumps(ret)


class AnalysisRequestAnalysesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    template = ViewPageTemplateFile("templates/analysisrequest_analyses.pt")

    def __init__(self, context, request):
        super(AnalysisRequestAnalysesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title',
                              'inactive_state': 'active',}
        self.context_actions = {}
        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisrequest_big.png"
        self.title = self.context.Title()
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.table_only = True
        self.show_select_all_checkbox = False
        self.pagesize = 1000
        analyses = self.context.getAnalyses(full_objects=True)
        self.analyses = dict([(a.getServiceUID(), a) for a in analyses])
        self.selected = [a.getServiceUID() for a in analyses]
        self.show_categories = self.context.bika_setup.getCategoriseAnalysisServices()
        self.expand_all_categories = False


        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title',
                      'sortable': False,},
            'Price': {'title': _('Price'),
                      'sortable': False,},
            'Partition': {'title': _('Partition'),
                          'sortable': False, },
        }

        ShowPrices = self.context.bika_setup.getShowPrices()
        columns = ['Title', 'Price', 'Partition'] if ShowPrices \
            else ['Title', 'Partition']

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': columns,
             'transitions': [{'id': 'empty'}, ],  # none
             'custom_actions': [{'id': 'save_analyses_button',
                                 'title': _('Save')}, ],
             },
        ]

        ## Create Partitions View for this ARs sample
        sample = self.context.getSample()
        p = SamplePartitionsView(sample, self.request)
        p.table_only = True
        p.allow_edit = False
        p.show_select_column = False
        p.review_states[0]['transitions'] = [{'id': 'empty'}, ]  # none
        p.review_states[0]['custom_actions'] = []
        p.review_states[0]['columns'] = ['PartTitle',
                                         'getContainer',
                                         'getPreservation',
                                         'state_title']

        if not context.bika_setup.getShowPartitions():
            self.review_states[0]['columns'].remove('Partition')

        self.parts = p.contents_table()

    def folderitems(self):
        self.categories = []

        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        self.allow_edit = 'LabManager' in roles or 'Manager' in roles
        items = BikaListingView.folderitems(self)
        sample = self.context.getSample()
        analyses = self.context.getAnalyses(full_objects = True)
        review_states = dict(
            [(a.getService().getKeyword(), wf.getInfoFor(a, 'review_state'))
             for a in analyses])

        partitions = [{'ResultValue':o.Title(), 'ResultText':o.getId()}
                      for o in
                      self.context.getSample().objectValues('SamplePartition')
                      if wf.getInfoFor(o, 'cancellation_state', 'active') == 'active']
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            cat = obj.getCategoryTitle()
            items[x]['category'] = cat
            if cat not in self.categories:
                self.categories.append(cat)

            items[x]['selected'] = items[x]['uid'] in self.selected

            items[x]['class']['Title'] = 'service_title'

            # js checks in row_data if an analysis may be removed.
            row_data = {}
            keyword = obj.getKeyword()
            if keyword in review_states.keys() \
               and review_states[keyword] not in ['sample_due',
                                                  'to_be_sampled',
                                                  'to_be_preserved',
                                                  'sample_received',
                                                  ]:
                row_data['disabled'] = True
            items[x]['row_data'] = json.dumps(row_data)

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()

            locale = locales.getLocale('en')
            currency = self.context.bika_setup.getCurrency()
            symbol = locale.numbers.currencies[currency].symbol
            items[x]['before']['Price'] = symbol
            items[x]['Price'] = obj.getPrice()
            items[x]['class']['Price'] = 'nowrap'
            items[x]['allow_edit'] = ['Price', 'Partition']
            if not items[x]['selected']:
                items[x]['edit_condition'] = {'Partition':False,
                                              'Price':False}

            items[x]['required'].append('Partition')
            items[x]['choices']['Partition'] = partitions

            if obj.UID() in self.analyses:
                part = self.analyses[obj.UID()].getSamplePartition()
                part = part and part or obj
                items[x]['Partition'] = part.Title()
            else:
                items[x]['Partition'] = ''

            after_icons = ''
            if obj.getAccredited():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/accredited.png'\
                title='%s'>"%(self.portal_url,
                              self.context.translate(
                                  _("Accredited")))
            if obj.getReportDryMatter():
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/dry.png'\
                title='%s'>"%(self.portal_url,
                              self.context.translate(
                                  _("Can be reported as dry matter")))
            if obj.getAttachmentOption() == 'r':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_reqd.png'\
                title='%s'>"%(self.portal_url,
                              self.context.translate(
                              _("Attachment required")))
            if obj.getAttachmentOption() == 'n':
                after_icons += "<img\
                src='%s/++resource++bika.lims.images/attach_no.png'\
                title='%s'>"%(self.portal_url,
                              self.context.translate(
                                  _('Attachment not permitted')))
            if after_icons:
                items[x]['after']['Title'] = after_icons

        self.categories.sort()
        return items

class AnalysisRequestManageResultsView(AnalysisRequestViewView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_manage_results.pt")

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')

        if workflow.getInfoFor(ar, 'cancellation_state') == "cancelled":
            self.request.response.redirect(ar.absolute_url())
        elif not(getSecurityManager().checkPermission(EditResults, ar)):
            self.request.response.redirect(ar.absolute_url())
        else:
            self.tables = {}
            for poc in POINTS_OF_CAPTURE:
                if self.context.getAnalyses(getPointOfCapture = poc):
                    t = self.createAnalysesView(ar,
                                     self.request,
                                     getPointOfCapture = poc,
                                     sort_on = 'getServiceTitle',
                                     show_categories = self.context.bika_setup.getCategoriseAnalysisServices())
                    t.form_id = "ar_manage_results_%s" % poc
                    t.allow_edit = True
                    t.review_states[0]['transitions'] = [{'id':'submit'},
                                                         {'id':'retract'},
                                                         {'id':'verify'}]
                    t.show_select_column = True
                    self.tables[POINTS_OF_CAPTURE.getValue(poc)] = t.contents_table()
            return self.template()

    def createAnalysesView(self, context, request, **kwargs):
        return AnalysesView(context, request, **kwargs)


class AnalysisRequestResultsNotRequestedView(AnalysisRequestManageResultsView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_analyses_not_requested.pt")

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')

        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            childid = childar and childar.getRequestID() or None
            message = _('This Analysis Request has been withdrawn and is shown '
                        'for trace-ability purposes only. Retest: %s.') \
                        % (childid or '')
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message), 'warning')

        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            message = _('This Analysis Request has been '
                        'generated automatically due to '
                        'the retraction of the Analysis '
                        'Request %s.') % par.getRequestID()
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message), 'info')

        if workflow.getInfoFor(ar, 'cancellation_state') == "cancelled":
            self.request.response.redirect(ar.absolute_url())
        elif not(getSecurityManager().checkPermission(ResultsNotRequested, ar)):
            self.request.response.redirect(ar.absolute_url())
        else:
            return self.template()

class AnalysisRequestSelectCCView(BikaListingView):

    template = ViewPageTemplateFile("templates/ar_select_cc.pt")

    def __init__(self, context, request):
        super(AnalysisRequestSelectCCView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/contact_big.png"
        self.title = _("Contacts to CC")
        self.description = _("Select the contacts that will receive analysis results for this request.")
        self.catalog = "portal_catalog"

        # c is the Context inside of which we will search for Contacts.
        c = None
        if context.portal_type == 'Batch':
            if hasattr(context, 'getClientUID'):
                client = self.portal_catalog(portal_type='Client', UID=context.getClientUID())
                if client:
                    c = client[0].getObject()
                else:
                    c = context
            else:
                c = context
        elif context.portal_type == 'AnalysisRequest':
            c = context.aq_parent
        if not c:
            c = context

        self.contentFilter = {'portal_type': 'Contact',
                              'sort_on':'sortable_title',
                              'inactive_state': 'active',
                              'path': {"query": "/".join(c.getPhysicalPath()),
                                       "level" : 0 }
                              }

        self.show_sort_column = False
        self.show_select_row = False
        self.show_workflow_action_buttons = True
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "select_cc"

        request.set('disable_border', 1)

        self.columns = {
            'Fullname': {'title': _('Full Name'),
                         'index': 'getFullname'},
            'EmailAddress': {'title': _('Email Address')},
            'BusinessPhone': {'title': _('Business Phone')},
            'MobilePhone': {'title': _('Mobile Phone')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Fullname',
                         'EmailAddress',
                         'BusinessPhone',
                         'MobilePhone'],
             'transitions': [{'id':'empty'}, ], # none
             'custom_actions':[{'id': 'save_selection_button', 'title': 'Save selection'}, ] # do not translate this title.
             }
        ]

    def folderitems(self, full_objects = False):
        pc = getToolByName(self.context, 'portal_catalog')
        self.contentsMethod = pc
        old_items = BikaListingView.folderitems(self)
        items = []
        for item in old_items:
            if not item.has_key('obj'):
                items.append(item)
                continue
            obj = item['obj']
            if obj.UID() in self.request.get('hide_uids', ()):
                continue
            item['Fullname'] = obj.getFullname()
            item['EmailAddress'] = obj.getEmailAddress()
            item['BusinessPhone'] = obj.getBusinessPhone()
            item['MobilePhone'] = obj.getMobilePhone()
            if self.request.get('selected_uids', '').find(item['uid']) > -1:
                item['selected'] = True
            items.append(item)
        return items

class AnalysisRequestSelectSampleView(BikaListingView):

    template = ViewPageTemplateFile("templates/ar_select_sample.pt")

    def __init__(self, context, request):
        super(AnalysisRequestSelectSampleView, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/sample_big.png"
        self.title = _("Select Sample")
        self.description = _("Select a sample to create a secondary AR")
        c = context.portal_type == 'AnalysisRequest' and context.aq_parent or context
        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'Sample',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'review_state': ['to_be_sampled', 'to_be_preserved',
                                               'sample_due', 'sample_received'],
                              'cancellation_state': 'active',
                              'path': {"query": "/".join(c.getPhysicalPath()),
                                       "level" : 0 }
                              }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.form_id = "select_sample"

        self.pagesize = 25

        request.set('disable_border', 1)

        self.columns = {
            'SampleID': {'title': _('Sample ID'),
                         'index': 'getSampleID', },
            'ClientSampleID': {'title': _('Client SID'),
                               'index': 'getClientSampleID', },
            'ClientReference': {'title': _('Client Reference'),
                                'index': 'getClientReference', },
            'SampleTypeTitle': {'title': _('Sample Type'),
                                'index': 'getSampleTypeTitle', },
            'SamplePointTitle': {'title': _('Sample Point'),
                                 'index': 'getSamplePointTitle', },
            'DateReceived': {'title': _('Date Received'),
                             'index': 'getDateReceived', },
            'SamplingDate': {'title': _('Sampling Date'),
                             'index': 'getSamplingDate', },
            'state_title': {'title': _('State'),
                            'index': 'review_state', },
        }

        self.review_states = [
            {'id':'default',
             'contentFilter':{},
             'title': _('All Samples'),
             'columns': ['SampleID',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'SamplingDate',
                         'state_title']},
            {'id':'due',
             'title': _('Sample Due'),
             'contentFilter': {'review_state': 'sample_due'},
             'columns': ['SampleID',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'SamplingDate']},
            {'id':'sample_received',
             'title': _('Sample received'),
             'contentFilter': {'review_state': 'sample_received'},
             'columns': ['SampleID',
                         'ClientReference',
                         'ClientSampleID',
                         'SampleTypeTitle',
                         'SamplePointTitle',
                         'SamplingDate',
                         'DateReceived']},
        ]

    def folderitems(self, full_objects = False):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['class']['SampleID'] = "select_sample"
            if items[x]['uid'] in self.request.get('hide_uids', ''): continue
            if items[x]['uid'] in self.request.get('selected_uids', ''):
                items[x]['selected'] = True
            items[x]['view_url'] = obj.absolute_url() + "/view"
            items[x]['ClientReference'] = obj.getClientReference()
            items[x]['ClientSampleID'] = obj.getClientSampleID()
            items[x]['SampleID'] = obj.getSampleID()
            if obj.getSampleType().getHazardous():
                items[x]['after']['SampleID'] = \
                     "<img src='%s/++resource++bika.lims.images/hazardous.png'\
                     title='%s'>"%(self.portal_url,
                                   self.context.translate(_("Hazardous")))
            items[x]['SampleTypeTitle'] = obj.getSampleTypeTitle()
            items[x]['SamplePointTitle'] = obj.getSamplePointTitle()
            items[x]['row_data'] = json.dumps({
                'SampleID': items[x]['title'],
                'ClientReference': items[x]['ClientReference'],
                'Requests': ", ".join([o.Title() for o in obj.getAnalysisRequests()]),
                'ClientSampleID': items[x]['ClientSampleID'],
                'DateReceived': obj.getDateReceived() and self.ulocalized_time(
                    obj.getDateReceived()) or '',
                'SamplingDate': obj.getSamplingDate() and self.ulocalized_time(
                    obj.getSamplingDate()) or '',
                'SampleType': items[x]['SampleTypeTitle'],
                'SamplePoint': items[x]['SamplePointTitle'],
                'Composite': obj.getComposite(),
                'AdHoc': obj.getAdHoc(),
                'SamplingDeviation': obj.getSamplingDeviation() and \
                                     obj.getSamplingDeviation().UID() or '',
                'field_analyses': self.FieldAnalyses(obj),
                'column': self.request.get('column', None),
            })
            items[x]['DateReceived'] = obj.getDateReceived() and \
                 self.ulocalized_time(obj.getDateReceived(), long_format=1) or ''
            items[x]['SamplingDate'] = obj.getSamplingDate() and \
                 self.ulocalized_time(obj.getSamplingDate(), long_format=1) or ''
        return items

    def FieldAnalyses(self, sample):
        """ Returns a dictionary of lists reflecting Field Analyses
            linked to this sample (meaning field analyses on this sample's
            first AR. For secondary ARs field analyses and their values are
            read/written from the first AR.)
            {category_uid: [service_uid, service_uid], ... }
        """
        res = {}
        ars = sample.getAnalysisRequests()
        if len(ars) > 0:
            for analysis in ars[0].getAnalyses(full_objects = True):
                service = analysis.getService()
                if service.getPointOfCapture() == 'field':
                    catuid = service.getCategoryUID()
                    if res.has_key(catuid):
                        res[catuid].append(service.UID())
                    else:
                        res[catuid] = [service.UID()]
        return res

class ajaxExpandCategory(BikaListingView):
    """ ajax requests pull this view for insertion when category header
    rows are clicked/expanded. """
    template = ViewPageTemplateFile("templates/analysisrequest_analysisservices.pt")

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)
        if hasattr(self.context, 'getRequestID'): self.came_from = "edit"
        return self.template()

    def bulk_discount_applies(self):
        if self.context.portal_type == 'AnalysisRequest':
            client = self.context.aq_parent
        elif self.context.portal_type == 'Batch':
            bc = getToolByName(self.context, 'bika_catalog')
            proxies = bc(portal_type="AnalysisRequest", getBatchUID=self.context.UID())
            client = proxies[0].getObject()
        elif self.context.portal_type == 'Client':
            client = self.context
        else:
            return False
        return client.getBulkDiscount()

    def Services(self, poc, CategoryUID):
        """ return a list of services brains """
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        services = bsc(portal_type = "AnalysisService",
                       sort_on = 'sortable_title',
                       inactive_state = 'active',
                       getPointOfCapture = poc,
                       getCategoryUID = CategoryUID)
        return services

class ajaxAnalysisRequestSubmit():

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):

        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)
        came_from = form.has_key('came_from') and form['came_from'] or 'add'
        wftool = getToolByName(self.context, 'portal_workflow')
        uc = getToolByName(self.context, 'uid_catalog')
        bc = getToolByName(self.context, 'bika_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')

        SamplingWorkflowEnabled =\
            self.context.bika_setup.getSamplingWorkflowEnabled()

        errors = {}
        def error(field = None, column = None, message = None):
            if not message:
                message = self.context.translate(
                    PMF('Input is required but no input given.'))
            if (column or field):
                error_key = " %s.%s" % (int(column) + 1, field or '')
            else:
                error_key = "Form Error"
            errors[error_key] = message

        form_parts = json.loads(self.request.form['parts'])

        # First make a list of non-empty columns
        columns = []
        for column in range(int(form['col_count'])):
            if not form.has_key("ar.%s" % column):
                continue
            ar = form["ar.%s" % column]
            if 'Analyses' not in ar.keys():
                continue
            columns.append(column)

        if len(columns) == 0:
            error(message = self.context.translate(_("No analyses have been selected")))
            return json.dumps({'errors':errors})

        # Now some basic validation
        required_fields = [field.getName() for field
                           in AnalysisRequestSchema.fields()
                           if field.required]

        for column in columns:
            formkey = "ar.%s" % column
            ar = form[formkey]

            # # Secondary ARs don't have sample fields present in the form data
            # if 'Sample_uid' in ar and ar['Sample_uid']:
            #     adapter = getAdapter(self.context, name='getWidgetVisibility')
            #     wv = adapter().get('secondary', {}).get('invisible', [])
            #     required_fields = [x for x in required_fields if x not in wv]

            # check that required fields have values
            for field in required_fields:
                # These two are still special.
                if field in ['Contact', 'RequestID']:
                    continue
                if (field in ar and not ar.get(field, '')):
                    error(field, column)

        if errors:
            return json.dumps({'errors':errors})

        prices = form.get('Prices', None)
        ARs = []

        # if a new profile is created automatically,
        # this flag triggers the status message
        new_profile = None

        # The actual submission
        for column in columns:
            if form_parts:
                parts = form_parts[str(column)]
            else:
                parts = []
            formkey = "ar.%s" % column
            values = form[formkey].copy()

            # resolved values is formatted as acceptable by archetypes
            # widget machines
            resolved_values = {}
            for k,v in values.items():
                # Analyses, we handle that specially.
                if k == 'Analyses':
                    continue
                # Contact things, there's only one on the form, so we
                # insert those values here manually.
                resolved_values['Contact'] = form['Contact']
                resolved_values['CCContact'] = form['cc_uids'].split(",")
                resolved_values['CCEmails'] = form['CCEmails']

                if values.has_key("%s_uid" % k):
                    resolved_values[k] = values["%s_uid"%k]
                else:
                    resolved_values[k] = values[k]

            client = uc(UID = values['Client_uid'])[0].getObject()
            if values.get('Sample_uid', ''):
                # Secondary AR
                sample = uc(UID=values['Sample_uid'])[0].getObject()
            else:
                # Primary AR
                _id = client.invokeFactory('Sample', id = 'tmp')
                sample = client[_id]
                saved_form = self.request.form
                self.request.form = resolved_values
                sample.processForm()
                self.request.form = saved_form
                if SamplingWorkflowEnabled:
                    wftool.doActionFor(sample, 'sampling_workflow')
                else:
                    wftool.doActionFor(sample, 'no_sampling_workflow')
                # Object has been renamed
                sample.edit(SampleID = sample.getId())

            resolved_values['Sample'] = sample
            resolved_values['Sample_uid'] = sample.UID()

            # Selecting a template sets the hidden 'parts' field to template values.
            # Selecting a profile will allow ar_add.js to fill in the parts field.
            # The result is the same once we are here.
            if not parts:
                parts = [{'services':[],
                         'container':[],
                         'preservation':'',
                         'separate':False}]

            # Apply DefaultContainerType to partitions without a container
            d_clist = []
            D_UID = values.get("DefaultContainerType_uid", None)
            if D_UID:
                d_clist = [c.UID for c in bsc(portal_type='Container')
                           if c.getObject().getContainerType().UID() == D_UID]
                for i in range(len(parts)):
                    if not parts[i].get('container', []):
                        parts[i]['container'] = d_clist

            # create the AR
            Analyses = values['Analyses']

            saved_form = self.request.form
            self.request.form = resolved_values
            client.invokeFactory('AnalysisRequest', id = 'tmp')
            ar = client['tmp']
            ar.processForm()
            self.request.form = saved_form
            # Object has been renamed
            ar.edit(RequestID = ar.getId())

            # Create sample partitions
            parts_and_services = {}
            for _i in range(len(parts)):
                p = parts[_i]
                part_prefix = sample.getId() + "-P"
                if '%s%s'%(part_prefix, _i+1) in sample.objectIds():
                    parts[_i]['object'] = sample['%s%s'%(part_prefix,_i+1)]
                    parts_and_services['%s%s'%(part_prefix, _i+1)] = p['services']
                else:
                    _id = sample.invokeFactory('SamplePartition', id = 'tmp')
                    part = sample[_id]
                    parts[_i]['object'] = part
                    # Sort available containers by capacity and select the
                    # smallest one possible.
                    containers = [_p.getObject() for _p in bsc(UID=p['container'])]
                    if containers:
                        containers.sort(lambda a,b:cmp(
                            a.getCapacity() \
                            and mg(float(a.getCapacity().lower().split(" ", 1)[0]), a.getCapacity().lower().split(" ", 1)[1]) \
                            or mg(0, 'ml'),
                            b.getCapacity() \
                            and mg(float(b.getCapacity().lower().split(" ", 1)[0]), b.getCapacity().lower().split(" ", 1)[1]) \
                            or mg(0, 'ml')
                        ))
                        container = containers[0]
                    else:
                        container = None

                    # If container is pre-preserved, set the part's preservation,
                    # and flag the partition to be transitioned below.
                    if container \
                       and container.getPrePreserved() \
                       and container.getPreservation():
                        preservation = container.getPreservation().UID()
                        parts[_i]['prepreserved'] = True
                    else:
                        preservation = p['preservation']
                        parts[_i]['prepreserved'] = False

                    part.edit(
                        Container = container,
                        Preservation = preservation,
                    )
                    part.processForm()
                    if SamplingWorkflowEnabled:
                        wftool.doActionFor(part, 'sampling_workflow')
                    else:
                        wftool.doActionFor(part, 'no_sampling_workflow')
                    parts_and_services[part.id] = p['services']

            if SamplingWorkflowEnabled:
                wftool.doActionFor(ar, 'sampling_workflow')
            else:
                wftool.doActionFor(ar, 'no_sampling_workflow')

            ARs.append(ar.getId())

            new_analyses = ar.setAnalyses(Analyses, prices = prices)
            ar_analyses = ar.objectValues('Analysis')

            # Add analyses to sample partitions
            for part in sample.objectValues("SamplePartition"):
                part_services = parts_and_services[part.id]
                analyses = [a for a in new_analyses
                            if a.getServiceUID() in part_services]
                if analyses:
                    part.edit(
                        Analyses = analyses,
                    )
                    for analysis in analyses:
                        analysis.setSamplePartition(part)

            # If Preservation is required for some partitions,
            # and the SamplingWorkflow is disabled, we need
            # to transition to to_be_preserved manually.
            if not SamplingWorkflowEnabled:
                to_be_preserved = []
                sample_due = []
                lowest_state = 'sample_due'
                for p in sample.objectValues('SamplePartition'):
                    if p.getPreservation():
                        lowest_state = 'to_be_preserved'
                        to_be_preserved.append(p)
                    else:
                        sample_due.append(p)
                for p in to_be_preserved:
                    doActionFor(p, 'to_be_preserved')
                for p in sample_due:
                    doActionFor(p, 'sample_due')
                doActionFor(sample, lowest_state)
                doActionFor(ar, lowest_state)

            # receive secondary AR
            if values.get('Sample_uid', ''):

                doActionFor(ar, 'sampled')
                doActionFor(ar, 'sample_due')
                not_receive = ['to_be_sampled', 'sample_due', 'sampled',
                               'to_be_preserved']
                sample_state = wftool.getInfoFor(sample, 'review_state')
                if sample_state not in not_receive:
                    doActionFor(ar, 'receive')
                for analysis in ar.getAnalyses(full_objects=1):
                    doActionFor(analysis, 'sampled')
                    doActionFor(analysis, 'sample_due')
                    if sample_state not in not_receive:
                        doActionFor(analysis, 'receive')

            # Transition pre-preserved partitions.
            for p in parts:
                if 'prepreserved' in p and p['prepreserved']:
                    part = p['object']
                    state = wftool.getInfoFor(part, 'review_state')
                    if state == 'to_be_preserved':
                        wftool.doActionFor(part, 'preserve')

        if len(ARs) > 1:
            message = self.context.translate(
                _("Analysis requests ${ARs} were "
                  "successfully created.",
                  mapping = {'ARs': ', '.join(ARs)}))
        else:
            message = self.context.translate(
                _("Analysis request ${AR} was "
                  "successfully created.",
                  mapping = {'AR': ARs[0]}))

        self.context.plone_utils.addPortalMessage(message, 'info')

        # automatic label printing
        # won't print labels for Register on Secondary ARs
        new_ars = None
        if came_from == 'add':
            new_ars = [ar for ar in ARs if ar[-2:] == '01']
        if 'register' in self.context.bika_setup.getAutoPrintLabels() and new_ars:
            return json.dumps({'success':message,
                               'labels':new_ars,
                               'labelsize':self.context.bika_setup.getAutoLabelSize()})
        else:
            return json.dumps({'success':message})

class AnalysisRequestsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)

        request.set('disable_plone.rightcolumn', 1)

        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type':'AnalysisRequest',
                              'sort_on':'created',
                              'sort_order': 'reverse',
                              'path': {"query": "/", "level" : 0 }
                              }

        self.context_actions = {}

        if self.context.portal_type == "AnalysisRequestsFolder":
            self.request.set('disable_border', 1)

        if self.view_url.find("analysisrequests") == -1:
            self.view_url = self.view_url + "/analysisrequests"

        translate = self.context.translate

        self.allow_edit = True

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.form_id = "analysisrequests"

        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisrequest_big.png"
        self.title = _("Analysis Requests")
        self.description = ""

        SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        user_is_preserver = 'Preserver' in member.getRoles()

        self.columns = {
            'getRequestID': {'title': _('Request ID'),
                             'index': 'getRequestID'},
            'getClientOrderNumber': {'title': _('Client Order'),
                                     'index': 'getClientOrderNumber',
                                     'toggle': True},
            'Creator': {'title': PMF('Creator'),
                                     'index': 'Creator',
                                     'toggle': True},
            'Created': {'title': PMF('Date Created'),
                        'index': 'created',
                        'toggle': False},
            'getSample': {'title': _("Sample"),
                          'toggle': True,},
            'BatchID': {'title': _("Batch ID"), 'toggle': True},
            'Client': {'title': _('Client'),
                       'toggle': True},
            'getClientReference': {'title': _('Client Ref'),
                                   'index': 'getClientReference',
                                   'toggle': True},
            'getClientSampleID': {'title': _('Client SID'),
                                  'index': 'getClientSampleID',
                                  'toggle': True},
            'ClientContact': {'title': _('Contact'),
                                 'toggle': False},
            'getSampleTypeTitle': {'title': _('Sample Type'),
                                   'index': 'getSampleTypeTitle',
                                   'toggle': True},
            'getSamplePointTitle': {'title': _('Sample Point'),
                                    'index': 'getSamplePointTitle',
                                    'toggle': False},
            'SamplingDeviation': {'title': _('Sampling Deviation'),
                                  'toggle': False},
            'AdHoc': {'title': _('Ad-Hoc'),
                      'toggle': False},
            'SamplingDate': {'title': _('Sampling Date'),
                             'index': 'getSamplingDate',
                             'toggle': True},
            'getDateSampled': {'title': _('Date Sampled'),
                               'index': 'getDateSampled',
                               'toggle': not SamplingWorkflowEnabled,
                               'input_class': 'datepicker_nofuture',
                               'input_width': '10'},
            'getSampler': {'title': _('Sampler'),
                           'toggle': not SamplingWorkflowEnabled},
            'getDatePreserved': {'title': _('Date Preserved'),
                                 'toggle': user_is_preserver,
                                 'input_class': 'datepicker_nofuture',
                                 'input_width': '10',
                                 'sortable': False}, # no datesort without index
            'getPreserver': {'title': _('Preserver'),
                             'toggle': user_is_preserver},
            'getDateReceived': {'title': _('Date Received'),
                                'index': 'getDateReceived',
                                'toggle': False},
            'getDatePublished': {'title': _('Date Published'),
                                 'index': 'getDatePublished',
                                 'toggle': False},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter':{'cancellation_state':'active',
                              'sort_on':'created',
                              'sort_order': 'reverse'},
             'transitions': [{'id':'sample'},
                             {'id':'preserve'},
                             {'id':'receive'},
                             {'id':'retract'},
                             {'id':'verify'},
                             {'id':'prepublish'},
                             {'id':'publish'},
                             {'id':'republish'},
                             {'id':'cancel'},
                             {'id':'reinstate'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'ClientContact',
                        'getClientSampleID',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'SamplingDate',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'state_title']},
            {'id':'sample_due',
             'title': _('Due'),
             'contentFilter': {'review_state': ('to_be_sampled',
                                                'to_be_preserved',
                                                'sample_due'),
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id':'sample'},
                             {'id':'preserve'},
                             {'id':'receive'},
                             {'id':'cancel'},
                             {'id':'reinstate'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'state_title']},
           {'id':'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'sample_received',
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id':'prepublish'},
                             {'id':'cancel'},
                             {'id':'reinstate'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
            {'id':'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'review_state': 'to_be_verified',
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id':'retract'},
                             {'id':'verify'},
                             {'id':'prepublish'},
                             {'id':'cancel'},
                             {'id':'reinstate'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
            {'id':'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state': 'verified',
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id':'publish'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
            {'id':'published',
             'title': _('Published'),
             'contentFilter': {'review_state': ('published','invalid'),
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id':'republish'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'review_state': ('to_be_sampled', 'to_be_preserved',
                                                'sample_due', 'sample_received',
                                                'to_be_verified', 'attachment_due',
                                                'verified', 'published'),
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id':'reinstate'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished',
                        'state_title']},
            {'id':'invalid',
             'title': _('Invalid'),
             'contentFilter': {'review_state': 'invalid',
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished']},
            {'id':'assigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/assigned.png'/>" % (
                       self.context.translate(_("Assigned")), self.portal_url),
             'contentFilter': {'worksheetanalysis_review_state': 'assigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published'),
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id':'retract'},
                             {'id':'verify'},
                             {'id':'prepublish'},
                             {'id':'publish'},
                             {'id':'republish'},
                             {'id':'cancel'},
                             {'id':'reinstate'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'state_title']},
            {'id':'unassigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/unassigned.png'/>" % (
                       self.context.translate(_("Unassigned")), self.portal_url),
             'contentFilter': {'worksheetanalysis_review_state': 'unassigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published'),
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id':'receive'},
                             {'id':'retract'},
                             {'id':'verify'},
                             {'id':'prepublish'},
                             {'id':'publish'},
                             {'id':'republish'},
                             {'id':'cancel'},
                             {'id':'reinstate'}],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'AdHoc',
                        'SamplingDate',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'state_title']},
            ]

    def folderitems(self, full_objects = False):
        workflow = getToolByName(self.context, "portal_workflow")
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            sample = obj.getSample()

            if getSecurityManager().checkPermission(EditResults, obj):
                url = obj.absolute_url() + "/manage_results"
            else:
                url = obj.absolute_url()

            items[x]['Client'] = obj.aq_parent.Title()
            if (hideclientlink == False):
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                    (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
            items[x]['Creator'] = self.user_fullname(obj.Creator())
            items[x]['getRequestID'] = obj.getRequestID()
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (url, items[x]['getRequestID'])
            items[x]['getSample'] = sample
            items[x]['replace']['getSample'] = \
                "<a href='%s'>%s</a>" % (sample.absolute_url(), sample.Title())

            batch = obj.getBatch()
            if batch:
                items[x]['BatchID'] = batch.getBatchID()
                items[x]['replace']['BatchID'] = "<a href='%s'>%s</a>" % \
                     (batch.absolute_url(), items[x]['BatchID'])
            else:
                items[x]['BatchID'] = ''

            samplingdate = obj.getSample().getSamplingDate()
            items[x]['SamplingDate'] = self.ulocalized_time(samplingdate, long_format=1)
            items[x]['getDateReceived'] = self.ulocalized_time(obj.getDateReceived())
            items[x]['getDatePublished'] = self.ulocalized_time(obj.getDatePublished())

            deviation = sample.getSamplingDeviation()
            items[x]['SamplingDeviation'] = deviation and deviation.Title() or ''

            items[x]['AdHoc'] = sample.getAdHoc() and True or ''

            after_icons = ""
            state = workflow.getInfoFor(obj, 'worksheetanalysis_review_state')
            if state == 'assigned':
                after_icons += "<img src='%s/++resource++bika.lims.images/worksheet.png' title='%s'/>" % \
                    (self.portal_url, self.context.translate(_("All analyses assigned")))
            if workflow.getInfoFor(obj, 'review_state') == 'invalid':
                after_icons += "<img src='%s/++resource++bika.lims.images/delete.png' title='%s'/>" % \
                    (self.portal_url, self.context.translate(_("Results have been withdrawn")))
            if obj.getLate():
                after_icons += "<img src='%s/++resource++bika.lims.images/late.png' title='%s'>" % \
                    (self.portal_url, self.context.translate(_("Late Analyses")))
            if samplingdate > DateTime():
                after_icons += "<img src='%s/++resource++bika.lims.images/calendar.png' title='%s'>" % \
                    (self.portal_url, self.context.translate(_("Future dated sample")))
            if obj.getInvoiceExclude():
                after_icons += "<img src='%s/++resource++bika.lims.images/invoice_exclude.png' title='%s'>" % \
                    (self.portal_url, self.context.translate(_("Exclude from invoice")))
            if sample.getSampleType().getHazardous():
                after_icons += "<img src='%s/++resource++bika.lims.images/hazardous.png' title='%s'>" % \
                    (self.portal_url, self.context.translate(_("Hazardous")))
            if after_icons:
                items[x]['after']['getRequestID'] = after_icons

            items[x]['Created'] = self.ulocalized_time(obj.created())

            if not samplingdate > DateTime():
                datesampled = self.ulocalized_time(sample.getDateSampled())

                if not datesampled:
                    datesampled = self.ulocalized_time(
                        DateTime(),
                        long_format=1)
                    items[x]['class']['getDateSampled'] = 'provisional'
                sampler = sample.getSampler().strip()
                if sampler:
                    items[x]['replace']['getSampler'] = self.user_fullname(sampler)
                if 'Sampler' in member.getRoles() and not sampler:
                    sampler = member.id
                    items[x]['class']['getSampler'] = 'provisional'
            else:
                datesampled = ''
                sampler = ''
            items[x]['getDateSampled'] = datesampled
            items[x]['getSampler'] = sampler

            items[x]['ClientContact'] = obj.getContact().Title()
            items[x]['replace']['ClientContact'] = "<a href='%s'>%s</a>" % \
                (obj.getContact().absolute_url(), obj.getContact().Title())

            # sampling workflow - inline edits for Sampler and Date Sampled
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(SampleSample, obj) \
                and not samplingdate > DateTime():
                items[x]['required'] = ['getSampler', 'getDateSampled']
                items[x]['allow_edit'] = ['getSampler', 'getDateSampled']
                samplers = getUsers(sample, ['Sampler', 'LabManager', 'Manager'])
                username = member.getUserName()
                users = [({'ResultValue': u, 'ResultText': samplers.getValue(u)})
                         for u in samplers]
                items[x]['choices'] = {'getSampler': users}
                Sampler = sampler and sampler or \
                    (username in samplers.keys() and username) or ''
                items[x]['getSampler'] = Sampler

            # These don't exist on ARs
            # XXX This should be a list of preservers...
            items[x]['getPreserver'] = ''
            items[x]['getDatePreserved'] = ''

            # inline edits for Preserver and Date Preserved
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(PreserveSample, obj):
                items[x]['required'] = ['getPreserver', 'getDatePreserved']
                items[x]['allow_edit'] = ['getPreserver', 'getDatePreserved']
                preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
                username = member.getUserName()
                users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                         for u in preservers]
                items[x]['choices'] = {'getPreserver': users}
                preserver = username in preservers.keys() and username or ''
                items[x]['getPreserver'] = preserver
                items[x]['getDatePreserved'] = self.ulocalized_time(
                    DateTime(),
                    long_format=1)
                items[x]['class']['getPreserver'] = 'provisional'
                items[x]['class']['getDatePreserved'] = 'provisional'

            # Submitting user may not verify results
            if items[x]['review_state'] == 'to_be_verified' and \
               not checkPermission(VerifyOwnResults, obj):
                self_submitted = False
                review_history = list(workflow.getInfoFor(obj, 'review_history'))
                review_history.reverse()
                for event in review_history:
                    if event.get('action') == 'submit':
                        if event.get('actor') == member.getId():
                            self_submitted = True
                        break
                if self_submitted:
                    items[x]['table_row_class'] = "state-submitted-by-current-user"

        # Hide Preservation/Sampling workflow actions if the edit columns
        # are not displayed.
        toggle_cols = self.get_toggle_cols()
        new_states = []
        for i,state in enumerate(self.review_states):
            if state['id'] == self.review_state:
                if 'getSampler' not in toggle_cols \
                   or 'getDateSampled' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('sample')
                    else:
                        state['hide_transitions'] = ['sample',]
                if 'getPreserver' not in toggle_cols \
                   or 'getDatePreserved' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('preserve')
                    else:
                        state['hide_transitions'] = ['preserve',]
            new_states.append(state)
        self.review_states = new_states

        return items


class AnalysisRequestPublishedResults(BikaListingView):
    """ View of published results
        Prints the list of pdf files with each publication dates, the user
        responsible of that publication, the emails of the addressees (and/or)
        client contact names with the publication mode used (pdf, email, etc.)
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestPublishedResults, self).__init__(context, request)
        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'ARReport',
                              'sort_order': 'reverse'}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_workflow_action_buttons = False
        self.pagesize = 50
        self.form_id = 'published_results'
        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"
        self.title = _("Published results")
        self.description = ""

        self.columns = {
            'Title': {'title': _('File')},
            'FileSize': {'title': _('Size')},
            'Date': {'title': _('Date')},
            'PublishedBy': {'title': _('Published By')},
            'Recipients': {'title': _('Recipients')},
        }
        self.review_states = [
            {'id':'default',
             'title':'All',
             'contentFilter':{},
             'columns': ['Title',
                         'FileSize',
                         'Date',
                         'PublishedBy',
                         'Recipients']},
        ]

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')

        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            childid = childar and childar.getRequestID() or None
            message = _('This Analysis Request has been withdrawn and is shown '
                        'for trace-ability purposes only. Retest: %s.') \
                        % (childid or '')
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message), 'warning')

        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            message = _('This Analysis Request has been '
                        'generated automatically due to '
                        'the retraction of the Analysis '
                        'Request %s.') % par.getRequestID()
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message), 'info')

        template = BikaListingView.__call__(self)
        return template

    def contentsMethod(self, contentFilter):
        return self.context.objectValues('ARReport')

    def folderitems(self):
        items = super(AnalysisRequestPublishedResults, self).folderitems()
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        if 'Manager' not in roles \
            and 'LabManager' not in roles:
            return []

        for x in range(len(items)):
            if 'obj' in items[x]:
                obj = items[x]['obj']
                obj_url = obj.absolute_url()
                pdf = obj.getPdf()

                items[x]['Title'] = "Download"
                items[x]['FileSize'] = '%sKb' % (pdf.get_size() / 1024)
                items[x]['Date'] = self.ulocalized_time(obj.created(), long_format=1)
                items[x]['PublishedBy'] = obj.Creator()
                recip=''
                for recipient in obj.getRecipients():
                    email = recipient['EmailAddress']
                    val = recipient['Fullname']
                    if email:
                        val = "<a href='mailto:%s'>%s</a>" % (email, val)
                    if len(recip) == 0:
                        recip = val
                    else:
                        recip += (", " +val)

                items[x]['replace']['Recipients'] = recip
                items[x]['replace']['Title'] = \
                     "<a href='%s/at_download/Pdf'>%s</a>" % \
                     (obj_url, _("Download"))
        return items


class AnalysisRequestLog(LogView):

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')

        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            childid = childar and childar.getRequestID() or None
            message = _('This Analysis Request has been withdrawn and is shown '
                        'for trace-ability purposes only. Retest: %s.') \
                        % (childid or '')
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message), 'warning')

        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            message = _('This Analysis Request has been '
                        'generated automatically due to '
                        'the retraction of the Analysis '
                        'Request %s.') % par.getRequestID()
            self.context.plone_utils.addPortalMessage(
                self.context.translate(message), 'info')

        template = LogView.__call__(self)
        return template


class ClientContactVocabularyFactory(CatalogVocabulary):

    def __call__(self):
        parent = self.context.aq_parent
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact',
            path={'query': "/".join(parent.getPhysicalPath()),
                  'level': 0}
        )


class WidgetVisibility(_WV):

    def __call__(self):
        ret = super(WidgetVisibility, self).__call__()
        if 'add' not in ret:
            ret['add'] = {}
        if 'visible' not in ret['add']:
            ret['add']['visible'] = []
        if 'hidden' not in ret['add']:
            ret['add']['hidden'] = []
        if self.context.aq_parent.portal_type == 'Client':
            ret['add']['visible'].remove('Client')
            ret['add']['hidden'].append('Client')
        if self.context.aq_parent.portal_type == 'Batch':
            ret['add']['visible'].remove('Batch')
            ret['add']['hidden'].append('Batch')
        return ret
