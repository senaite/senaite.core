from bika.lims.permissions import AddBatch
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.config import ManageInvoices
from bika.lims.utils import t
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims.browser import BrowserView
from zope.interface import implements
import plone
import json


class BatchFolderContentsView(BikaListingView):

    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {
            'portal_type': 'Batch',
            'sort_on': 'created',
            'sort_order': 'reverse',
        }
        self.context_actions = {}
        self.icon = self.portal_url + "/++resource++bika.lims.images/batch_big.png"
        self.title = self.context.translate(_("Batches"))
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title')},
            'BatchID': {'title': _('Batch ID')},
            'Description': {'title': _('Description')},
            'BatchDate': {'title': _('Date')},
            'state_title': {'title': _('State'), 'sortable': False},
        }

        self.review_states = [  # leave these titles and ids alone
            {'id': 'default',
             'contentFilter': {'review_state': 'open',
                               'cancellation_state': 'active'},
             'title': _('Open'),
             'transitions': [{'id': 'close'}, {'id': 'cancel'}],
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
                         'Description',
                         'state_title', ]
             },
            {'id': 'closed',
             'contentFilter': {'review_state': 'closed',
                               'cancellation_state': 'active'},
             'title': _('Closed'),
             'transitions': [{'id': 'open'}],
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
                         'Description',
                         'state_title', ]
             },
            {'id': 'cancelled',
             'title': _('Cancelled'),
             'transitions': [{'id': 'reinstate'}],
             'contentFilter': {'cancellation_state': 'cancelled'},
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
                         'Description',
                         'state_title', ]
             },
            {'id': 'all',
             'title': _('All'),
             'transitions': [],
             'contentFilter':{},
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
                         'Description',
                         'state_title', ]
             },
        ]

    def __call__(self):
        if self.context.absolute_url() == self.portal.batches.absolute_url():
            # in contexts other than /batches, we do want to show the edit border
            self.request.set('disable_border', 1)
        if self.context.absolute_url() == self.portal.batches.absolute_url() \
        and self.portal_membership.checkPermission(AddBatch, self.portal.batches):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=Batch',
                 'icon': self.portal.absolute_url() + '/++resource++bika.lims.images/add.png'}
        return super(BatchFolderContentsView, self).__call__()

    def folderitems(self):
        self.filter_indexes = None

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']

            bid = obj.getBatchID()
            items[x]['BatchID'] = bid
            items[x]['replace']['BatchID'] = "<a href='%s/%s'>%s</a>" % (items[x]['url'], 'analysisrequests', bid)

            title = obj.Title()
            items[x]['Title'] = title
            items[x]['replace']['Title'] = "<a href='%s/%s'>%s</a>" % (items[x]['url'], 'analysisrequests', title)

            date = obj.Schema().getField('BatchDate').get(obj)
            if callable(date):
                date = date()
            items[x]['BatchDate'] = date
            items[x]['replace']['BatchDate'] = self.ulocalized_time(date)

        return items


class BatchFolderExportCSV(BatchFolderContentsView):

    def __call__(self, REQUEST, RESPONSE):
        """
        Export invoice batch in csv format.
        Writes the csv file into the RESPONSE to allow
        the file to be streamed to the user.
        Nothing gets returned.
        """
        import pdb;pdb.set_trace()
        import csv
        from cStringIO import StringIO
        delimiter = ','
        filename = 'batch.txt'

        container = self.unrestrictedTraverse(REQUEST.get('current_path'))
        assert container

        container.plone_log("Exporting InvoiceBatch to CSV format for PASTEL")
        invoices = container.listFolderContents()

        if not len(invoices):
            container.plone_log("InvoiceBatch contains no entries")

        rows = []
        _ordNum = 'starting at none'
        for invoice in invoices:
            new_invoice = True
            _invNum = "%s" % invoice.getId()[:8]
            _clientNum = "%s" % invoice.getClient().getAccountNumber()
            _invDate = "%s" % invoice.getInvoiceDate().strftime('%Y-%m-%d')
            _monthNum = invoice.getInvoiceDate().month()
            if _monthNum < 7:
                _periodNum = _monthNum + 6
            else:
                _periodNum = _monthNum - 6
            _periodNum = "%s" % _monthNum
        import pdb;pdb.set_trace()
    #         _message1 = ''
    #         _message2 = ''
    #         _message3 = ''

    # items = invoice.invoice_lineitems # objectValues('InvoiceLineItem')
    #         mixed = [(item.getClientOrderNumber(), item) for item in items]
    #         mixed.sort()
    #         lines = [t[1] for t in mixed]

    # iterate through each invoice line
    #         for line in lines:
    #             if new_invoice or line.getClientOrderNumber() != _ordNum:
    #                 new_invoice = False
    #                 _ordNum = line.getClientOrderNumber()

    # create header csv entry as a list
    #                 header = [ \
    #                     "Header", _invNum, " ", " ", _clientNum, _periodNum, \
    #                     _invDate, _ordNum, "N", 0, _message1, _message2, \
    #                     _message3, "", "", "", "", "", "", 0, "", "", "", "", \
    #                     0, "", "", "N"]
    #                 rows.append(header)

    #             _quant = 1
    #             _unitp = line.getSubtotal()
    #             _inclp = line.getTotal()
    #             _item = line.getItemDescription()
    #             _desc = "Analysis: %s" % _item[:40]
    #             if _item.startswith('Water') or _item.startswith('water'):
    #                 _icode = "002"
    #             else:
    #                 _icode = "001"
    #             _ltype = "4"
    #             _ccode = ""
    # create detail csv entry as a list
    #             detail = ["Detail", 0, _quant, _unitp, _inclp, \
    #                       "", "01", "0", "0", _icode, _desc, \
    #                       _ltype, _ccode, ""]
    #             rows.append(detail)
    # convert lists to csv string
    #     ramdisk = StringIO()
    #     writer = csv.writer(ramdisk, delimiter = delimiter)
    #     assert(writer)
    #     writer.writerows(rows)
    #     result = ramdisk.getvalue()
    #     ramdisk.close()
    # stream file to browser
    #     setheader = RESPONSE.setHeader
    #     setheader('Content-Length', len(result))
    #     setheader('Content-Type',
    #         'text/x-comma-separated-values')
    #     setheader('Content-Disposition', 'inline; filename=%s' % filename)
    #     RESPONSE.write(result)
    #     return


class ajaxGetBatches(BrowserView):

    """ Vocabulary source for jquery combo dropdown box
    """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        rows = []

        batches = self.bika_catalog(portal_type='Batch')

        for batch in batches:
            batch = batch.getObject()
            if self.portal_workflow.getInfoFor(batch, 'review_state', 'open') != 'open' \
               or self.portal_workflow.getInfoFor(batch, 'cancellation_state') == 'cancelled':
                continue
            if batch.Title().lower().find(searchTerm) > -1 \
            or batch.Description().lower().find(searchTerm) > -1:
                rows.append({'BatchID': batch.getBatchID(),
                             'Description': batch.Description(),
                             'BatchUID': batch.UID()})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'BatchID'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
