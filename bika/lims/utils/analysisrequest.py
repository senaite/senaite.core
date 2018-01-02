# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISample, IAnalysisService, IRoutineAnalysis
from bika.lims.utils import tmpID
from bika.lims.utils import to_utf8
from bika.lims.utils import encode_header
from bika.lims.utils import createPdf
from bika.lims.utils import attachPdf
from bika.lims.utils.sample import create_sample
from bika.lims.utils.samplepartition import create_samplepartition
from bika.lims.workflow import doActionFor
from bika.lims.workflow import doActionsFor
from bika.lims.workflow import getReviewHistoryActionsList
from copy import deepcopy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from plone import api
from Products.CMFPlone.utils import _createObjectByType
import os
import tempfile

def create_analysisrequest(client, request, values, analyses=None,
                           partitions=None, specifications=None, prices=None):
    """This is meant for general use and should do everything necessary to
    create and initialise an AR and any other required auxilliary objects
    (Sample, SamplePartition, Analysis...)

    :param client:
        The container (Client) in which the ARs will be created.
    :param request:
        The current Request object.
    :param values:
        a dict, where keys are AR|Sample schema field names.
    :param analyses:
        Analysis services list.  If specified, augments the values in
        values['Analyses']. May consist of service objects, UIDs, or Keywords.
    :param partitions:
        A list of dictionaries, if specific partitions are required.  If not
        specified, AR's sample is created with a single partition.
    :param specifications:
        These values augment those found in values['Specifications']
    :param prices:
        Allow different prices to be set for analyses.  If not set, prices
        are read from the associated analysis service.
    """
    # Don't pollute the dict param passed in
    values = deepcopy(values)

    # Create new sample or locate the existing for secondary AR
    secondary = False
    sample = None
    if not values.get('Sample', False):
        sample = create_sample(client, request, values)
    else:
        sample = get_sample_from_values(client, values)
        secondary = True

    # Create the Analysis Request
    ar = _createObjectByType('AnalysisRequest', client, tmpID())

    # Set some required fields manually before processForm is called
    ar.setSample(sample)
    values['Sample'] = sample
    ar.processForm(REQUEST=request, values=values)
    ar.edit(RequestID=ar.getId())

    # Set analysis request analyses. 'Analyses' param are analyses services
    analyses = analyses if analyses else []
    service_uids = get_services_uids(
        context=client, analyses_serv=analyses, values=values)
    # processForm already has created the analyses, but here we create the
    # analyses with specs and prices. This function, even it is called 'set',
    # deletes the old analyses, so eventually we obtain the desired analyses.
    ar.setAnalyses(service_uids, prices=prices, specs=specifications)
    analyses = ar.getAnalyses(full_objects=True)

    # Create sample partitions
    if not partitions:
        partitions = values.get('Partitions',
                                [{'services': service_uids}])

    part_num = 0
    prefix = sample.getId() + "-P"
    if secondary:
        # Always create new partitions if is a Secondary AR, cause it does
        # not make sense to reuse the partitions used in a previous AR!
        sparts = sample.getSamplePartitions()
        for spart in sparts:
            spartnum = int(spart.getId().split(prefix)[1])
            if spartnum > part_num:
                part_num = spartnum

    for n, partition in enumerate(partitions):
        # Calculate partition id
        partition_id = '%s%s' % (prefix, part_num + 1)
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
        part_num += 1

    # At this point, we have a fully created AR, with a Sample, Partitions and
    # Analyses, but the state of all them is the initial ("sample_registered").
    # We can now transition the whole thing (instead of doing it manually for
    # each object we created). After and Before transitions will take care of
    # cascading and promoting the transitions in all the objects "associated"
    # to this Analysis Request.
    sampling_workflow_enabled = sample.getSamplingWorkflowEnabled()
    action = 'no_sampling_workflow'
    if sampling_workflow_enabled:
        action = 'sampling_workflow'
    # Transition the Analysis Request and related objects to "sampled" (if
    # sampling workflow not enabled) or to "to_be_sampled" statuses.
    doActionFor(ar, action)

    if secondary:
        # If secondary AR, then we need to manually transition the AR (and its
        # children) to fit with the Sample Partition's current state
        sampleactions = getReviewHistoryActionsList(sample)
        doActionsFor(ar, sampleactions)
        # We need a workaround here in order to transition partitions.
        # auto_no_preservation_required and auto_preservation_required are
        # auto transitions applied to analysis requests, but partitions don't
        # have them, so we need to replace them by the sample_workflow
        # equivalent.
        if 'auto_no_preservation_required' in sampleactions:
            index = sampleactions.index('auto_no_preservation_required')
            sampleactions[index] = 'sample_due'
        elif 'auto_preservation_required' in sampleactions:
            index = sampleactions.index('auto_preservation_required')
            sampleactions[index] = 'to_be_preserved'
        # We need to transition the partition manually
        # Transition pre-preserved partitions
        for partition in partitions:
            part = partition['object']
            doActionsFor(part, sampleactions)

    # Transition pre-preserved partitions
    for p in partitions:
        if 'prepreserved' in p and p['prepreserved']:
            part = p['object']
            doActionFor(part, 'preserve')

    # Once the ar is fully created, check if there are rejection reasons
    reject_field = values.get('RejectionReasons', '')
    if reject_field and reject_field.get('checkbox', False):
        doActionFor(ar, 'reject')

    return ar


def get_sample_from_values(context, values):
    """values may contain a UID or a direct Sample object.
    """
    if ISample.providedBy(values['Sample']):
        sample = values['Sample']
    else:
        bc = getToolByName(context, 'bika_catalog')
        brains = bc(UID=values['Sample'])
        if brains:
            sample = brains[0].getObject()
        else:
            raise RuntimeError("create_analysisrequest: invalid sample "
                               "value provided. values=%s" % values)
    if not sample:
        raise RuntimeError("create_analysisrequest: invalid sample "
                           "value provided. values=%s" % values)
    return sample


