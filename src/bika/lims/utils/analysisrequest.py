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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import itertools
from collections import OrderedDict
from string import Template

import six
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api.mail import compose_email
from bika.lims.api.mail import is_valid_email_address
from bika.lims.api.mail import send_email
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IAnalysisRequestRetest
from bika.lims.interfaces import IAnalysisRequestSecondary
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IReceived
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import copy_field_values
from bika.lims.utils import get_link
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from DateTime import DateTime
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFPlone.utils import _createObjectByType
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.idserver import renameAfterCreation
from senaite.core.permissions.sample import can_receive
from senaite.core.workflow import ANALYSIS_WORKFLOW
from senaite.core.workflow import SAMPLE_WORKFLOW
from zope import event
from zope.interface import alsoProvides


def create_analysisrequest(client, request, values, analyses=None,
                           results_ranges=None, prices=None):
    """Creates a new AnalysisRequest (a Sample) object
    :param client: The container where the Sample will be created
    :param request: The current Http Request object
    :param values: A dict, with keys as AnalaysisRequest's schema field names
    :param analyses: List of Services or Analyses (brains, objects, UIDs,
        keywords). Extends the list from values["Analyses"]
    :param results_ranges: List of Results Ranges. Extends the results ranges
        from the Specification object defined in values["Specification"]
    :param prices: Mapping of AnalysisService UID -> price. If not set, prices
        are read from the associated analysis service.
    """
    # Don't pollute the dict param passed in
    values = dict(values.items())

    # Explicitly set client instead of relying on the passed in vales.
    # This might happen if this function is called programmatically outside of
    # the sample add form.
    values["Client"] = client

    # Resolve the Service uids of analyses to be added in the Sample. Values
    # passed-in might contain Profiles and also values that are not uids. Also,
    # additional analyses can be passed-in through either values or services
    service_uids = to_services_uids(values=values, services=analyses)

    # Remove the Analyses from values. We will add them manually
    values.update({"Analyses": []})

    # Remove the specificaton to set it *after* the analyses have been added
    specification = values.pop("Specification", None)

    # Create the Analysis Request and submit the form
    ar = _createObjectByType("AnalysisRequest", client, tmpID())
    # mark the sample as temporary to avoid indexing
    api.mark_temporary(ar)
    # NOTE: We call here `_processForm` (with underscore) to manually unmark
    #       the creation flag and trigger the `ObjectInitializedEvent`, which
    #       is used for snapshot creation.
    ar._processForm(REQUEST=request, values=values)

    # Set the analyses manually
    ar.setAnalyses(service_uids, prices=prices, specs=results_ranges)

    # Explicitly set the specification to the sample
    if specification:
        ar.setSpecification(specification)

    # Handle hidden analyses from template and profiles
    # https://github.com/senaite/senaite.core/issues/1437
    # https://github.com/senaite/senaite.core/issues/1326
    apply_hidden_services(ar)

    # Handle rejection reasons
    rejection_reasons = resolve_rejection_reasons(values)
    ar.setRejectionReasons(rejection_reasons)

    # Handle secondary Analysis Request
    primary = ar.getPrimaryAnalysisRequest()
    if primary:
        # Mark the secondary with the `IAnalysisRequestSecondary` interface
        alsoProvides(ar, IAnalysisRequestSecondary)

        # Set dates to match with those from the primary
        ar.setDateSampled(primary.getDateSampled())
        ar.setSamplingDate(primary.getSamplingDate())

        # Force the transition of the secondary to received and set the
        # description/comment in the transition accordingly.
        date_received = primary.getDateReceived()
        if date_received:
            receive_sample(ar, date_received=date_received)

    parent_sample = ar.getParentAnalysisRequest()
    if parent_sample:
        # Always set partition to received
        date_received = parent_sample.getDateReceived()
        receive_sample(ar, date_received=date_received)

    if not IReceived.providedBy(ar):
        setup = api.get_setup()
        auto_receive = setup.getAutoreceiveSamples()

        if ar.getSamplingRequired():
            # sample has not been collected yet
            changeWorkflowState(ar, SAMPLE_WORKFLOW, "to_be_sampled",
                                action="to_be_sampled")

        elif auto_receive and ar.getDateSampled() and can_receive(ar):
            # auto-receive the sample, but only if the user (that might be
            # a client) has enough privileges and the sample has a value set
            # for DateSampled. Otherwise, sample_due
            receive_sample(ar)

        else:
            # sample_due is the default initial status of the sample
            changeWorkflowState(ar, SAMPLE_WORKFLOW, "sample_due",
                                action="no_sampling_workflow")

    renameAfterCreation(ar)
    # AT only
    ar.unmarkCreationFlag()
    # unmark the sample as temporary
    api.unmark_temporary(ar)
    # explicit reindexing after sample finalization
    api.catalog_object(ar)
    # notify object initialization (also creates a snapshot)
    event.notify(ObjectInitializedEvent(ar))

    # If rejection reasons have been set, reject the sample automatically
    if rejection_reasons:
        do_rejection(ar)

    return ar


