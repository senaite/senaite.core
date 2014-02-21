from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF
from bika.lims.adapters.referencewidgetvocabulary import DefaultReferenceWidgetVocabulary
from bika.lims.adapters.widgetvisibility import WidgetVisibility as _WV
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.analyses import QCAnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.header_table import HeaderTableView
from bika.lims.browser.log import LogView
from bika.lims.browser.publish import doPublish
from bika.lims.browser.sample import SamplePartitionsView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.config import VERIFIED_STATES
from bika.lims.content.analysisrequest import schema as AnalysisRequestSchema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IAnalysisRequestAddView
from bika.lims.interfaces import IDisplayListVocabulary
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.interfaces import IInvoiceView
from bika.lims.permissions import *
from bika.lims.subscribers import doActionFor
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import createPdf
from bika.lims.utils import encode_header
from bika.lims.utils import getUsers
from bika.lims.utils import isActive
from bika.lims.utils import logged_in_client
from bika.lims.utils import tmpID
from bika.lims.utils import to_unicode as _u
from bika.lims.vocabularies import CatalogVocabulary
from DateTime import DateTime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from magnitude import mg
from pkg_resources import resource_filename
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
from zope.component import getAdapters
from zope.i18n.locales import locales
from zope.interface import implements

import App
import Globals
import Missing
import json
import os
import plone
import urllib
import zope.event

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
                    _id = sample.invokeFactory('SamplePartition', id=tmpID())
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

            Analyses = objects.keys()
            prices = form.get("Price", [None])[0]
            specs = {}
            if form.get("min", None):
                for service_uid in Analyses:
                    specs[service_uid] = {
                        "min": form["min"][0][service_uid],
                        "max": form["max"][0][service_uid],
                        "error": form["error"][0][service_uid]
                    }
            else:
                for service_uid in Analyses:
                    specs[service_uid] = {"min": "", "max": "", "error": ""}
            new = ar.setAnalyses(Analyses, prices=prices, specs=specs)

            # link analyses and partitions
            # If Bika Setup > Analyses > 'Display individual sample
            # partitions' is checked, no Partitions available.
            # https://github.com/bikalabs/Bika-LIMS/issues/1030
            if 'Partition' in form:
                for service_uid, service in objects.items():
                    part_id = form['Partition'][0][service_uid]
                    part = sample[part_id]
                    analysis = ar[service.getKeyword()]
                    analysis.setSamplePartition(part)
                    analysis.reindexObject()

            if new:
                for analysis in new:
                    # if the AR has progressed past sample_received, we need to bring it back.
                    ar_state = workflow.getInfoFor(ar, 'review_state')
                    if ar_state in ('attachment_due', 'to_be_verified'):
                        # Apply to AR only; we don't want this transition to cascade.
                        ar.REQUEST['workflow_skiplist'].append("retract all analyses")
                        workflow.doActionFor(ar, 'retract')
                        ar.REQUEST['workflow_skiplist'].remove("retract all analyses")
                        ar_state = workflow.getInfoFor(ar, 'review_state')
                    # Then we need to forward new analyses state
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
            submissable = []
            for uid, analysis in selected_analyses.items():
                if uid not in results or not results[uid]:
                    continue
                can_submit = True
                # guard_submit does a lot of the same stuff, too.
                # the code there has also been commented.
                # we must find a better way to allow dependencies to control
                # this process.
                # for dependency in analysis.getDependencies():
                #     dep_state = workflow.getInfoFor(dependency, 'review_state')
                #     if hasInterims[uid]:
                #         if dep_state in ('to_be_sampled', 'to_be_preserved',
                #                          'sample_due', 'sample_received',
                #                          'attachment_due', 'to_be_verified',):
                #             can_submit = False
                #             break
                #     else:
                #         if dep_state in ('to_be_sampled', 'to_be_preserved',
                #                          'sample_due', 'sample_received',):
                #             can_submit = False
                #             break
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
            except Exception as msg:
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
        newar.title=ar.title
        newar.description=ar.description
        RequestID=newar.getId()
        newar.setContact(ar.getContact())
        newar.setCCContact(ar.getCCContact())
        newar.setCCEmails(ar.getCCEmails())
        newar.setBatch(ar.getBatch())
        newar.setTemplate(ar.getTemplate())
        newar.setProfile(ar.getProfile())
        newar.setSamplingDate(ar.getSamplingDate())
        newar.setSampleType(ar.getSampleType())
        newar.setSamplePoint(ar.getSamplePoint())
        newar.setSamplingDeviation(ar.getSamplingDeviation())
        newar.setPriority(ar.getPriority())
        newar.setSampleCondition(ar.getSampleCondition())
        newar.setSample(ar.getSample())
        newar.setClientOrderNumber(ar.getClientOrderNumber())
        newar.setClientReference(ar.getClientReference())
        newar.setClientSampleID(ar.getClientSampleID())
        newar.setDefaultContainerType(ar.getDefaultContainerType())
        newar.setAdHoc(ar.getAdHoc())
        newar.setComposite(ar.getComposite())
        newar.setReportDryMatter(ar.getReportDryMatter())
        newar.setInvoiceExclude(ar.getInvoiceExclude())
        newar.setAttachment(ar.getAttachment())
        newar.setInvoice(ar.getInvoice())
        newar.setDateReceived(ar.getDateReceived())
        newar.setMemberDiscount(ar.getMemberDiscount())
        # Set the results for each AR analysis
        ans = ar.getAnalyses(full_objects=True)
        for an in ans:
            newar.invokeFactory("Analysis", id=an.getKeyword())
            nan = newar[an.getKeyword()]
            nan.setService(an.getService())
            nan.setCalculation(an.getCalculation())
            nan.setInterimFields(an.getInterimFields())
            nan.setResult(an.getResult())
            nan.setResultDM(an.getResultDM())
            nan.setRetested=False,
            nan.setMaxTimeAllowed(an.getMaxTimeAllowed())
            nan.setDueDate(an.getDueDate())
            nan.setDuration(an.getDuration())
            nan.setReportDryMatter(an.getReportDryMatter())
            nan.setAnalyst(an.getAnalyst())
            nan.setInstrument(an.getInstrument())
            nan.setSamplePartition(an.getSamplePartition())
            nan.unmarkCreationFlag()
            zope.event.notify(ObjectInitializedEvent(nan))
            changeWorkflowState(nan, 'bika_analysis_workflow',
                                'to_be_verified')
            nan.reindexObject()

        newar.reindexObject()
        newar.aq_parent.reindexObject()
        renameAfterCreation(newar)
        newar.setRequestID(newar.getId())

        if hasattr(ar, 'setChildAnalysisRequest'):
            ar.setChildAnalysisRequest(newar)
        newar.setParentAnalysisRequest(ar)
        return newar


