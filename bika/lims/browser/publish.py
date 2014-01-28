from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.interfaces import IFieldIcons
from bika.lims.utils import encode_header, createPdf, attachPdf
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from os.path import join
from pkg_resources import resource_filename
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
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
        # 1) pub spec first
        # 2) AR spec attribute
        # 3) None
        spec_uid = self.request.get('PublicationSpecification', '')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        obj = None
        if spec_uid:
            brains = bsc(UID=spec_uid)
            if brains:
                obj = brains[0].getObject()
        if hasattr(self.context, 'getSpecification') and not obj:
            if self.context.getSpecification():
                obj = self.context.getSpecification()
        return obj

    def get_active_spec_title(self):
        obj = self.get_active_spec_object()
        if obj:
            return obj.Title()
        return ""

    def get_active_spec_dict(self, analysis):
        # 1) pub/AR spec first
        # 2) specs directly on the analysis
        # 3) None

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
        We scan IFieldIcons adapters, and return True if any IAnalysis
        adapters trigger a result.
        """
        adapters = getAdapters((analysis, ), IFieldIcons)
        bsc = getToolByName(self.context, "bika_setup_catalog")
        spec = self.get_active_spec_dict(analysis)
        for name, adapter in adapters:
            obj = self.get_active_spec_object()
            if not spec:
                return False
            alerts = adapter(specification=spec)
            if alerts and analysis.UID() in alerts:
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

    def __call__(self):

        debug_mode = App.config.getConfiguration().debug_mode
        out_path = join(Globals.INSTANCE_HOME, 'var') if debug_mode else None
        workflow = getToolByName(self.context, 'portal_workflow')
        # reporting user
        member = self.context.portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        self.reporter = self.user_fullname(username)
        self.reporter_email = self.user_email(username)
        self.reporter_signature = ""
        c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
             if x.getObject().getUsername() == username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                self.reporter_signature = sf.absolute_url() + "/Signature"

        # lab address
        # forced into a table for weasy-print.
        self.laboratory = laboratory = self.context.bika_setup.laboratory
        lab_address = laboratory.getPostalAddress() \
            or laboratory.getBillingAddress() \
            or laboratory.getPhysicalAddress()
        if lab_address:
            _keys = ['address', 'city', 'state', 'zip', 'country']
            _list = ["<div>%s</div>"%lab_address.get(v) for v in _keys
                     if lab_address.get(v)]
            self.lab_address = "".join(_list)
        else:
            self.lab_address = None

        for ar in self.analysis_requests:
            self.ar = ar
            self.contact = ar.getContact()
            self.pub_pref = self.contact.getPublicationPreference()

            # client address
            self.client = ar.aq_parent
            client_address = self.client.getPostalAddress() \
                or self.contact.getBillingAddress() \
                or self.contact.getPhysicalAddress()
            if client_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = ["<div>%s</div>"%client_address.get(v) for v in _keys
                         if client_address.get(v)]
                self.client_address = "".join(_list)
            else:
                self.client_address = None

            self.Footer = self.context.bika_setup.getResultFooter()

            self.any_drymatter = ar.getReportDryMatter()
            self.any_accredited = False

            out_fn = ar.Title()

            analyses = ar.getAnalyses(full_objects=True,
                                      review_state=self.publish_states)
            analyses.sort(
                lambda x, y: cmp(x.Title().lower(), y.Title().lower()))

            self.services = {}
            self.qcservices = {}

            for analysis in analyses:

                service = analysis.getService()
                poc = POINTS_OF_CAPTURE.getValue(service.getPointOfCapture())
                cat = service.getCategoryTitle()
                if poc not in self.services:
                    self.services[poc] = {}
                if cat not in self.services[poc]:
                    self.services[poc][cat] = []
                if service not in self.services[poc][cat]:
                    self.services[poc][cat].append(service)
                if (service.getAccredited()):
                    self.any_accredited = True

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
                poc = POINTS_OF_CAPTURE.getValue(service.getPointOfCapture())
                if poc not in self.qcservices[qctype]:
                    self.qcservices[qctype][poc] = {}
                cat = service.getCategoryTitle()
                if cat not in self.qcservices[qctype][poc]:
                    self.qcservices[qctype][poc][cat] = []
                # if service not in self.qcservices[qctype][poc][cat]:
                self.qcservices[qctype][poc][cat].append(
                    {'service': service,
                     'analysis': qcanalysis})

            # Create the html report
            ar_results = safe_unicode(self.template()).encode('utf-8')
            if out_path:
                open(join(out_path, out_fn + ".html"), "w").write(ar_results)

            # Create the pdf report (will always be attached to the AR)
            pdf_outfile = join(out_path, out_fn + ".pdf") if out_path else None
            pdf_css = resource_filename(
                "bika.lims", "skins/bika/analysisrequest_results_pdf.css")
            ar_css = join(self.portal_url, "analysisrequest_results.css")
            ar_results = ar_results.replace(ar_css, pdf_css)
            pdf_report = createPdf(ar_results, pdf_outfile, css=pdf_css)

            if pdf_report:
                reportid =  self.context.generateUniqueId('ARReport')
                ar.invokeFactory(id=reportid, type_name="ARReport")
                report = ar._getOb(reportid)
                report.edit(
                    AnalysisRequest=ar.UID(),
                    Pdf=pdf_report,
                    Html=ar_results,
                    Recipients=[{'UID': self.contact.UID(),
                                'Username': self.contact.getUsername(),
                                'Fullname': self.contact.getFullname(),
                                'EmailAddress': self.contact.getEmailAddress(),
                                'PublicationModes': self.pub_pref
                                 }]
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
                            (encode_header(laboratory.getName()),
                             laboratory.getEmailAddress()))
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
                        if not debug_mode:
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
                                (encode_header(laboratory.getName()),
                                 laboratory.getEmailAddress()))
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
                        if not debug_mode:
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
        return [p.getObject().Title() for p in uc(UID=uids)]

    def get_recipients(self, ar):
        """ Return an array with the recipients and all its publication prefs
        """
        recips = []

        # Contact and CC's
        contact = ar.getContact()
        recips.append({'title': contact.Title(),
                       'email': contact.getEmailAddress(),
                       'pubpref': contact.getPublicationPreference()})
        for cc in ar.getCCContact():
            recips.append({'title': cc.Title(),
                           'email': cc.getEmailAddress(),
                           'pubpref': contact.getPublicationPreference()})

        return recips
