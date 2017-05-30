# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
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
from DateTime import DateTime
from Products.Archetypes.interfaces import IDateTimeField, IFileField, \
    ILinesField, IReferenceField, IStringField, ITextField
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView, ulocalized_time
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequest, IResultOutOfRange
from bika.lims.utils import attachPdf, createPdf, encode_header
from bika.lims.utils import formatDecimalMark, to_utf8
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.vocabularies import getARReportTemplates
from plone.api.portal import get
from plone.api.portal import get_registry_record
from plone.api.portal import get_tool
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
        elif self.context.portal_type == 'AnalysisRequestsFolder' \
                and self.request.get('items', ''):
            uids = self.request.get('items').split(',')
            uc = get_tool('uid_catalog')
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
        uc = get_tool('uid_catalog')
        ars = uc(UID=aruid)
        if not ars or len(ars) != 1:
            return []

        ar = ars[0].getObject()
        wf = get_tool('portal_workflow')
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
                if email != '':
                    to.append(formataddr((encode_header(name), email)))

            if len(to) > 0:
                # Send the email to the managers
                mime_msg['To'] = ','.join(to)
                attachPdf(mime_msg, pdf_report, ar.id)

                try:
                    host = get_tool('MailHost')
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
                host = get_tool('MailHost')
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
                           'pubpref': contact.getPublicationPreference()})

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
        bsc = get_tool("bika_setup_catalog")
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
                cat = analysis.getCategoryTitle()
                an_title = analysis.Title()
                if cat not in analyses:
                    analyses[cat] = {
                        an_title: {
                            # The report should not mind receiving 'analysis'
                            # here - service fields are all inside!
                            'service': analysis,
                            'accredited': analysis.getAccredited(),
                            'ars': {ar.id: an.getFormattedResult()}
                        }
                    }
                elif an_title not in analyses[cat]:
                    analyses[cat][an_title] = {
                        'service': analysis,
                        'accredited': analysis.getAccredited(),
                        'ars': {ar.id: an.getFormattedResult()}
                    }
                else:
                    d = analyses[cat][an_title]
                    d['ars'][ar.id] = an.getFormattedResult()
                    analyses[cat][an_title] = d
        return analyses


# By default we don't care about these schema fields when creating
# dictionaries from the schema of objects.
SKIP_FIELDNAMES = [
    'allowDiscussion', 'subject', 'location', 'contributors', 'creators',
    'effectiveDate', 'expirationDate', 'language', 'rights', 'relatedItems',
    'modification_date', 'immediatelyAddableTypes', 'locallyAllowedTypes',
    'nextPreviousEnabled', 'constrainTypesMode', 'RestrictedCategories',
]


