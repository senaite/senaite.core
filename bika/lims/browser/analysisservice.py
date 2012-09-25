from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.content.analysisservice import getContainers
from bika.lims.browser.bika_listing import BikaListingView
from Products.CMFCore.utils import getToolByName
import json, plone
import plone.protect
from magnitude import mg, MagnitudeError
import re

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

class ajaxGetPreservations(BrowserView):
    """ajax Preservations - for pre-preserved containers
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        container_uid = self.request.get('container_uid', [])
        container = bsc(UID=container_uid)
        if container:
            container = container[0].getObject()
            if container.getPrePreserved():
                preservation = container.getPreservation()
                if preservation:
                    return preservation.UID()
        return ''

class ajaxServicePopup(BrowserView):

    template = ViewPageTemplateFile("templates/analysisservice_popup.pt")

    def __init__(self, context, request):
        super(ajaxServicePopup, self).__init__(context, request)
        self.icon = "++resource++bika.lims.images/analysisservice_big.png"

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')

        service_title = self.request.get('service_title', '').strip()
        if not service_title:
            return ''

        brains = bsc(portal_type="AnalysisService", Title=service_title)
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

