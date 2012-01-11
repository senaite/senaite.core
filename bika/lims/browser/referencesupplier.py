from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import TimeOrDate

class ReferenceSamplesView(BikaListingView):

    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)
        self.icon = "++resource++bika.lims.images/referencesample_big.png"
        self.title = _("Reference Samples")
        rs_path = context.getPhysicalPath()
        self.contentFilter = {'portal_type': 'ReferenceSample',
                              'sort_on': 'id',
                              'sort_order': 'reverse',
                              'path': {"query": ["/".join(rs_path),],
                                       "level" : 0 }}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=ReferenceSample',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = {
            'ID': {'title': _('ID')},
            'Title': {'title': _('Title')},
            'Manufacturer': {'title': _('Manufacturer')},
            'Definition': {'title': _('Reference Definition')},
            'DateSampled': {'title': _('Date Sampled')},
            'DateReceived': {'title': _('Date Received')},
            'DateOpened': {'title': _('Date Opened')},
            'ExpiryDate': {'title': _('Expiry Date')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['ID',
                         'Title',
                         'Manufacturer',
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
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'title': _('Expired'), 'id':'expired',
             'columns': ['ID',
                         'Title',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
            {'title': _('Disposed'), 'id':'disposed',
             'columns': ['ID',
                         'Title',
                         'Manufacturer',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'DateOpened',
                         'ExpiryDate']},
        ]


    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ID'] = obj.id
            items[x]['Manufacturer'] = obj.getReferenceManufacturer() and \
                 obj.getReferenceManufacturer().Title() or ''
            items[x]['Definition'] = obj.getReferenceDefinition() and \
                 obj.getReferenceDefinition().Title() or ''
            items[x]['DateSampled'] = \
                 TimeOrDate(self.context, obj.getDateSampled())
            items[x]['DateReceived'] = \
                 TimeOrDate(self.context, obj.getDateReceived())
            items[x]['DateOpened'] = \
                 TimeOrDate(self.context, obj.getDateOpened())
            items[x]['ExpiryDate'] = \
                 TimeOrDate(self.context, obj.getExpiryDate())

            after_icons = ''
            if obj.getBlank():
                after_icons += "<img src='++resource++bika.lims.images/blank.png' title='Blank'>"
            if obj.getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous.png' title='Hazardous'>"
            items[x]['replace']['ID'] = "<a href='%s/base_view'>%s</a>&nbsp;%s" % \
                 (items[x]['url'], items[x]['ID'], after_icons)

        return items


class ContactsView(BikaListingView):
    contentFilter = {'portal_type': 'SupplierContact'}
    context_actions = {_('Add'):
                       {'url': 'createObject?type_name=SupplierContact',
                        'icon': '++resource++bika.lims.images/add.png'}}
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 25

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
        self.icon = "++resource++bika.lims.images/referencesupplier_contact_big.png"
        self.title = _("contacts_title", default="Contacts")
        self.descriotion = _("contacts_descr", default="")

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            obj = items[x]['obj']
            items[x]['getFullname'] = obj.getFullname()
            items[x]['getEmailAddress'] = obj.getEmailAddress()
            items[x]['getBusinessPhone'] = obj.getBusinessPhone()
            items[x]['getMobilePhone'] = obj.getMobilePhone()

            items[x]['replace']['getFullName'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getFullname'])

        return items
