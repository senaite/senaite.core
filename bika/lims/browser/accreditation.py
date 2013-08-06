from bika.lims.controlpanel.bika_analysisservices import AnalysisServicesView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import to_utf8 as _c
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements

class AccreditationView(AnalysisServicesView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(AccreditationView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title',
                              'getAccredited': True,
                              'inactive_state': 'active'}
        self.context_actions = {}
        self.icon = self.portal_url + "/++resource++bika.lims.images/accredited_big.png"
        self.title = _("Accreditation")

        lab = context.bika_setup.laboratory
        accredited = lab.getLaboratoryAccredited()
        self.mapping = {'accredited': accredited,
                        'labname': lab.getName(),
                        'labcountry': lab.getPhysicalAddress().get('country', ''),
                        'confidence': lab.getConfidence(),
                        'abbr': lab.getAccreditationBody(),
                        'body': lab.getAccreditationBodyLong(),
                        'url': lab.getAccreditationBodyURL(),
                        'accr': lab.getAccreditation(),
                        'ref': lab.getAccreditationReference()
                        }
        if accredited:
            translate = self.context.translate
            msg = translate(_("${labname} has been accredited as ${accr} " +
                    "conformant by ${abbr}, (${body}). ${abbr} is " +
                    "recognised by government as a national " +
                    "accreditation body in ${labcountry}. ",
                    mapping=self.mapping))

        else:
            msg = _("The lab is not accredited, or accreditation has not "
                    "been configured. ")
        self.description = context.translate(_c(msg))
        msg = _("All Accredited analysis services are listed here.")
        self.description = "%s<p><br/>%s</p>" % (self.description,
                                               context.translate(_c(msg)))

        self.show_select_column = False
        request.set('disable_border', 1)

        self.columns = {
            'Title': {'title': _('Service'), 'sortable': False},
            'Keyword': {'title': _('Keyword'), 'sortable': False},
            'Category': {'title': _('Category'), 'sortable': False},
            'Department': {'title': _('Department'), 'sortable': False},
            'Instrument': {'title': _('Instrument'), 'sortable': False},
            'Unit': {'title': _('Unit'), 'sortable': False},
            'Price': {'title': _('Price'), 'sortable': False},
            'MaxTimeAllowed': {'title': _('Max Time'), 'sortable': False},
            'DuplicateVariation': {'title': _('Dup Var'), 'sortable': False},
            'Calculation': {'title': _('Calculation'), 'sortable': False},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [{'id': 'empty'}, ],  # none
             'columns': ['Title',
                         'Keyword',
                         'Category',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         ],
             },
        ]

    def selected_cats(self, items):
        """return a list of all categories with accredited services
        """
        cats = []
        for item in items:
            if 'category' in item and item['category'] not in cats:
                cats.append(item['category'])
        return cats
