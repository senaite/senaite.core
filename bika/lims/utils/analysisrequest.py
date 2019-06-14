# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

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
from bika.lims.interfaces import IAnalysisRequest, IReceived
from bika.lims.interfaces import IAnalysisRequestRetest
from bika.lims.interfaces import IAnalysisRequestSecondary
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.utils import attachPdf
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import copy_field_values
from bika.lims.utils import createPdf
from bika.lims.utils import encode_header
from bika.lims.utils import tmpID
from bika.lims.utils import to_utf8
from bika.lims.workflow import ActionHandlerPool
from bika.lims.workflow import doActionFor
from bika.lims.workflow import push_reindex_to_actions_pool
from bika.lims.workflow.analysisrequest import AR_WORKFLOW_ID
from bika.lims.workflow.analysisrequest import do_action_to_analyses
from email.Utils import formataddr
from zope.interface import alsoProvides
from zope.lifecycleevent import modified


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

    # Create the Analysis Request
    ar = _createObjectByType('AnalysisRequest', client, tmpID())

    # Resolve the services uids and set the analyses for this Analysis Request
    service_uids = get_services_uids(context=client, values=values,
                                     analyses_serv=analyses)
    ar.setAnalyses(service_uids, prices=prices, specs=specifications)
    values.update({"Analyses": service_uids})
    ar.processForm(REQUEST=request, values=values)

    # Handle rejection reasons
    rejection_reasons = resolve_rejection_reasons(values)
    ar.setRejectionReasons(rejection_reasons)

    # Handle secondary Analysis Request
    primary = ar.getPrimaryAnalysisRequest()
    if primary:
        # Mark the secondary with the `IAnalysisRequestSecondary` interface
        alsoProvides(ar, IAnalysisRequestSecondary)

        # Rename the secondary according to the ID server setup
        renameAfterCreation(ar)

        # Set dates to match with those from the primary
        ar.setDateSampled(primary.getDateSampled())
        ar.setSamplingDate(primary.getSamplingDate())
        ar.setDateReceived(primary.getDateReceived())

        # Force the transition of the secondary to received and set the
        # description/comment in the transition accordingly.
        if primary.getDateReceived():
            primary_id = primary.getId()
            comment = "Auto-received. Secondary Sample of {}".format(primary_id)
            changeWorkflowState(ar, AR_WORKFLOW_ID, "sample_received",
                                action="receive", comments=comment)

            # Mark the secondary as received
            alsoProvides(ar, IReceived)

            # Initialize analyses
            do_action_to_analyses(ar, "initialize")

            # Notify the ar has ben modified
            modified(ar)

            # Reindex the AR
            ar.reindexObject()

            # If rejection reasons have been set, reject automatically
            if rejection_reasons:
                doActionFor(ar, "reject")

            # In "received" state already
            return ar

    # Try first with no sampling transition, cause it is the most common config
    success, message = doActionFor(ar, "no_sampling_workflow")
    if not success:
        doActionFor(ar, "to_be_sampled")

    # If rejection reasons have been set, reject the sample automatically
    if rejection_reasons:
        doActionFor(ar, "reject")

    return ar


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
        return []

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
        analysisrequest.addAttachment(att)
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

    # Open the actions pool
    actions_pool = ActionHandlerPool.get_instance()
    actions_pool.queue_pool()

    # Create the Retest (Analysis Request)
    ignore = ['Analyses', 'DatePublished', 'Invalidated', 'Sample']
    retest = _createObjectByType("AnalysisRequest", ar.aq_parent, tmpID())
    copy_field_values(ar, retest, ignore_fieldnames=ignore)

    # Mark the retest with the `IAnalysisRequestRetest` interface
    alsoProvides(retest, IAnalysisRequestRetest)

    # Assign the source to retest
    retest.setInvalidated(ar)

    # Rename the retest according to the ID server setup
    renameAfterCreation(retest)

    # Copy the analyses from the source
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

    # Transition the retest to "sample_received"!
    changeWorkflowState(retest, 'bika_ar_workflow', 'sample_received')
    alsoProvides(retest, IReceived)

    # Initialize analyses
    for analysis in retest.getAnalyses(full_objects=True):
        if not IRoutineAnalysis.providedBy(analysis):
            continue
        changeWorkflowState(analysis, "bika_analysis_workflow", "unassigned")

    # Reindex and other stuff
    push_reindex_to_actions_pool(retest)
    push_reindex_to_actions_pool(retest.aq_parent)

    # Resume the actions pool
    actions_pool.resume()
    return retest


