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

class ajaxGetMethodServiceInstruments(BrowserView):
    """ Returns a json list with the instruments assigned to the method
        and to the analysis service with the following structure:
        [{'uid': <instrument_uid>,
          'title': <instrument_absolute_path>,
          'url': <instrument_url>,
          'outofdate': True|False,
          'qcfail': True|False,
          'isvalid': True|False},
        ]
        If no method assigned, returns the instruments assigned to the
        service that have no method assigned.
        If no service assigned, returns empty
    """
    def __call__(self):
        instruments = []
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(instruments)

        uc = getToolByName(self, 'uid_catalog')
        service = uc(portal_type='AnalysisService', UID=self.request.get("suid", '0'))
        if not service or len(service) != 1:
            return json.dumps(instruments)

        service = service[0].getObject()
        sinstr = service.getAvailableInstruments()
        if not sinstr:
            return json.dumps(instruments)

        method = uc(portal_type='Method', UID=self.request.get("muid", '0'))
        if not method or len(method) != 1:
            for i in sinstr:
                if not i.getMethod():
                    instrument = { 'uid' : i.UID(),
                                   'title': i.Title(),
                                   'url': i.absolute_url_path(),
                                   'outofdate': i.isOutOfDate(),
                                   'qcfail': not i.isQCValid(),
                                   'isvalid': i.isValid()}
                    instruments.append(instrument)
            return json.dumps(instruments)

        method = method[0].getObject()
        iuids = [s.UID() for s in sinstr]
        for i in method.getInstruments():
            if i.UID() in iuids:
                instrument = { 'uid' : i.UID(),
                               'title': i.Title(),
                               'url': i.absolute_url_path(),
                               'outofdate': i.isOutOfDate(),
                               'qcfail': not i.isQCValid(),
                               'isvalid': i.isValid()}
                instruments.append(instrument)
        return json.dumps(instruments)
