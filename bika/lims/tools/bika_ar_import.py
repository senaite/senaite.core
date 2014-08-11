from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from bika.lims.config import ManageAnalysisRequests
from bika.lims.tools import ToolFolder
import csv
from bika.lims.interfaces.tools import Ibika_ar_import
from zope.interface import implements

class bika_ar_import(UniqueObject, SimpleItem):
    """ ARImportTool """

    implements(Ibika_ar_import)

    security = ClassSecurityInfo()
    id = 'bika_ar_import'
    title = 'AR Import Tool'
    description = 'Imports Analysis Request Data.'
    meta_type = 'AR Import Tool'

    security.declareProtected(ManageAnalysisRequests, 'import_file')
    def import_file(self, csvfile, filename, client_id, state):
        import pdb; pdb.set_trace()
        slash = filename.rfind('\\')
        full_name = filename[slash + 1:]
        ext = full_name.rfind('.')
        if ext == -1:
            actual_name = full_name
        else:
            actual_name = full_name[:ext]
        log = []
        r = self.portal_catalog(portal_type = 'Client', id = client_id)
        if len(r) == 0:
            log.append('   Could not find Client %s' % client_id)
            return '\n'.join(log)
        client = r[0].getObject()
        workflow = getToolByName(self, 'portal_workflow')
        updateable_states = ['sample_received', 'assigned']
        reader = csv.reader(csvfile)
        samples = []
        sample_headers = None
        batch_headers = None
        row_count = 0
        sample_count = 0
        batch_remarks = []

        for row in reader:
            row_count = row_count + 1
            if not row: continue
            # a new batch starts
            if row_count == 1:
                if row[0] == 'Header':
                    continue
                else:
                    msg = '%s invalid batch header' % row
#                    transaction_note(msg)
                    return state.set(status = 'failure', portal_status_message = msg)
            if row_count == 2:
                msg = None
                if row[1] != 'Import':
                    msg = 'Invalid batch header - Import required in cell B2'
#                    transaction_note(msg)
                    return state.set(status = 'failure', portal_status_message = msg)
                full_name = row[2]
                ext = full_name.rfind('.')
                if ext == -1:
                    entered_name = full_name
                else:
                    entered_name = full_name[:ext]
                if entered_name.lower() != actual_name.lower():
                    msg = 'Actual filename, %s, does not match entered filename, %s' % (actual_name, row[2])