def receive_sample(sample, check_permission=False, date_received=None):
    """Receive the sample without transition
    """

    # NOTE: In `sample_registered` state we do not grant any roles the
    #       permission to receive a sample! Not sure if this can be ignored
    #       when the LIMS is configured to auto-receive samples?
    if check_permission and not can_receive(sample):
        return False

    changeWorkflowState(sample, SAMPLE_WORKFLOW, "sample_received",
                        action="receive")

    # Mark the secondary as received
    alsoProvides(sample, IReceived)
    # Manually set the received date
    if not date_received:
        date_received = DateTime()
    sample.setDateReceived(date_received)

    # Initialize analyses
    # NOTE: We use here `objectValues` instead of `getAnalyses`,
    #       because the Analyses are not yet indexed!
    for obj in sample.objectValues():
        if obj.portal_type != "Analysis":
            continue
        changeWorkflowState(obj, ANALYSIS_WORKFLOW, "unassigned",
                            action="initialize")

    return True


def apply_hidden_services(sample):
    """
    Applies the hidden setting to the sample analyses in accordance with the
    settings from its template and/or profiles
    :param sample: the sample that contains the analyses
    """
    hidden = list()

    # Get the "hidden" service uids from the template
    template = sample.getTemplate()
    hidden = get_hidden_service_uids(template)

    # Get the "hidden" service uids from profiles
    profiles = sample.getProfiles()
    hid_profiles = map(get_hidden_service_uids, profiles)
    hid_profiles = list(itertools.chain(*hid_profiles))
    hidden.extend(hid_profiles)

    # Update the sample analyses
    if api.is_temporary(sample):
        # sample is in create process. Just return the object values.
        analyses = sample.objectValues(spec="Analysis")
    else:
        analyses = sample.getAnalyses(full_objects=True)
    analyses = filter(lambda an: an.getServiceUID() in hidden, analyses)
    for analysis in analyses:
        analysis.setHidden(True)


def get_hidden_service_uids(profile_or_template):
    """Returns a list of service uids that are set as hidden
    :param profile_or_template: ARTemplate or AnalysisProfile object
    """
    if not profile_or_template:
        return []
    settings = profile_or_template.getAnalysisServicesSettings()
    hidden = filter(lambda ser: ser.get("hidden", False), settings)
    return map(lambda setting: setting["uid"], hidden)


def to_services_uids(services=None, values=None):
    """Returns a list of Analysis Services UIDS

    :param services: A list of service items (uid, keyword, brain, obj, title)
    :param values: a dict, where keys are AR|Sample schema field names.
    :returns: a list of Analyses Services UIDs
    """
    def to_list(value):
        if not value:
            return []
        if isinstance(value, six.string_types):
            return [value]
        if isinstance(value, (list, tuple)):
            return value
        logger.warn("Cannot convert to a list: {}".format(value))
        return []

    services = services or []
    values = values or {}

    # Merge analyses from analyses_serv and values into one list
    uids = to_list(services) + to_list(values.get("Analyses"))

    # Convert them to a list of service uids
    uids = filter(None, map(to_service_uid, uids))

    # Get the service uids without duplicates, but preserving the order
    return list(OrderedDict.fromkeys(uids).keys())


