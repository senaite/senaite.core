from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.content.analysisservice import getContainers
from Products.CMFCore.utils import getToolByName
import json, plone
import plone.protect
from magnitude import mg, MagnitudeError
import re

### AJAX methods for AnalysisService context

# partition setup widget

class ajaxGetContainers(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        uc = getToolByName(self, 'uid_catalog')
        st_uid = 'st_uid' in self.request and self.request['st_uid'] or ''
        st = st_uid and uc(UID=st_uid)[0].getObject() or None
        pres_uid = 'pres_uid' in self.request and self.request['pres_uid'] or ''
        minvol = 'minvol' in self.request and self.request['minvol'].split(" ") or []
        try:
            minvol = mg(float(minvol[0]), " ".join(minvol[1:]))
        except:
            minvol = mg(0)

        pres = pres_uid and uc(UID=pres_uid) or None
        if pres:
            pres = pres[0].getObject()
            containers = getContainers(self.context,
                                       preservation = pres,
                                       minvol = minvol)
        else:
            containers = getContainers(self.context,
                                       minvol = minvol)
        return json.dumps(containers)
