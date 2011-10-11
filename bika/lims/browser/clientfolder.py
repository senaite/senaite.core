from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IClientFolder
from plone.app.content.browser.interfaces import IFolderContentsView
from Products.Five.browser import BrowserView
from zope.interface import implements

class ClientFolderContentsView(BikaListingView):

    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(ClientFolderContentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Client',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Client'):
                                    "createObject?type_name=Client"}
        self.icon = "++resource++bika.lims.images/client_big.png"
        self.title = _("Clients")
        self.description = ""
        self.show_editable_border = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.show_filters = False
        self.pagesize = 20

        self.columns = {
                   'title': {'title': _('Name')},
                   'EmailAddress': {'title': _('Email Address')},
                   'Phone': {'title': _('Phone')},
                   'Fax': {'title': _('Fax')},
                  }

        self.review_states = [
                        {'title': _('All'), 'id':'all',
                         'columns':['title',
                                    'EmailAddress',
                                    'Phone',
                                    'Fax', ]
                         },
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            items[x]['replace']['title'] = "<a href='%s'>%s</a>"%\
                 (items[x]['url'], items[x]['title'])

            items[x]['EmailAddress'] = obj.getEmailAddress()
            items[x]['replace']['EmailAddress'] = "<a href='%s'>%s</a>"%\
                     ('mailto:%s' % obj.getEmailAddress(),
                      obj.getEmailAddress())
            items[x]['Phone'] = obj.getPhone()
            items[x]['Fax'] = obj.getFax()
        return items

    def __call__(self):
        return self.template()