def get_services_uids(context=None, analyses_serv=None, values=None):
    """
    This function returns a list of UIDs from analyses services from its
    parameters.
    :param analyses_serv: A list (or one object) of service-related info items.
        see _resolve_items_to_service_uids() docstring.
    :type analyses_serv: list
    :param values: a dict, where keys are AR|Sample schema field names.
    :type values: dict
    :returns: a list of analyses services UIDs
    """
    if analyses_serv is None:
        analyses_serv = []
    if values is None:
        values = {}

    if not context or (not analyses_serv and not values):
        raise RuntimeError(
            "get_services_uids: Missing or wrong parameters.")
    uid_catalog = getToolByName(context, 'uid_catalog')
    anv = values['Analyses'] if values.get('Analyses', None) else []
    analyses_services = anv + analyses_serv
    # It is possible to create analysis requests
    # by JSON petitions and services, profiles or types aren't allways send.
    # Sometimes we can get analyses and profiles that doesn't match and we
    # should act in consequence.
    # Getting the analyses profiles
    analyses_profiles = values.get('Profiles', [])
    if not isinstance(analyses_profiles, (list, tuple)):
        # Plone converts the incoming form value to a list, if there are
        # multiple values; but if not, it will send a string (a single UID).
        analyses_profiles = [analyses_profiles]
    if not analyses_services and not analyses_profiles:
        raise RuntimeError(
                "create_analysisrequest: no analyses services or analysis"
                " profile provided")
    # Add analysis services UIDs from profiles to analyses_services variable.
    for profile_uid in analyses_profiles:
        # When creating an AR, JS builds a query from selected fields.
        # Although it doesn't set empty values to any
        # Field, somehow 'Profiles' field can have an empty value in the set.
        # Thus, we should avoid querying by empty UID through 'uid_catalog'.
        if profile_uid:
            profile = uid_catalog(UID=profile_uid)
            profile = profile[0].getObject()
            # Only services UIDs
            services_uids = profile.getRawService()
            # _resolve_items_to_service_uids() will remove duplicates
            analyses_services += services_uids
    return _resolve_items_to_service_uids(analyses_services)


def _resolve_items_to_service_uids(items):
    """ Returns a list of service uids without duplicates based on the items
    :param items:
        A list (or one object) of service-related info items. The list can be
        heterogeneous and each item can be:
        - Analysis Service instance
        - Analysis instance
        - Analysis Service title
        - Analysis Service UID
        - Analysis Service Keyword
        If an item that doesn't match any of the criterias above is found, the
        function will raise a RuntimeError
    """
    portal = None
    bsc = None
    service_uids = []

    # Maybe only a single item was passed
    if type(items) not in (list, tuple):
        items = [items, ]
    for item in items:
        # service objects
        if IAnalysisService.providedBy(item):
            uid = item.UID()
            service_uids.append(uid)
            continue

        # Analysis objects (shortcut for eg copying analyses from other AR)
        if IRoutineAnalysis.providedBy(item):
            service_uids.append(item.getServiceUID())
            continue

        # An object UID already there?
        if item in service_uids:
            continue

        # Maybe object UID.
        portal = portal if portal else api.portal.get()
        bsc = bsc if bsc else getToolByName(portal, 'bika_setup_catalog')
        brains = bsc(UID=item)
        if brains:
            uid = brains[0].UID
            service_uids.append(uid)
            continue

        # Maybe service Title
        brains = bsc(portal_type='AnalysisService', title=item)
        if brains:
            uid = brains[0].UID
            service_uids.append(uid)
            continue

        # Maybe service Keyword
        brains = bsc(portal_type='AnalysisService', getKeyword=item)
        if brains:
            uid = brains[0].UID
            service_uids.append(uid)
            continue

        raise RuntimeError(
            str(item) + " should be the UID, title, keyword "
                        " or title of an AnalysisService.")
    return list(set(service_uids))


def notify_rejection(analysisrequest):
    """
    Notifies via email that a given Analysis Request has been rejected. The
    notification is sent to the Client contacts assigned to the Analysis
    Request.

    :param analysisrequest: Analysis Request to which the notification refers
    :returns: true if success
    """

    # We do this imports here to avoid circular dependencies until we deal
    # better with this notify_rejection thing.
    from bika.lims.browser.analysisrequest.reject import \
        AnalysisRequestRejectPdfView, AnalysisRequestRejectEmailView

    arid = analysisrequest.getId()

    # This is the template to render for the pdf that will be either attached
    # to the email and attached the the Analysis Request for further access
    tpl = AnalysisRequestRejectPdfView(analysisrequest, analysisrequest.REQUEST)
    html = tpl.template()
    html = safe_unicode(html).encode('utf-8')
    filename = '%s-rejected' % arid
    pdf_fn = tempfile.mktemp(suffix=".pdf")
    pdf = createPdf(htmlreport=html, outfile=pdf_fn)
    if pdf:
        # Attach the pdf to the Analysis Request
        attid = analysisrequest.aq_parent.generateUniqueId('Attachment')
        att = _createObjectByType(
            "Attachment", analysisrequest.aq_parent, attid)
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
    tpl = AnalysisRequestRejectEmailView(
        analysisrequest, analysisrequest.REQUEST)
    html = tpl.template()
    html = safe_unicode(html).encode('utf-8')

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
    except:
        logger.warning(
            "Email with subject %s was not sent (SMTP connection error)" % mailsubject)

    return True