#                    transaction_note(msg)
                    return state.set(status = 'failure', portal_status_message = msg)

                batch_headers = row[0:]
                arimport_id = self.generateUniqueId('ARImport')
                client.invokeFactory(id = arimport_id, type_name = 'ARImport')
                arimport = client._getOb(arimport_id)
                arimport.processForm()
                continue
            if row_count == 3:
                sample_count = sample_count + 1
                sample_headers = row[9:]
                continue
            if row_count == 4:
                continue
            if row_count == 5:
                continue
            if row_count == 6:
                continue

            samples.append(row)

        pad = 8192 * ' '
        REQUEST = self.REQUEST
        REQUEST.RESPONSE.write(self.progress_bar(REQUEST = REQUEST))
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressType" value="Analysis request import">')
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressDone" value="Validating...">')
        REQUEST.RESPONSE.write(pad + '<input style="display: none;" id="inputTotal" value="%s">' % len(samples))

        row_count = 0
        next_id = self.generateUniqueId('ARImportItem', batch_size = len(samples))
        (prefix, next_num) = next_id.split('_')
        next_num = int(next_num)
        for sample in samples:
            row_count = row_count + 1
            REQUEST.RESPONSE.write(pad + '<input style="display: none;" name="inputProgress" value="%s">' % row_count)
            item_remarks = []
            analyses = []
            for i in range(9, len(sample)):
                if sample[i] != '1':
                    continue
                analyses.append(sample_headers[(i - 9)])
            if len(analyses) > 0:
                aritem_id = '%s_%s' % (prefix, (str(next_num)))
                arimport.invokeFactory(id = aritem_id, type_name = 'ARImportItem')
                aritem = arimport._getOb(aritem_id)
                aritem.processForm()
                aritem.edit(
                    SampleName = sample[0],
                    ClientRef = sample[1],
                    ClientSid = sample[2],
                    SampleDate = sample[3],
                    SampleType = sample[4],
                    PickingSlip = sample[5],
                    ReportDryMatter = sample[6],
                    )

                aritem.setRemarks(item_remarks)
                aritem.setAnalyses(analyses)
                next_num += 1

        arimport.edit(
            ImportOption = 'c',
            FileName = batch_headers[2],
            ClientTitle = batch_headers[3],
            ClientID = batch_headers[4],
            ContactID = batch_headers[5],
            CCContactID = batch_headers[6],
            CCEmails = batch_headers[7],
            OrderID = batch_headers[8],
            QuoteID = batch_headers[9],
            SamplePoint = batch_headers[10],
            Remarks = batch_remarks,
            Analyses = sample_headers,
            DateImported = DateTime(),
            )

        valid = self.validate_arimport_c(arimport)
        REQUEST.RESPONSE.write('<script>document.location.href="%s/client_arimports?portal_status_message=%s%%20imported"</script>' % (client.absolute_url(), arimport_id))


    security.declareProtected(ManageAnalysisRequests, 'import_file_s')
    def import_file_s(self, csvfile, client_id, state):

        log = []
        r = self.portal_catalog(portal_type = 'Client', id = client_id)
        if len(r) == 0:
            log.append('   Could not find Client %s' % client_id)
            return '\n'.join(log)
        client = r[0].getObject()
        workflow = getToolByName(self, 'portal_workflow')
        reader = csv.reader(csvfile)
        samples = []
        sample_headers = None
        batch_headers = None
        row_count = 0
        sample_count = 0
        batch_remarks = []
        in_footers = False
        last_rows = False
        temp_row = False
        temperature = ''

        for row in reader:
            row_count = row_count + 1
            if not row: continue

            if last_rows:
                continue
            if in_footers:
                continue
                if temp_row:
                    temperature = row[8]
                    temp_row = False
                    last_rows = True
                if row[8] == 'Temperature on Arrival:':
                    temp_row = True
                    continue

            if row_count > 11:
                if row[0] == '':
                    in_footers = True

            if row_count == 5:
                client_orderid = row[10]
                continue

            if row_count < 7:
                continue

            if row_count == 7:
                if row[0] != 'Client Name':
                    log.append('  Invalid file')
                    return '\n'.join(log)
                batch_headers = row[0:]
                arimport_id = self.generateUniqueId('ARImport')
                client.invokeFactory(id = arimport_id, type_name = 'ARImport')
                arimport = client._getOb(arimport_id)
                clientname = row[1]
                clientphone = row[5]
                continue

            if row_count == 8:
                clientaddress = row[1]
                clientfax = row[5]
                continue
            if row_count == 9:
                clientcity = row[1]
                clientemail = row[5]
                continue
            if row_count == 10:
                contact = row[1]
                ccemail = row[5]
                continue
            if row_count == 11:
                continue


            if not in_footers:
                samples.append(row)

        pad = 8192 * ' '
        REQUEST = self.REQUEST
        REQUEST.RESPONSE.write(self.progress_bar(REQUEST = REQUEST))
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressType" value="Analysis request import">')
        REQUEST.RESPONSE.write('<input style="display: none;" id="progressDone" value="Validating...">')
        REQUEST.RESPONSE.write(pad + '<input style="display: none;" id="inputTotal" value="%s">' % len(samples))

        row_count = 0
        for sample in samples:
            row_count = row_count + 1
            REQUEST.RESPONSE.write(pad + '<input style="display: none;" name="inputProgress" value="%s">' % row_count)

            profiles = []
            for profile in sample[6:8]:
                if profile != None:
                    profiles.append(profile.strip())

            analyses = []
            for analysis in sample[8:11]:
                if analysis != None:
                    analyses.append(analysis.strip())

            aritem_id = self.generateUniqueId('ARImportItem')
            arimport.invokeFactory(id = aritem_id, type_name = 'ARImportItem')
            aritem = arimport._getOb(aritem_id)
            aritem.edit(
                ClientRef = sample[0],
                ClientRemarks = sample[1],
                ClientSid = sample[2],
                SampleDate = sample[3],
                SampleType = sample[4],
                NoContainers = sample[5],
                AnalysisProfile = profiles,
                Analyses = analyses,
                )
            aritem.processForm()


        arimport.edit(
            ImportOption = 's',
            ClientTitle = clientname,
            ClientID = client_id,
            ClientPhone = clientphone,
            ClientFax = clientfax,
            ClientAddress = clientaddress,
            ClientCity = clientcity,
            ClientEmail = clientemail,
            ContactName = contact,
            CCEmails = ccemail,
            Remarks = batch_remarks,
            OrderID = client_orderid,
            Temperature = temperature,
            DateImported = DateTime(),
            )
        arimport.processForm()

        valid = self.validate_arimport_s(arimport)
        REQUEST.RESPONSE.write('<script>document.location.href="%s/client_arimports?portal_status_message=%s%%20imported"</script>' % (client.absolute_url(), arimport_id))

InitializeClass(bika_ar_import)
