from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _

class ReferenceSuppliersView(BikaListingView):

    def __init__(self, context, request):
        super(ReferenceSuppliersView,self).__init__(context, request)
        self.title = _("Reference Suppliers")
        self.icon = "++resource++bika.lims.images/referencesupplier_big.png"
        self.description = _("")
        self.contentFilter = {'portal_type': 'ReferenceSupplier'}
        self.content_add_actions = {_('Add'): "createObject?type_name=ReferenceSupplier"}
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.request.set('disable_border', 1)

        self.columns = {
            'Name': {'title': _('Name')},
            'Email': {'title': _('Email')},
            'Phone': {'title': _('Phone')},
            'Fax': {'title': _('Fax')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['Name',
                         'Email',
                         'Phone',
                         'Fax']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Name'] = obj.getName()
            items[x]['Email'] = obj.getEmailAddress()
            items[x]['Phone'] = obj.getPhone()
            items[x]['Fax'] = obj.getFax()
            items[x]['replace']['Name'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Name'])

        return items
