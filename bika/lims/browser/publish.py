from operator import itemgetter
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.utils import encode_header, createPdf, attachPdf
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from bika.lims.utils import to_utf8
from os.path import join
from pkg_resources import resource_filename
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from smtplib import SMTPRecipientsRefused
from smtplib import SMTPServerDisconnected
from zope.component import getAdapters

import App
import Globals


class doPublish(BrowserView):
    """Pre/Re/Publish analysis requests"""
    template = ViewPageTemplateFile("mailtemplates/analysisrequest_results.pt")

    def __init__(self, context, request, action, analysis_requests):
        self.context = context
        self.request = request
        self.field_icons = {}
        # the workflow transition that invoked us
        self.action = action

        self.member = None
        self.username = ""
        self.reporter = ""
        self.reporter_email = ""
        self.reporter_signature = ""

        self.check_previous = context.bika_setup.getIncludePreviousFromBatch()
        self.previous_results = {}
        self.prev_strings = {}
        self.any_prev = False

        # the list of ARs that we will process.
        # Filter them here so we only publish those with verified analyses.
        workflow = getToolByName(self.context, 'portal_workflow')
        self.analysis_requests = []
        self.publish_states = ['verified', 'published']
        for ar in analysis_requests:
            if workflow.getInfoFor(ar, 'review_state') in self.publish_states \
                    or ar.getAnalyses(review_state=self.publish_states):
                self.analysis_requests.append(ar)

    def get_active_spec_object(self):
        """ Return the specification that should be used for this analysis' result
            1. If the request contains PublicationSpecificaton (a UID)
               it is used.
            2. If there is a Specification field (on an AR at least there is),
               we return it's result
            3. None
        """
        spec_uid = self.request.get('PublicationSpecification', '')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        brains = bsc(UID=spec_uid) if spec_uid else None
        spec = brains[0].getObject() if brains else None
        if spec:
            return spec
        if hasattr(self.context, 'getSpecification'):
            return self.context.getSpecification()
        return None

    def get_active_spec_title(self):
        obj = self.get_active_spec_object()
        if obj:
            return to_utf8(obj.Title())
        return ""

    def get_active_spec_dict(self, analysis):
        """ Return value of get_active_spec_object as a nice dict
        """
        obj = self.get_active_spec_object()
        if obj:
            rr = obj.getResultsRangeDict()
            keyword = analysis.getKeyword()
            if keyword in rr:
                return rr[keyword]
        if hasattr(analysis, "specification") and analysis.specification:
            return analysis.specification
        return {"max": "", "min": "", "error": ""}

    def ResultOutOfRange(self, analysis):
        """ Template wants to know, is this analysis out of range?
        We scan IResultOutOfRange adapters, and return True if any IAnalysis
        adapters trigger a result.
        """
        adapters = getAdapters((analysis, ), IResultOutOfRange)
        bsc = getToolByName(self.context, "bika_setup_catalog")
        spec = self.get_active_spec_dict(analysis)
        for name, adapter in adapters:
            if not spec:
                return False
            ret = adapter(specification=spec)
            if ret and ret['out_of_range']:
                return True

    def getAnalysisSpecsStr(self, spec):
        specstr = ''
        if spec['min'] and spec['max']:
            specstr = '%s - %s' % (spec['min'], spec['max'])
        elif spec['min']:
            specstr = '> %s' % spec['min']
        elif spec['max']:
            specstr = '< %s' % spec['max']
        return specstr

    def _get_user_attributes(self):
        self.member = self.context.portal_membership.getAuthenticatedMember()
        self.username = self.member.getUserName()
        self.reporter = to_utf8(self.user_fullname(self.username))
        self.reporter_email = to_utf8(self.user_email(self.username))
        self.reporter_signature = ""
        c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
             if x.getObject().getUsername() == self.username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                self.reporter_signature = sf.absolute_url() + "/Signature"

    def _get_lab_attributes(self):
        lab = self.context.bika_setup.laboratory
        lab_address = lab.getPostalAddress() \
                      or lab.getBillingAddress() \
                      or lab.getPhysicalAddress()
        if lab_address:
            _keys = ['address', 'city', 'state', 'zip', 'country']
            _list = ["<div>%s</div>" % lab_address.get(v) for v in _keys
                     if lab_address.get(v)]
            lab_address = "".join(_list)
        else:
            lab_address = ''
        self.laboratory = {
            'obj': lab,
            'Title': to_utf8(lab.Title()),
            'getLabURL': to_utf8(lab.getLabURL()),
            'address': to_utf8(lab_address),
            'getAccreditationBody': to_utf8(lab.getAccreditationBody()),
        }

    def _get_client_attribues(self, ar):
        client = ar.aq_parent
        client_address = client.getPostalAddress()
        contact = ar.getContact()
        if contact and not client_address:
            client_address = contact.getBillingAddress()
            if not client_address:
                client_address = contact.getPhysicalAddress()
        if client_address:
            _keys = ['address', 'city', 'state', 'zip', 'country']
            _list = ["<div>%s</div>" % client_address.get(v) for v in _keys
                     if client_address.get(v)]
            client_address = "".join(_list)
        else:
            client_address = ''
        self.client = {
            'obj': client,
            'Name': to_utf8(client.getName()),
            'getPhone': to_utf8(client.getPhone()),
            'getFax': to_utf8(client.getFax()),
            'address': to_utf8(client_address),
        }

    def _get_ar_attributes(self, ar):
        self.ar = {
            'obj': ar,
            'getClientReference': to_utf8(ar.getClientReference()),
        }

    def _get_batch_attributes(self, ar):
        # Batch attributes
        batch = ar.getBatch()
        self.batch = {
            'obj': batch,
            'getClientBatchID': to_utf8(batch.getClientBatchID()),
            'getBatchLabels': batch.getBatchLabels(),
        } if batch else {'obj': None}

    def _get_sample_attributes(self, ar):
        # Sample attributes
        sample = ar.getSample()
        self.sample = {
            'obj': sample,
            'getClientSampleID': to_utf8(sample.getClientSampleID()),
            'sampletype_title': to_utf8(sample.getSampleType().Title()),
        }

    def _get_contact_attributes(self, ar):
        # ## Primary contact attributes
        contact = ar.getContact()
        self.contact = {
            'obj': contact,
            'getFullname': to_utf8(contact.getFullname()),
            'getEmailAddress': to_utf8(contact.getEmailAddress()),
            'getPublicationPreference': contact.getPublicationPreference(),
        } if contact else {
            'obj': contact,
            'getFullname': "",
            'getEmailAddress': "",
            'getPublicationPreference': "",
        }

    def get_previous_results(self, analysis):
        # Collect all results for this AnalysisService, in the same batch.
        # return a string of "result, result, result".
        workflow = getToolByName(self.context, 'portal_workflow')
        keyword = analysis.getKeyword()
        analyses = []
        batch = self.batch['obj']
        if not batch:
            return
        batch_ars = self.batch['obj'].getAnalysisRequests()
        result_visible_states = ['verified', 'published']
        for ar in batch_ars:
            if analysis.aq_parent == ar:
                continue
            if keyword not in ar:
                continue
            an = ar[keyword]
            an_state = workflow.getInfoFor(an, 'review_state')
            if an.getResult() and an_state in result_visible_states:
                self.any_prev = True
                analyses.append({"analysis": an,
                                 "request_id": ar.getId(),
                                 "spec": self.get_active_spec_dict(an),
                                 "date": an.getResultCaptureDate(),
                                 "result": an.getResult(),
                                 "unit": an.getService().getUnit(),
                                 "out_of_range": self.ResultOutOfRange(an)})
        analyses = sorted(analyses, key=itemgetter("date"))
        self.previous_results[analysis.getKeyword()] = analyses
        self.prev_strings[analysis.getKeyword()] = \
            ", ".join([self.formattedResult(p['analysis']) for p in analyses[-5:]])

    def _get_categorized_services(self, ar):
        self.any_accredited = False
        self.services = {}
        analyses = ar.getAnalyses(full_objects=True,
            review_state=self.publish_states)
        analyses.sort(lambda x, y: cmp(x.Title().lower(), y.Title().lower()))
        for analysis in analyses:
            service = analysis.getService()
            poc = to_utf8(POINTS_OF_CAPTURE.getValue(service.getPointOfCapture()))
            cat = to_utf8(service.getCategoryTitle())
            if poc not in self.services:
                self.services[poc] = {}
            if cat not in self.services[poc]:
                self.services[poc][cat] = []
            if self.check_previous:
                self.get_previous_results(analysis)
            if service not in self.services[poc][cat]:
                self.services[poc][cat].append(service)
            if service.getAccredited():
                self.any_accredited = True

    def _get_categorized_qcservices(self, ar):
        self.qcservices = {}
        for qcanalysis in ar.getQCAnalyses():
            service = qcanalysis.getService()
            qctype = ''
            if qcanalysis.portal_type == 'DuplicateAnalysis':
                qctype = "d"
            elif qcanalysis.portal_type == 'ReferenceAnalysis':
                qctype = qcanalysis.getReferenceType()
            else:
                continue
            if qctype not in self.qcservices:
                self.qcservices[qctype] = {}
            poc = to_utf8(
                POINTS_OF_CAPTURE.getValue(service.getPointOfCapture()))
            if poc not in self.qcservices[qctype]:
                self.qcservices[qctype][poc] = {}
            cat = to_utf8(service.getCategoryTitle())
            if cat not in self.qcservices[qctype][poc]:
                self.qcservices[qctype][poc][cat] = []
            # if service not in self.qcservices[qctype][poc][cat]:
            self.qcservices[qctype][poc][cat].append(
                {'service': service,
                 'analysis': qcanalysis})

    def __call__(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        # SMTP errors are silently ignored if server is in debug mode
        self.debug_mode = App.config.getConfiguration().debug_mode
        # PDF and HTML files are written to disk if server is in debug mode
        self.out_path = join(Globals.INSTANCE_HOME, 'var') if self.debug_mode \
            else None
        self._get_user_attributes()
        self._get_lab_attributes()

        # This for loop prints each AR individually to a PDF stored in the AR,
        # and sends whatever publication is required
        for ar_nr, ar in enumerate(self.analysis_requests):
            self.any_drymatter = ar.getReportDryMatter()
            self._get_ar_attributes(ar)
            self._get_client_attribues(ar)
            self._get_batch_attributes(ar)
            self._get_sample_attributes(ar)
            self._get_contact_attributes(ar)
            self._get_categorized_services(ar)
            self._get_categorized_qcservices(ar)
            self.Footer = to_utf8(self.context.bika_setup.getResultFooter())
            out_fn = to_utf8(ar.Title())


            # Create the html report
            ar_results = safe_unicode(self.template()).encode('utf-8')
            if self.out_path:
                open(join(self.out_path, out_fn + ".html"), "w").write(ar_results)

            # Create the pdf report (will always be attached to the AR)
            pdf_outfile = join(self.out_path,
                out_fn + ".pdf") if self.out_path else None
            pdf_css = resource_filename(
                "bika.lims", "skins/bika/analysisrequest_results_pdf.css")
            ar_css = join(self.portal_url, "analysisrequest_results.css")
            ar_results = ar_results.replace(ar_css, pdf_css)
            pdf_report = createPdf(ar_results, pdf_outfile, css=pdf_css)

            if self.contact['obj']:
                recipients = [{
                    'UID': self.contact['obj'].UID(),
                    'Username': to_utf8(self.contact['obj'].getUsername()),
                    'Fullname': to_utf8(self.contact['obj'].getFullname()),
                    'EmailAddress': to_utf8(self.contact['obj'].getEmailAddress()),
                    'PublicationModes': self.contact['obj'].getPublicationPreference()
                }]
            else:
                recipients = []

            if pdf_report:
                reportid = self.context.generateUniqueId('ARReport')
                report = _createObjectByType("ARReport", ar, reportid)
                report.edit(
                    AnalysisRequest=ar.UID(),
                    Pdf=pdf_report,
                    Html=ar_results,
                    Recipients=recipients
                )
                report.unmarkCreationFlag()
                from bika.lims.idserver import renameAfterCreation

                renameAfterCreation(report)

                # Set status to published
                if self.action == 'publish':
                    try:
                        workflow.doActionFor(ar, 'publish')
                    except WorkflowException:
                        pass

                # compose and send email.
                # The managers of the departments for which the current AR has
                # at least one AS must receive always the pdf report by email.
                # https://github.com/bikalabs/Bika-LIMS/issues/1028
                mime_msg = MIMEMultipart('related')
                mime_msg['Subject'] = self.get_mail_subject(ar)[0]
                mime_msg['From'] = formataddr(
                    (encode_header(self.laboratory['obj'].getName()),
                     self.laboratory['obj'].getEmailAddress()))
                mime_msg.preamble = 'This is a multi-part MIME message.'
                msg_txt = MIMEText(ar_results, _subtype='html')
                mime_msg.attach(msg_txt)

                to = []
                mngrs = ar.getResponsible()
                for mngrid in mngrs['ids']:
                    name = mngrs['dict'][mngrid].get('name', '')
                    email = mngrs['dict'][mngrid].get('email', '')
                    if (email != ''):
                        to.append(formataddr((encode_header(name), email)))

                if len(to) > 0:
                    # Send the email to the managers
                    mime_msg['To'] = ','.join(to)
                    attachPdf(mime_msg, pdf_report, out_fn)

                    try:
                        host = getToolByName(self.context, 'MailHost')
                        host.send(mime_msg.as_string(), immediate=True)
                    except SMTPServerDisconnected as msg:
                        pass
                        if not self.debug_mode:
                            raise SMTPServerDisconnected(msg)
                    except SMTPRecipientsRefused as msg:
                        raise WorkflowException(str(msg))

                    to = []

                # Send report to recipients
                recips = self.get_recipients(ar)
                for recip in recips:
                    if 'email' not in recip.get('pubpref', []) \
                            or not recip.get('email', ''):
                        continue

                    title = encode_header(recip.get('title', ''))
                    email = recip.get('email')
                    formatted = formataddr((title, email))

                    # Create the new mime_msg object, cause the previous one
                    # has the pdf already attached
                    mime_msg = MIMEMultipart('related')
                    mime_msg['Subject'] = self.get_mail_subject(ar)[0]
                    mime_msg['From'] = formataddr(
                        (encode_header(self.laboratory['obj'].getName()),
                         self.laboratory['obj'].getEmailAddress()))
                    mime_msg.preamble = 'This is a multi-part MIME message.'
                    msg_txt = MIMEText(ar_results, _subtype='html')
                    mime_msg.attach(msg_txt)
                    mime_msg['To'] = formatted

                    # Attach the pdf to the email if requested
                    if pdf_report and 'pdf' in recip.get('pubpref'):
                        attachPdf(mime_msg, pdf_report, out_fn)

                    # For now, I will simply ignore mail send under test.
                    if hasattr(self.portal, 'robotframework'):
                        continue

                    try:
                        host = getToolByName(self.context, 'MailHost')
                        host.send(mime_msg.as_string(), immediate=True)
                    except SMTPServerDisconnected as msg:
                        if not self.debug_mode:
                            raise SMTPServerDisconnected(msg)
                    except SMTPRecipientsRefused as msg:
                        raise WorkflowException(str(msg))

        return [ar.RequestID for ar in self.analysis_requests]

    def formattedResult(self, analysis):
        """Formatted result:
        1. Print ResultText of matching ResulOptions
        2. If the result is floatable, render it to the correct precision
        If analysis is None, returns empty string
        """
        if analysis is None:
            return ''

        result = analysis.getResult()
        service = analysis.getService()
        choices = service.getResultOptions()

        # 1. Print ResultText of mathching ResulOptions
        match = [x['ResultText'] for x in choices
                 if str(x['ResultValue']) == str(result)]
        if match:
            return match[0]

        # 2. If the result is floatable, render it to the correct precision
        precision = service.getPrecision()
        if not precision:
            precision = '2'
        try:
            result = str("%%.%sf" % precision) % float(result)
        except:
            pass

        return result

    def containsInvalidARs(self):
        for ar in self.batch:
            if ar.isInvalid():
                return True
        return False

    def get_managers_from_request(self, ar):
        managers = {'ids': [], 'dict': {}}
        departments = {}
        ar_mngrs = ar.getResponsible()
        for id in ar_mngrs['ids']:
            new_depts = ar_mngrs['dict'][id]['departments'].split(',')
            if id in managers['ids']:
                for dept in new_depts:
                    if dept not in departments[id]:
                        departments[id].append(dept)
            else:
                departments[id] = new_depts
                managers['ids'].append(id)
                managers['dict'][id] = ar_mngrs['dict'][id]

        mngrs = departments.keys()
        for mngr in mngrs:
            final_depts = ''
            for dept in departments[mngr]:
                if final_depts:
                    final_depts += ', '
                final_depts += dept
            managers['dict'][mngr]['departments'] = final_depts

        return managers

    def get_mail_subject(self, ar):
        client = ar.aq_parent
        subject_items = client.getEmailSubject()
        ai = co = cr = cs = False
        if 'ar' in subject_items:
            ai = True
        if 'co' in subject_items:
            co = True
        if 'cr' in subject_items:
            cr = True
        if 'cs' in subject_items:
            cs = True
        ais = []
        cos = []
        crs = []
        css = []
        blanks_found = False
        if ai:
            ais.append(ar.getRequestID())
        if co:
            if ar.getClientOrderNumber():
                if not ar.getClientOrderNumber() in cos:
                    cos.append(ar.getClientOrderNumber())
            else:
                blanks_found = True
        if cr or cs:
            sample = ar.getSample()
        if cr:
            if sample.getClientReference():
                if not sample.getClientReference() in crs:
                    crs.append(sample.getClientReference())
            else:
                blanks_found = True
        if cs:
            if sample.getClientSampleID():
                if not sample.getClientSampleID() in css:
                    css.append(sample.getClientSampleID())
            else:
                blanks_found = True
        tot_line = ''
        if ais:
            ais.sort()
            ar_line = _('ARs: %s') % ', '.join(ais)
            tot_line = ar_line
        if cos:
            cos.sort()
            cos_line = _('Orders: %s') % ', '.join(cos)
            if tot_line:
                tot_line += ' '
            tot_line += cos_line
        if crs:
            crs.sort()
            crs_line = _('Refs: %s') % ', '.join(crs)
            if tot_line:
                tot_line += ' '
            tot_line += crs_line
        if css:
            css.sort()
            css_line = _('Samples: %s') % ', '.join(css)
            if tot_line:
                tot_line += ' '
            tot_line += css_line
        if tot_line:
            subject = _('Analysis results for %s') % tot_line
            if blanks_found:
                subject += (' ' + _('and others'))
        else:
            subject = _('Analysis results')
        return subject, tot_line

    def get_titles_for_uids(self, *uids):
        uc = getToolByName(self.context, 'uid_catalog')
        return [to_utf8(p.getObject().Title()) for p in uc(UID=uids)]

    def get_recipients(self, ar):
        """ Return an array with the recipients and all its publication prefs
        """
        recips = []

        # Contact and CC's
        contact = ar.getContact()
        if contact:
            recips.append({'title': to_utf8(contact.Title()),
                           'email': contact.getEmailAddress(),
                           'pubpref': contact.getPublicationPreference()})
        for cc in ar.getCCContact():
            recips.append({'title': to_utf8(cc.Title()),
                           'email': cc.getEmailAddress(),
                           'pubpref': contact.getPublicationPreference()})

        return recips
