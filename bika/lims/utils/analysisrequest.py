from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISample, IAnalysisService, IAnalysis
from bika.lims.utils import tmpID
from bika.lims.utils import to_utf8
from bika.lims.utils import encode_header
from bika.lims.utils import createPdf
from bika.lims.utils import attachPdf
from bika.lims.utils.sample import create_sample
from bika.lims.utils.samplepartition import create_samplepartition
from bika.lims.workflow import doActionFor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from os.path import join
from plone import api
from Products.CMFPlone.utils import _createObjectByType
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
import os
import tempfile

def create_analysisrequest(
        context,
        request,
        values,  # {field: value, ...}
        analyses=[],
        # uid, service or analysis; list of uids, services or analyses
        partitions=None,
        # list of dictionaries with container, preservation etc)
        specifications=None,
        prices=None):
    """This is meant for general use and should do everything necessary to
    create and initialise the AR and it's requirements.
    XXX The ar-add form's ajaxAnalysisRequestSubmit should be calling this.
    """
    # Gather neccesary tools
    workflow = getToolByName(context, 'portal_workflow')
    bc = getToolByName(context, 'bika_catalog')

    # It's necessary to modify these and we don't want to pollute the
    # parent's data
    values = values.copy()

    # Create new sample or locate the existing for secondary AR
    if not values.get('Sample', False):
        secondary = False
        workflow_enabled = context.bika_setup.getSamplingWorkflowEnabled()
        sample = create_sample(context, request, values)
    else:
        secondary = True
        if ISample.providedBy(values['Sample']):
            sample = values['Sample']
        else:
            brains = bc(UID=values['Sample'])
            if brains:
                sample = brains[0].getObject()
        if not sample:
            raise RuntimeError(
                "create_analysisrequest No sample. values=%s" % values)
        workflow_enabled = sample.getSamplingWorkflowEnabled()

    # Create the Analysis Request
    ar = _createObjectByType('AnalysisRequest', context, tmpID())
    # Set some required fields manually before processForm is called
    ar.setSample(sample)
    values['Sample'] = sample
    ar.processForm(REQUEST=request, values=values)
    # Object has been renamed
    ar.edit(RequestID=ar.getId())

    # Set initial AR state
    action = '{0}sampling_workflow'.format('' if workflow_enabled else 'no_')
    workflow.doActionFor(ar, action)

    # Set analysis request analyses
    service_uids = _resolve_items_to_service_uids(analyses)
    analyses = ar.setAnalyses(service_uids, prices=prices, specs=specifications)

    if secondary:
        # Only 'sample_due' and 'sample_recieved' samples can be selected
        # for secondary analyses
        api.content.transition(obj=ar, to_state='sampled')
        api.content.transition(obj=ar, to_state='sample_due')
        sample_state = workflow.getInfoFor(sample, 'review_state')
        if sample_state == 'sample_received':
            doActionFor(ar, 'receive')

        for analysis in ar.getAnalyses(full_objects=1):
            doActionFor(analysis, 'sample')
            doActionFor(analysis, 'sample_due')
            analysis_transition_ids = [t['id'] for t in
                                       workflow.getTransitionsFor(analysis)]
            if 'receive' in analysis_transition_ids and sample_state == 'sample_received':
                doActionFor(analysis, 'receive')

    if not secondary:
        # Create sample partitions
        if not partitions:
            partitions = [{'services': analyses}]
        for n, partition in enumerate(partitions):
            # Calculate partition id
            partition_prefix = sample.getId() + "-P"
            partition_id = '%s%s' % (partition_prefix, n + 1)
            partition['part_id'] = partition_id
            # Point to or create sample partition
            if partition_id in sample.objectIds():
                partition['object'] = sample[partition_id]
            else:
                partition['object'] = create_samplepartition(
                    sample,
                    partition,
                    analyses
                )
        # If Preservation is required for some partitions,
        # and the SamplingWorkflow is disabled, we need
        # to transition to to_be_preserved manually.
        if not workflow_enabled:
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

        # Transition pre-preserved partitions
        for p in partitions:
            if 'prepreserved' in p and p['prepreserved']:
                part = p['object']
                state = workflow.getInfoFor(part, 'review_state')
                if state == 'to_be_preserved':
                    workflow.doActionFor(part, 'preserve')

    # Return the newly created Analysis Request
    return ar


