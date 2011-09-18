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
    show_select_row = True
    show_select_column = True
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
                             'ExpiryDate']},
                ]

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ID'] = obj.id
            items[x]['Supplier'] = obj.aq_parent.Title()
            items[x]['Manufacturer'] = obj.getReferenceManufacturer() and \
                 obj.getReferenceManufacturer().Title() or ''
            items[x]['CatalogueNumber'] = obj.getCatalogueNumber()
            items[x]['LotNumber'] = obj.getLotNumber()
            items[x]['Definition'] = obj.getReferenceDefinition() and \
                 obj.getReferenceDefinition().Title() or ''
            items[x]['DateSampled'] = \
                 self.context.toLocalizedTime(obj.getDateSampled(), long_format = 0)
            items[x]['DateReceived'] = \
                 self.context.toLocalizedTime(obj.getDateReceived(), long_format = 0)
            items[x]['ExpiryDate'] = \
                 self.context.toLocalizedTime(obj.getExpiryDate(), long_format = 0)

            after_icons = ''
            if obj.getBlank():
                after_icons += "<img src='++resource++bika.lims.images/blank.png' title='Blank'>"
            if obj.getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous_small.png' title='Hazardous'>"
            items[x]['replace']['ID'] = "<a href='%s'>%s</a>&nbsp;%s" % \
                 (items[x]['url'], items[x]['ID'], after_icons)

        return items
