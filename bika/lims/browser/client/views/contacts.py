from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IContacts
from bika.lims.vocabularies import CatalogVocabulary
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class ClientContactsView(BikaListingView):
    implements(IViewView, IContacts)

    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'Contact',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0
            }
        }
        self.context_actions = {
            _('Add'):
                {'url': 'createObject?type_name=Contact',
                 'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "contacts"

        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/client_contact_big.png"
        self.title = self.context.translate(_("Contacts"))
        self.description = ""

        self.columns = {
            'getFullname': {'title': _('Full Name'),
                            'index': 'getFullname'},
            'Username': {'title': _('User Name')},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['getFullname',
                         'Username',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['getFullname',
                         'Username',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['getFullname',
                         'Username',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue

            obj = items[x]['obj']
            items[x]['getFullname'] = obj.getFullname()
            items[x]['getEmailAddress'] = obj.getEmailAddress()
            items[x]['getBusinessPhone'] = obj.getBusinessPhone()
            items[x]['getMobilePhone'] = obj.getMobilePhone()
            username = obj.getUsername()
            items[x]['Username'] = username and username or ''

            items[x]['replace']['getFullname'] = \
                "<a href='%s'>%s</a>" % (
                    items[x]['url'], items[x]['getFullname'])

            if items[x]['getEmailAddress']:
                addr = items[x]['getEmailAddress']
                items[x]['replace']['getEmailAddress'] = \
                    "<a href='mailto:%s'>%s</a>" % (addr, addr)

        return items


class ClientContactVocabularyFactory(CatalogVocabulary):
    def __call__(self):
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact',
            path={'query': "/".join(self.context.getPhysicalPath()),
                  'level': 0}
        )
