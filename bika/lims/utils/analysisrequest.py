# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import os
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISample, IAnalysisService, IRoutineAnalysis, \
    IAnalysisRequest
from bika.lims.utils import attachPdf
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import createPdf
from bika.lims.utils import encode_header
from bika.lims.utils import tmpID, copy_field_values
from bika.lims.utils import to_utf8
from bika.lims.utils.sample import create_sample
from bika.lims.workflow import doActionFor, ActionHandlerPool, \
    push_reindex_to_actions_pool
from email.Utils import formataddr


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
    values = dict(values.items())

    # Create new sample or locate the existing for secondary AR
    secondary = False
    # TODO Sample Cleanup - Manage secondary ARs properly
    #if values.get('Sample', None):
    #    secondary = True
    #    values["Sample"] = get_sample_from_values(client, values)
    #else:
    #    values["Sample"] = create_sample(client, request, values)

    # Create the Analysis Request
    ar = _createObjectByType('AnalysisRequest', client, tmpID())
    ar.processForm(REQUEST=request, values=values)

    # Resolve the services uids and set the analyses for this Analysis Request
    service_uids = get_services_uids(context=client, values=values,
                                     analyses_serv=analyses)
    ar.setAnalyses(service_uids, prices=prices, specs=specifications)

    # TODO Sample Cleanup - Manage secondary ARs properly
    if secondary:
        # Secondary AR does not longer comes from a Sample, rather from an AR.
        # If the Primary AR has been received, then force the transition of the
        # secondary to received and set the description/comment in the
        # transition accordingly so it will be displayed later in the log tab
        logger.warn("Sync transition for secondary AR is still missing")

    # Needs to be rejected from the very beginning?
    reject_field = values.get("RejectionReasons", None)
    if reject_field and reject_field.get("checkbox", False):
        doActionFor(ar, "reject")
    else:
        succeed, message = doActionFor(ar, "no_sampling_workflow")
        if not succeed:
            doActionFor(ar, "sampling_workflow")

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
    if not analyses_serv:
        analyses_serv = []
    if not values:
        values = {}

    if not context or (not analyses_serv and not values):
        raise RuntimeError(
            "get_services_uids: Missing or wrong parameters.")

    # Merge analyses from analyses_serv and values into one list
    analyses_services = analyses_serv + (values.get("Analyses", None) or [])

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
    if analyses_profiles:
        uid_catalog = getToolByName(context, 'uid_catalog')
        for brain in uid_catalog(UID=analyses_profiles):
            profile = api.get_object(brain)
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
    def resolve_to_uid(item):
        if api.is_uid(item):
            return item
        elif IAnalysisService.providedBy(item):
            return item.UID()
        elif IRoutineAnalysis.providedBy(item):
            return item.getServiceUID()

        bsc = api.get_tool("bika_setup_catalog")
        brains = bsc(portal_type='AnalysisService', getKeyword=item)
        if brains:
            return brains[0].UID
        brains = bsc(portal_type='AnalysisService', title=item)
        if brains:
            return brains[0].UID
        raise RuntimeError(
            str(item) + " should be the UID, title, keyword "
                        " or title of an AnalysisService.")

    # Maybe only a single item was passed
    if type(items) not in (list, tuple):
        items = [items, ]
    service_uids = map(resolve_to_uid, list(set(items)))
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


def create_retest(ar):
    """Creates a retest (Analysis Request) from an invalidated Analysis Request
    :param ar: The invalidated Analysis Request
    :type ar: IAnalysisRequest
    :rtype: IAnalysisRequest
    """
    if not ar:
        raise ValueError("Source Analysis Request cannot be None")

    if not IAnalysisRequest.providedBy(ar):
        raise ValueError("Type not supported: {}".format(repr(type(ar))))

    if ar.getRetest():
        # Do not allow the creation of another retest!
        raise ValueError("Retest already set")

    if not ar.isInvalid():
        # Analysis Request must be in 'invalid' state
        raise ValueError("Cannot do a retest from an invalid Analysis Request"
                         .format(repr(ar)))

    # 0. Open the actions pool
    actions_pool = ActionHandlerPool.get_instance()
    actions_pool.queue_pool()

    # 1. Create the Retest (Analysis Request)
    ignore = ['Analyses', 'DatePublished', 'Invalidated', 'Sample']
    retest = _createObjectByType("AnalysisRequest", ar.aq_parent, tmpID())
    retest.setSample(ar.getSample())
    copy_field_values(ar, retest, ignore_fieldnames=ignore)
    renameAfterCreation(retest)

    # 2. Copy the analyses from the source
    intermediate_states = ['retracted', 'reflexed']
    for an in ar.getAnalyses(full_objects=True):
        if (api.get_workflow_status_of(an) in intermediate_states):
            # Exclude intermediate analyses
            continue

        nan = _createObjectByType("Analysis", retest, an.getKeyword())

        # Make a copy
        ignore_fieldnames = ['DataAnalysisPublished']
        copy_field_values(an, nan, ignore_fieldnames=ignore_fieldnames)
        nan.unmarkCreationFlag()
        push_reindex_to_actions_pool(nan)

    # 3. Assign the source to retest
    retest.setInvalidated(ar)

    # 4. Transition the retest to "sample_received"!
    changeWorkflowState(retest, 'bika_ar_workflow', 'sample_received')

    # 5. Reindex and other stuff
    push_reindex_to_actions_pool(retest)
    push_reindex_to_actions_pool(retest.aq_parent)

    # 6. Resume the actions pool
    actions_pool.resume()
    return retest
