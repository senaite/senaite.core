from bika.lims.browser import BrowserView
from Products.CMFCore.utils import getToolByName
import plone
import json

class ajaxGetInstruments(BrowserView):
    """ Returns a json list with the instruments assigned to the method
        with the following structure:
        [{'uid': <instrument_uid>,
          'title': <instrument_absolute_path>,
          'url': <instrument_url>,
          'outofdate': True|False,
          'qcfail': True|False,
          'isvalid': True|False},
        ]
    """
    def __call__(self):
        instruments = []
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(instruments)
        bsc = getToolByName(self, 'portal_catalog')
        method = bsc(portal_type='Method', UID=self.request.get("uid", '0'))
        if method and len(method) == 1:
            method = method[0].getObject()
            for i in method.getInstruments():
                instrument = { 'uid' : i.UID(),
                               'title': i.Title(),
                               'url': i.absolute_url_path(),
                               'outofdate': i.isOutOfDate(),
                               'qcfail': not i.isQCValid(),
                               'isvalid': i.isValid()}
                instruments.append(instrument)
        return json.dumps(instruments)


