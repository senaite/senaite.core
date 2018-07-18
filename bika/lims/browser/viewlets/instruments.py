# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from plone.app.layout.viewlets import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class InstrumentQCFailuresViewlet(ViewletBase):
    """ Print a viewlet showing failed instruments
    """
    index = ViewPageTemplateFile("templates/instrument_qc_failures_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(InstrumentQCFailuresViewlet, self).__init__(
            context, request, view, manager=manager)
        self.nr_failed = 0
        self.failed = {
            'out-of-date': [],
            'qc-fail': [],
            'next-test': [],
            'validation': [],
            'calibration': [],
        }

    def get_failed_instruments(self):
        """ Find all active instruments who have failed QC tests
            Find instruments whose certificate is out of date
            Find instruments which are disposed until next calibration test

            Return a dictionary with all info about expired/invalid instruments

        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        insts = bsc(portal_type='Instrument', inactive_state='active')
        for i in insts:
            i = i.getObject()
            instr = {
                'uid': i.UID(),
                'title': i.Title(),
            }
            if i.isValidationInProgress():
                instr['link'] = '<a href="%s/validations">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['validation'].append(instr)
            elif i.isCalibrationInProgress():
                instr['link'] = '<a href="%s/calibrations">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['calibration'].append(instr)
            elif i.isOutOfDate():
                instr['link'] = '<a href="%s/certifications">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['out-of-date'].append(instr)
            elif not i.isQCValid():
                instr['link'] = '<a href="%s/referenceanalyses">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['qc-fail'].append(instr)
            elif i.getDisposeUntilNextCalibrationTest():
                instr['link'] = '<a href="%s/referenceanalyses">%s</a>' % (
                    i.absolute_url(), i.Title()
                )
                self.nr_failed += 1
                self.failed['next-test'].append(instr)

    def render(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        allowed = 'LabManager' in roles or 'Manager' in roles

        self.get_failed_instruments()

        if allowed and self.nr_failed:
            return self.index()
        else:
            return ""
