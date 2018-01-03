# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import os
import re
import tempfile
import traceback
from copy import copy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from operator import itemgetter
from smtplib import SMTPAuthenticationError
from smtplib import SMTPRecipientsRefused, SMTPServerDisconnected

import App
import transaction
from DateTime import DateTime
from Products.Archetypes.interfaces import IDateTimeField, IFileField, \
    ILinesField, IReferenceField, IStringField, ITextField
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import POINTS_OF_CAPTURE, bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView, ulocalized_time
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequest, IResultOutOfRange
from bika.lims.interfaces.field import IUIDReferenceField
from bika.lims.utils import attachPdf, createPdf, encode_header, \
    format_supsub, \
    isnumber
from bika.lims.utils import formatDecimalMark, to_utf8
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.vocabularies import getARReportTemplates
from bika.lims.workflow import wasTransitionPerformed
from plone.api.portal import get_registry_record
from plone.api.portal import set_registry_record
from plone.app.blob.interfaces import IBlobField
from plone.registry import Record
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.resource.utils import queryResourceDirectory
from zope.component import getAdapters, getUtility


class AnalysisRequestPublishView(BrowserView):
    template = ViewPageTemplateFile("templates/analysisrequest_publish.pt")
    _ars = []
    _arsbyclient = []
    _current_ar_index = 0
    _current_arsbyclient_index = 0
    _publish = False

    def __init__(self, context, request, publish=False):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request
        self._publish = publish
        self._ars = [self.context]
        self._digester = AnalysisRequestDigester()

    @property
    def _DEFAULT_TEMPLATE(self):
        registry = getUtility(IRegistry)
        return registry.get(
            'bika.lims.analysisrequest.default_arreport_template', 'default.pt')

    def next_certificate_number(self):
        """Get a new certificate id.  These are throwaway IDs, until the
        publication is actually done.  So each preview gives us a new ID.
        """
        key = 'bika.lims.current_coa_number'
        registry = getUtility(IRegistry)
        if key not in registry:
            registry.records[key] = \
                Record(field.Int(title=u"Current COA number"), 0)
        val = get_registry_record(key) + 1
        set_registry_record(key, val)
        return "%05d" % int(val)

    def __call__(self):
        if self.context.portal_type == 'AnalysisRequest':
            self._ars = [self.context]
        elif self.context.portal_type in ('AnalysisRequestsFolder', 'Client') \
                and self.request.get('items', ''):
            uids = self.request.get('items').split(',')
            uc = getToolByName(self.context, 'uid_catalog')
            self._ars = [obj.getObject() for obj in uc(UID=uids)]
        else:
            # Do nothing
            self.destination_url = self.request.get_header(
                "referer", self.context.absolute_url())

        # Group ARs by client
        groups = {}
        for ar in self._ars:
            idclient = ar.aq_parent.id
            if idclient not in groups:
                groups[idclient] = [ar]
            else:
                groups[idclient].append(ar)
        self._arsbyclient = [group for group in groups.values()]

        # Report may want to print current date
        self.current_date = self.ulocalized_time(DateTime(), long_format=True)

        # Do publish?
        if self.request.form.get('publish', '0') == '1':
            self.publishFromPOST()
        else:
            return self.template()

    def showOptions(self):
        """Returns true if the options top panel will be displayed
        in the template
        """
        return self.request.get('pub', '1') == '1'

    def getAvailableFormats(self):
        """Returns the available formats found in templates/reports
        """
        return getARReportTemplates()

    def getAnalysisRequests(self):
        """Returns a dict with the analysis requests to manage
        """
        return self._ars

    def getAnalysisRequestsCount(self):
        """Returns the number of analysis requests to manage
        """
        return len(self._ars)

    def getGroupedAnalysisRequestsCount(self):
        """Returns the number of groups of analysis requests to manage when
        a multi-ar template is selected. The ARs are grouped by client
        """
        return len(self._arsbyclient)

    def getAnalysisRequestObj(self):
        """Returns the analysis request objects to be managed
        """
        return self._ars[self._current_ar_index]

    def getAnalysisRequest(self, analysisrequest=None):
        """Returns the dict for the Analysis Request specified. If no AR set,
        returns the current analysis request
        """
        if analysisrequest:
            return self._digester(analysisrequest)
        else:
            return self._digester(self._ars[self._current_ar_index])

    def getAnalysisRequestGroup(self):
        """Returns the current analysis request group to be managed
        """
        return self._arsbyclient[self._current_arsbyclient_index]

    def getAnalysisRequestGroupData(self):
        """Returns an array that contains the dicts (ar_data) for each
        analysis request from the current group
        """
        return [self._digester(ar) for ar in self.getAnalysisRequestGroup()]

    def _nextAnalysisRequest(self):
        """Move to the next analysis request
        """
        if self._current_ar_index < len(self._ars):
            self._current_ar_index += 1

    def _nextAnalysisRequestGroup(self):
        """Move to the next analysis request group
        """
        if self._current_arsbyclient_index < len(self._arsbyclient):
            self._current_arsbyclient_index += 1

    def _renderTemplate(self):
        """Returns the html template to be rendered in accordance with the
        template specified in the request ('template' parameter)
        """
        templates_dir = 'templates/reports'
        embedt = self.request.form.get('template', self._DEFAULT_TEMPLATE)
        if embedt.find(':') >= 0:
            prefix, template = embedt.split(':')
            templates_dir = queryResourceDirectory('reports', prefix).directory
            embedt = template
        embed = ViewPageTemplateFile(os.path.join(templates_dir, embedt))
        return embedt, embed(self)

    def getReportTemplate(self):
        """Returns the html template for the current ar and moves to
        the next ar to be processed. Uses the selected template
        specified in the request ('template' parameter)
        """
        embedt = ""
        try:
            embedt, reptemplate = self._renderTemplate()
        except:
            tbex = traceback.format_exc()
            arid = self._ars[self._current_ar_index].id
            reptemplate = \
                "<div class='error-report'>%s - %s '%s':<pre>%s</pre></div>" \
                % (arid, _("Unable to load the template"), embedt, tbex)
        self._nextAnalysisRequest()
        return reptemplate

    def getGroupedReportTemplate(self):
        """Returns the html template for the current group of ARs and moves to
        the next group to be processed. Uses the selected template
        specified in the request ('template' parameter)
        """
        embedt = ""
        try:
            embedt, reptemplate = self._renderTemplate()
        except:
            tbex = traceback.format_exc()
            reptemplate = \
                "<div class='error-report'>%s '%s':<pre>%s</pre></div>" \
                % (_("Unable to load the template"), embedt, tbex)
        self._nextAnalysisRequestGroup()
        return reptemplate

    def getReportStyle(self):
        """Returns the css style to be used for the current template.
        If the selected template is 'default.pt', this method will
        return the content from 'default.css'. If no css file found
        for the current template, returns empty string
        """
        template = self.request.form.get('template', self._DEFAULT_TEMPLATE)
        content = ''
        if template.find(':') >= 0:
            prefix, template = template.split(':')
            resource = queryResourceDirectory('reports', prefix)
            css = '{0}.css'.format(template[:-3])
            if css in resource.listDirectory():
                content = resource.readFile(css)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, 'templates/reports/')
            path = '%s/%s.css' % (templates_dir, template[:-3])
            with open(path, 'r') as content_file:
                content = content_file.read()
        return content

    def isSingleARTemplate(self):
        seltemplate = self.request.form.get('template', self._DEFAULT_TEMPLATE)
        seltemplate = seltemplate.split(':')[-1].strip()
        return not seltemplate.lower().startswith('multi')

    def isQCAnalysesVisible(self):
        """Returns if the QC Analyses must be displayed
        """
        return self.request.form.get('qcvisible', '0').lower() in ['true', '1']

    def isHiddenAnalysesVisible(self):
        """Returns true if hidden analyses are visible
        """
        return self.request.form.get('hvisible', '0').lower() in ['true', '1']

    def isLandscape(self):
        """ Returns if the layout is landscape
        """
        return self.request.form.get('landscape', '0').lower() in ['true', '1']

    def localise_images(self, htmlreport):
        """WeasyPrint will attempt to retrieve attachments directly from the URL
        referenced in the HTML report, which may refer back to a single-threaded
        (and currently occupied) zeoclient, hanging it.  All "attachments"
        using urls ending with at_download/AttachmentFile must be converted
        to local files.

        Returns a list of files which were created, and a modified copy
        of htmlreport.
        """
        cleanup = []

        _htmltext = to_utf8(htmlreport)
        # first regular image tags
        for match in re.finditer(
                """http.*at_download/AttachmentFile""", _htmltext, re.I):
            url = match.group()
            att_path = url.replace(self.portal_url + "/", "")
            attachment = self.portal.unrestrictedTraverse(att_path)
            af = attachment.getAttachmentFile()
            filename = af.filename
            extension = "." + filename.split(".")[-1]
            outfile, outfilename = tempfile.mkstemp(suffix=extension)
            outfile = open(outfilename, 'wb')
            outfile.write(str(af.data))
            outfile.close()
            _htmltext.replace(url, outfilename)
            cleanup.append(outfilename)
        return cleanup, _htmltext

    def publishFromPOST(self):
        html = self.request.form.get('html')
        style = self.request.form.get('style')
        uids = self.request.form.get('uid').split(':')
        reporthtml = "<html><head>%s</head><body><div " \
                     "id='report'>%s</body></html>" % (style, html)
        publishedars = []
        for uid in uids:
            ars = self.publishFromHTML(
                uid, safe_unicode(reporthtml).encode('utf-8'))
            publishedars.extend(ars)
        return publishedars

    def publishFromHTML(self, aruid, results_html):
        # The AR can be published only and only if allowed
        uc = getToolByName(self.context, 'uid_catalog')
        ars = uc(UID=aruid)
        if not ars or len(ars) != 1:
            return []

        ar = ars[0].getObject()
        wf = getToolByName(self.context, 'portal_workflow')
        allowed_states = ['verified', 'published']
        # Publish/Republish allowed?
        if wf.getInfoFor(ar, 'review_state') not in allowed_states:
            # Pre-publish allowed?
            if not ar.getAnalyses(review_state=allowed_states):
                return []

        # HTML written to debug file
        debug_mode = App.config.getConfiguration().debug_mode
        if debug_mode:
            tmp_fn = tempfile.mktemp(suffix=".html")
            logger.debug("Writing HTML for %s to %s" % (ar.Title(), tmp_fn))
            open(tmp_fn, "wb").write(results_html)

        # Create the pdf report (will always be attached to the AR)
        # we must supply the file ourself so that createPdf leaves it alone.
        pdf_fn = tempfile.mktemp(suffix=".pdf")
        pdf_report = createPdf(htmlreport=results_html, outfile=pdf_fn)

        # PDF written to debug file
        if debug_mode:
            logger.debug("Writing PDF for %s to %s" % (ar.Title(), pdf_fn))
        else:
            os.remove(pdf_fn)

        recipients = []
        contact = ar.getContact()
        lab = ar.bika_setup.laboratory
        if pdf_report:
            if contact:
                recipients = [{
                    'UID': contact.UID(),
                    'Username': to_utf8(contact.getUsername()),
                    'Fullname': to_utf8(contact.getFullname()),
                    'EmailAddress': to_utf8(contact.getEmailAddress()),
                    'PublicationModes': contact.getPublicationPreference()
                }]
            reportid = ar.generateUniqueId('ARReport')
            report = _createObjectByType("ARReport", ar, reportid)
            report.edit(
                AnalysisRequest=ar.UID(),
                Pdf=pdf_report,
                Recipients=recipients
            )
            report.unmarkCreationFlag()
            renameAfterCreation(report)

            # Set status to prepublished/published/republished
            status = wf.getInfoFor(ar, 'review_state')
            transitions = {'verified': 'publish',
                           'published': 'republish'}
            transition = transitions.get(status, 'prepublish')
            try:
                wf.doActionFor(ar, transition)
            except WorkflowException:
                pass

            # compose and send email.
            # The managers of the departments for which the current AR has
            # at least one AS must receive always the pdf report by email.
            # https://github.com/bikalabs/Bika-LIMS/issues/1028
            mime_msg = MIMEMultipart('related')
            mime_msg['Subject'] = self.get_mail_subject(ar)[0]
            mime_msg['From'] = formataddr(
                (encode_header(lab.getName()), lab.getEmailAddress()))
            mime_msg.preamble = 'This is a multi-part MIME message.'
            msg_txt = MIMEText(results_html, _subtype='html')
            mime_msg.attach(msg_txt)

            to = []
            mngrs = ar.getResponsible()
            for mngrid in mngrs['ids']:
                name = mngrs['dict'][mngrid].get('name', '')
                email = mngrs['dict'][mngrid].get('email', '')
                if email:
                    to.append(formataddr((encode_header(name), email)))

            if len(to) > 0:
                # Send the email to the managers
                mime_msg['To'] = ','.join(to)
                attachPdf(mime_msg, pdf_report, ar.id)

                try:
                    host = getToolByName(self.context, 'MailHost')
                    host.send(mime_msg.as_string(), immediate=True)
                except SMTPServerDisconnected as msg:
                    logger.warn("SMTPServerDisconnected: %s." % msg)
                except SMTPRecipientsRefused as msg:
                    raise WorkflowException(str(msg))
                except SMTPAuthenticationError as msg:
                    logger.warn("SMTPAuthenticationFailed: %s." % msg)

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
                (encode_header(lab.getName()), lab.getEmailAddress()))
            mime_msg.preamble = 'This is a multi-part MIME message.'
            msg_txt = MIMEText(results_html, _subtype='html')
            mime_msg.attach(msg_txt)
            mime_msg['To'] = formatted

            # Attach the pdf to the email if requested
            if pdf_report and 'pdf' in recip.get('pubpref'):
                attachPdf(mime_msg, pdf_report, ar.id)

            # For now, I will simply ignore mail send under test.
            if hasattr(self.portal, 'robotframework'):
                continue

            msg_string = mime_msg.as_string()

            # content of outgoing email written to debug file
            if debug_mode:
                tmp_fn = tempfile.mktemp(suffix=".email")
                logger.debug(
                    "Writing MIME message for %s to %s" % (ar.Title(), tmp_fn))
                open(tmp_fn, "wb").write(msg_string)

            try:
                host = getToolByName(self.context, 'MailHost')
                host.send(msg_string, immediate=True)
            except SMTPServerDisconnected as msg:
                logger.warn("SMTPServerDisconnected: %s." % msg)
            except SMTPRecipientsRefused as msg:
                raise WorkflowException(str(msg))
            except SMTPAuthenticationError as msg:
                logger.warn("SMTPAuthenticationFailed: %s." % msg)

        return [ar]

    def publish(self):
        """Publish the AR report/s. Generates a results pdf file associated
        to each AR, sends an email with the report to the lab manager and
        sends a notification (usually an email with the PDF attached) to the
        AR's contact and CCs. Transitions each published AR to statuses
        'published', 'prepublished' or 'republished'. Returns a list with the
        AR identifiers that have been published/prepublished/republished
        (only those 'verified', 'published' or at least have one 'verified'
        result).
        """
        if len(self._ars) > 1:
            published_ars = []
            for ar in self._ars:
                arpub = AnalysisRequestPublishView(
                    ar, self.request, publish=True)
                ar = arpub.publish()
                published_ars.extend(ar)
            published_ars = [par.id for par in published_ars]
            return published_ars

        results_html = safe_unicode(self.template()).encode('utf-8')
        return self.publishFromHTML(results_html)

    def get_recipients(self, ar):
        """Returns a list with the recipients and all its publication prefs
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
                           'pubpref': cc.getPublicationPreference()})

        # CC Emails
        # https://github.com/senaite/bika.lims/issues/361
        plone_utils = getToolByName(self.context, "plone_utils")
        ccemails = map(lambda x: x.strip(), ar.getCCEmails().split(","))
        for ccemail in ccemails:
            # Better do that with a field validator
            if not plone_utils.validateSingleEmailAddress(ccemail):
                logger.warn(
                    "Skipping invalid email address '{}'".format(ccemail))
                continue
            recips.append({
                'title': ccemail,
                'email': ccemail,
                'pubpref': ('email', 'pdf',), })

        return recips

    def get_mail_subject(self, ar):
        """Returns the email subject in accordance with the client
        preferences
        """
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
            ais.append(ar.getId())
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
        line_items = []
        if ais:
            ais.sort()
            li = t(_('ARs: ${ars}', mapping={'ars': ', '.join(ais)}))
            line_items.append(li)
        if cos:
            cos.sort()
            li = t(_('Orders: ${orders}', mapping={'orders': ', '.join(cos)}))
            line_items.append(li)
        if crs:
            crs.sort()
            li = t(_(
                'Refs: ${references}', mapping={'references': ', '.join(crs)}))
            line_items.append(li)
        if css:
            css.sort()
            li = t(_(
                'Samples: ${samples}', mapping={'samples': ', '.join(css)}))
            line_items.append(li)
        tot_line = ' '.join(line_items)
        if tot_line:
            subject = t(_('Analysis results for ${subject_parts}',
                          mapping={'subject_parts': tot_line}))
            if blanks_found:
                subject += (' ' + t(_('and others')))
        else:
            subject = t(_('Analysis results'))
        return subject, tot_line

    def sorted_by_sort_key(self, category_keys):
        """Sort categories via catalog lookup on title. """
        bsc = getToolByName(self.context, "bika_setup_catalog")
        analysis_categories = bsc(
            portal_type="AnalysisCategory", sort_on="sortable_title")
        sort_keys = dict([(b.Title, "{:04}".format(a))
                          for a, b in enumerate(analysis_categories)])
        return sorted(category_keys,
                      key=lambda title, sk=sort_keys: sk.get(title))

    def getAnaysisBasedTransposedMatrix(self, ars):
        """Returns a dict with the following structure:
        {'category_1_name':
            {'service_1_title':
                {'service_1_uid':
                    {'service': <AnalysisService-1>,
                     'ars': {'ar1_id': [<Analysis (for as-1)>,
                                       <Analysis (for as-1)>],
                             'ar2_id': [<Analysis (for as-1)>]
                            },
                    },
                },
            {'service_2_title':
                 {'service_2_uid':
                    {'service': <AnalysisService-2>,
                     'ars': {'ar1_id': [<Analysis (for as-2)>,
                                       <Analysis (for as-2)>],
                             'ar2_id': [<Analysis (for as-2)>]
                            },
                    },
                },
            ...
            },
        }
        """
        analyses = {}
        for ar in ars:
            ans = [an.getObject() for an in ar.getAnalyses()]
            for an in ans:
                cat = an.getCategoryTitle()
                an_title = an.Title()
                if cat not in analyses:
                    analyses[cat] = {
                        an_title: {
                            # The report should not mind receiving 'an'
                            # here - service fields are all inside!
                            'service': an,
                            'accredited': an.getAccredited(),
                            'ars': {ar.id: an.getFormattedResult()}
                        }
                    }
                elif an_title not in analyses[cat]:
                    analyses[cat][an_title] = {
                        'service': an,
                        'accredited': an.getAccredited(),
                        'ars': {ar.id: an.getFormattedResult()}
                    }
                else:
                    d = analyses[cat][an_title]
                    d['ars'][ar.id] = an.getFormattedResult()
                    analyses[cat][an_title] = d
        return analyses

    def _lab_address(self, lab):
        lab_address = lab.getPostalAddress() \
                      or lab.getBillingAddress() \
                      or lab.getPhysicalAddress()
        return _format_address(lab_address)

    def explode_data(self, data, padding=''):
        out = ''
        for k, v in data.items():
            if type(v) is dict:
                pad = '%s&nbsp;&nbsp;&nbsp;&nbsp;' % padding
                exploded = self.explode_data(v, pad)
                out = "%s<br/>%s'%s':{%s}" % (out, padding, str(k), exploded)
            elif type(v) is list:
                out = "%s<br/>%s'%s':[]" % (out, padding, str(k))
            elif type(v) is str:
                out = "%s<br/>%s'%s':''" % (out, padding, str(k))
        return out

    def currentDate(self):
        """
        This method returns the current time. It is useful if you want to
        get the current time in a report.
        :return: DateTime()
        """
        return DateTime()


class AnalysisRequestDigester:
    """Read AR data which could be useful during publication, into a data
    dictionary. This class should be instantiated once, and the instance
    called for all subsequent digestion.  This allows the instance to cache
    data for objects that may be read multiple times for different ARs.

    Passing overwrite=True when calling the instance will cause the
    ar.Digest field to be overwritten with a new digestion.  This flag
    is set True by default in the EndRequestHandler that is responsible for
    automated re-building.

    It should be run once when the AR is verified (or when a verified AR is
    modified) to pre-digest the data so that AnalysisRequestPublishView will
    run a little faster.

    Note: ProxyFields are not included in the reading of the schema.  If you
    want to access sample fields in the report template, you must refer
    directly to the correct field in the Sample data dictionary.

    Note: ComputedFields are removed from the schema while creating the dict.
    XXX: Add all metadata columns for the AR into the dict.

    """

    def __init__(self):
        # By default we don't care about these schema fields when creating
        # dictionaries from the schemas of objects.
        self.SKIP_FIELDNAMES = [
            'allowDiscussion', 'subject', 'location', 'contributors',
            'creators', 'effectiveDate', 'expirationDate', 'language', 'rights',
            'relatedItems', 'modification_date', 'immediatelyAddableTypes',
            'locallyAllowedTypes', 'nextPreviousEnabled', 'constrainTypesMode',
            'RestrictedCategories', 'Digest',
        ]

    def __call__(self, ar, overwrite=False):
        # cheating
        self.context = ar
        self.request = ar.REQUEST

        # if AR was previously digested, use existing data (if exists)
        verified = wasTransitionPerformed(ar, 'verify')
        if not overwrite and verified:
            # Prevent any error related with digest
            data = ar.getDigest() if hasattr(ar, 'getDigest') else {}
            if data:
                # Check if the department managers have changed since
                # verification:
                saved_managers = data.get('managers', {})
                saved_managers_ids = set(saved_managers.get('ids', []))
                current_managers = self.context.getManagers()
                current_managers_ids = set([man.getId() for man in
                                            current_managers])
                # The symmetric difference of two sets A and B is the set of
                # elements which are in either of the sets A or B but not
                # in both.
                are_different = saved_managers_ids.symmetric_difference(
                    current_managers_ids)
                if len(are_different) == 0:
                    # Seems that sometimes the 'obj' is wrong in the saved
                    # data.
                    data['obj'] = ar
                    # Always set results interpretation
                    self._set_results_interpretation(ar, data)
                    return data

        logger.info("=========== creating new data for %s" % ar)

        # Set data to the AR schema field, and return it.
        data = self._ar_data(ar)
        if hasattr(ar, 'setDigest'):
            ar.setDigest(data)
        logger.info("=========== new data for %s created." % ar)
        return data

    def _schema_dict(self, instance, skip_fields=None, recurse=True):
        """Return a dict of all mutated field values for all schema fields.
        This isn't used, as right now the digester just uses old code directly
        for BBB purposes.  But I'm keeping it here for future use.
        :param instance: The item who's schema will be exploded into a dict.
        :param skip_fields: A list of fieldnames which will not be rendered.
        :param recurse: If true, reference values will be recursed into.
        """
        data = {
            'obj': instance,
        }

        fields = instance.Schema().fields()
        for fld in fields:
            fieldname = fld.getName()
            if fieldname in self.SKIP_FIELDNAMES \
                    or (skip_fields and fieldname in skip_fields) \
                    or fld.type == 'computed':
                continue

            rawvalue = fld.get(instance)

            if rawvalue is True or rawvalue is False:
                # Booleans are special; we'll str and return them.
                data[fieldname] = str(rawvalue)

            elif rawvalue is 0:
                # Zero is special: it's false-ish, but the value is important.
                data[fieldname] = 0

            elif not rawvalue:
                # Other falsy values can simply return an empty string.
                data[fieldname] = ''

            elif fld.type == 'analyses':
                # AR.Analyses field is handled separately of course.
                data[fieldname] = ''

            elif IDateTimeField.providedBy(fld):
                # Date fields get stringed to rfc8222
                data[fieldname] = rawvalue.rfc822() if rawvalue else ''

            elif IReferenceField.providedBy(fld) \
                    or IUIDReferenceField.providedBy(fld):
                # mutate all reference targets into dictionaries
                # Assume here that allowed_types excludes incompatible types.
                if recurse and fld.multiValued:
                    v = [self._schema_dict(x, recurse=False) for x in rawvalue]
                elif recurse and not fld.multiValued:
                    v = self._schema_dict(rawvalue, recurse=False)
                elif not recurse and fld.multiValued:
                    v = [val.Title() for val in rawvalue if val]
                else:
                    v = rawvalue.Title() if rawvalue else ''
                data[fieldname] = v

                # Include a [fieldname]Title[s] field containing the title
                # or titles of referenced objects.
                if fld.multiValued:
                    data[fieldname + "Titles"] = [x.Title() for x in rawvalue]
                else:
                    data[fieldname + "Title"] = rawvalue.Title()

            # Text/String comes after UIDReferenceField.
            elif ITextField.providedBy(fld) or IStringField.providedBy(fld):
                rawvalue = str(rawvalue).strip()
                data[fieldname] = rawvalue

            # FileField comes after StringField.
            elif IFileField.providedBy(fld) or IBlobField.providedBy(fld):
                # We ignore file field values; we'll add the ones we want.
                data[fieldname] = ''

            elif ILinesField.providedBy(fld):
                # LinesField turns into a single string of lines
                data[fieldname] = "<br/>".join(rawvalue)

            elif fld.type == 'record':
                # Record returns a dictionary.
                data[fieldname] = rawvalue

            elif fld.type == 'records':
                # Record returns a list of dictionaries.
                data[fieldname] = rawvalue

            elif fld.type == 'address':
                # This is just a Record field
                data[fieldname + "_formatted"] = _format_address(rawvalue)
                # Also include un-formatted address
                data[fieldname] = rawvalue

            elif fld.type == 'duration':
                # Duration returns a formatted string like 1d 3h 1m.
                data[fieldname + "_formatted"] = \
                    ' '.join(["%s%s" % (rawvalue[key], key[0])
                              for key in ('days', 'hours', 'minutes')])
                # Also include unformatted duration.
                data[fieldname] = rawvalue

            else:
                data[fieldname] = rawvalue

        return data

    def getDimension(self):
        """ Returns the dimension of the report
        """
        return self.request.form.get("layout", "A4")

    def isLandscape(self):
        """ Returns if the layout is landscape
        """
        return self.request.form.get('landscape', '0').lower() in ['true', '1']

    def getDirection(self):
        """ Return landscape or horizontal
        """
        return self.isLandscape() and "landscape" or "horizontal"

    def getLayout(self):
        """ Returns the layout of the report
        """
        mapping = {
            "A4": (210, 297),
            "letter": (216, 279)
        }
        dimension = self.getDimension()
        layout = mapping.get(dimension, mapping.get("A4"))
        if self.isLandscape():
            layout = tuple(reversed(layout))
        return layout

    def _workflow_data(self, instance):
        """Add some workflow information for all actions performed against
        this instance. Only values for the last action event for any
        transition will be set here, previous transitions will be ignored.

        The default format for review_history is a list of lists; this function
        returns rather a dictionary of dictionaries, keyed by action_id
        """
        workflow = getToolByName(self.context, 'portal_workflow')
        history = copy(list(workflow.getInfoFor(instance, 'review_history')))
        data = {e['action']: {
            'actor': e['actor'],
            'time': ulocalized_time(e['time'], long_format=True)
        } for e in history if e['action']}
        return data

    def _ar_data(self, ar, excludearuids=None):
        """ Creates an ar dict, accessible from the view and from each
            specific template.
        """
        if not excludearuids:
            excludearuids = []
        bs = ar.bika_setup
        data = {'obj': ar,
                'id': ar.getId(),
                'client_order_num': ar.getClientOrderNumber(),
                'client_reference': ar.getClientReference(),
                'client_sampleid': ar.getClientSampleID(),
                'adhoc': ar.getAdHoc(),
                'composite': ar.getComposite(),
                'report_drymatter': ar.getReportDryMatter(),
                'invoice_exclude': ar.getInvoiceExclude(),
                'date_received': ulocalized_time(ar.getDateReceived(),
                                                 long_format=1),
                'member_discount': ar.getMemberDiscount(),
                'date_sampled': ulocalized_time(
                    ar.getDateSampled(), long_format=1),
                'date_published': ulocalized_time(DateTime(), long_format=1),
                'invoiced': ar.getInvoiced(),
                'late': ar.getLate(),
                'subtotal': ar.getSubtotal(),
                'vat_amount': ar.getVATAmount(),
                'totalprice': ar.getTotalPrice(),
                'invalid': ar.isInvalid(),
                'url': ar.absolute_url(),
                'remarks': to_utf8(ar.getRemarks()),
                'footer': to_utf8(bs.getResultFooter()),
                'prepublish': False,
                'child_analysisrequest': None,
                'parent_analysisrequest': None,
                'resultsinterpretation':ar.getResultsInterpretation(),
                'ar_attachments': self._get_ar_attachments(ar),
                'an_attachments': self._get_an_attachments(ar),
        }

        # Sub-objects
        excludearuids.append(ar.UID())
        puid = ar.getRawParentAnalysisRequest()
        if puid and puid not in excludearuids:
            data['parent_analysisrequest'] = self._ar_data(
                ar.getParentAnalysisRequest(), excludearuids)
        cuid = ar.getRawChildAnalysisRequest()
        if cuid and cuid not in excludearuids:
            data['child_analysisrequest'] = self._ar_data(
                ar.getChildAnalysisRequest(), excludearuids)

        wf = ar.portal_workflow
        allowed_states = ['verified', 'published']
        data['prepublish'] = wf.getInfoFor(ar,
                                           'review_state') not in allowed_states

        data['contact'] = self._contact_data(ar)
        data['client'] = self._client_data(ar)
        data['sample'] = self._sample_data(ar)
        data['batch'] = self._batch_data(ar)
        data['specifications'] = self._specs_data(ar)
        data['analyses'] = self._analyses_data(ar, ['verified', 'published'])
        data['qcanalyses'] = self._qcanalyses_data(ar,
                                                   ['verified', 'published'])
        data['points_of_capture'] = sorted(
            set([an['point_of_capture'] for an in data['analyses']]))
        data['categories'] = sorted(
            set([an['category'] for an in data['analyses']]))
        data['haspreviousresults'] = len(
            [an['previous_results'] for an in data['analyses'] if
             an['previous_results']]) > 0
        data['hasblanks'] = len([an['reftype'] for an in data['qcanalyses'] if
                                 an['reftype'] == 'b']) > 0
        data['hascontrols'] = len([an['reftype'] for an in data['qcanalyses'] if
                                   an['reftype'] == 'c']) > 0
        data['hasduplicates'] = len(
            [an['reftype'] for an in data['qcanalyses'] if
             an['reftype'] == 'd']) > 0

        # Categorize analyses
        data['categorized_analyses'] = {}
        data['department_analyses'] = {}
        for an in data['analyses']:
            poc = an['point_of_capture']
            cat = an['category']
            pocdict = data['categorized_analyses'].get(poc, {})
            catlist = pocdict.get(cat, [])
            catlist.append(an)
            pocdict[cat] = catlist
            data['categorized_analyses'][poc] = pocdict

            # Group by department too
            anobj = an['obj']
            dept = anobj.getDepartment()
            if dept:
                dept = dept.UID()
                dep = data['department_analyses'].get(dept, {})
                dep_pocdict = dep.get(poc, {})
                dep_catlist = dep_pocdict.get(cat, [])
                dep_catlist.append(an)
                dep_pocdict[cat] = dep_catlist
                dep[poc] = dep_pocdict
                data['department_analyses'][dept] = dep

        # Categorize qcanalyses
        data['categorized_qcanalyses'] = {}
        for an in data['qcanalyses']:
            qct = an['reftype']
            poc = an['point_of_capture']
            cat = an['category']
            qcdict = data['categorized_qcanalyses'].get(qct, {})
            pocdict = qcdict.get(poc, {})
            catlist = pocdict.get(cat, [])
            catlist.append(an)
            pocdict[cat] = catlist
            qcdict[poc] = pocdict
            data['categorized_qcanalyses'][qct] = qcdict

        data['reporter'] = self._reporter_data(ar)
        data['managers'] = self._managers_data(ar)

        portal = self.context.portal_url.getPortalObject()
        data['portal'] = {'obj': portal,
                          'url': portal.absolute_url()}
        data['laboratory'] = self._lab_data()

        # results interpretation
        data = self._set_results_interpretation(ar, data)

        return data

    def _get_attachment_info(self, attachment):
        attachment_file = attachment.getAttachmentFile()
        attachment_size = attachment.get_size()
        attachment_type = attachment.getAttachmentType()
        attachment_mime = attachment_file.getContentType()

        def get_kb_size():
            size = attachment_size / 1024
            if size < 1:
                return 1
            return size

        info = {
            "obj": attachment,
            "uid": attachment.UID(),
            "keywords": attachment.getAttachmentKeys(),
            "type": attachment_type and attachment_type.Title() or "",
            "file": attachment_file,
            "filename": attachment_file.filename,
            "filesize": attachment_size,
            "size": "{} Kb".format(get_kb_size()),
            "download": "{}/at_download/AttachmentFile".format(
                attachment.absolute_url()),
            "mimetype": attachment_mime,
            "title": attachment_file.Title(),
            "icon": attachment_file.icon(),
            "inline": "<embed src='{}/AttachmentFile' class='inline-attachment inline-attachment-{}'/>".format(
                attachment.absolute_url(), self.getDirection()),
            "renderoption": attachment.getReportOption(),
        }
        if attachment_mime.startswith("image"):
            info["inline"] = "<img src='{}/AttachmentFile' class='inline-attachment inline-attachment-{}'/>".format(
                attachment.absolute_url(), self.getDirection())
        return info

    def _sorted_attachments(self, ar, attachments=[]):
        """Sorter to return the attachments in the same order as the user
        defined in the attachments viewlet
        """
        inf = float("inf")
        view = ar.restrictedTraverse("attachments_view")
        order = view.get_attachments_order()

        def att_cmp(att1, att2):
            _n1 = att1.get('uid')
            _n2 = att2.get('uid')
            _i1 = _n1 in order and order.index(_n1) + 1 or inf
            _i2 = _n2 in order and order.index(_n2) + 1 or inf
            return cmp(_i1, _i2)

        return sorted(attachments, cmp=att_cmp)

    def _get_ar_attachments(self, ar):
        attachments = []
        for attachment in ar.getAttachment():
            # Skip attachments which have the (i)gnore flag set
            if attachment.getReportOption() == "i":
                continue
            attachments.append(self._get_attachment_info(attachment))

        return self._sorted_attachments(ar, attachments)

    def _get_an_attachments(self, ar):
        attachments = []
        for analysis in ar.getAnalyses(full_objects=True):
            for attachment in analysis.getAttachment():
                # Skip attachments which have the (i)gnore flag set
                if attachment.getReportOption() == "i":
                    continue
                attachments.append(self._get_attachment_info(attachment))
        return self._sorted_attachments(ar, attachments)

    def _batch_data(self, ar):
        data = {}
        batch = ar.getBatch()
        if batch:
            data = {'obj': batch,
                    'id': batch.id,
                    'url': batch.absolute_url(),
                    'title': to_utf8(batch.Title()),
                    'date': batch.getBatchDate(),
                    'client_batchid': to_utf8(batch.getClientBatchID()),
                    'remarks': to_utf8(batch.getRemarks())}

            uids = batch.Schema()['BatchLabels'].getAccessor(batch)()
            uc = getToolByName(self.context, 'uid_catalog')
            data['labels'] = [to_utf8(p.getObject().Title()) for p in
                              uc(UID=uids)]

        return data

    def _sample_data(self, ar):
        data = {}
        sample = ar.getSample()
        if sample:
            data = {'obj': sample,
                    'id': sample.id,
                    'url': sample.absolute_url(),
                    'client_sampleid': sample.getClientSampleID(),
                    'date_sampled': sample.getDateSampled(),
                    'sampling_date': sample.getSamplingDate(),
                    'sampler': self._sampler_data(sample),
                    'date_received': sample.getDateReceived(),
                    'composite': sample.getComposite(),
                    'date_expired': sample.getDateExpired(),
                    'date_disposal': sample.getDisposalDate(),
                    'date_disposed': sample.getDateDisposed(),
                    'adhoc': sample.getAdHoc(),
                    'remarks': sample.getRemarks(),
                    'sample_type': self._sample_type(sample),
                    'sample_point': self._sample_point(sample)}
        return data

    def _sampler_data(self, sample=None):
        data = {}
        if not sample or not sample.getSampler():
            return data
        sampler = sample.getSampler()
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getMemberById(sampler)
        if member:
            mfullname = member.getProperty('fullname')
            memail = member.getProperty('email')
            mhomepage = member.getProperty('home_page')
            pc = getToolByName(self.context, 'portal_catalog')
            contact = pc(portal_type='LabContact', getUsername=member.getId())
            # Only one LabContact should be found
            if len(contact) > 1:
                logger.warn(
                    "Incorrect number of user with the same "
                    "memberID. '{0}' users found with {1} as ID"
                    .format(len(contact), member.id))
            contact = contact[0].getObject() if contact else None
            cfullname = contact.getFullname() if contact else None
            cemail = contact.getEmailAddress() if contact else None
            physical_address = _format_address(
                contact.getPhysicalAddress()) if contact else ''
            postal_address =\
                    _format_address(contact.getPostalAddress())\
                if contact else ''
            data = {'id': member.id,
                    'fullname': to_utf8(cfullname) if cfullname else to_utf8(
                        mfullname),
                    'email': cemail if cemail else memail,
                    'business_phone': contact.getBusinessPhone() if contact else '',
                    'business_fax': contact.getBusinessFax() if contact else '',
                    'home_phone': contact.getHomePhone() if contact else '',
                    'mobile_phone': contact.getMobilePhone() if contact else '',
                    'job_title': to_utf8(contact.getJobTitle()) if contact else '',
                    'physical_address': physical_address,
                    'postal_address': postal_address,
                    'home_page': to_utf8(mhomepage)}
        return data

    def _sample_type(self, sample=None):
        data = {}
        sampletype = sample.getSampleType() if sample else None
        if sampletype:
            data = {'obj': sampletype,
                    'id': sampletype.id,
                    'title': sampletype.Title(),
                    'url': sampletype.absolute_url()}
        return data

    def _sample_point(self, sample=None):
        samplepoint = sample.getSamplePoint() if sample else None
        data = {}
        if samplepoint:
            data = {'obj': samplepoint,
                    'id': samplepoint.id,
                    'title': samplepoint.Title(),
                    'url': samplepoint.absolute_url()}
        return data

    def _lab_address(self, lab):
        lab_address = lab.getPostalAddress() \
                      or lab.getBillingAddress() \
                      or lab.getPhysicalAddress()
        return _format_address(lab_address)

    def _lab_data(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        lab = self.context.bika_setup.laboratory
        sv = lab.getSupervisor()
        sv = sv.getFullname() if sv else ""
        return {'obj': lab,
                'title': to_utf8(lab.Title()),
                'url': to_utf8(lab.getLabURL()),
                'supervisor': to_utf8(sv),
                'address': to_utf8(self._lab_address(lab)),
                'confidence': lab.getConfidence(),
                'accredited': lab.getLaboratoryAccredited(),
                'accreditation_body': to_utf8(lab.getAccreditationBody()),
                'accreditation_logo': lab.getAccreditationBodyLogo(),
                'logo': "%s/logo_print.png" % portal.absolute_url()}

    def _contact_data(self, ar):
        data = {}
        contact = ar.getContact()
        if contact:
            data = {'obj': contact,
                    'fullname': to_utf8(contact.getFullname()),
                    'email': to_utf8(contact.getEmailAddress()),
                    'pubpref': contact.getPublicationPreference()}
        return data

    def _client_data(self, ar):
        data = {}
        client = ar.aq_parent
        if client:
            data['obj'] = client
            data['id'] = client.id
            data['url'] = client.absolute_url()
            data['name'] = to_utf8(client.getName())
            data['phone'] = to_utf8(client.getPhone())
            data['fax'] = to_utf8(client.getFax())

            data['address'] = to_utf8(get_client_address(ar))
        return data

    def _specs_data(self, ar):
        data = {}
        specs = ar.getPublicationSpecification()
        if not specs:
            specs = ar.getSpecification()

        if specs:
            data['obj'] = specs
            data['id'] = specs.id
            data['url'] = specs.absolute_url()
            data['title'] = to_utf8(specs.Title())
            data['resultsrange'] = specs.getResultsRangeDict()

        return data

    def _analyses_data(self, ar, analysis_states=None):
        if not analysis_states:
            analysis_states = ['verified', 'published']
        analyses = []
        dm = ar.aq_parent.getDecimalMark()
        batch = ar.getBatch()
        workflow = getToolByName(self.context, 'portal_workflow')
        showhidden = self.isHiddenAnalysesVisible()

        catalog = getToolByName(self.context, CATALOG_ANALYSIS_LISTING)
        brains = catalog({'getRequestUID': ar.UID(),
                          'review_state': analysis_states,
                          'sort_on': 'sortable_title'})
        for brain in brains:
            an = brain.getObject()
            # Omit hidden analyses?
            if not showhidden and an.getHidden():
                continue

            # Build the analysis-specific dict
            andict = self._analysis_data(an, dm)

            # Are there previous results for the same AS and batch?
            andict['previous'] = []
            andict['previous_results'] = ""
            if batch:
                keyword = an.getKeyword()
                bars = [bar for bar in batch.getAnalysisRequests()
                        if an.aq_parent.UID() != bar.UID()
                        and keyword in bar]
                for bar in bars:
                    pan = bar[keyword]
                    pan_state = workflow.getInfoFor(pan, 'review_state')
                    if pan.getResult() and pan_state in analysis_states:
                        pandict = self._analysis_data(pan)
                        andict['previous'].append(pandict)

                andict['previous'] = sorted(
                    andict['previous'], key=itemgetter("capture_date"))
                andict['previous_results'] = ", ".join(
                    [p['formatted_result'] for p in andict['previous'][-5:]])

            analyses.append(andict)
        return analyses

    def _analysis_data(self, analysis, decimalmark=None):

        andict = {'obj': analysis,
                  'id': analysis.id,
                  'title': analysis.Title(),
                  'keyword': analysis.getKeyword(),
                  'scientific_name': analysis.getScientificName(),
                  'accredited': analysis.getAccredited(),
                  'point_of_capture': to_utf8(
                      POINTS_OF_CAPTURE.getValue(analysis.getPointOfCapture())),
                  'category': to_utf8(analysis.getCategoryTitle()),
                  'result': analysis.getResult(),
                  'isnumber': isnumber(analysis.getResult()),
                  'unit': to_utf8(analysis.getUnit()),
                  'formatted_unit': format_supsub(to_utf8(analysis.getUnit())),
                  'capture_date': analysis.getResultCaptureDate(),
                  'request_id': analysis.aq_parent.getId(),
                  'formatted_result': '',
                  'uncertainty': analysis.getUncertainty(),
                  'formatted_uncertainty': '',
                  'retested': analysis.getRetested(),
                  'remarks': to_utf8(analysis.getRemarks()),
                  'resultdm': to_utf8(analysis.getResultDM()),
                  'outofrange': False,
                  'type': analysis.portal_type,
                  'reftype': analysis.getReferenceType() \
                      if hasattr(analysis, 'getReferenceType') \
                      else None,
                  'worksheet': None,
                  'specs': {},
                  'formatted_specs': ''}

        if analysis.portal_type == 'DuplicateAnalysis':
            andict['reftype'] = 'd'

        ws = analysis.getBackReferences('WorksheetAnalysis')
        andict['worksheet'] = ws[0].id if ws and len(ws) > 0 else None
        andict['worksheet_url'] = ws[0].absolute_url() \
            if ws and len(ws) > 0 else None
        andict['refsample'] = analysis.getSample().id \
            if analysis.portal_type == 'Analysis' \
            else '%s - %s' % (analysis.aq_parent.id, analysis.aq_parent.Title())

        if analysis.portal_type == 'ReferenceAnalysis':
            # The analysis is a Control or Blank. We might use the
            # reference results instead other specs
            uid = analysis.getServiceUID()
            specs = analysis.aq_parent.getResultsRangeDict().get(uid, {})

        else:
            # Get the specs directly from the analysis. The getResultsRange
            # function already takes care about which are the specs to be used:
            # AR, client or lab.
            specs = analysis.getResultsRange()

        andict['specs'] = specs
        scinot = self.context.bika_setup.getScientificNotationReport()
        fresult = analysis.getFormattedResult(
            specs=specs, sciformat=int(scinot), decimalmark=decimalmark)

        # We don't use here cgi.encode because results fields must be rendered
        # using the 'structure' wildcard. The reason is that the result can be
        # expressed in sci notation, that may include <sup></sup> html tags.
        # Please note the default value for the 'html' parameter from
        # getFormattedResult signature is set to True, so the service will
        # already take into account LDLs and UDLs symbols '<' and '>' and escape
        # them if necessary.
        andict['formatted_result'] = fresult

        fs = ''
        if specs.get('min', None) and specs.get('max', None):
            fs = '%s - %s' % (specs['min'], specs['max'])
        elif specs.get('min', None):
            fs = '> %s' % specs['min']
        elif specs.get('max', None):
            fs = '< %s' % specs['max']
        andict['formatted_specs'] = formatDecimalMark(fs, decimalmark)
        andict['formatted_uncertainty'] = format_uncertainty(
            analysis, analysis.getResult(), decimalmark=decimalmark,
            sciformat=int(scinot))

        # Out of range?
        if specs:
            adapters = getAdapters((analysis,), IResultOutOfRange)
            for name, adapter in adapters:
                ret = adapter(specification=specs)
                if ret and ret['out_of_range']:
                    andict['outofrange'] = True
                    break
        return andict

    def _qcanalyses_data(self, ar, analysis_states=None):
        if not analysis_states:
            analysis_states = ['verified', 'published']
        analyses = []

        for an in ar.getQCAnalyses(review_state=analysis_states):

            # Build the analysis-specific dict
            andict = self._analysis_data(an)

            # Are there previous results for the same AS and batch?
            andict['previous'] = []
            andict['previous_results'] = ""

            analyses.append(andict)
        analyses.sort(
            lambda x, y: cmp(x.get('title').lower(), y.get('title').lower()))
        return analyses

    def _reporter_data(self, ar):
        data = {}
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        username = member.getUserName()
        data['username'] = username
        brains = [x for x in bsc(portal_type='LabContact')
                  if x.getObject().getUsername() == username]
        if brains:
            contact = brains[0].getObject()
            data['fullname'] = contact.getFullname()
            data['email'] = contact.getEmailAddress()
            sf = contact.getSignature()
            if sf:
                data['signature'] = sf.absolute_url() + "/Signature"
        else:
            data['signature'] = ''
            data['fullname'] = username
            data['email'] = ''

        return data

    def _managers_data(self, ar):
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
                final_depts += to_utf8(dept)
            managers['dict'][mngr]['departments'] = final_depts

        return managers

    def _set_results_interpretation(self, ar, data):
        """
        This function updates the 'results interpretation' data.
        :param ar: an AnalysisRequest object.
        :param data: The data dictionary.
        :return: The 'data' dictionary with the updated values.
        """
        # General interpretation
        data['resultsinterpretation'] = ar.getResultsInterpretation()
        # Interpretations by departments
        ri = {}
        if ar.getResultsInterpretationByDepartment(None):
            ri[''] = ar.getResultsInterpretationByDepartment(None)
        depts = ar.getDepartments()
        for dept in depts:
            ri[dept.Title()] = ar.getResultsInterpretationByDepartment(dept)
        data['resultsinterpretationdepts'] = ri
        return data

    def isHiddenAnalysesVisible(self):
        """Returns true if hidden analyses are visible
        """
        return self.request.form.get('hvisible', '0').lower() in ['true', '1']


def ARModifiedHandler(instance, event):
    """After any modification of an AR that has already been verified,
    re-populate the ar.Digest.
    """
    if IAnalysisRequest.providedBy(instance):
        if wasTransitionPerformed(instance, 'verify'):
            request = instance.REQUEST
            ars_to_digest = set(request.get('ars_to_digest', []))
            ars_to_digest.add(instance)
            request['ars_to_digest'] = ars_to_digest


def AnalysisAfterTransitionHandler(instance, event):
    """After a 'verify' transition on any analysis, we must set a flag in
    the request so that the AR is digested before the request terminates.
    We're doing it here so that the digestion happens only once at the end
    of the request, regardless of how many children were transitioned.
    """
    if event.transition and event.transition.id == 'verify':
        request = instance.REQUEST
        ar = instance.aq_parent
        ars_to_digest = set(request.get('ars_to_digest', []))
        ars_to_digest.add(ar)
        request['ars_to_digest'] = ars_to_digest


def EndRequestHandler(event):
    """At the end of the request, we check, to see if any pre-digestion is
    required, for any ars or analyses that were processed during the request.
    """
    request = event.request
    ars_to_digest = set(request.get('ars_to_digest', []))
    digester = AnalysisRequestDigester()
    if ars_to_digest:
        for ar in ars_to_digest:
            digester(ar, overwrite=True)
    # If this commit() is not here, then the data does not appear to be
    # saved.  IEndRequest happens outside the transaction?
    transaction.commit()


def get_client_address(context):
    if context.portal_type == 'AnalysisRequest':
        client = context.aq_parent
    else:
        client = context
    client_address = client.getPostalAddress()
    if not client_address:
        ar = context
        if not IAnalysisRequest.providedBy(ar):
            return ""
        # Data from the first contact
        contact = ar.getContact()
        if contact and contact.getBillingAddress():
            client_address = contact.getBillingAddress()
        elif contact and contact.getPhysicalAddress():
            client_address = contact.getPhysicalAddress()
    return _format_address(client_address)


def _format_address(address):
    """Takes a value from an AddressField, returns a div class=address
    with spans inside, containing the address field values.
    """
    addr = ''
    if address:
        # order of divs in output html
        keys = ['address', 'city', 'district', 'state', 'zip', 'country']
        addr = ''.join(["<span>%s</span>" % address.get(v) for v in keys
                        if address.get(v, None)])
    return "<div class='address'>%s</div>" % addr
