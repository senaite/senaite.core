from bika.lims import bikaMessageFactory as _
from bika.lims.utils import to_utf8
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import sys, traceback

class AnalysisRequestPublishView(BrowserView):
    template = ViewPageTemplateFile("templates/analysisrequest_publish.pt")

    def getAvailableFormats(self):
        return [ {'id': 'A4_default.pt',
                  'title': 'A4 Default' },
                 {'id': 'A4_custom_01.pt',
                  'title': 'A4 Custom' } ]

    def __call__(self):
        return self.template()


    def getReportTemplate(self):
        embedt = self.request.get('template', 'A4_default.pt')
        embed = ViewPageTemplateFile("templates/reports/%s" % embedt);
        try:
            return embed(self)
        except:
            tbex = traceback.format_exc()
            return "<div class='error'>%s '%s':<pre>%s</pre></div>" % (_("Unable to load the template"), embedt, tbex)

    def getAnalysisRequest(self):
        return self.context

    def getDataSource(self):
        datasource = {}
        portal = self.context.portal_url.getPortalObject()

        datasource['portal'] = {'obj': portal,
                                'url': portal.absolute_url()}

        datasource['laboratory'] = self._lab_data()
        datasource['contact'] = self._contact_data()
        datasource['client'] = self._client_data()

        # More stuff here to fill datasource

        return datasource

    def _lab_data(self):
        portal = self.context.portal_url.getPortalObject()
        lab = self.context.bika_setup.laboratory
        lab_address = lab.getPostalAddress() \
                        or lab.getBillingAddress() \
                        or lab.getPhysicalAddress()
        if lab_address:
            _keys = ['address', 'city', 'state', 'zip', 'country']
            _list = ["<div>%s</div>" % lab_address.get(v) for v in _keys
                     if lab_address.get(v)]
            lab_address = "".join(_list)
        else:
            lab_address = ''

        return {'obj': lab,
                'title': to_utf8(lab.Title()),
                'url': to_utf8(lab.getLabURL()),
                'address': to_utf8(lab_address),
                'accreditation_body': to_utf8(lab.getAccreditationBody()),
                'logo': "%s/logo_print.jpg" % portal.absolute_url()}

    def _contact_data(self):
        data = {'obj': None,
                'fullname': '',
                'email': '',
                'pubpref': '',}

        contact = self.getAnalysisRequest().getContact()
        if contact:
            data['obj'] = contact
            data['fullname'] = to_utf8(contact.getFullname())
            data['email'] = to_utf8(contact.getEmailAddress())
            data['pubpref'] = contact.getPublicationPreference()

        return data

    def _client_data(self):
        data = {'obj': None,
                'name': '',
                'phone': '',
                'fax': '',
                'address': '',}

        client = self.getAnalysisRequest().aq_parent
        if client:
            data['obj'] = client
            data['name'] = to_utf8(client.getName())
            data['phone'] = to_utf8(client.getPhone())
            data['fax'] = to_utf8(client.getFax())

            client_address = client.getPostalAddress()
            if not client_address:
                # Data from the first contact
                contact = self.getAnalysisRequest().getContact()
                if contact and contact.getBillingAddress():
                    client_address = contact.getBillingAddress()
                elif contact and contact.getPhysicalAddress():
                    client_address = contact.getPhysicalAddress()

            if client_address:
                _keys = ['address', 'city', 'state', 'zip', 'country']
                _list = ["<div>%s</div>" % client_address.get(v) for v in _keys
                         if client_address.get(v)]
                client_address = "".join(_list)
            else:
                client_address = ''
            data['address'] = to_utf8(client_address)

        return data