class ResultOutOfRange(object):
    """Return alerts for any analyses inside the context ar
    """
    implements(IFieldIcons)
    adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):
        workflow = getToolByName(self.context, 'portal_workflow')
        items = self.context.getAnalyses()
        field_icons = {}
        for obj in items:
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj
            uid = obj.UID()
            astate = workflow.getInfoFor(obj, 'review_state')
            if astate == 'retracted':
                continue
            adapters = getAdapters((obj, ), IFieldIcons)
            for name, adapter in adapters:
                alerts = adapter(obj)
                if alerts:
                    if uid in field_icons:
                        field_icons[uid].extend(alerts[uid])
                    else:
                        field_icons[uid] = alerts[uid]
        return field_icons


class AnalysisRequestViewView(BrowserView):
    """ AR View form
        The AR fields are printed in a table, using analysisrequest_view.py
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")
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

        emails = self.context.getCCEmails()
        if type(emails) == str:
            emails = emails and [emails,] or []
        cc_emails = []
        cc_hrefs = []
        for cc in emails:
            cc_emails.append(cc)
            cc_hrefs.append("<a href='mailto:%s'>%s</a>"%(cc, cc))

        ## render header table
        self.header_table = HeaderTableView(self.context, self.request)

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
            message = _('These results have been withdrawn and are '
                        'listed here for trace-ability purposes. Please follow '
                        'the link to the retest')
            if childar:
                message = (message + " %s.") % childar.getRequestID()
            else:
                message = message + "."

            self.addMessage(message, 'warning')

        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
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

    def get_custom_fields(self):
        """ Returns a dictionary with custom fields to be rendered after
            header_table with this structure:
            {<fieldid>:{title:<title>, value:<html>}
        """
        custom = {}
        ar = self.context
        workflow = getToolByName(self.context, 'portal_workflow')

        # If is a retracted AR, show the link to child AR and show a warn msg
        if workflow.getInfoFor(ar, 'review_state') == 'invalid':
            childar = hasattr(ar, 'getChildAnalysisRequest') \
                        and ar.getChildAnalysisRequest() or None
            anchor = childar and ("<a href='%s'>%s</a>"%(childar.absolute_url(),childar.getRequestID())) or None
            if anchor:
                custom['ChildAR'] = {'title': self.context.translate(
                                            _("AR for retested results")),
                                     'value': anchor}

        # If is an AR automatically generated due to a Retraction, show it's
        # parent AR information
        if hasattr(ar, 'getParentAnalysisRequest') \
            and ar.getParentAnalysisRequest():
            par = ar.getParentAnalysisRequest()
            anchor = "<a href='%s'>%s</a>" % (par.absolute_url(), par.getRequestID())
            custom['ParentAR'] = {'title': self.context.translate(
                                        _("Invalid AR retested")),
                                  'value': anchor}

        return custom


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
        self.col_count = self.request.get('col_count', 4)
        try:
            self.col_count = int(self.col_count)
        except:
            self.col_count == 4

    def __call__(self):
        self.request.set('disable_border', 1)
        return self.template()

    def getContacts(self):
        adapter = getAdapter(self.context.aq_parent, name='getContacts')
        return adapter()

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

        self.columns = {
            'Title': {'title': _('Service'),
                      'index': 'sortable_title',
                      'sortable': False,},
            'Price': {'title': _('Price'),
                      'sortable': False,},
            'Partition': {'title': _('Partition'),
                          'sortable': False, },
            'min': {'title': _('Min')},
            'max': {'title': _('Max')},
            'error': {'title': _('Permitted Error %')},
        }

        columns = ['Title', ]
        ShowPrices = self.context.bika_setup.getShowPrices()
        if ShowPrices:
            columns.append('Price')
        ShowPartitions = self.context.bika_setup.getShowPartitions()
        if ShowPartitions:
            columns.append('Partition')
        EnableARSpecs = self.context.bika_setup.getEnableARSpecs()
        if EnableARSpecs:
            columns.append('min')
            columns.append('max')
            columns.append('error')

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
        p.form_id = "parts"
        p.show_select_column = False
        p.show_table_footer = False
        p.review_states[0]['transitions'] = [{'id': 'empty'}, ]  # none
        p.review_states[0]['custom_actions'] = []
        p.review_states[0]['columns'] = ['PartTitle',
                                         'getContainer',
                                         'getPreservation',
                                         'state_title']

        self.parts = p.contents_table()

    def folderitems(self):
        self.categories = []

        analyses = self.context.getAnalyses(full_objects=True)
        self.analyses = dict([(a.getServiceUID(), a) for a in analyses])
        self.selected = self.analyses.keys()
        self.show_categories = self.context.bika_setup.getCategoriseAnalysisServices()
        self.expand_all_categories = False

        wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')

        self.allow_edit = mtool.checkPermission('Modify portal content', self.context)

        items = BikaListingView.folderitems(self)
        analyses = self.context.getAnalyses(full_objects=True)

        partitions = [{'ResultValue': o.Title(),
                       'ResultText': o.getId()}
                      for o in self.context.getSample().objectValues('SamplePartition')
                      if wf.getInfoFor(o, 'cancellation_state', 'active') == 'active']
        for x in range(len(items)):
            if not 'obj' in items[x]:
                continue
            obj = items[x]['obj']

            cat = obj.getCategoryTitle()
            items[x]['category'] = cat
            if cat not in self.categories:
                self.categories.append(cat)

            items[x]['selected'] = items[x]['uid'] in self.selected

            items[x]['class']['Title'] = 'service_title'

            # js checks in row_data if an analysis may be removed.
            row_data = {}
            # keyword = obj.getKeyword()
            # if keyword in review_states.keys() \
            #    and review_states[keyword] not in ['sample_due',
            #                                       'to_be_sampled',
            #                                       'to_be_preserved',
            #                                       'sample_received',
            #                                       ]:
            #     row_data['disabled'] = True
            items[x]['row_data'] = json.dumps(row_data)

            calculation = obj.getCalculation()
            items[x]['Calculation'] = calculation and calculation.Title()

            locale = locales.getLocale('en')
            currency = self.context.bika_setup.getCurrency()
            symbol = locale.numbers.currencies[currency].symbol
            items[x]['before']['Price'] = symbol
            items[x]['Price'] = obj.getPrice()
            items[x]['class']['Price'] = 'nowrap'

            if items[x]['selected']:
                items[x]['allow_edit'] = ['Partition', 'min', 'max', 'error']
                if not logged_in_client(self.context):
                    items[x]['allow_edit'].append('Price')

            items[x]['required'].append('Partition')
            items[x]['choices']['Partition'] = partitions

            if obj.UID() in self.analyses:
                analysis = self.analyses[obj.UID()]
                part = analysis.getSamplePartition()
                part = part and part or obj
                items[x]['Partition'] = part.Title()
                spec = analysis.specification \
                    if hasattr(analysis, 'specification') \
                    else {"min": "", "max": "", "error": ""}
                items[x]["min"] = spec["min"]
                items[x]["max"] = spec["max"]
                items[x]["error"] = spec["error"]
                #Add priority premium
                items[x]['Price'] = analysis.getPrice()
            else:
                items[x]['Partition'] = ''
                items[x]["min"] = ''
                items[x]["max"] = ''
                items[x]["error"] = ''

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
                # This one is still special.
                if field in ['RequestID']:
                    continue
                # And these are not required if this is a secondary AR
                if ar.get('Sample', '') != '' and field in [
                    'SamplingDate',
                    'SampleType'
                ]:
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

                if values.has_key("%s_uid" % k):
                    v = values["%s_uid"%k]
                    if v and "," in v:
                        v = v.split(",")
                    resolved_values[k] = values["%s_uid"%k]
                else:
                    resolved_values[k] = values[k]

            client = uc(UID = values['Client_uid'])[0].getObject()
            if values.get('Sample_uid', ''):
                # Secondary AR
                sample = uc(UID=values['Sample_uid'])[0].getObject()
            else:
                # Primary AR
                _id = client.invokeFactory('Sample', id=tmpID())
                sample = client[_id]
                saved_form = self.request.form
                self.request.form = resolved_values
                sample.setSampleType(resolved_values['SampleType'])
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
            Analyses = values["Analyses"]

            specs = {}
            if len(values.get("min", [])):
                for i, service_uid in enumerate(Analyses):
                    specs[service_uid] = {
                        "min": values["min"][i],
                        "max": values["max"][i],
                        "error": values["error"][i]
                    }

            saved_form = self.request.form
            self.request.form = resolved_values
            clientid = client.invokeFactory('AnalysisRequest', id=tmpID())
            ar = client[clientid]
            ar.setSample(sample)
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
                    _id = sample.invokeFactory('SamplePartition', id = tmpID())
                    part = sample[_id]
                    parts[_i]['object'] = part
                    # Sort available containers by capacity and select the
                    # smallest one possible.
                    if p.get('container', ''):
                        containers = [_p.getObject() for _p in bsc(UID=p['container'])]
                        if containers:
                            try:
                                containers.sort(lambda a,b:cmp(
                                    a.getCapacity() \
                                    and mg(float(a.getCapacity().lower().split(" ", 1)[0]), a.getCapacity().lower().split(" ", 1)[1]) \
                                    or mg(0, 'ml'),
                                    b.getCapacity() \
                                    and mg(float(b.getCapacity().lower().split(" ", 1)[0]), b.getCapacity().lower().split(" ", 1)[1]) \
                                    or mg(0, 'ml')
                                ))
                            except:
                                pass
                            container = containers[0]
                        else:
                            container = None
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
                        preservation = p.get('preservation', '')
                        parts[_i]['prepreserved'] = False

                    part.edit(
                        Container=container,
                        Preservation=preservation,
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

            new_analyses = ar.setAnalyses(Analyses, prices=prices, specs=specs)
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
            'Priority': {'title': _('Priority'),
                            'index': 'Priority',
                            'toggle': True},
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
            'getProfileTitle': {'title': _('Profile'),
                                'index': 'getProfileTitle',
                                'toggle': False},
            'getTemplateTitle': {'title': _('Template'),
                                 'index': 'getTemplateTitle',
                                 'toggle': False},
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
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
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'SamplingDeviation',
                        'Priority',
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
            priority = obj.getPriority()
            items[x]['Priority'] = priority and priority.Title() or ''

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

            SamplingWorkflowEnabled =\
                self.context.bika_setup.getSamplingWorkflowEnabled()

            if not samplingdate > DateTime() and SamplingWorkflowEnabled:
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
                try:
                    review_history = list(workflow.getInfoFor(obj, 'review_history'))
                    review_history.reverse()
                    for event in review_history:
                        if event.get('action') == 'submit':
                            if event.get('actor') == member.getId():
                                self_submitted = True
                            break
                    if self_submitted:
                        items[x]['after']['state_title'] = \
                             "<img src='++resource++bika.lims.images/submitted-by-current-user.png' title='%s'/>" % \
                             (self.context.translate(_("Cannot verify: Submitted by current user")))
                except Exception:
                    pass

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
                filesize = 0
                title = _('Download')
                anchor = "<a href='%s/at_download/Pdf'>%s</a>" % \
                         (obj_url, _("Download"))
                try:
                    filesize = pdf.get_size()
                    filesize = filesize / 1024 if filesize > 0 else 0
                except:
                    # POSKeyError: 'No blob file'
                    # Show the record, but not the link
                    title = _('Not available')
                    anchor = title

                items[x]['Title'] = title
                items[x]['FileSize'] = '%sKb' % filesize
                items[x]['Date'] = self.ulocalized_time(obj.created(), long_format=1)
                items[x]['PublishedBy'] = self.user_fullname(obj.Creator())
                recip = ''
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
                items[x]['replace']['Title'] = anchor
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


class InvoiceView(BrowserView):

    implements(IInvoiceView)

    template = ViewPageTemplateFile("templates/analysisrequest_invoice.pt")
    content = ViewPageTemplateFile("templates/analysisrequest_invoice_content.pt")
    title = _('Invoice')
    description = ''

    def __call__(self):
        context = self.context
        workflow = getToolByName(context, 'portal_workflow')
        # Collect related data and objects
        invoice = context.getInvoice()
        sample = context.getSample()
        samplePoint = sample.getSamplePoint()
        reviewState = workflow.getInfoFor(context, 'review_state')
        # Collection invoice information
        if invoice:
            self.invoiceId = invoice.getId()
        else:
            self.invoiceId = _('Proforma (Not yet invoiced)')
        # Collect verified invoice information
        verified = reviewState in VERIFIED_STATES
        if verified:
            self.verifiedBy = context.getVerifier()
        self.verified = verified
        self.request['verified'] = verified
        # Collect published date
        datePublished = context.getDatePublished()
        if datePublished != None:
            datePublished = self.ulocalized_time(
                datePublished, long_format=1
            )
        self.datePublished = datePublished
        # Collect received date
        dateRecieved = context.getDateReceived()
        if dateRecieved != None:
            dateRecieved = self.ulocalized_time(dateRecieved, long_format=1)
        self.dateRecieved = dateRecieved
        # Collect general information
        self.reviewState = reviewState
        self.contact = context.getContact().Title()
        self.clientOrderNumber = context.getClientOrderNumber()
        self.clientReference = context.getClientReference()
        self.clientSampleId = sample.getClientSampleID()
        self.sampleType = sample.getSampleType().Title()
        self.samplePoint = samplePoint and samplePoint.Title()
        self.requestId = context.getRequestID()
        # Retrieve required data from analyses collection
        analyses = []
        for analysis in context.getRequestedAnalyses():
            service = analysis.getService()
            categoryName = service.getCategory().Title()
            # Find the category
            try:
                category = (
                    o for o in analyses if o['name'] == categoryName
                ).next()
            except:
                category = {'name':categoryName, 'analyses':[]}
                analyses.append(category)
            # Append the analysis to the category
            category['analyses'].append({
                'title': analysis.Title(),
                'price': analysis.getPrice(),
                'priceVat': "%.2f" % analysis.getVATAmount(),
                'priceTotal': "%.2f" % analysis.getTotalPrice(),
            })
        self.analyses = analyses
        # Get totals
        self.subtotal = context.getSubtotal()
        self.vatTotal = "%.2f" % context.getVATTotal()
        self.totalPrice = "%.2f" % context.getTotalPrice()
        # Render the template
        return self.template()


class InvoicePrintView(InvoiceView):

    template = ViewPageTemplateFile("templates/analysisrequest_invoice_print.pt")

    def __call__(self):
        return InvoiceView.__call__(self)


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

        workflow = getToolByName(self.context, 'portal_workflow')
        state = workflow.getInfoFor(self.context, 'review_state')

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

        # header_table default visible fields
        ret['header_table'] = {
            'prominent': ['Contact', 'CCContact', 'CCEmails'],
            'visible': [
                'Sample',
                'Batch',
                'Template',
                'Profile',
                'SamplingDate',
                'SampleType',
                'Specification',
                'PublicationSpecification',
                'SamplePoint',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'SamplingDeviation',
                'Priority',
                'SampleCondition',
                'DateSampled',
                'DateReceived',
                'DatePublished',
                'ReportDryMatter',
                'AdHoc',
                'Composite',
                'MemberDiscount',
                'InvoiceExclude',
                ]}

        # Edit and View widgets are displayed/hidden in different workflow
        # states.  The widget.visible is used as a default.  This is placed
        # here to manage the header_table display.
        if state in ('to_be_sampled', 'to_be_preserved', 'sample_due', ):
            ret['header_table']['visible'].remove('DateReceived')
            ret['header_table']['visible'].remove('DatePublished')
            ret['edit']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'AdHoc',
                'Batch',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'Composite',
                'InvoiceExclude'
                'SampleCondition',
                'SamplingDate',
                'SamplingDeviation',
                'Priority',
            ]
            ret['view']['visible'] = [
                'DateSampled',
                'MemberDiscount',
                'Profile',
                'ReportDryMatter',
                'Specification',
                'Sample',
                'SamplePoint',
                'Specification',
                'SampleType',
                'Template',
            ]
        elif state in ('sample_received', ):
            ret['header_table']['visible'].remove('DatePublished')
            ret['edit']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'Batch',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'InvoiceExclude',
            ]
            ret['view']['visible'] = [
                'AdHoc',
                'Composite',
                'DateReceived',
                'MemberDiscount',
                'Profile',
                'ReportDryMatter',
                'Sample',
                'SampleCondition',
                'SampleType',
                'Specification',
                'SamplingDate',
                'SamplePoint',
                'SamplingDeviation',
                'Priority',
                'Template',
            ]
        # include this in to_be_verified - there may be verified analyses to
        # pre-publish
        elif state in ('to_be_verified', 'verified', ):
            ret['header_table']['visible'].remove('DatePublished')
            ret['edit']['visible'] = [
                'PublicationSpecification',
            ]
            ret['view']['visible'] = [
                'Contact',
                'CCContact',
                'CCEmails',
                'AdHoc',
                'Batch',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'Composite',
                'DateReceived',
                'InvoiceExclude',
                'MemberDiscount',
                'Profile',
                'ReportDryMatter',
                'Sample',
                'SampleCondition',
                'SamplePoint',
                'Specification',
                'SampleType',
                'SamplingDate',
                'SamplingDeviation',
                'Priority',
                'Template',
            ]
        elif state in ('published', ):
            ret['edit']['visible'] = [
                'PublicationSpecification',
            ]
            ret['view']['visible'] = [
                'AdHoc',
                'Batch',
                'ClientOrderNumber',
                'ClientReference',
                'ClientSampleID',
                'Composite',
                'DatePublished',
                'DateReceived',
                'InvoiceExclude'
                'MemberDiscount',
                'Profile',
                'ReportDryMatter',
                'Sample',
                'SampleCondition',
                'SamplePoint',
                'Specification',
                'SampleType',
                'SamplingDate',
                'SamplingDeviation',
                'Priority',
                'Template',
            ]

        return ret


class ReferenceWidgetVocabulary(DefaultReferenceWidgetVocabulary):
    def __call__(self):
        base_query = json.loads(self.request['base_query'])

        # In client context, restrict samples to client samples only
        if 'portal_type' in base_query \
        and (base_query['portal_type'] == 'Sample'
             or base_query['portal_type'][0] == 'Sample'):
            base_query['getClientUID'] = self.context.aq_parent.UID()
            self.request['base_query'] = json.dumps(base_query)

        return DefaultReferenceWidgetVocabulary.__call__(self)


class JSONReadExtender(object):
    """- Adds the full details of all analyses to the AR.Analyses field
    """

    implements(IJSONReadExtender)
    adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def ar_analysis_values(self):
        ret = []
        workflow = getToolByName(self.context, 'portal_workflow')
        analyses = self.context.getAnalyses(cancellation_state='active')
        for proxy in analyses:
            analysis = proxy.getObject()
            service = analysis.getService()
            if proxy.review_state == 'retracted':
                continue
            # things that are manually inserted into the analysis.
            method = analysis.getMethod()
            if not method:
                method = service.getMethod()
            ret.append({
                "Uncertainty": analysis.getService().getUncertainty(analysis.getResult()),
                "Method": method.Title() if method else '',
                "specification": analysis.specification if hasattr(analysis, "specification") else {},
            })
            # Place all proxy attributes into the result.
            for index in proxy.indexes():
                if index in proxy:
                    val = getattr(proxy, index)
                    if val != Missing.Value:
                        try:
                            json.dumps(val)
                        except:
                            continue
                        ret[-1][index] = val
            # Then schema field values
            schema = analysis.Schema()
            for field in schema.fields():
                accessor = field.getAccessor(analysis)
                if accessor and callable(accessor):
                    val = accessor()
                    if hasattr(val, 'Title') and callable(val.Title):
                        val = val.Title()
                    try:
                        json.dumps(val)
                    except:
                        val = str(val)
                    ret[-1][field.getName()] = val
            if analysis.getRetested():
                retracted = self.context.getAnalyses(review_state='retracted',
                                            title=analysis.Title(),
                                            full_objects=True)
                prevs = sorted(retracted, key=lambda item: item.created())
                prevs = [{'created': str(p.created()),
                          'Result': p.getResult(),
                          'InterimFields': p.getInterimFields()}
                         for p in prevs]
                ret[-1]['Previous Results'] = prevs
        return ret

    def __call__(self, request, obj_data):
        ret = obj_data.copy()
        include_fields = []
        if "include_fields" in request:
            include_fields = [x.strip() for x in request.get("include_fields", "").split(",")
                              if x.strip()]
        if "include_fields[]" in request:
            include_fields = request['include_fields[]']
        if not include_fields or "Analyses" in include_fields:
            ret['Analyses'] = self.ar_analysis_values()
        return ret
class PriorityIcons(object):

    """An icon provider for indicating AR priorities
    """

    implements(IFieldIcons)
    adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        result = {
            'msg': '',
            'field': 'Priority',
            'icon': '',
        }
        priority = self.context.getPriority()
        if priority:
            result['msg'] = priority.Title()
            icon = priority.getSmallIcon()
            if icon:
                result['icon'] = icon.absolute_url()

        return {self.context.UID(): [result]}