def create_partition(analysis_request, request, analyses, sample_type=None,
                     container=None, preservation=None, skip_fields=None,
                     remove_primary_analyses=True, internal_use=True):
    """
    Creates a partition for the analysis_request (primary) passed in
    :param analysis_request: uid/brain/object of IAnalysisRequest type
    :param request: the current request object
    :param analyses: uids/brains/objects of IAnalysis type
    :param sampletype: uid/brain/object of SampleType
    :param container: uid/brain/object of Container
    :param preservation: uid/brain/object of Preservation
    :param skip_fields: names of fields to be skipped on copy from primary
    :param remove_primary_analyses: removes the analyses from the parent
    :return: the new partition
    """
    partition_skip_fields = [
        "Analyses",
        "Attachment",
        "Client",
        "Profile",
        "Profiles",
        "RejectionReasons",
        "Remarks",
        "ResultsInterpretation",
        "ResultsInterpretationDepts",
        "Sample",
        "Template",
        "creation_date",
        "id",
        "modification_date",
        "ParentAnalysisRequest",
        "PrimaryAnalysisRequest",
    ]
    if skip_fields:
        partition_skip_fields.extend(skip_fields)
        partition_skip_fields = list(set(partition_skip_fields))

    # Copy field values from the primary analysis request
    ar = api.get_object(analysis_request)
    record = fields_to_dict(ar, partition_skip_fields)

    # Update with values that are partition-specific
    record.update({
        "InternalUse": internal_use,
        "ParentAnalysisRequest": api.get_uid(ar),
    })
    if sample_type is not None:
        record["SampleType"] = sample_type and api.get_uid(sample_type) or ""
    if container is not None:
        record["Container"] = container and api.get_uid(container) or ""
    if preservation is not None:
        record["Preservation"] = preservation and api.get_uid(preservation) or ""

    # Create the Partition
    client = ar.getClient()
    analyses = list(set(map(api.get_object, analyses)))
    services = map(lambda an: an.getAnalysisService(), analyses)
    specs = ar.getSpecification()
    specs = specs and specs.getResultsRange() or []
    partition = create_analysisrequest(client, request=request, values=record,
                                       analyses=services, specifications=specs)

    # Remove analyses from the primary
    if remove_primary_analyses:
        analyses_ids = map(api.get_id, analyses)
        ar.manage_delObjects(analyses_ids)

    # Reindex Parent Analysis Request
    ar.reindexObject(idxs=["isRootAncestor"])

    # Manually set the Date Received to match with its parent. This is
    # necessary because crar calls to processForm, so DateReceived is not
    # set because the partition has not been received yet
    partition.setDateReceived(ar.getDateReceived())
    partition.reindexObject(idxs="getDateReceived")

    # Force partition to same status as the primary
    status = api.get_workflow_status_of(ar)
    changeWorkflowState(partition, "bika_ar_workflow", status)
    if IReceived.providedBy(ar):
        alsoProvides(partition, IReceived)

    # And initialize the analyses the partition contains. This is required
    # here because the transition "initialize" of analyses rely on a guard,
    # so the initialization can only be performed when the sample has been
    # received (DateReceived is set)
    ActionHandlerPool.get_instance().queue_pool()
    for analysis in partition.getAnalyses(full_objects=True):
        doActionFor(analysis, "initialize")
    ActionHandlerPool.get_instance().resume()
    return partition


def fields_to_dict(obj, skip_fields=None):
    """
    Generates a dictionary with the field values of the object passed in, where
    keys are the field names. Skips computed fields
    """
    data = {}
    obj = api.get_object(obj)
    for field_name, field in api.get_fields(obj).items():
        if skip_fields and field_name in skip_fields:
            continue
        if field.type == "computed":
            continue
        data[field_name] = field.get(obj)
    return data


def resolve_rejection_reasons(values):
    """Resolves the rejection reasons from the submitted values to the format
    supported by Sample's Rejection Reason field
    """
    rejection_reasons = values.get("RejectionReasons")
    if not rejection_reasons:
        return []

    # Predefined reasons selected?
    selected = rejection_reasons[0] or {}
    if selected.get("checkbox") == "on":
        selected = selected.get("multiselection") or []
    else:
        selected = []

    # Other reasons set?
    other = values.get("RejectionReasons.textfield")
    if other:
        other = other[0] or {}
        other = other.get("other", "")
    else:
        other = ""

    # If neither selected nor other reasons are set, return empty
    if any([selected, other]):
        return [{"selected": selected, "other": other}]

    return []
