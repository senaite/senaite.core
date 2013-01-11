from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.controlpanel.bika_instruments import InstrumentsView
from bika.lims import bikaMessageFactory as _

class SupplierInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(SupplierInstrumentsView, self).__init__(context, request)
    
    def folderitems(self):
        items = InstrumentsView.folderitems(self)
        uidsup = self.context.UID()
        outitems = []
        for x in range(len(items)):
            obj = items[x]['obj']
            if obj.getSupplier().UID() == uidsup:
                outitems.append(items[x])
        return outitems

class ContactsView(BikaListingView):

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {'portal_type': 'SupplierContact'}
        self.context_actions = {_('Add'):
            {'url': 'createObject?type_name=SupplierContact',
             'icon': '++resource++bika.lims.images/add.png'}
        }
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.icon = "++resource++bika.lims.images/supplier_contact_big.png"
        self.title = _("Contacts")

        self.columns = {
            'getFullname': {'title': _('Full Name')},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
            'getFax': {'title': _('Fax')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['getFullName'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['obj'].getFullname())

        return items