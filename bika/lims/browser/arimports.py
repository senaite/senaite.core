from bika.lims import logger, bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IClient
from bika.lims.utils import tmpID
from collective.progressbar.events import InitialiseProgressBar
from collective.progressbar.events import ProgressBar
from collective.progressbar.events import ProgressState
from collective.progressbar.events import UpdateProgressEvent
from DateTime import DateTime
from plone.app.content.browser.interfaces import IContentsPage
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest
from zope.event import notify
from zope.interface import implements, alsoProvides

import csv
import os
import plone


class ARImportView(BrowserView):
    implements(IViewView)

    def __init__(self, context, request):
        alsoProvides(request, IContentsPage)
        super(ARImportView, self).__init__(context, request)

    def getImportOption(self):
        return self.context.getImportOption()

    def getDateImported(self):
        dt = self.context.getDateImported()
        if dt:
            plone_view = self.context.restrictedTraverse('@@plone')
            return plone_view.toLocalizedTime(dt, long_format=1)

    def getDateApplied(self):
        dt = self.context.getDateApplied()
        if dt:
            plone_view = self.context.restrictedTraverse('@@plone')
            return plone_view.toLocalizedTime(dt, long_format=1)

    def validate_arimport(self):
        """ validate the current ARImport object """
        request = self.request
        arimport = self.context
        if arimport.getImportOption() in ('c', 'p'):
            valid = arimport.validateIt()
            if not valid:
                msg = 'AR Import invalid'
                IStatusMessage(request).addStatusMessage(_(msg), "error")
        else:
            msg = 'validation not yet implemented'
            IStatusMessage(request).addstatusmessage(_(msg), "error")
        request.response.redirect('%s/view' % arimport.absolute_url())

    def isSubmitted(self):
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(
            self.context.aq_parent, 'review_state') == 'submitted'


class BaseARImportsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(BaseARImportsView, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', 1)

        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'ARImport',
            'sort_on': 'sortable_title',
        }
        self.context_actions = {}
        if IClient.providedBy(self.context):
            self.context_actions = \
                {_('AR Import'):
                     {'url': 'arimport_add',
                      'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50
        self.form_id = "arimports"

        self.icon = \
            self.portal_url + "/++resource++bika.lims.images/arimport_big.png"
        self.title = self.context.translate(_("Analysis Request Imports"))
        self.description = ""

        self.columns = {
            'title': {'title': _('Import')},
            'getClientTitle': {'title': _('Client')},
            'getDateImported': {'title': _('Date Imported')},
            'getStatus': {'title': _('Validity')},
            'getDateApplied': {'title': _('Date Submitted')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title',
                         'getClientTitle',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied',
                         'state_title']},
            {'id': 'imported',
             'title': _('Imported'),
             'contentFilter': {'review_state': 'imported'},
             'columns': ['title',
                         'getClientTitle',
                         'getDateImported',
                         'getStatus']},
            {'id': 'submitted',
             'title': _('Applied'),
             'contentFilter': {'review_state': 'submitted'},
             'columns': ['title',
                         'getClientTitle',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue

            obj = items[x]['obj']
            items[x]['replace']['title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['title'])
            items[x]['replace']['getClientTitle'] = \
                "<a href='%s'>%s</a>" % (
                    obj.aq_parent.absolute_url(), obj.aq_parent.Title())

        return items

    def getAR(self):
        pass


class GlobalARImportsView(BaseARImportsView):
    def __init__(self, context, request):
        super(GlobalARImportsView, self).__init__(context, request)
        request.set('disable_border', 1)


class ClientARImportsView(BaseARImportsView):
    def __init__(self, context, request):
        super(ClientARImportsView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'ARImport',
            'path': {'query': '/'.join(context.getPhysicalPath())},
            'sort_on': 'sortable_title',
        }
        self.columns = {
            'title': {'title': _('Import')},
            'getDateImported': {'title': _('Date Imported')},
            'getStatus': {'title': _('Validity')},
            'getDateApplied': {'title': _('Date Submitted')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied',
                         'state_title']},
            {'id': 'imported',
             'title': _('Imported'),
             'contentFilter': {'review_state': 'imported'},
             'columns': ['title',
                         'getDateImported',
                         'getStatus']},
            {'id': 'submitted',
             'title': _('Applied'),
             'contentFilter': {'review_state': 'submitted'},
             'columns': ['title',
                         'getDateImported',
                         'getStatus',
                         'getDateApplied']},
        ]


class ClientARImportAddView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile('templates/arimport_add_form.pt')

    def __init__(self, context, request):
        alsoProvides(request, IContentsPage)
        super(ClientARImportAddView, self).__init__(context, request)

    def __call__(self):
        request = self.request
        response = request.response
        form = request.form
        plone.protect.CheckAuthenticator(form)
        if form.get('submitted'):
            csvfile = form.get('csvfile', False)
            option = form.get('ImportOption', False)
            client_id = form.get('ClientID', False)
            if not all([csvfile, option, client_id]):
                raise BadRequest("csvfile, option or client_id not specified")
            if option not in ('c', 'p'):
                raise BadRequest("Import option must be 'c' or 'p'")

            arimport, msg = self._import_file(option, csvfile, client_id)

            if arimport:
                arimport.reindexObject()
                IStatusMessage(request).addStatusMessage(_(msg), "info")
                response.write("<script type='text/javascript'>"
                               "window.location.href='%s'</script>" %
                               arimport.absolute_url())
                return
            else:
                IStatusMessage(request).addStatusMessage(_(msg), "error")
                response.write("<script type='text/javascript'>"
                               "window.location.href='%s/arimport_add'</script>" %
                               self.context.absolute_url())
                return
        return self.template()

    def lookup(self, allowed_types, **kwargs):
        """Lookup an object of type (allowed_types).  kwargs is sent
        directly to the catalog.
        """
        at = getToolByName(self.context, 'archetype_tool')
        for portal_type in allowed_types:
            catalog = at.catalog_map.get(portal_type, [None])[0]
            catalog = getToolByName(self.context, catalog)
            kwargs['portal_type'] = portal_type
            brains = catalog(**kwargs)
            if brains:
                return brains

    def munge_field_values(self, schema, values):
        """Convert spreadsheet values into data that fields can digest.
        - boolean: All values are true except '', 'false', or '0'.
        - reference: Any object in field.allowed_types.  value is expected to
        be the referenced object's title.
        """
        for key, value in values.items():
            if key not in schema:
                logger.info("ARImport: %s not in schema, ignored" % key)
                continue
            field = schema[key]
            if field.type == 'boolean':
                value = str(value).strip().lower()
                values[key] = value not in ('', '0', 'false')
            if field.type == 'reference':
                value = str(value).strip()
                brains = self.lookup(field.allowed_types, Title=value)
                if not brains:
                    logger.info("(type in %s) and Title=%s found; ignored"
                                % field.allowed_types)
                    continue
                if field.multiValued:
                    values[key] = [b.UID for b in brains] if brains else []
                else:
                    values[key] = brains[0].UID if brains else None

    def get_header_values(self, lines):
        """Scape the "Header" and "Header Data" rows into a dictionary.
        """
        reader = csv.reader(lines)
        for row in reader:
            if row[0].strip().lower() == 'header':
                header_fields = [x.strip() for x in row][1:]
                continue
            if row[0].strip().lower() == 'header data':
                header_data = [x.strip() for x in row][1:]
                break
        else:
            # No batch data row found? then quit.
            return None
        # No values specified? then quit.
        if not any(header_data):
            return None
        values = dict(zip(header_fields, header_data))
        return values

    def get_or_create_batch(self, lines, client):
        """Find or create a Batch to which newly created ARs will be assigned.

        The batch will be created when the ARImport is created, and will continue
        to exist even if the ARImport is never finalised.

        - If id is specified and found, the existing batch will be used
        unmodified.
        - If id is specified, but does not exist, it will be used as the ID
        of the newly created batch.
        - If no fields are found or specified, then no batch will be created
        """
        reader = csv.reader(lines)
        for row in reader:
            if row[0].strip().lower() == 'batch fields':
                batch_fields = [x.strip() for x in row][1:]
                continue
            if row[0].strip().lower() == 'batch data':
                batch_data = [x.strip() for x in row][1:]
                break
        else:
            # No batch data row found? then quit.
            return None
        # No values specified? then quit.
        if not any(batch_data):
            return None
        values = dict(zip(batch_fields, batch_data))
        # specified id accuses an existing batch?
        # Inject us out of here!
        batch_id = values.get('id', False)
        if batch_id:
            proxies = self.bika_catalog(portal_type='Batch', id=values['id'])
            if proxies:
                return proxies[0].getObject()
        else:
            if 'id' in values:
                del (values['id'])
        # So it has come to this.
        batch = _createObjectByType('Batch', client, tmpID())
        batch.unmarkCreationFlag()
        self.munge_field_values(batch.Schema(), values)
        batch.edit(**values)
        # Maybe we want to set the new Batch ID
        if batch_id:
            batch.setId(batch_id)
        else:
            # and maybe we don't.
            batch._renameAfterCreation()
        self.batch_data = values
        return batch

    def get_sample_data(self, lines):
        """Read the rows specifying Samples and return a dictionary with
        related data.

        keys are:
            headers - row with "Samples" in column 0.  These headers are
               used as dictionary keys in the rows below.
            prices - Row with "Analysis Price" in column 0.
            total_analyses - Row with "Total analyses" in colmn 0
            price_totals - Row with "Total price excl Tax" in column 0
            samples - All other sample rows.

        """
        res = {'samples': []}
        reader = csv.reader(lines)
        next_rows_are_sample_rows = False
        for row in reader:
            if next_rows_are_sample_rows:
                vals = [x.strip() for x in row]
                if not any(vals):
                    continue
                res['samples'].append(zip(res['headers'], vals))
            elif row[0].strip().lower() == 'samples':
                res['headers'] = [x.strip() for x in row]
            elif row[0].strip().lower() == 'analysis price':
                res['prices'] = zip(res['headers'],
                                    [x.strip() for x in row])
            elif row[0].strip().lower() == 'total analyses':
                res['total_analyses'] = zip(res['headers'],
                                            [x.strip() for x in row])
            elif row[0].strip().lower() == 'total price excl tax':
                res['price_totals'] = zip(res['headers'],
                                          [x.strip() for x in row])
                next_rows_are_sample_rows = True
        return res

    def make_title(self, client, filename):
        title, idx = filename, 1
        titles = [i.Title() for i in client.objectValues()]
        while title in titles:
            title = '%s-%s' % (filename, idx)
            idx += 1
        return title

    def _import_file(self, importoption, csvfile, client_id):
        fullfilename = os.path.split(csvfile.filename)[-1]
        filename = os.path.splitext(fullfilename)[0]
        lines = csvfile.readlines()

        r = self.portal_catalog(portal_type='Client', id=client_id)
        if len(r) == 0:
            # This is not a user input issue - client_id is added to template
            return None, 'Could not find Client %s' % client_id
        client = r[0].getObject()
        arimport = _createObjectByType("ARImport", client, tmpID())
        arimport.processForm()

        header = self.get_header_values(lines)
        if not header:
            return None, 'Invalid or missing batch header'
        if header['Import / Export'] != 'Import':
            return None, 'Invalid batch header - Import required in cell B2'
        if header['File name'].lower() != filename.lower():
            msg = 'Filename (%s) does not match entered filename (%s)' % \
                  (filename, header['File name'])
            return None, msg

        self.batch_data = []  # get_or_create_batch might set batch_data
        batch = self.get_or_create_batch(lines, client)

        sampledata = self.get_sample_data(lines)
        samples = sampledata['samples']

        title = 'Importing file'
        bar = ProgressBar(self.context, self.request, title, description='')
        notify(InitialiseProgressBar(bar))

        keywords = self.context.bika_setup_catalog.uniqueValuesFor('getKeyword')
        used_keywords = set()

        sample_count = len(samples)
        cnt = next_num = 0
        for sample in samples:
            sample = dict(sample)
            cnt += 1
            progress_index = float(cnt) / float(sample_count) * 100.0
            progress = ProgressState(self.request, progress_index)
            notify(UpdateProgressEvent(progress))
            analyses = []
            for keyword, value in sample.items():
                if keyword in keywords and value in (1, '1'):
                    analyses.append(keyword)
                    used_keywords.add(keyword)
            if len(analyses) > 0:
                next_num += 1
                aritem = _createObjectByType("ARImportItem", arimport,
                                             'aritem-%s' % next_num)
                aritem.edit(
                    SampleName=sample['Samples'],
                    ClientRef=self.batch_data.get('ClientReference', ''),
                    ClientSid=sample.get('Client Sample ID', ''),
                    SampleDate=sample.get('Sampling date', ''),
                    SampleType=sample.get('Sample Type', ''),
                    SamplePoint=sample.get('Sample Point', ''),
                    PickingSlip=sample.get('Picking Slip', ''),
                    SampleMatrix=sample.get('Sample Matrix', ''),
                    ContainerType=sample.get('Container Type', ''),
                    ReportDryMatter=sample.get('Report DM', ''),
                    Priority=sample.get('Priority', ''),
                )

                if importoption == 'c':
                    aritem.setAnalyses(analyses)
                elif importoption == 'p':
                    aritem.setAnalysisProfile(analyses)

        val = header.get('CC Names - Report', '')
        cc_names_report = ','.join([i.strip() for i in val.split(';')])
        val = header.get('CC Emails - Report', '')
        cc_emails_report = ','.join([i.strip() for i in val.split(';')])
        val = header.get('CC Emails - Invoice', '')
        cc_emails_invoice = ','.join([i.strip() for i in val.split(';')])

        try:
            nr_samples = int(header.get('No of Samples', 0))
        except ValueError:
            nr_samples = 0

        arimport.edit(
            title=self.make_title(client, filename),
            ImportOption=importoption,
            FileName=header.get('File name', ''),
            OriginalFile=csvfile,
            ClientTitle=header.get('Client name', ''),
            ClientID=header.get('Client ID', ''),
            ContactID=header.get('Contact ID', ''),
            CCNamesReport=cc_names_report,
            CCEmailsReport=cc_emails_report,
            CCEmailsInvoice=cc_emails_invoice,
            OrderID=header.get('Order ID', ''),
            ###QuoteID=header.get('Q', '')
            ###'Client Reference': 'Q123',
            NumberSamples=nr_samples,
            Analyses=list(used_keywords),
            DateImported=DateTime(),
            Batch=batch
        )

        valid = arimport.validateIt()
        return arimport, "AR Import complete"
