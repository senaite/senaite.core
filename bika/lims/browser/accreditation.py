# encoding=utf-8

from Products.CMFPlone.utils import safe_unicode
from bika.lims.controlpanel.bika_analysisservices import AnalysisServicesView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements


class AccreditationView(AnalysisServicesView):
    """
    >>> portal = layer['portal']
    >>> portal_url = portal.absolute_url()
    >>> from plone.app.testing import SITE_OWNER_NAME
    >>> from plone.app.testing import SITE_OWNER_PASSWORD

    >>> browser = layer['getBrowser'](portal)
    >>> browser.open(portal_url+"/accreditation")
    >>> 'SAI is the' in browser.contents
    True

    """
    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(AccreditationView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisService',
                              'sort_on': 'sortable_title',
                              'getAccredited': True,
                              'inactive_state': 'active'}
        self.context_actions = {}
        self.icon = self.portal_url + "/++resource++bika.lims.images/accredited_big.png"
        self.title = self.context.translate(_("Accreditation"))

        lab = context.bika_setup.laboratory
        accredited = lab.getLaboratoryAccredited()
        self.mapping = {'lab_is_accredited': accredited,
                        'lab_name': safe_unicode(lab.getName()),
                        'lab_country': safe_unicode(lab.getPhysicalAddress().get('country', '')),
                        'confidence': safe_unicode(lab.getConfidence()),
                        'accreditation_body_abbr': safe_unicode(lab.getAccreditationBody()),
                        'accreditation_body_name': safe_unicode(lab.getAccreditationBodyURL()),
                        'accreditation_standard': safe_unicode(lab.getAccreditation()),
                        'accreditation_reference': safe_unicode(lab.getAccreditationReference())
        }
        if accredited:
            self.description = t(_(safe_unicode(lab.getAccreditationPageHeader()),
                                   mapping=self.mapping
            ))
        else:
            self.description = t(_("The lab is not accredited, or accreditation has "
                    "not been configured. "))
        msg = t(_("All Accredited analysis services are listed here."))
        self.description = "%s<p><br/>%s</p>" % (self.description, msg)

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
