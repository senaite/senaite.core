from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.content.analysisservice import getContainers
from Products.CMFCore.utils import getToolByName
import json, plone
import plone.protect
from magnitude import mg, MagnitudeError
import re

### AJAX methods for AnalysisService context

# ajax Preservaition/Container widget filter
# in preservationwidget rows,we get st_uid, pres_uid and minvol.
# in Service Setup context, all we get is [pres_uid,]

class ajaxGetContainers(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        uc = getToolByName(self, 'uid_catalog')
        st_uid = self.request.get('st_uid', [])
        st = st_uid and uc(UID=st_uid)[0].getObject() or None
        allow_blank = self.request.get('allow_blank', False) == 'true'
        pres_uid = json.loads(self.request.get('pres_uid', '[]'))
        minvol = self.request.get('minvol', '').split(" ")
        try:
            minvol = mg(float(minvol[0]), " ".join(minvol[1:]))
        except:
            minvol = mg(0)

        if not type(pres_uid) in (list, tuple):
            pres_uid = [pres_uid,]
        preservations = [p and uc(UID=p)[0].getObject() or '' for p in pres_uid]

        containers = getContainers(self.context,
                                   preservation = preservations and preservations or [],
                                   minvol = minvol,
                                   allow_blank = allow_blank)

        return json.dumps(containers)
