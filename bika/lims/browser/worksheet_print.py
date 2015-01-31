# coding=utf-8
from bika.lims import bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.utils import to_utf8, createPdf
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
from zope.component import getAdapters
import glob, os, sys, traceback
import App
import Globals

class WorksheetPrintView(BrowserView):
    """ Print view for a worksheet. This view acts as a placeholder, so
        the user can select the preferred options (AR by columns, AR by
        rows, etc.) for printing. Both a print button and pdf button
        are shown.
    """

    template = ViewPageTemplateFile("worksheet/templates/worksheet_print.pt")
    _DEFAULT_TEMPLATE = 'ar_by_column.pt'
    _TEMPLATES_DIR = 'worksheet/templates/print'
    # Add-on folder to look for templates
    _TEMPLATES_ADDON_DIR = 'worksheets'
    _current_ws_index = 0
    _worksheets = []

    def __init__(self, context, request):
        super(WorksheetPrintView, self).__init__(context, request)
        self._worksheets = [self.context]


    def __call__(self):
        """ Entry point of WorksheetPrintView.
            If context.portal_type is a Worksheet, then the PrintView
            is initialized to manage only that worksheet. If the
            context.portal_type is a WorksheetFolder and there are
            items selected in the request (items param), the PrintView
            will show the preview for all the selected Worksheets.
            By default, returns a HTML-encoded template, but if the
            request contains a param 'pdf' with value 1, will flush a
            pdf for the worksheet.
        """

        if self.context.portal_type == 'Worksheet':
            self._worksheets = [self.context]

        elif self.context.portal_type == 'WorksheetFolder' \
            and self.request.get('items', ''):
            uids = self.request.get('items').split(',')
            uc = getToolByName(self.context, 'uid_catalog')
            self._worksheets = [obj.getObject() for obj in uc(UID=uids)]

        else:
            # Warn and redirect to referer
            logger.warning('WorksheetPrintView: type not allowed: %s' %
                            self.context.portal_type)
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())

        # Generate PDF?
        if self.request.form.get('pdf', '0') == '1':
            return self._flush_pdf()
        else:
            return self.template()

    def getWSTemplates(self):
        """ Returns a DisplayList with the available templates found in
            templates/worksheets
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        tempath = '%s/%s' % (templates_dir, '*.pt')
        templates = [t.split('/')[-1] for t in glob.glob(tempath)]
        out = []
        for template in templates:
            out.append({'id': template, 'title': template[:-3]})
        for templates_resource in iterDirectoriesOfType(self._TEMPLATES_ADDON_DIR):
            prefix = templates_resource.__name__
            templates = [tpl for tpl in templates_resource.listDirectory() if tpl.endswith('.pt')]
            for template in templates:
                out.append({
                    'id': '{0}:{1}'.format(prefix, template),
                    'title': '{0} ({1})'.format(template[:-3], prefix),
                })
        return out


    def renderWSTemplate(self):
        """ Returns the current worksheet rendered with the template
            specified in the request (param 'template').
            Moves the iterator to the next worksheet available.
        """
        templates_dir = self._TEMPLATES_DIR
        embedt = self.request.get('template', self._DEFAULT_TEMPLATE)
        if embedt.find(':') >= 0:
            prefix, embedt = embedt.split(':')
            templates_dir = queryResourceDirectory(self._TEMPLATES_ADDON_DIR, prefix).directory
        embed = ViewPageTemplateFile(os.path.join(templates_dir, embedt))
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except:
            tbex = traceback.format_exc()
            wsid = self._worksheets[self._current_ws_index].id
            reptemplate = "<div class='error-print'>%s - %s '%s':<pre>%s</pre></div>" % (wsid, _("Unable to load the template"), embedt, tbex)
        if self._current_ws_index < len(self._worksheets):
            self._current_ws_index += 1
        return reptemplate


    def getWorksheets(self):
        """ Returns the list of worksheets to be printed
        """
        return self._worksheets;


    def getWorksheet(self):
        """ Returns the current worksheet from the list. Returns None when
            the iterator reaches the end of the array.
        """
        ws = None
        if self._current_ws_index < len(self._worksheets):
            ws = self._ws_data(self._worksheets[self._current_ws_index])
        return ws


    def _lab_data(self):
        portal = self.context.portal_url.getPortalObject()
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

        return {'obj': lab,
                'title': to_utf8(lab.Title()),
                'url': to_utf8(lab.getLabURL()),
                'address': to_utf8(lab_address),
                'confidence': lab.getConfidence(),
                'accredited': lab.getLaboratoryAccredited(),
                'accreditation_body': to_utf8(lab.getAccreditationBody()),
                'accreditation_logo': lab.getAccreditationBodyLogo(),
                'logo': "%s/logo_print.jpg" % portal.absolute_url()}


    def _ws_data(self, ws):
        """ Creates an ws dict, accessible from the view and from each
            specific template.
        """
        data = {'obj': ws,
                'id': ws.id,
                'url': ws.absolute_url(),
                'template_title': ws.getWorksheetTemplateTitle(),
                'remarks': ws.getRemarks(),
                'date_printed': self.ulocalized_time(DateTime(), long_format=1),
                'date_created': self.ulocalized_time(ws.created(), long_format=1)}

        # Sub-objects
        # Analyses
        # Instrument

        data['createdby'] = self._createdby_data(ws)
        data['analyst'] = self._analyst_data(ws)
        data['printedby'] = self._printedby_data(ws)

        portal = self.context.portal_url.getPortalObject()
        data['portal'] = {'obj': portal,
                          'url': portal.absolute_url()}
        data['laboratory'] = self._lab_data()
        return data


    def _createdby_data(self, ws):
        username = ws.getOwner().getUserName()
        return {'username': username,
                'fullname': to_utf8(self.user_fullname(username)),
                'email': to_utf8(self.user_email(username))}

    def _analyst_data(self, ws):
        username = ws.getAnalyst();
        return {'username': username,
                'fullname': to_utf8(self.user_fullname(username)),
                'email': to_utf8(self.user_email(username))}


    def _printedby_data(self, ws):
        data = {}
        member = self.context.portal_membership.getAuthenticatedMember()
        if member:
            username = member.getUserName()
            data['username'] = username
            data['fullname'] = to_utf8(self.user_fullname(username))
            data['email'] = to_utf8(self.user_email(username))

            c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
                 if x.getObject().getUsername() == username]
            if c:
                sf = c[0].getObject().getSignature()
                if sf:
                    data['signature'] = sf.absolute_url() + "/Signature"

        return data


    def _flush_pdf():
        """ Generates a PDF using the current layout as the template and
            returns the chunk of bytes.
        """
        return ""
