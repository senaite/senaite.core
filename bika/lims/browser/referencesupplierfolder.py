from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _

class ReferenceSuppliersView(BikaListingView):
    title = _("Reference Suppliers")
    description = _("")
    contentFilter = {'portal_type': 'ReferenceSupplier'}
    content_add_actions = {_('Reference Supplier'): "createObject?type_name=ReferenceSupplier"}
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = True
    show_select_column = True
    pagesize = 50

    columns = {
           'Name': {'title': _('Name')},
           'Email': {'title': _('Email')},
           'Phone': {'title': _('Phone')},
           'Fax': {'title': _('Fax')},
          }
    review_states = [
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
            obj = items[x]['obj'].getObject()
            items[x]['Name'] = obj.getName()
            items[x]['Email'] = obj.getEmailAddress()
            items[x]['Phone'] = obj.getPhone()
            items[x]['Fax'] = obj.getFax()
            items[x]['replace']['Name'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Name'])

        return items