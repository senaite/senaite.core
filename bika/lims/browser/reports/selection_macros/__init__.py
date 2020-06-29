# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.utils import getUsers
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF
from plone.memoize import ram
from time import time


def update_timer():
    """
    This function sets the time between updates of cached values
    """
    return time() // (24 *60 * 60)


def _cache_key_select_state(method, self, workflow_id, field_id, field_title):
    """
    This function returns the key used to decide if select_state has to be recomputed
    """
    key = update_timer(), workflow_id, field_id, field_title
    return key


def _cache_key_select_analysiscategory(method, self, style=None):
    """
    This function returns the key used to decide if method select_analysiscategory has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_analysisservice(method, self, allow_blank,
                                      multiselect, style=None):
    """
    This function returns the key used to decide if method select_analysisservice has to be recomputed
    """
    key = update_timer(), allow_blank, multiselect, style
    return key


def _cache_key_select_analysisspecification(method, self, style=None):
    """
    This function returns the key used to decide if method select_analysisspecification has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_analyst(method, self, allow_blank=False, style=None):
    """
    This function returns the key used to decide if method select_analyst has to be recomputed
    """
    key = update_timer(),allow_blank, style
    return key


def _cache_key_select_user(method, self, allow_blank=True, style=None):
    """
    This function returns the key used to decide if method select_user has to be recomputed
    """
    key = update_timer(), allow_blank, style
    return key


def _cache_key_select_client(method, self, style=None):
    """
    This function returns the key used to decide if method select_client has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_contact(method, self, style=None):
    """
    This function returns the key used to decide if method select_contact has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_daterange(method, self, field_id, field_title, style=None):
    """
    This function returns the key used to decide if method select_daterange has to be recomputed
    """
    key = update_timer(), field_id, field_title, style
    return key


def _cache_key_select_instrument(method, self, style=None):
    """
    This function returns the key used to decide if method select_instrument has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_period(method, self, style=None):
    """
    This function returns the key used to decide if method select_period has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_profile(method, self, style=None):
    """
    This function returns the key used to decide if method select_profile has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_supplier(method, self, style=None):
    """
    This function returns the key used to decide if method select_supplier has to be recomputed
    """
    key = update_timer(), style
    return key

def _cache_key_select_reference_sample(method, self, style=None):
    """
    This function returns the key used to decide if method select_reference_sample has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_reference_service(method, self, style=None):
    """
    This function returns the key used to decide if method select_reference_service has to be recomputed
    """
    key = update_timer(), style
    return key


def _cache_key_select_sample_type(method, self, allow_blank=True, multiselect=False, style=None):
    """
    This function returns the key used to decide if method select_sample_type has to be recomputed
    """
    key = update_timer(), allow_blank, multiselect, style
    return key


def _cache_key_select_groupingperiod(method, self, allow_blank=True, multiselect=False, style=None):
    """
    This function returns the key used to decide if method select_groupingperiod has to be recomputed
    """
    key = update_timer(), allow_blank, multiselect, style
    return key


def _cache_key_select_output_format(method, self, style=None):
    """
    This function returns the key used to decide if method select_output_format has to be recomputed
    """
    key = update_timer(), style
    return key