def to_service_uid(uid_brain_obj_str):
    """Resolves the passed in element to a valid uid. Returns None if the value
    cannot be resolved to a valid uid
    """
    if api.is_uid(uid_brain_obj_str) and uid_brain_obj_str != "0":
        return uid_brain_obj_str

    if api.is_object(uid_brain_obj_str):
        obj = api.get_object(uid_brain_obj_str)

        if IAnalysisService.providedBy(obj):
            return api.get_uid(obj)

        elif IRoutineAnalysis.providedBy(obj):
            return obj.getServiceUID()

        else:
            logger.error("Type not supported: {}".format(obj.portal_type))
            return None

    if isinstance(uid_brain_obj_str, six.string_types):
        # Maybe is a keyword?
        query = dict(portal_type="AnalysisService", getKeyword=uid_brain_obj_str)
        brains = api.search(query, SETUP_CATALOG)
        if len(brains) == 1:
            return api.get_uid(brains[0])

        # Or maybe a title
        query = dict(portal_type="AnalysisService", title=uid_brain_obj_str)
        brains = api.search(query, SETUP_CATALOG)
        if len(brains) == 1:
            return api.get_uid(brains[0])

    return None


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
        raise ValueError("Cannot do a retest from an invalid Analysis Request")

    # Create the Retest (Analysis Request)
    ignore = ['Analyses', 'DatePublished', 'Invalidated', 'Sample', 'Remarks']
    retest = _createObjectByType("AnalysisRequest", ar.aq_parent, tmpID())
    copy_field_values(ar, retest, ignore_fieldnames=ignore)

    # Mark the retest with the `IAnalysisRequestRetest` interface
    alsoProvides(retest, IAnalysisRequestRetest)

    # Assign the source to retest
    retest.setInvalidated(ar)

    # Rename the retest according to the ID server setup
    renameAfterCreation(retest)

    # Copy the analyses from the source
    intermediate_states = ['retracted', ]
    for an in ar.getAnalyses(full_objects=True):
        # skip retests
        if an.isRetest():
            continue

        if api.get_workflow_status_of(an) in intermediate_states:
            # Exclude intermediate analyses
            continue

        # Original sample might have multiple copies of same analysis
        keyword = an.getKeyword()
        analyses = retest.getAnalyses(full_objects=True)
        analyses = filter(lambda ret: ret.getKeyword() == keyword, analyses)
        if analyses:
            keyword = '{}-{}'.format(keyword, len(analyses))

        # Create the analysis retest
        nan = _createObjectByType("Analysis", retest, keyword)

        # Make a copy
        ignore_fieldnames = ['DataAnalysisPublished']
        copy_field_values(an, nan, ignore_fieldnames=ignore_fieldnames)
        nan.unmarkCreationFlag()
        nan.reindexObject()

    # Transition the retest to "sample_received"!
    changeWorkflowState(retest, SAMPLE_WORKFLOW, 'sample_received')
    alsoProvides(retest, IReceived)

    # Initialize analyses
    for analysis in retest.getAnalyses(full_objects=True):
        if not IRoutineAnalysis.providedBy(analysis):
            continue
        changeWorkflowState(analysis, ANALYSIS_WORKFLOW, "unassigned")

    # Reindex and other stuff
    retest.reindexObject()
    retest.aq_parent.reindexObject()

    return retest


