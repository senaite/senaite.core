from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IPricelistFolder
from bika.lims.permissions import AddPricelist, ManageBika
from DateTime import DateTime
from email.Utils import formataddr
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.utils import sendmail, encode_header
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface.declarations import implements


class PricelistsView(BikaListingView):
    implements(IFolderContentsView, IViewView, IPricelistFolder)

    def __init__(self, context, request):
        super(PricelistsView, self).__init__(context, request)
        self.catalog = 'portal_catalog'
        self.contentFilter = {'portal_type': 'Pricelist',
                              'sort_on': 'sortable_title'}
        self.context_actions = {}
        self.title = self.context.translate(_("Pricelists"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/pricelist_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'getEffectiveDate': {'title': _('Start Date'),
                            'index': 'getEffectiveDate',
                            'toggle': True},
            'getExpirationDate': {'title': _('End Date'),
                            'index': 'getExpirationDate',
                            'toggle': True},
        }

        now = DateTime()
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'getEffectiveDate': {'query': now,
                                                    'range': 'max'},
                               'getExpirationDate': {'query': now,
                                                     'range': 'min'},
                               'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title', 'getExpirationDate']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'getEffectiveDate': {'query': now,
                                                    'range': 'min'},
                               'getExpirationDate': {'query': now,
                                                     'range': 'max'},
                               'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title', 'getExpirationDate']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title', 'getEffectiveDate', 'getExpirationDate']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddPricelist, self.context):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=Pricelist',
                'icon': '++resource++bika.lims.images/add.png'
            }
        now = DateTime()
        if not mtool.checkPermission(ManageBika, self.context):
            self.show_select_column = False
            self.review_states = [
                {'id': 'default',
                 'title': _('Active'),
                 'contentFilter': {'getEffectiveDate': {'query': now,
                                                     'range': 'max'},
                                   'getExpirationDate': {'query': now,
                                                      'range': 'min'},
                                   'inactive_state': 'active'},
                 'transitions': [{'id': 'deactivate'}, ],
                 'columns': ['Title', 'getExpirationDate']},
                ]
        return super(PricelistsView, self).__call__()

    def folderitems(self):

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['getEffectiveDate'] = self.ulocalized_time(items[x]['obj'].getEffectiveDate())
            items[x]['getExpirationDate'] = self.ulocalized_time(items[x]['obj'].getExpirationDate())

        return items


class PricelistView(BrowserView):
    template = ViewPageTemplateFile("templates/pricelist_view.pt")
    lineitems_pt = ViewPageTemplateFile("templates/pricelist_content.pt")

    def __call__(self):
        self.items = self.context.objectValues()
        self.pricelist_content = self.lineitems_pt()
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class PricelistPrintView(BrowserView):
    template = ViewPageTemplateFile("templates/pricelist_print.pt")
    lineitems_pt = ViewPageTemplateFile("templates/pricelist_content.pt")

    def __call__(self):
        self.items = self.context.objectValues()
        self.pricelist_content = self.lineitems_pt()
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class PricelistEmailView(BrowserView):
    form_template = ViewPageTemplateFile("templates/pricelist_email_form.pt")
    template = ViewPageTemplateFile("templates/pricelist_email.pt")
    lineitems_pt = ViewPageTemplateFile("templates/pricelist_content.pt")

    def __call__(self):
        if 'submitted' in self.request:
            self.items = self.context.objectValues()
            self.pricelist_content = self.lineitems_pt()

            portal = context.portal_url.getPortalObject()
            lab = context.bika_labinfo.laboratory
            request = context.REQUEST

            ar_query_results = portal.portal_mailtemplates.getTemplate(
                'bika', request.mail_template)

            headers = {}
            headers['Date'] = DateTime().rfc822()
            from_addr = headers['From'] = formataddr(
                (encode_header(lab.Title()), lab.getEmailAddress())
            )

            if 'Contact_email_address' in request:
                contact_address = request.Contact_email_address
                msg = 'portal_status_message=Pricelist sent to %s' % (
                    contact_address)
            else:
                contact = context.reference_catalog.lookupObject(request.Contact_uid)
                contact_address = formataddr(
                    (encode_header(contact.getFullname()),
                      contact.getEmailAddress())
                )
                msg = 'portal_status_message=Pricelist sent to %s at %s' % (
                    contact.Title(), contact.getEmailAddress())

            to_addrs = []
            to_addr = headers['To'] = contact_address
            to_addrs.append(to_addr)
            # send copy to lab
            to_addrs.append(from_addr)

            to_addrs = tuple(to_addrs)
            info = {'request': request,
                    'pricelist': context,
                    'portal': portal}

            message = pmt.createMessage(
                'bika', request.mail_template, info, headers, text_format='html')
            sendmail(portal, from_addr, to_addrs, message)

            request.RESPONSE.redirect('%s?%s' % (context.absolute_url(), msg))

            return self.template()
        else:
            return self.form_template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()
