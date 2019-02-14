from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.workflow import WorkflowActionGenericAdapter, \
    RequestContextAware
from bika.lims.interfaces import IAnalysisRequest, IWorkflowActionUIDsAdapter
from bika.lims.utils import encode_header
from bika.lims.utils import t
from email.Utils import formataddr
from zope.component.interfaces import implements


class WorkflowActionCopyToNewAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'copy_to_new' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/ar_add?ar_count={}&copy_from={}".format(
            self.back_url, len(uids), ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionPrintStickersAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'print_stickers' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/sticker?template={}&items={}".format(self.back_url,
            self.context.bika_setup.getAutoStickerTemplate(), ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionCreatePartitionsAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'copy_to_new' action
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        url = "{}/partition_magic?uids={}".format(self.back_url, ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionPublishAdapter(RequestContextAware):
    """Adapter in charge of Analysis Requests 'publish'-like actions
    """
    implements(IWorkflowActionUIDsAdapter)

    def __call__(self, action, uids):
        purl = self.context.portal_url()
        uids = ",".join(uids)
        url = "{}/analysisrequests/publish?items={}".format(purl, uids)
        return self.redirect(redirect_url=url)


class WorkflowActionReceiveAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request receive action
    """

    def __call__(self, action, objects):
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        auto_partitions = filter(self.is_auto_partition_required, objects)
        if auto_partitions:
            # Redirect to the partitioning view
            uids = ",".join(map(api.get_uid, auto_partitions))
            url = "{}/partition_magic?uids={}".format(self.back_url, uids)
            return self.redirect(redirect_url=url)

        if self.is_auto_print_stickers_enabled():
            # Redirect to the auto-print stickers view
            uids = ",".join(map(api.get_uid, transitioned))
            sticker_template = self.context.bika_setup.getAutoStickerTemplate()
            url = "{}/sticker?autoprint=1&template={}&items={}".format(
                self.back_url, sticker_template, uids)
            return self.redirect(redirect_url=url)

        # Redirect the user to success page
        return self.success(transitioned)

    def is_auto_partition_required(self, brain_or_object):
        """Returns whether the passed in object needs to be partitioned
        """
        obj = api.get_object(brain_or_object)
        if not IAnalysisRequest.providedBy(obj):
            return False
        template = obj.getTemplate()
        return template and template.getAutoPartition()

    def is_auto_print_stickers_enabled(self):
        """Returns whether the auto print of stickers on reception is enabled
        """
        return "receive" in self.context.bika_setup.getAutoPrintStickers()


class WorkflowActionInvalidateAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request invalidate action
    """

    def __call__(self, action, objects):
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Need to notify client contacts?
        if not self.context.bika_setup.getNotifyOnARRetract():
            return self.success(transitioned)

        # Alert the client contacts who ordered the results, stating that a
        # possible mistake has been picked up and is under investigation.
        for sample in transitioned:
            self.notify_ar_retract(sample)

        # Redirect the user to success page
        return self.success(transitioned)

    def notify_ar_retract(self, sample):
        """Sends an email notification to sample's client contact if the sample
        passed in has a retest associated
        """
        retest = sample.getRetest()
        if not retest:
            logger.warn("No retest found for {}. And it should!"
                        .format(api.get_id(sample)))
            return

        # Email fields
        sample_id = api.get_id(sample)
        subject = t(_("Erroneous result publication from {}").format(sample_id))
        lab_address = api.get_bika_setup().laboratory.getPrintAddress()
        emails_lab = self.get_lab_managers_formatted_emails()
        emails_sample = self.get_sample_contacts_formatted_emails(sample)
        recipients = list(set(emails_lab + emails_sample))

        msg = MIMEMultipart("related")
        msg["Subject"] = subject
        msg["From"] = self.get_laboratory_formatted_email()
        msg["To"] = ", ".join(recipients)
        body = Template("Some errors have been detected in the results report "
                        "published from the Sample $sample_link. The Sample "
                        "$retest_link has been created automatically and the "
                        "previous has been invalidated.<br/>"
                        "The possible mistake has been picked up and is under "
                        "investigation.<br/><br/>"
                        "$lab_address").safe_substitute(
            dict(sample_link=self.get_html_link(sample),
                 retest_link=self.get_html_link(retest),
                 lab_address = "<br/>".join(lab_address)))
        msg_txt = MIMEText(safe_unicode(body).encode('utf-8'), _subtype='html')
        msg.preamble = 'This is a multi-part MIME message.'
        msg.attach(msg_txt)

        # Send the email
        try:
            host = api.get_tool("MailHost")
            host.send(msg.as_string(), immediate=True)
        except Exception as err_msg:
            message = _("Unable to send an email to alert lab "
                        "client contacts that the Sample has been "
                        "retracted: ${error}",
                        mapping={'error': safe_unicode(err_msg)})
            self.context.plone_utils.addPortalMessage(message, 'warning')

    def get_formatted_email(self, email_name):
        """Formats a email
        """
        return formataddr((encode_header(email_name[0]), email_name[1]))

    def get_laboratory_formatted_email(self):
        """Returns the laboratory email formatted
        """
        lab = api.get_bika_setup().laboratory
        return self.get_formatted_email((lab.getEmailAddress(), lab.getName()))

    def get_lab_managers_formatted_emails(self):
        """Returns a list with lab managers formatted emails
        """
        users = api.get_users_by_roles("LabManager")
        users = map(lambda user: (user.getProperty("email"),
                                  user.getProperty("fullname")), users)
        return map(self.get_formatted_email, users)

    def get_contact_formatted_email(self, contact):
        """Returns a string with the formatted email for the given contact
        """
        contact_name = contact.Title()
        contact_email = contact.getEmailAddress()
        return self.get_formatted_email((contact_email, contact_name))

    def get_sample_contacts_formatted_emails(self, sample):
        """Returns a list with the formatted emails from sample contacts
        """
        contacts = list(set([sample.getContact()] + sample.getCCContact()))
        return map(self.get_contact_formatted_email, contacts)

    def get_html_link(self, obj):
        """Returns an html formatted link for the given object
        """
        return "<a href='{}'>{}</a>".format(api.get_url(obj), api.get_id(obj))


class WorkflowActionPrintSampleAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of Analysis Request print_sample action
    """

    def __call__(self, action, objects):
        # Update printed times
        transitioned = filter(lambda obj: self.set_printed_time(obj), objects)
        if not transitioned:
            return self.redirect(message=_("No changes made"), level="warning")

        # Redirect the user to success page
        return self.success(transitioned)

    def set_printed_time(self, sample):
        """Updates the printed time of the last results report from the sample
        """
        if api.get_workflow_status_of(sample) != "published":
            return False
        reports = sample.objectValues("ARReport")
        reports = sorted(reports, key=lambda report: report.getDatePublished())
        last_report = reports[-1]
        if not last_report.getDatePrinted():
            last_report.setDatePrinted(DateTime())
            sample.reindexObject(idxs=["getPrinted"])
        return True
