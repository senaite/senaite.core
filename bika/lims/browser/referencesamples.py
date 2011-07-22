from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _

class ReferenceSamplesView(BikaListingView):
    title = _("Reference Samples")
    description = _("")
    contentFilter = {'portal_type': 'ReferenceSample', 'path':{"query": ["/"], "level" : 0 }}
    content_add_actions = {}
    show_editable_border = False
    show_filters = True
    show_sort_column = False
    show_select_row = False
    show_select_column = False
    pagesize = 50

    columns = {
           'ID': {'title': _('ID')},
           'Title': {'title': _('Title')},
           'Supplier': {'title': _('Supplier')},
           'Manufacturer': {'title': _('Manufacturer')},
           'CatalogueNumber': {'title': _('Catalogue Number')},
           'LotNumber': {'title': _('Lot Number')},
           'Definition': {'title': _('Reference Definition')},
           'DateSampled': {'title': _('Date Sampled')},
           'DateReceived': {'title': _('Date Received')},
           'DateOpened': {'title': _('Date Opened')},
           'ExpiryDate': {'title': _('Expiry Date')},
           'state_title': {'title': _('State')},
          }
    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns': ['ID',
                             'Title',
                             'Supplier',
                             'Manufacturer',
                             'CatalogueNumber',
                             'LotNumber',
                             'Definition',
                             'DateSampled',
                             'DateReceived',
                             'DateOpened',
                             'ExpiryDate',
                             'state_title']},
                {'title': _('Current'), 'id':'current',
                 'columns': ['ID',
                             'Title',
                             'Supplier',
                             'Manufacturer',
                             'CatalogueNumber',
                             'LotNumber',
                             'Definition',
                             'DateSampled',
                             'DateReceived',
                             'DateOpened',
                             'ExpiryDate']},
                {'title': _('Expired'), 'id':'expired',
                 'columns': ['ID',
                             'Title',
                             'Supplier',
                             'Manufacturer',
                             'CatalogueNumber',
                             'LotNumber',
                             'Definition',
                             'DateSampled',
                             'DateReceived',
                             'DateOpened',
                             'ExpiryDate']},
                {'title': _('Disposed'), 'id':'disposed',
                 'columns': ['ID',
                             'Title',
                             'Supplier',
                             'Manufacturer',
                             'CatalogueNumber',
                             'LotNumber',
                             'Definition',
                             'DateSampled',
                             'DateReceived',
                             'DateOpened',
                             'ExpiryDate']},
                ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['ID'] = obj.id
            items[x]['Title'] = obj.getReferenceTitle()
            items[x]['Supplier'] = obj.aq_parent.Title()
            items[x]['Manufacturer'] = obj.getReferenceManufacturer().Title()
            items[x]['CatalogueNumber'] = obj.getCatalogueNumber()
            items[x]['LotNumber'] = obj.getLotNumber()
            items[x]['Definition'] = obj.getReferenceDefinition().Title()
            items[x]['DateSampled'] = \
                 self.context.toLocalizedTime(obj.getDateSampled(), long_format = 0)
            items[x]['DateReceived'] = \
                 self.context.toLocalizedTime(obj.getDateReceived(), long_format = 0)
            items[x]['DateOpened'] = \
                 self.context.toLocalizedTime(obj.getDateOpened(), long_format = 0)
            items[x]['ExpiryDate'] = \
                 self.context.toLocalizedTime(obj.getExpiryDate(), long_format = 0)
            items[x]['links'] = {'ID': items[x]['url']}

        return items