class AnalysisRequestDigester:
    """Read AR data which could be useful during publication, into a data
    dictionary. This class should be instantiated once, and the instance used 
    for all subsequent digestion.  This allows the instance to cache data for 
    objects that may be read multiple times for different ARs.
    
    Reads field values in a general way, to allow schema changes to be 
    represented here without modifying this code. Also include data for 
    associated objects, and previous results, etc.
    
    This is expensive!  It should be run once when the AR is verified
    (or when a verified AR is modified) to pre-digest the data so that
    AnalysisRequestPublishView will run a little faster.
    
    Note: ProxyFields are not included in the reading of the schema.  If you
    want to access sample fields in the report template, you must refer
    directly to the correct field in the Sample data dictionary.    
    """

    def __init__(self):
        # I will store dictionaries here for the schema values for all
        # objects that this instance digests. Then each object will be digested
        # only once in this request.
        self._cache = {}

    def __call__(self, ar):
        # if AR was previously digested, use existing data
        data = ar.getDigest()
        if data:
            return data

        # First include general schema field value handling
        data = self._schema_dict(ar)

        # Variables from workflow history
        data['review_history'] = self._workflow_data(ar)

        # Now individual fields that require treatment

        data['sub_total'] = ar.getSubtotal()
        data['vat_amount'] = ar.getVATAmount()
        data['total_price'] = ar.getTotalPrice()
        data['late'] = ar.getLate()
        data['invalid'] = ar.isInvalid()
        data['specifications'] = self._specs_data(ar)
        data['analyses'] = self._analyses_data(ar)
        data['qcanalyses'] = self._qcanalyses_data(ar)

        points_of_capture = [an['point_of_capture'] for an in data['analyses']]
        data['points_of_capture'] = sorted(set(points_of_capture))

        categories = set([an['category'] for an in data['analyses']])
        data['categories'] = sorted(categories)

        has_prevs = [an['previous_results'] for an in data['analyses']
                     if an['previous_results']]
        data['haspreviousresults'] = len(has_prevs) > 0

        blanks = [an['reftype'] for an in data['qcanalyses']
                  if an['reftype'] == 'b']
        controls = [an['reftype'] for an in data['qcanalyses']
                    if an['reftype'] == 'c']
        duplicates = [an['reftype'] for an in data['qcanalyses']
                      if an['reftype'] == 'd']
        data['hasblanks'] = len(blanks) > 0
        data['hascontrols'] = len(controls) > 0
        data['hasduplicates'] = len(duplicates) > 0

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
            dept = anobj.getService().getDepartment() \
                if anobj.getService() else None
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

        portal = get()
        bs = get_tool('bika_setup')
        data['portal'] = {'obj': portal,
                          'url': portal.absolute_url()}
        data['laboratory'] = self._schema_dict(bs.laboratory)

        # results interpretation
        ri = {}
        if ar.getResultsInterpretationByDepartment(None):
            ri[''] = ar.getResultsInterpretationByDepartment(None)
        depts = ar.getDepartments()
        for dept in depts:
            ri[dept.Title()] = ar.getResultsInterpretationByDepartment(dept)
        data['resultsinterpretationdepts'] = ri

        # Set data to the AR schema field, and return.
        ar.setDigest(data)
        return data

    def _schema_dict(self, instance, skip_fields=None):
        """Return a dict of all mutated field values for all schema fields.
        """
        uid = instance.UID()
        if uid in self._cache:
            return self._cache[uid]
        data = {}
        fields = instance.Schema().fields()
        for fld in fields:
            fieldname = fld.getName()
            if fieldname in SKIP_FIELDNAMES \
                    or (skip_fields and fieldname in skip_fields):
                continue
            if fld.type == 'computed':
                logger.info("skip computed field %s.%s" %
                            (instance.getId(), fieldname))
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
            elif ITextField.providedBy(fld) or IStringField.providedBy(fld):
                # Strings are returned without molestation
                data[fieldname] = rawvalue.strip()
            elif IFileField.providedBy(fld) or IBlobField.providedBy(fld):
                # We ignore file field values; we'll add the ones we want.
                data[fieldname] = ''
            elif IReferenceField.providedBy(fld):
                # mutate all reference targets into dictionaries
                # Assume here that allowed_types excludes incompatible types.
                data[fieldname] = [self._schema_dict(x) for x in rawvalue] \
                    if fld.multiValued else self._schema_dict(rawvalue)
                # Include a [fieldname]Title[s] field containing the title
                # or titles of referenced objects.
                if fld.multiValued:
                    data[fieldname + "Titles"] = [x.Title() for x in rawvalue]
                else:
                    data[fieldname + "Title"] = rawvalue.Title()
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
                data[fieldname + "_formatted"] = self._format_address(rawvalue)
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
                logger.warning("Using unmutated value for field {}: {}".format(
                    fld, rawvalue
                ))
                data[fieldname] = rawvalue
        self._cache[uid] = data
        return data

    def _workflow_data(self, instance):
        """Add some workflow information for all actions performed against 
        this instance. Only values for the last action event for any 
        transition will be set here, previous transitions will be ignored.

        The default format for review_history is a list of lists; this function
        returns rather a dictionary of dictionaries, keyed by action_id
        """
        workflow = get_tool('portal_workflow')
        history = copy(list(workflow.getInfoFor(instance, 'review_history')))
        data = {e['action']: {
            'actor': e['actor'],
            'time': ulocalized_time(e['time'], long_format=True)
        } for e in history if e['action']}
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

    def _analyses_data(self, ar, contentFilter=None):
        """Return data for analyses in the provided AR. contentFilter is 
        passed directly to the catalog. If contentFilter is not specified,
        or review_state is not present in the provided contentFilter,
        then review_state=['verified', 'published'] is used.
        """
        analyses = []
        batch = ar.getBatch()
        workflow = get_tool('portal_workflow')
        showhidden = ar.REQUEST.form.get('hvisible', '0').lower() \
                     in ['true', '1']

        if not contentFilter:
            contentFilter = {}
        if 'review_state' not in contentFilter:
            contentFilter['review_state'] = ['verified', 'published']

        for an in ar.getAnalyses(full_objects=True, **contentFilter):

            # Omit hidden analyses?
            if not showhidden:
                serv = an.getService()
                asets = ar.getAnalysisServiceSettings(serv.UID())
                if asets.get('hidden'):
                    # Hide analysis
                    continue

            # Build the analysis-specific dict
            andict = self._analysis_data(an)

            # Are there previous results for the same AS and batch?
            andict['previous'] = []
            andict['previous_results'] = ""
            review_state = contentFilter['review_state']
            if batch:
                keyword = an.getKeyword()
                bars = [bar for bar in batch.getAnalysisRequests()
                        if an.aq_parent.UID() != bar.UID()
                        and keyword in bar]
                for bar in bars:
                    pan = bar[keyword]
                    pan_state = workflow.getInfoFor(pan, 'review_state')
                    if pan.getResult() and pan_state in review_state:
                        pandict = self._analysis_data(pan)
                        andict['previous'].append(pandict)

                andict['previous'] = sorted(
                    andict['previous'], key=itemgetter("capture_date"))
                andict['previous_results'] = ", ".join(
                    [p['formatted_result'] for p in andict['previous'][-5:]])

            analyses.append(andict)
        return analyses

    def _analysis_data(self, analysis):

        decimalmark = analysis.aq_parent.aq_parent.getDecimalMark()
        andict = self._schema_dict(analysis)

        if analysis.portal_type == 'DuplicateAnalysis':
            andict['reftype'] = 'd'

        ws = analysis.getBackReferences('WorksheetAnalysis')
        andict['worksheet'] = ws[0].id if ws and len(ws) > 0 else None
        andict['worksheet_url'] = ws[0].absolute_url \
            if ws and len(ws) > 0 else None
        andict['refsample'] = analysis.getSample().id \
            if analysis.portal_type == 'Analysis' \
            else '%s - %s' % (analysis.aq_parent.id, analysis.aq_parent.Title())

        # Set analysis specs or reference results, depending on the type
        # of the analysis.
        if analysis.portal_type == 'ReferenceAnalysis':
            # We might use the reference results instead other specs
            uid = analysis.getServiceUID()
            specs = analysis.aq_parent.getResultsRangeDict().get(uid, {})

        else:
            # The getResultsRange function already takes care about which are
            #  the specs to be used: AR, client or lab.
            specs = analysis.getResultsRange()
        andict['specs'] = specs

        # We don't use here cgi.encode because results fields must be rendered
        # using the 'structure' wildcard. The reason is that the result can be
        # expressed in sci notation, that may include <sup></sup> html tags.
        # Please note the default value for the 'html' parameter from
        # getFormattedResult signature is set to True, so the service will
        # already take into account LDLs and UDLs symbols '<' and '>' and escape
        # them if necessary.
        bs = get_tool('bika_setup')
        scinot = bs.getScientificNotationReport()
        fresult = analysis.getFormattedResult(
            specs=specs, sciformat=int(scinot), decimalmark=decimalmark)
        andict['formatted_result'] = fresult

        # Formatted specs and formatted uncertainty.
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

    def _qcanalyses_data(self, ar, review_states=None):
        """Get QC Analyses data for the provided AR.  If no review_states
        are supplied, 
        """
        analyses = []
        if not review_states or not type(review_states) not in (list, tuple):
            review_states = ['verified', 'published']
        for an in ar.getQCAnalyses(review_state=review_states):
            # Build the analysis-specific dict
            andict = self._analysis_data(an)
            # Are there previous results for the same AS and batch?
            andict['previous'] = []
            andict['previous_results'] = ""
            analyses.append(andict)
        analyses.sort(key=itemgetter('title'))
        return analyses

    def _reporter_data(self):
        data = {}
        pm = get_tool('portal_membership')
        member = pm.getAuthenticatedMember()
        if member:
            username = member.getUserName()
            data['username'] = username
            bs = get_tool('bika_setup')
            brains = [x for x in bs(portal_type='LabContact')
                 if x.getObject().getUsername() == username]
            if brains:
                contact = brains[0].getObject()
                data.update(self._schema_dict(contact))

        return data

    def _managers_data(self, ar):
        managers = {'ids': [], 'dict': {}}
        departments = {}
        ar_mngrs = ar.getResponsible()
        for mid in ar_mngrs['ids']:
            new_depts = ar_mngrs['dict'][mid]['departments'].split(',')
            if mid in managers['ids']:
                for dept in new_depts:
                    if dept not in departments[mid]:
                        departments[mid].append(dept)
            else:
                departments[mid] = new_depts
                managers['ids'].append(mid)
                managers['dict'][mid] = ar_mngrs['dict'][mid]

        mngrs = departments.keys()
        for mngr in mngrs:
            final_depts = ''
            for dept in departments[mngr]:
                if final_depts:
                    final_depts += ', '
                final_depts += to_utf8(dept)
            managers['dict'][mngr]['departments'] = final_depts

        return managers

    def _format_address(self, address):
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


def AfterTransitionEventHandler(instance, event):
    """After a 'verify' transition on an AR, create a data dictionary
    in ar.Digest field containing all information required for publication.
    """
    if event.transition and event.transition.id == 'verify':
        digester = AnalysisRequestDigester()
        digester(instance)


def _verified(instance):
    """True if the 'verify' transition has ever been fired against instance.
    """
    workflow = get_tool('portal_workflow')
    review_history = list(workflow.getInfoFor(instance, 'review_history'))
    for event in review_history:
        if event['action'] == 'verify':
            return True


def ModifiedHandler(instance, event):
    """After any modification of an AR that has been verified, re-populate 
    the ar.Digest field containing all information required for publication.
    """
    if IAnalysisRequest.providedBy(instance) and _verified(instance):
        digester = AnalysisRequestDigester()
        digester(instance)
