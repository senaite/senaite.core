from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.jsonapi import load_field_values, get_include_fields
from bika.lims.utils import t
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.browser.log import LogView
from bika.lims.content.analysisservice import getContainers
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IJSONReadExtender
from Products.CMFCore.utils import getToolByName
from magnitude import mg, MagnitudeError
from zope.component import adapts
from zope.interface import implements
import json, plone
import plone.protect
import re
from bika.lims.utils import to_unicode

### AJAX methods for AnalysisService context

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
        uc = getToolByName(self, 'uid_catalog')

        allow_blank = self.request.get('allow_blank', False) == 'true'
        show_container_types = json.loads(self.request.get('show_container_types', 'true'))
        show_containers = json.loads(self.request.get('show_containers', 'true'))
        minvol = self.request.get("minvol", "0")
        try:
            minvol =  minvol.split()
            minvol = mg(float(minvol[0]), " ".join(minvol[1:]))
        except:
            minvol = mg(0)

        containers = getContainers(
            self.context,
            minvol = minvol,
            allow_blank = allow_blank,
            show_containers=show_containers,
            show_container_types=show_container_types,
        )

        return json.dumps(containers)

class ajaxServicePopup(BrowserView):

    template = ViewPageTemplateFile("templates/analysisservice_popup.pt")

    def __init__(self, context, request):
        super(ajaxServicePopup, self).__init__(context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisservice_big.png"

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        uc = getToolByName(self.context, 'uid_catalog')

        service_title = self.request.get('service_title', '').strip()
        if not service_title:
            return ''

        analysis = uc(UID=self.request.get('analysis_uid', None))
        if analysis:
            analysis = analysis[0].getObject()
            self.request['ajax_load'] = 1
            tmp = LogView(analysis, self.request)
            self.log = tmp.folderitems()
            self.log.reverse()
        else:
            self.log = []

        brains = bsc(portal_type="AnalysisService",
                     title=to_unicode(service_title))
        if not brains:
            return ''

        self.service = brains[0].getObject()

        self.calc = self.service.getCalculation()

        self.partsetup = self.service.getPartitionSetup()

        # convert uids to comma-separated list of display titles
        for i,ps in enumerate(self.partsetup):

            self.partsetup[i]['separate'] = \
                ps.has_key('separate') and _('Yes') or _('No')

            if type(ps['sampletype']) == str:
                ps['sampletype'] = [ps['sampletype'],]
            sampletypes = []
            for st in ps['sampletype']:
                res = bsc(UID=st)
                sampletypes.append(res and res[0].Title or st)
            self.partsetup[i]['sampletype'] = ", ".join(sampletypes)

            if ps.has_key('container'):
                if type(ps['container']) == str:
                    self.partsetup[i]['container'] = [ps['container'],]
                try:
                    containers = [bsc(UID=c)[0].Title for c in ps['container']]
                except IndexError:
                    containers = [c for c in ps['container']]
                self.partsetup[i]['container'] = ", ".join(containers)
            else:
                self.partsetup[i]['container'] = ''

            if ps.has_key('preservation'):
                if type(ps['preservation']) == str:
                    ps['preservation'] = [ps['preservation'],]
                try:
                    preservations = [bsc(UID=c)[0].Title for c in ps['preservation']]
                except IndexError:
                    preservations = [c for c in ps['preservation']]
                self.partsetup[i]['preservation'] = ", ".join(preservations)
            else:
                self.partsetup[i]['preservation'] = ''

        return self.template()


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

    ServiceDependencies - services our calculation depends on
    ServiceDependants - services who's calculation depend on us
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

        if not include_fields or "ServiceDependencies" in include_fields:
            data["ServiceDependencies"] = []
            calc = self.context.getCalculation()
            if calc:
                services = [self.service_info(service) for service
                    in calc.getCalculationDependencies(flat=True)
                    if service.UID() != self.context.UID()]
                data["ServiceDependencies"] = services

        if not include_fields or "ServiceDependants" in include_fields:
            data["ServiceDependants"] = []
            calcs = self.context.getBackReferences('CalculationAnalysisService')
            if calcs:
                for calc in calcs:
                    services = [self.service_info(service) for service
                        in calc.getCalculationDependants()
                        if service.UID() != self.context.UID()]
                    data["ServiceDependants"].extend(services)

        if not include_fields or "MethodInstruments" in include_fields:
            data["MethodInstruments"] = {}
            for method in self.context.getAvailableMethods():
                for instrument in method.getInstruments():
                    if method.UID() not in data["MethodInstruments"]:
                        data["MethodInstruments"][method.UID()] = []
                    data["MethodInstruments"][method.UID()].append(
                        load_field_values(instrument, include_fields=[]))