def create_partition(analysis_request, request, analyses, sample_type=None,
                     container=None, preservation=None, skip_fields=None,
                     internal_use=True):
    """
    Creates a partition for the analysis_request (primary) passed in
    :param analysis_request: uid/brain/object of IAnalysisRequest type
    :param request: the current request object
    :param analyses: uids/brains/objects of IAnalysis type
    :param sampletype: uid/brain/object of SampleType
    :param container: uid/brain/object of Container
    :param preservation: uid/brain/object of SamplePreservation
    :param skip_fields: names of fields to be skipped on copy from primary
    :return: the new partition
    """
    partition_skip_fields = [
        "Analyses",
        "Attachment",
        "Client",
        "DetachedFrom",
        "Profile",
        "Profiles",
        "RejectionReasons",
        "Remarks",
        "ResultsInterpretation",
        "ResultsInterpretationDepts",
        "Sample",
        "Template",
        "creation_date",
        "modification_date",
        "ParentAnalysisRequest",
        "PrimaryAnalysisRequest",
        # default fields
        "id",
        "description",
        "allowDiscussion",
        "subject",
        "location",
        "contributors",
        "creators",
        "effectiveDate",
        "expirationDate",
        "language",
        "rights",
        "creation_date",
        "modification_date",
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

    # Populate the root's ResultsRanges to partitions
    results_ranges = ar.getResultsRange() or []

    partition = create_analysisrequest(client,
                                       request=request,
                                       values=record,
                                       analyses=services,
                                       results_ranges=results_ranges)

    # Reindex Parent Analysis Request
    ar.reindexObject(idxs=["isRootAncestor"])

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

    # XXX RejectionReasons returns a list with a single dict
    reasons = rejection_reasons[0] or {}
    if reasons.get("checkbox") != "on":
        # reasons entry is toggled off
        return []

    # Predefined reasons selected?
    selected = reasons.get("multiselection") or []

    # Other reasons set?
    other = reasons.get("other") or ""

    # If neither selected nor other reasons are set, return empty
    if any([selected, other]):
        return [{"selected": selected, "other": other}]

    return []


def do_rejection(sample, notify=None):
    """Rejects the sample and if succeeds, generates the rejection pdf and
    sends a notification email. If notify is None, the notification email will
    only be sent if the setting in Setup is enabled
    """
    sample_id = api.get_id(sample)
    if not sample.getRejectionReasons():
        logger.warn("Cannot reject {} w/o rejection reasons".format(sample_id))
        return

    success, msg = doActionFor(sample, "reject")
    if not success:
        logger.warn("Cannot reject the sample {}".format(sample_id))
        return

    # Generate a pdf with the rejection reasons
    pdf = get_rejection_pdf(sample)

    # Attach the PDF to the sample
    filename = "{}-rejected.pdf".format(sample_id)
    attachment = sample.createAttachment(pdf, filename=filename)
    pdf_file = attachment.getAttachmentFile()

    # Do we need to send a notification email?
    if notify is None:
        setup = api.get_setup()
        notify = setup.getNotifyOnSampleRejection()

    if notify:
        # Compose and send the email
        mime_msg = get_rejection_mail(sample, pdf_file)
        if mime_msg:
            # Send the email
            send_email(mime_msg)


def get_rejection_pdf(sample):
    """Generates a pdf with sample rejection reasons
    """
    # Avoid circular dependencies
    from senaite.core.browser.samples.rejection.report import RejectionReport

    # Render the html's rejection document
    tpl = RejectionReport(sample, api.get_request())
    return tpl.to_pdf()


def get_rejection_email_recipients(sample):
    """Returns a list with the email addresses to send the rejection report
    """
    # extract the emails from contacts
    contacts = [sample.getContact()] + sample.getCCContact()
    contacts = filter(None, contacts)
    emails = map(lambda contact: contact.getEmailAddress(), contacts)

    # extend with the CC emails
    emails = list(emails) + sample.getCCEmails(as_list=True)
    emails = filter(is_valid_email_address, emails)
    return list(emails)



def get_rejection_mail(sample, rejection_pdf=None):
    """Generates an email to sample contacts with rejection reasons
    """
    # Get the reasons
    reasons = sample.getRejectionReasons()
    reasons = reasons and reasons[0] or {}
    reasons = reasons.get("selected", []) + [reasons.get("other")]
    reasons = filter(None, reasons)
    reasons = "<br/>- ".join(reasons)

    # Render the email body
    setup = api.get_setup()
    lab_address = setup.laboratory.getPrintAddress()
    email_body = Template(setup.getEmailBodySampleRejection())
    email_body = email_body.safe_substitute({
        "lab_address": "<br/>".join(lab_address),
        "reasons": reasons and "<br/>-{}".format(reasons) or "",
        "sample_id": api.get_id(sample),
        "sample_link": get_link(api.get_url(sample), api.get_id(sample))
    })

    def to_valid_email_address(contact):
        if not contact:
            return None
        address = contact.getEmailAddress()
        if not is_valid_email_address(address):
            return None
        return address

    # Get the recipients
    _to = get_rejection_email_recipients(sample)
    if not _to:
        # Cannot send an e-mail without recipient!
        logger.warn("No valid recipients for {}".format(api.get_id(sample)))
        return None

    lab = api.get_setup().laboratory
    attachments = rejection_pdf and [rejection_pdf] or []

    return compose_email(
        from_addr=lab.getEmailAddress(),
        to_addr=_to,
        subj=_("%s has been rejected") % api.get_id(sample),
        body=email_body,
        html=True,
        attachments=attachments)
