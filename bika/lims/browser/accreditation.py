# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.controlpanel.bika_analysisservices import AnalysisServicesView
from bika.lims.utils import t
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements


class AccreditationView(AnalysisServicesView):
    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(AccreditationView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'AnalysisService',
            'sort_on': 'sortable_title',
            'getAccredited': True,
            'inactive_state': 'active'}
        self.context_actions = {}
        self.title = self.context.translate(_("Accreditation"))
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/accredited_big.png"

        lab = context.bika_setup.laboratory
        accredited = lab.getLaboratoryAccredited()
        self.mapping = {
            'lab_is_accredited':
                accredited,
            'lab_name':
                safe_unicode(lab.getName()),
            'lab_country':
                safe_unicode(lab.getPhysicalAddress().get('country', '')),
            'confidence':
                safe_unicode(lab.getConfidence()),
            'accreditation_body_abbr':
                safe_unicode(lab.getAccreditationBody()),
            'accreditation_body_name':
                safe_unicode(lab.getAccreditationBodyURL()),
            'accreditation_standard':
                safe_unicode(lab.getAccreditation()),
            'accreditation_reference':
                safe_unicode(lab.getAccreditationReference())
        }
        if accredited:
            self.description = t(_(
                safe_unicode(lab.getAccreditationPageHeader()),
                mapping=self.mapping
            ))
        else:
            self.description = t(_(
                "The lab is not accredited, or accreditation has not been "
                "configured. "
            ))
        msg = t(_("All Accredited analysis services are listed here."))
        self.description = "%s<p><br/>%s</p>" % (self.description, msg)

        self.show_select_column = False
        request.set('disable_border', 1)

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [{'id': 'empty'}, ],  # none
             'columns': ['Title',
                         'Keyword',
                         'Price',
                         'MaxTimeAllowed',
                         'DuplicateVariation',
                         ],
             },
        ]

        if not self.context.bika_setup.getShowPrices():
            self.review_states[0]['columns'].remove('Price')

    def selected_cats(self, items):
        """return a list of all categories with accredited services
        """
        cats = []
        for item in items:
            if 'category' in item and item['category'] not in cats:
                cats.append(item['category'])
        return cats
