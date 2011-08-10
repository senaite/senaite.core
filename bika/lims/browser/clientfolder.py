from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IClientFolder
from plone.app.content.browser.interfaces import IFolderContentsView
from Products.Five.browser import BrowserView
from zope.interface import implements

class ClientFolderContentsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Client', 'sort_on': 'sortable_title'}
    content_add_actions = {_('Client'): "createObject?type_name=Client"}
    title = _("Clients")
    description = ""
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = False
    pagesize = 20

    columns = {
               'title': {'title': _('Name')},
               'getEmailAddress': {'title': _('Email Address')},
               'getPhone': {'title': _('Phone')},
               'getFax': {'title': _('Fax')},
              }

    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns':['title',
                                'getEmailAddress',
                                'getPhone',
                                'getFax', ]
                     },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue

            items[x]['replace']['title'] = "<a href='%s'>%s</a>"%\
                 (items[x]['url'], items[x]['title'])

            if items[x]['getEmailAddress']:
                items[x]['replace']['getEmailAddress'] = "<a href='%s'>%s</a>"%\
                     ('mailto:%s' % items[x]['getEmailAddress'],
                      items[x]['getEmailAddress'])

        return items

    def __call__(self):
        return self.template()

