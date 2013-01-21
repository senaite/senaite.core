from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from bika.lims.config import ManageAnalysisRequests
from bika.lims.tools import ToolFolder
from cStringIO import StringIO
import csv
from bika.lims.interfaces.tools import Ibika_ar_export
from zope.interface import implements

class bika_ar_export(UniqueObject, SimpleItem):
    """ ARExportTool """

    implements(Ibika_ar_export)

    security = ClassSecurityInfo()
    id = 'bika_ar_export'
    title = 'AR Export Tool'
    description = 'Exports Analysis Request Data.'
    meta_type = 'AR Export Tool'

    security.declareProtected(ManageAnalysisRequests, 'export_file')
    def export_file(self, info):
        plone_view = self.restrictedTraverse('@@plone')

        """ create the output file """
        delimiter = ','

        # make filename unique
        now = DateTime()
        filename = 'BikaResults%s.csv' % (now.strftime('%Y%m%d-%H%M%S'))

        if self.bika_setup.getARAttachmentOption() == 'n':
            allow_ar_attach = False
        else:
            allow_ar_attach = True

        if self.bika_setup.getAnalysisAttachmentOption() == 'n':
            allow_analysis_attach = False
        else:
            allow_analysis_attach = True

        # group the analyses
        analysisrequests = info['analysis_requests']
        ars = {}
        services = {}
        categories = {}
        dry_matter = 0
        for ar in analysisrequests:
            ar_id = ar.getId()
            ars[ar_id] = {}
            ars[ar_id]['Analyses'] = {}
            ars[ar_id]['Price'] = 0
            ars[ar_id]['Count'] = 0
            if ar.getReportDryMatter():
                dry_matter = 1
                ars[ar_id]['DM'] = True
            else:
                ars[ar_id]['DM'] = False


            analyses = {}
            # extract the list of analyses in this batch
            for analysis in ar.getPublishedAnalyses():
                ars[ar_id]['Price'] += analysis.getPrice()
                ars[ar_id]['Count'] += 1
                service = analysis.Title()
                analyses[service] = {}
                analyses[service]['AsIs'] = analysis.getResult()
                analyses[service]['DM'] = analysis.getResultDM() or None
                analyses[service]['attach'] = analysis.getAttachment() or []
                if not services.has_key(service):
                    service_obj = analysis.getService()
                    category = service_obj.getCategoryTitle()
                    category_uid = service_obj.getCategoryUID()

                    if not categories.has_key(category):
                        categories[category] = []
                    categories[category].append(service)
                    services[service] = {}
                    services[service]['unit'] = service_obj.getUnit()
                    services[service]['DM'] = service_obj.getReportDryMatter()
                    services[service]['DMOn'] = False
                    if allow_analysis_attach:
                        if service_obj.getAttachmentOption() == 'n':
                            services[service]['attach'] = False
                        else:
                            services[service]['attach'] = True
                if services[service]['DM'] == True \
                and ar.getReportDryMatter():
                    services[service]['DMOn'] = True

            ars[ar_id]['Analyses'] = analyses

        # sort by category and title
        c_array = categories.keys()
        c_array.sort(lambda x, y:cmp(x.lower(), y.lower()))

        client = analysisrequests[0].aq_parent
        client_id = client.getClientID()
        client_name = client.Title()

        contact = info['contact']
        contact_id = contact.getUsername()
        contact_name = contact.getFullname()

        rows = []

        # header labels
        header = ['Header', 'Import/Export', 'Filename', 'Client', \
                  'Client ID', 'Contact', 'Contact ID', 'CC Recipients', 'CCEmails']
        rows.append(header)

        # header values
        cc_contacts = [cc.getUsername() for cc in ar.getCCContact()]
        ccs = ', '.join(cc_contacts)
        header = ['Header Data', 'Export', filename, client_name, \
                  client_id, contact_name, contact_id, ccs, ar.getCCEmails(), \
                  '']
        rows.append(header)

        # category headers
        s_array = []
        header = ['', '', '', '', '', '', '', '', '', '', '']
        for cat_name in c_array:
            service_array = categories[cat_name]
            service_array.sort(lambda x, y:cmp(x.lower(), y.lower()))
            for service_name in service_array:
                header.append(cat_name)
                if services[service_name]['DMOn']:
                    header.append('')
                if services[service_name]['attach']:
                    header.append('')
            s_array.extend(service_array)
        rows.append(header)

        # column headers
        header = ['Samples', 'Order ID', 'Client Reference', 'Client SID', 'Sample Type', \
                  'Sample Point', 'Sampling Date', 'Bika Sample ID', \
                  'Bika AR ID', 'Date Received', 'Date Published']

        for service_name in s_array:
            if services[service_name]['unit']:
                analysis_service = '%s (%s)' % (service_name, services[service_name]['unit'])
            else:
                analysis_service = service_name
            if services[service_name]['DMOn']:
                analysis_service = '%s [As Fed]' % (analysis_service)
            header.append(analysis_service)
            if services[service_name]['DMOn']:
                analysis_dm = '%s [Dry]' % (service_name)
                header.append(analysis_dm)
            if services[service_name]['attach']:
                header.append('Attachments')
        count_cell = len(header)
        header.append('Total number of analyses')
        header.append('Price excl VAT')
        if allow_ar_attach:
            header.append('Attachments')


        rows.append(header)


        # detail lines
        total_count = 0
        total_price = 0
        count = 1
        for ar in analysisrequests:
            sample_num = 'Sample %s' % count
            ar_id = ar.getId()
            sample = ar.getSample()
            sample_id = sample.getId()
            sampletype = sample.getSampleType().Title()
            samplepoint = sample.getSamplePoint() and sample.getSamplePoint().Title() or ''
            datereceived = plone_view.toLocalizedTime(ar.getDateReceived(), \
                           long_format = 1)
            datepublished = plone_view.toLocalizedTime(ar.getDatePublished(), \
                           long_format = 1)
            if sample.getDateSampled():
                datesampled = plone_view.toLocalizedTime(sample.getDateSampled(), long_format = 1)
            else:
                datesampled = None

            # create detail line
            detail = [sample_num, ar.getClientOrderNumber(), \
                      sample.getClientReference(), sample.getClientSampleID(), sampletype, \
                      samplepoint, datesampled, sample_id, ar_id, \
                      datereceived, datepublished]

            for service_name in s_array:
                if ars[ar_id]['Analyses'].has_key(service_name):
                    detail.append(ars[ar_id]['Analyses'][service_name]['AsIs'])
                    if services[service_name]['DMOn']:
                        detail.append(ars[ar_id]['Analyses'][service_name]['DM'])
                    if allow_analysis_attach:
                        if services[service_name]['attach'] == True:
                            attachments = ''
                            for attach in ars[ar_id]['Analyses'][service_name]['attach']:
                                file = attach.getAttachmentFile()
                                fname = getattr(file, 'filename')
                                attachments += fname
                            detail.append(attachments)
                else:
                    detail.append(' ')
                    if services[service_name]['DMOn']:
                        detail.append(' ')
                    if services[service_name]['attach'] == True:
                        detail.append(' ')

            for i in range(len(detail), count_cell):
                detail.append('')
            detail.append(ars[ar_id]['Count'])
            detail.append(ars[ar_id]['Price'])
            total_count += ars[ar_id]['Count']
            total_price += ars[ar_id]['Price']

            if allow_ar_attach:
                attachments = ''
                for attach in ar.getAttachment():
                    file = attach.getAttachmentFile()
                    fname = getattr(file, 'filename')
                    if attachments:
                        attachments += ', '
                    attachments += fname
                detail.append(attachments)

            rows.append(detail)
            count += 1

        detail = []
        for i in range(count_cell - 1):
            detail.append('')
        detail.append('Total')
        detail.append(total_count)
        detail.append(total_price)
        rows.append(detail)

        #convert lists to csv string
        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter = delimiter, \
                quoting = csv.QUOTE_NONNUMERIC)
        assert(writer)

        writer.writerows(rows)
        result = ramdisk.getvalue()
        ramdisk.close()

        file_data = {}
        file_data['file'] = result
        file_data['file_name'] = filename
        return file_data

InitializeClass(bika_ar_export)
