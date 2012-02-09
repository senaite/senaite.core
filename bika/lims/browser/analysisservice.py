from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.content.analysisservice import getContainers
from Products.CMFCore.utils import getToolByName
import json, plone
import plone.protect
from magnitude import mg
import re

### AJAX methods for AnalysisService context

# partition setup widget

class ajaxGetContainers(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        uc = getToolByName(self, 'uid_catalog')
        st_uid = self.request['st_uid']
        st = uc(UID=st_uid)[0].getObject()
        pres_uid = self.request['pres_uid']
        vol = self.request['vol'] and self.request['vol'] or "0 ml"
        pres = uc(UID=pres_uid)
        if pres:
            pres = pres[0].getObject()
            containers = getContainers(self.context,
                                       preservation=pres,
                                       minvol=minvol)
        else:
            containers = getContainers(self.context, minvol=vol)
        return json.dumps(containers)
