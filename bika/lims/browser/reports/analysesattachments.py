from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import formatDateQuery, formatDateParms, logged_in_client
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class AnalysesAttachments(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        # get all the data into datalines

        pc = getToolByName(self.context, 'portal_catalog')
        sc = getToolByName(self.context, 'bika_setup_catalog')
        bc = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        localTimeFormat = self.context.portal_properties.site_properties.getProperty('localTimeFormat')
        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        headings['header'] = _("Attachments")
        headings['subheader'] = _("The attachments linked to analysis requests and analyses")

        count_all = 0
        query = {'portal_type': 'Attachment'}
        if self.request.form.has_key('getClientUID'):
            client_uid = self.request.form['getClientUID']
            query['getClientUID'] = client_uid
            client = rc.lookupObject(client_uid)
            client_title = client.Title()
        else:
            client = logged_in_client(self.context)
            if client:
                client_title = client.Title()
                query['getClientUID'] = client.UID()
            else:
                client_title = 'Undefined'
        parms.append(
            { 'title': _('Client'),
             'value': client_title,
             'type': 'text'})

        date_query = formatDateQuery(self.context, 'DateLoaded')
        if date_query:
            query['getDateLoaded'] = date_query
            loaded = formatDateParms(self.context, 'DateLoaded')
        else:
            loaded = 'Undefined'
        parms.append(
            { 'title': _('Loaded'),
             'value': loaded,
             'type': 'text'})


        # and now lets do the actual report lines
        formats = {'columns': 6,
                   'col_heads': [ _('Request'), \
                                  _('File'), \
                                  _('Attachment type'), \
                                  _('Content type'), \
                                  _('Size'), \
                                  _('Loaded'), \
                                  ],
                   'class': '',
                  }

        datalines = []
        attachments = pc(query)
        for a_proxy in attachments:
            attachment = a_proxy.getObject()
            attachment_file = attachment.getAttachmentFile()
            icon = attachment_file.getBestIcon()
            filename = attachment_file.filename
            filesize = attachment_file.get_size()
            filesize = filesize / 1024
            sizeunit = "Kb"
            if filesize > 1024:
                filesize = filesize / 1024
                sizeunit = "Mb"
            dateloaded = attachment.getDateLoaded()
            dataline = []
            dataitem = {'value': attachment.getTextTitle()}
            dataline.append(dataitem)
            dataitem = {'value': filename,
                        'img_before': icon}
            dataline.append(dataitem)
            dataitem = {'value': attachment.getAttachmentType().Title()}
            dataline.append(dataitem)
            dataitem = {'value': self.context.lookupMime(attachment_file.getContentType())}
            dataline.append(dataitem)
            dataitem = {'value': '%s%s' %(filesize, sizeunit)}
            dataline.append(dataitem)
            dataitem = {'value': dateloaded.asdatetime().strftime(localTimeFormat)}
            dataline.append(dataitem)


            datalines.append(dataline)

            count_all += 1

        # footer data
        footlines = []
        footline = []
        footitem = {'value': _('Total'),
                    'colspan': 5,
                    'class': 'total_label'}
        footline.append(footitem)
        footitem = {'value': count_all}
        footline.append(footitem)
        footlines.append(footline)


        self.report_content = {
                'headings': headings,
                'parms': parms,
                'formats': formats,
                'datalines': datalines,
                'footings': footlines}


        return self.template()