class SelectionMacrosView(BrowserView):
    """ Display snippets for the query form, and
        parse their results to contentFilter

    These methods are called directlly from tal:

        context/@@selection_macros/analysts

    To parse form values in reports:

        python:view.selection_macros.parse_analysisservice(allow_blank=False)

    The parse_ functions return {'contentFilter': (k,v),
                                 'parms': (k,v),
                                 'title': string
                                 }

    """

    def __init__(self, context, request):
        super(SelectionMacrosView, self).__init__(context, request)
        self.bc = self.bika_catalog
        self.bac = self.bika_analysis_catalog
        self.bsc = self.bika_setup_catalog
        self.pc = self.portal_catalog
        self.rc = self.reference_catalog

    select_analysiscategory_pt = ViewPageTemplateFile(
        "select_analysiscategory.pt")

    @ram.cache(_cache_key_select_analysiscategory)
    def select_analysiscategory(self, style=None):
        self.style = style
        self.analysiscategories = self.bsc(portal_type='AnalysisCategory',
                                           sort_on='sortable_title')
        return self.select_analysiscategory_pt()

    select_analysisservice_pt = ViewPageTemplateFile("select_analysisservice.pt")

    @ram.cache(_cache_key_select_analysisservice)
    def select_analysisservice(self, allow_blank=True, multiselect=False,
                               style=None):
        self.style = style
        self.allow_blank = allow_blank
        self.multiselect = multiselect
        self.analysisservices = self.bsc(portal_type='AnalysisService',
                                         sort_on='sortable_title')
        return self.select_analysisservice_pt()

    def parse_analysisservice(self, request):
        val = request.form.get("ServiceUID", "")
        if val:
            if not type(val) in (list, tuple):
                val = (val,)  # Single service
            val = [self.rc.lookupObject(s) for s in val]
            uids = [o.UID() for o in val]
            titles = [o.Title() for o in val]
            res = {}
            res['contentFilter'] = ('getServiceUID', uids)
            res['parms'] = {'title': _("Services"), 'value': ','.join(titles)}
            res['titles'] = ','.join(titles)
            return res

    select_analysisspecification_pt = ViewPageTemplateFile(
        "select_analysisspecification.pt")

    @ram.cache(_cache_key_select_analysisspecification)
    def select_analysisspecification(self, style=None):
        self.style = style
        res = []
        bsc = getToolByName(self.context, "bika_setup_catalog")
        for s in bsc(portal_type='AnalysisSpec'):
            res.append({'uid': s.UID, 'title': s.Title})
        self.specs = res
        return self.select_analysisspecification_pt()

    select_analyst_pt = ViewPageTemplateFile("select_analyst.pt")

    @ram.cache(_cache_key_select_analyst)
    def select_analyst(self, allow_blank=False, style=None):
        self.style = style
        self.analysts = getUsers(self.context,
                                 ['Manager', 'Analyst', 'LabManager'],
                                 allow_blank)
        return self.select_analyst_pt()

    select_user_pt = ViewPageTemplateFile("select_user.pt")

    @ram.cache(_cache_key_select_user)
    def select_user(self, allow_blank=True, style=None):
        self.style = style
        self.allow_blank = allow_blank
        self.users = getUsers(self.context, None, allow_blank)
        return self.select_user_pt()

    select_client_pt = ViewPageTemplateFile("select_client.pt")

    @ram.cache(_cache_key_select_client)
    def select_client(self, style=None):
        self.style = style
        self.clients = self.pc(portal_type='Client',
                               sort_on='sortable_title')
        return self.select_client_pt()

    def parse_client(self, request):
        val = request.form.get("ClientUID", "")
        if val:
            obj = val and self.rc.lookupObject(val)
            title = obj.Title()
            res = {}
            res['contentFilter'] = ('getClientUID', val)
            res['parms'] = {'title': _("Client"), 'value': title}
            res['titles'] = title
            return res

    select_contact_pt = ViewPageTemplateFile("select_contact.pt")

    @ram.cache(_cache_key_select_contact)
    def select_contact(self, style=None):
        self.style = style
        self.contacts = self.pc(portal_type='Contact', is_active=True,
                                sort_on='sortable_title')
        return self.select_contact_pt()

    select_daterange_pt = ViewPageTemplateFile("select_daterange.pt")

    def _select_daterange(self, field_id, field_title, style=None):
        self.style = style
        self.field_id = field_id
        self.field_title = _(field_title)
        return self.select_daterange_pt()

    @ram.cache(_cache_key_select_daterange)
    def select_daterange(self, field_id, field_title, style=None):
        return self._select_daterange(field_id, field_title, style)

    @ram.cache(_cache_key_select_daterange)
    def select_daterange_requested(self, field_id, field_title, style=None):
        return self._select_daterange(field_id, field_title, style)

    @ram.cache(_cache_key_select_daterange)
    def select_daterange_created(self, field_id, field_title, style=None):
        return self._select_daterange(field_id, field_title, style)

    @ram.cache(_cache_key_select_daterange)
    def select_daterange_received(self, field_id, field_title, style=None):
        return self._select_daterange(field_id, field_title, style)

    @ram.cache(_cache_key_select_daterange)
    def select_daterange_published(self, field_id, field_title, style=None):
        return self._select_daterange(field_id, field_title, style)

    @ram.cache(_cache_key_select_daterange)
    def select_daterange_loaded(self, field_id, field_title, style=None):
        return self._select_daterange(field_id, field_title, style)

    def parse_daterange(self, request, field_id, field_title):
        from_date = request.get('%s_fromdate' % field_id, None)
        from_date = from_date and from_date + ' 00:00' or None
        to_date = request.get('%s_todate' % field_id, None)
        to_date = to_date and to_date + ' 23:59' or None
        if from_date and to_date:
            query = {'query': [from_date, to_date], 'range': 'min:max'}
        elif from_date or to_date:
            query = {'query': from_date or to_date,
                     'range': from_date and 'min' or 'max'}
        else:
            return None

        if from_date and to_date:
            parms = translate(_("From ${start_date} to ${end_date}",
                               mapping={"start_date":from_date, "end_date":to_date}))
        elif from_date:
            parms = translate(_("Before ${start_date}",
                               mapping={"start_date":from_date}))
        elif to_date:
            parms = translate(_("After ${end_date}",
                               mapping={"end_date":to_date}))

        res = {}
        res['contentFilter'] = (field_id, query)
        res['parms'] = {'title': field_title, 'value': parms}
        res['titles'] = parms
        return res

    select_instrument_pt = ViewPageTemplateFile("select_instrument.pt")

    @ram.cache(_cache_key_select_instrument)
    def select_instrument(self, style=None):
        self.style = style
        self.instruments = self.bsc(portal_type='Instrument',
                                    is_active=True,
                                    sort_on='sortable_title')
        return self.select_instrument_pt()

    select_period_pt = ViewPageTemplateFile("select_period.pt")

    @ram.cache(_cache_key_select_period)
    def select_period(self, style=None):
        self.style = style
        return self.select_period_pt()

    select_profile_pt = ViewPageTemplateFile("select_profile.pt")

    @ram.cache(_cache_key_select_profile)
    def select_profile(self, style=None):
        self.style = style
        self.analysisprofiles = self.bsc(portal_type='AnalysisProfile',
                                         is_active=True,
                                         sort_on='sortable_title')
        return self.select_profile_pt()

    select_supplier_pt = ViewPageTemplateFile("select_supplier.pt")

    @ram.cache(_cache_key_select_supplier)
    def select_supplier(self, style=None):
        self.style = style
        self.suppliers = self.bsc(portal_type='Supplier', is_active=True,
                                  sort_on='sortable_title')
        return self.select_supplier_pt()

    select_reference_sample_pt = ViewPageTemplateFile(
        "select_reference_sample.pt")

    @ram.cache(_cache_key_select_reference_sample)
    def select_reference_sample(self, style=None):
        self.style = style
        return self.select_reference_sample_pt()

    select_reference_service_pt = ViewPageTemplateFile(
        "select_reference_service.pt")

    @ram.cache(_cache_key_select_reference_service)
    def select_reference_service(self, style=None):
        self.style = style
        return self.select_reference_service_pt()

    select_state_pt = ViewPageTemplateFile("select_state.pt")

    def _select_state(self, workflow_id, field_id, field_title, style=None):
        self.style = style
        self.field_id = field_id
        self.field_title = field_title
        states = self.portal_workflow[workflow_id].states
        self.states = []
        for state_id in states:
            state = states[state_id]
            self.states.append({'id': state.getId(), 'title': state.title})
        return self.select_state_pt()

    @ram.cache(_cache_key_select_state)
    def select_state(self, workflow_id, field_id, field_title, style=None):
        return self._select_state(workflow_id, field_title, field_title, style)

    @ram.cache(_cache_key_select_state)
    def select_state_analysis(self, workflow_id, field_id, field_title, style=None):
        return self._select_state(workflow_id, field_id, field_title, style)

    def parse_state(self, request, workflow_id, field_id, field_title):
        val = request.form.get(field_id, "")
        states = self.portal_workflow[workflow_id].states
        if val in states:
            state_title = states[val].title
            res = {}
            res['contentFilter'] = (field_id, val)
            res['parms'] = {'title': _('State'), 'value': state_title}
            res['titles'] = state_title
            return res

    select_sampletype_pt = ViewPageTemplateFile("select_sampletype.pt")

    @ram.cache(_cache_key_select_sample_type)
    def select_sampletype(self, allow_blank=True, multiselect=False, style=None):
        self.style = style
        self.allow_blank = allow_blank
        self.multiselect = multiselect
        self.sampletypes = self.bsc(portal_type='SampleType',
                                    is_active=True,
                                    sort_on='sortable_title')
        return self.select_sampletype_pt()

    def parse_sampletype(self, request):
        val = request.form.get("SampleTypeUID", "")
        if val:
            obj = val and self.rc.lookupObject(val)
            title = obj.Title()
            res = {}
            res['contentFilter'] = ('getSampleTypeUID', val)
            res['parms'] = {'title': _("Sample Type"), 'value': title}
            res['titles'] = title
            return res

    select_groupingperiod_pt = ViewPageTemplateFile("select_groupingperiod.pt")

    @ram.cache(_cache_key_select_groupingperiod)
    def select_groupingperiod(self, allow_blank=True, multiselect=False,
                              style=None):
        self.style = style
        self.allow_blank = allow_blank
        return self.select_groupingperiod_pt()

    select_output_format_pt = ViewPageTemplateFile("select_output_format.pt")

    @ram.cache(_cache_key_select_output_format)
    def select_output_format(self, style=None):
        self.style = style
        return self.select_output_format_pt()
