from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _

class ReferenceSamplesView(BikaListingView):
    title = _("Reference Samples")
    description = _("")
    contentFilter = {'portal_type': 'ReferenceSample'}
    content_add_actions = {_('Reference Sample'): "createObject?type_name=ReferenceSample"}
    show_editable_border = True
    show_filters = False
    show_sort_column = False
    show_select_row = True
    show_select_column = True
    pagesize = 50

    columns = {
           'ID': {'title': _('ID')},
           'Title': {'title': _('Title')},
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
                             'Manufacturer',
                             'CatalogueNumber',
                             'LotNumber',
                             'Definition',
                             'DateSampled',
                             'DateReceived',
                             'DateOpened',
                             'ExpiryDate']},
                ]


    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['ID'] = obj.id
            items[x]['Title'] = obj.getReferenceTitle()
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
            items[x]['DateOpened'] = \
                 self.context.toLocalizedTime(obj.getDateOpened(), long_format = 0)
            items[x]['ExpiryDate'] = \
                 self.context.toLocalizedTime(obj.getExpiryDate(), long_format = 0)

            items[x]['replace']['ID'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['ID'])

        return items


class ContactsView(BikaListingView):
    contentFilter = {'portal_type': 'SupplierContact'}
    content_add_actions = {_('Contact'): "createObject?type_name=SupplierContact"}
    show_editable_border = True
    show_filters = False
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
           'getFullname': {'title': _('Full Name')},
           'getEmailAddress': {'title': _('Email Address')},
           'getBusinessPhone': {'title': _('Business Phone')},
           'getMobilePhone': {'title': _('Mobile Phone')},
           'getFax': {'title': _('Fax')},
          }

    review_states = [
                {'title': 'All', 'id':'all',
                 'columns': ['getFullname',
                             'getEmailAddress',
                             'getBusinessPhone',
                             'getMobilePhone',
                             'getFax']},
                ]

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Contacts"))
        self.description = ""

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            items[x]['replace']['getFullName'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getFullName'])

        return items