def _resolve_items_to_service_uids(items):
    portal = api.portal.get()
    # We need to send a list of service UIDS to setAnalyses function.
    # But we may have received one, or a list of:
    #   AnalysisService instances
    #   Analysis instances
    #   service titles
    #   service UIDs
    #   service Keywords
    service_uids = []
    # Maybe only a single item was passed
    if type(items) not in (list, tuple):
        items = [items, ]
    for item in items:
        uid = False
        # service objects
        if IAnalysisService.providedBy(item):
            uid = item.UID()
            service_uids.append(uid)
        # Analysis objects (shortcut for eg copying analyses from other AR)
        if IAnalysis.providedBy(item):
            uid = item.getService().UID()
            service_uids.append(uid)
        # Maybe object UID.
        bsc = getToolByName(portal, 'bika_setup_catalog')
        brains = bsc(UID=item)
        if brains:
            uid = brains[0].UID
            service_uids.append(uid)
        # Maybe service Title
        bsc = getToolByName(portal, 'bika_setup_catalog')
        brains = bsc(portal_type='AnalysisService', title=item)
        if brains:
            uid = brains[0].UID
            service_uids.append(uid)
        # Maybe service Title
        bsc = getToolByName(portal, 'bika_setup_catalog')
        brains = bsc(portal_type='AnalysisService', getKeyword=item)
        if brains:
            uid = brains[0].UID
            service_uids.append(uid)
        if not uid:
            raise RuntimeError(
                str(item) + " should be the UID, title, keyword "
                            " or title of an AnalysisService.")
    return service_uids

def notify_rejection(analysisrequest):
    """
    Notifies via email that a given Analysis Request has been rejected. The
    notification is sent to the Client contacts assigned to the Analysis
    Request.

    :param analysisrequest: Analysis Request to which the notification refers
    :returns: true if success
    """
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    tplbase = '../browser/analysisrequest/templates/'
    arid = analysisrequest.getRequestID()

    # This is the template to render for the pdf that will be either attached
    # to the email and attached the the Analysis Request for further access
    tpl = ViewPageTemplateFile(tplbase + '/analysisrequest_retract_pdf.pt')
    tpl.context = analysisrequest
    html = safe_unicode(tpl.read()).encode('utf-8')
    filename = '%s-rejected' % arid
    pdf_fn = tempfile.mktemp(suffix=".pdf")
    pdf = createPdf(htmlreport=html, outfile=pdf_fn)
    if pdf:
        # Attach the pdf to the Analysis Request
        attid = analysisrequest.aq_parent.generateUniqueId('Attachment')
        att = _createObjectByType("Attachment", analysisrequest.aq_parent, tmpID())
        att.setAttachmentFile(open(pdf_fn))
        # Awkward workaround to rename the file
        attf = att.getAttachmentFile()
        attf.filename = '%s.pdf' % filename
        att.setAttachmentFile(attf)
        att.unmarkCreationFlag()
        renameAfterCreation(att)
        atts = analysisrequest.getAttachment() + [att] if \
                analysisrequest.getAttachment() else [att]
        atts = [a.UID() for a in atts]
        analysisrequest.setAttachment(atts)
        os.remove(pdf_fn)

    # This is the message for the email's body
    tpl = ViewPageTemplateFile(tplbase + '/analysisrequest_retract_mail.pt')
    tpl.context = analysisrequest
    html = safe_unicode(tpl.read()).encode('utf-8')

    # compose and send email.
    mailto = []
    lab = analysisrequest.bika_setup.laboratory
    mailfrom = formataddr((encode_header(lab.getName()), lab.getEmailAddress()))
    mailsubject = _('%s has been rejected') % arid
    contacts = [analysisrequest.getContact()] + analysisrequest.getCCContact()
    for contact in contacts:
        name = to_utf8(contact.getFullname())
        email = to_utf8(contact.getEmailAddress())
        if email:
            mailto.append(formataddr((encode_header(name), email)))

    if not mailto:
        return False
    mime_msg = MIMEMultipart('related')
    mime_msg['Subject'] = mailsubject
    mime_msg['From'] = mailfrom
    mime_msg['To'] = ','.join(mailto)
    mime_msg.preamble = 'This is a multi-part MIME message.'
    msg_txt = MIMEText(html, _subtype='html')
    mime_msg.attach(msg_txt)
    if pdf:
        attachPdf(mime_msg, pdf, filename)

    try:
        host = getToolByName(analysisrequest, 'MailHost')
        host.send(mime_msg.as_string(), immediate=True)
    except SMTPServerDisconnected as msg:
        logger.warn("SMTPServerDisconnected: %s." % msg)
    except SMTPRecipientsRefused as msg:
        raise WorkflowException(str(msg))

    return True
