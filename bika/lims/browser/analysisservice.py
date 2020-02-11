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

import json

import plone
import plone.protect
from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.content.analysisservice import getContainers
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.jsonapi import get_include_fields
from bika.lims.jsonapi import load_field_values
from bika.lims.permissions import ViewLogTab
from bika.lims.utils import get_image
from magnitude import mg
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.i18n.locales import locales
from zope.interface import implements


class AnalysisServiceInfoView(BrowserView):
    """Show details of the Analysis Service
    """
    template = ViewPageTemplateFile("templates/analysisservice_info.pt")

    def __init__(self, context, request):
        super(AnalysisServiceInfoView, self).__init__(context, request)

    def __call__(self):
        # disable the editable border
        self.request.set("disable_border", 1)
        return self.template()

    @view.memoize
    def show_prices(self):
        """Checks if prices should be shown or not
        """
        setup = api.get_setup()
        return setup.getShowPrices()

    @view.memoize
    def get_currency_symbol(self):
        """Get the currency Symbol
        """
        locale = locales.getLocale('en')
        setup = api.get_setup()
        currency = setup.getCurrency()
        return locale.numbers.currencies[currency].symbol

    def get_icon_for(self, typename):
        image = "{}_big.png".format(typename)
        return get_image(
            image, width="20px", style="vertical-align: baseline;")

    @view.memoize
    def get_service(self):
        service_uid = self.request.form.get("service_uid")
        return api.get_object_by_uid(service_uid, None)

    @view.memoize
    def get_service_url(self):
        service = self.get_service()
        return api.get_url(service)

    @view.memoize
    def is_accredited(self):
        service = self.get_service()
        return service.getAccredited()

    def get_analysis_or_service(self):
        analysis = self.get_analysis()
        if analysis:
            return analysis
        return self.get_service()

    def get_methods(self):
        if not self.get_service():
            return None
        return self.get_service().getMethods()

    @view.memoize
    def get_analysis(self):
        analysis_uid = self.request.form.get("analysis_uid")
        return api.get_object_by_uid(analysis_uid, None)

    @view.memoize
    def get_calculation(self):
        if not self.get_analysis_or_service():
            return None
        return self.get_analysis_or_service().getCalculation()

    def get_dependent_services(self):
        if not self.get_calculation():
            return []
        return self.get_calculation().getDependentServices()

    def get_calculation_dependencies(self):
        if not self.get_calculation():
            return []
        return self.get_calculation().getCalculationDependencies()

    def can_view_logs_of(self, obj):
        """Checks if the current user is allowed to see the logs
        """
        return check_permission(ViewLogTab, obj)

    def analysis_log_view(self):
        """Get the log view of the requested analysis
        """
        service = self.get_analysis_or_service()
        if not self.can_view_logs_of(service):
            return None
        view = api.get_view("auditlog", context=service, request=self.request)
        view.update()
        view.before_render()
        return view


class ajaxGetContainers(BrowserView):
    """ajax Preservation/Container widget filter
    request values:
    - allow_blank: print blank value in return
    - show_container_types
    - show_containers
    - minvol: magnitude (string).
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)

        allow_blank = self.request.get('allow_blank', False) == 'true'
        show_container_types = json.loads(self.request.get('show_container_types', 'true'))
        show_containers = json.loads(self.request.get('show_containers', 'true'))
        minvol = self.request.get("minvol", "0")
        try:
            minvol = minvol.split()
            minvol = mg(float(minvol[0]), " ".join(minvol[1:]))
        except:
            minvol = mg(0)

        containers = getContainers(
            self.context,
            minvol=minvol,
            allow_blank=allow_blank,
            show_containers=show_containers,
            show_container_types=show_container_types,
        )

        return json.dumps(containers)


class ajaxGetServiceInterimFields:
    "Tries to fall back to Calculation for defaults"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        service_url = self.request['service_url']
        service_id = service_url.split('/')[-1]
        services = bsc(portal_type='AnalysisService', id=service_id)
        if services:
            service = services[0].getObject()
            service_interims = service.getInterimFields()
        else:
            # portal_factory has no service
            return

        calc = service.getCalculation()
        if calc:
            calc_interims = calc.getInterimFields()
        else:
            calc_interims = []

        # overwrite existing fields in position
        for s_i in service_interims:
            placed = 0
            for c_i in calc_interims:
                if s_i['keyword'] == c_i['keyword']:
                    c_i['value'] = s_i['value']
                    placed = 1
                    break
            if placed:
                continue
            # otherwise, create new ones (last)
            calc_interims.append(s_i)

        return json.dumps(calc_interims)


class JSONReadExtender(object):
    """- Adds fields to Analysis Service:

    MethodInstruments - A dictionary of instruments:
        keys: Method UID
        values: list of instrument UIDs

    """

    implements(IJSONReadExtender)
    adapts(IAnalysisService)

    def __init__(self, context):
        self.context = context

    def service_info(self, service):
        ret = {
            "Category": service.getCategory().Title(),
            "Category_uid": service.getCategory().UID(),
            "Service": service.Title(),
            "Service_uid": service.UID(),
            "Keyword": service.getKeyword(),
            "PointOfCapture": service.getPointOfCapture(),
            "PointOfCapture_title": POINTS_OF_CAPTURE.getValue(service.getPointOfCapture()),
        }
        return ret

    def __call__(self, request, data):
        include_fields = get_include_fields(request)

        if not include_fields or "MethodInstruments" in include_fields:
            data["MethodInstruments"] = {}
            for method in self.context.getAvailableMethods():
                for instrument in method.getInstruments():
                    if method.UID() not in data["MethodInstruments"]:
                        data["MethodInstruments"][method.UID()] = []
                    data["MethodInstruments"][method.UID()].append(
                        load_field_values(instrument, include_fields=[]))
