from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import TimeOrDate
import json, plone

class QCView(BrowserView):
    pass
#    template = ViewPageTemplateFile("templates/reference_qc.pt")
#    def __call__(self):
#        return self.template()

class ajaxGetReferenceDefinitionInfo():
    """ Returns a JSON encoded copy of the ReferenceResults field for a ReferenceDefinition,
        and a list of category UIDS that contain services with results.
        Also returns the 'blank' boolean, to select the checkbox on the edit form if required.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        uid = self.request.get('uid', None)
        if not uid:
            return json.dumps({'errors':["No UID specified in request.",]})
        rc = getToolByName(self.context, 'reference_catalog')

        # first grab the reference results themselves
        ref_def = rc.lookupObject(uid)
        if not ref_def:
            return json.dumps({'errors':["Reference Definition %s does not exist."%uid,]})
        results = ref_def.getReferenceResults()
        if not results:
            return json.dumps({'errors':["The reference definition does not define any values.",]})

        # we return a list of category uids so the javascript knows which ones to expand
        categories = []
        for result in results:
            service = rc.lookupObject(result['uid'])
            cat_uid = service.getCategory().UID()
            if cat_uid not in categories: categories.append(cat_uid)

        return json.dumps({'results':results,
                           'categories':categories,
                           'blank':ref_def.getBlank(),
                           'hazardous':ref_def.getHazardous()})


class ReferenceSamplesView(BikaListingView):
    """Main reference samples folder view
    """
    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)
        self.title = _("Reference Samples")
        self.icon = "++resource++bika.lims.images/referencesample_big.png"
        self.description = _("")
        self.contentFilter = {'portal_type': 'ReferenceSample', 'path':{"query": ["/"], "level" : 0 }}
        self.content_add_actions = {}
        self.show_editable_border = False
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = {
            'ID': {'title': _('ID')},
            'Title': {'title': _('Title')},
            'Supplier': {'title': _('Supplier')},
            'Manufacturer': {'title': _('Manufacturer')},
            'CatalogueNumber': {'title': _('Catalogue Number')},
            'LotNumber': {'title': _('Lot Number')},
            'Definition': {'title': _('Reference Definition')},
            'DateSampled': {'title': _('Date Sampled')},
            'DateReceived': {'title': _('Date Received')},
            'ExpiryDate': {'title': _('Expiry Date')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'CatalogueNumber',
                         'LotNumber',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate',
                         'state_title']},
            {'title': _('Current'), 'id':'current',
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'CatalogueNumber',
                         'LotNumber',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'title': _('Expired'), 'id':'expired',
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'CatalogueNumber',
                         'LotNumber',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
            {'title': _('Disposed'), 'id':'disposed',
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Manufacturer',
                         'CatalogueNumber',
                         'LotNumber',
                         'Definition',
                         'DateSampled',
                         'DateReceived',
                         'ExpiryDate']},
        ]

    def folderitems(self):
        items = super(ReferenceSamplesView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ID'] = obj.id
            items[x]['Supplier'] = obj.aq_parent.Title()
            items[x]['Manufacturer'] = obj.getReferenceManufacturer() and \
                 obj.getReferenceManufacturer().Title() or ''
            items[x]['CatalogueNumber'] = obj.getCatalogueNumber()
            items[x]['LotNumber'] = obj.getLotNumber()
            items[x]['Definition'] = obj.getReferenceDefinition() and \
                 obj.getReferenceDefinition().Title() or ''
            items[x]['DateSampled'] = \
                 TimeOrDate(self.context, obj.getDateSampled(), long_format=0)
            items[x]['DateReceived'] = \
                 TimeOrDate(self.context, obj.getDateReceived(), long_format=0)
            items[x]['ExpiryDate'] = \
                 TimeOrDate(self.context, obj.getExpiryDate(), long_format=0)

            after_icons = ''
            if obj.getBlank():
                after_icons += "<img src='++resource++bika.lims.images/blank.png' title='Blank'>"
            if obj.getHazardous():
                after_icons += "<img src='++resource++bika.lims.images/hazardous.png' title='Hazardous'>"
            items[x]['replace']['ID'] = "<a href='%s'>%s</a>&nbsp;%s" % \
                 (items[x]['url'], items[x]['ID'], after_icons)

        return items
