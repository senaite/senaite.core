# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.worksheet.tools import (checkUserAccess,
                                               showRejectionMessage)
from bika.lims.browser.worksheet.views import (AnalysesTransposedView,
                                               AnalysesView)
from bika.lims.config import WORKSHEET_LAYOUT_OPTIONS
from bika.lims.utils import getUsers
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements


class ManageResultsView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("../templates/results.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.getAnalysts = getUsers(context, ['Manager', 'LabManager', 'Analyst'])
        self.layout_displaylist = WORKSHEET_LAYOUT_OPTIONS

    def __call__(self):

        # Deny access to foreign analysts
        if checkUserAccess(self.context, self.request) is False:
            return []

        showRejectionMessage(self.context)

        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"

        # Save the results layout
        rlayout = self.request.get('resultslayout', '')
        if rlayout and rlayout in WORKSHEET_LAYOUT_OPTIONS.keys() \
           and rlayout != self.context.getResultsLayout():
            self.context.setResultsLayout(rlayout)
            message = _("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')

        # Here we create an instance of WorksheetAnalysesView
        if self.context.getResultsLayout() == '2':
            # Transposed view
            self.Analyses = AnalysesTransposedView(self.context, self.request)
        else:
            # Classic view
            self.Analyses = AnalysesView(self.context, self.request)

        self.analystname = self.context.getAnalystName()
        self.instrumenttitle = self.context.getInstrument() and self.context.getInstrument().Title() or ''

        # Check if the instruments used are valid
        self.checkInstrumentsValidity()

        return self.template()

    def getInstruments(self):
        # TODO: Return only the allowed instruments for at least one contained analysis
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(o.UID, o.Title) for o in
                              bsc(portal_type='Instrument',
                                  inactive_state='active')]
        o = self.context.getInstrument()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return DisplayList(list(items))

    def isAssignmentAllowed(self):
        workflow = getToolByName(self.context, 'portal_workflow')
        review_state = workflow.getInfoFor(self.context, 'review_state', '')
        edit_states = ['open', 'attachment_due', 'to_be_verified']
        return review_state in edit_states \
            and self.context.checkUserManage()

    def getWideInterims(self):
        """ Returns a dictionary with the analyses services from the current
            worksheet which have at least one interim with 'Wide' attribute
            set to true and state 'sample_received'
            The structure of the returned dictionary is the following:
            <Analysis_keyword>: {
                'analysis': <Analysis_name>,
                'keyword': <Analysis_keyword>,
                'interims': {
                    <Interim_keyword>: {
                        'value': <Interim_default_value>,
                        'keyword': <Interim_key>,
                        'title': <Interim_title>
                    }
                }
            }
        """
        outdict = {}
        allowed_states = ['sample_received']
        for analysis in self._getAnalyses():
            wf = getToolByName(analysis, 'portal_workflow')
            if wf.getInfoFor(analysis, 'review_state') not in allowed_states:
                continue

            if analysis.getKeyword() in outdict.keys():
                continue

            calculation = analysis.getCalculation()
            if not calculation:
                continue

            andict = {'analysis': analysis.Title(),
                      'keyword': analysis.getKeyword(),
                      'interims': {}}

            # Analysis Service interim defaults
            for field in analysis.getInterimFields():
                if field.get('wide', False):
                    andict['interims'][field['keyword']] = field

            # Interims from calculation
            for field in calculation.getInterimFields():
                if field['keyword'] not in andict['interims'].keys() \
                   and field.get('wide', False):
                    andict['interims'][field['keyword']] = field

            if andict['interims']:
                outdict[analysis.getKeyword()] = andict
        return outdict

    def checkInstrumentsValidity(self):
        """ Checks the validity of the instruments used in the Analyses
            If an analysis with an invalid instrument (out-of-date or
            with calibration tests failed) is found, a warn message
            will be displayed.
        """
        invalid = []
        ans = self._getAnalyses()
        for an in ans:
            valid = an.isInstrumentValid()
            if not valid:
                inv = '%s (%s)' % (safe_unicode(an.Title()), safe_unicode(an.getInstrument().Title()))
                if inv not in invalid:
                    invalid.append(inv)
        if len(invalid) > 0:
            message = _("Some analyses use out-of-date or uncalibrated instruments. Results edition not allowed")
            message = "%s: %s" % (message, (', '.join(invalid)))
            self.context.plone_utils.addPortalMessage(message, 'warn')

    def _getAnalyses(self):
        """
        This function returns a list with the analyses related to the worksheet
        and filtered by the current selected department in the department
        porlet.
        @returna list of analyses objects.
        """
        ans = [a for a in self.context.getAnalyses() if self._isItemAllowed(a)]
        return ans

    def _isItemAllowed(self, obj):
        """
        It checks if the analysis service can be added to the list depending
        on the department filter. If the analysis service is not assigned to a
        department, show it.
        If department filtering is disabled in bika_setup, will return True.
        @Obj: it is an analysis object.
        @return: boolean
        """
        if not self.context.bika_setup.getAllowDepartmentFiltering():
            return True
        # Gettin the department from analysis service
        serv_dep = obj.getDepartment()
        result = True
        if serv_dep:
            # Getting the cookie value
            cookie_dep_uid = self.request.get('filter_by_department_info', '')
            # Comparing departments' UIDs
            result = True if serv_dep.UID() in\
                cookie_dep_uid.split(',') else False
        return result
