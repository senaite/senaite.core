from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import json

class AnalysisRequestAddView(BrowserView):
    """ The main AR Add form
    """
    template = ViewPageTemplateFile("templates/analysisrequest_add.pt")

    col_count = 4

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        request.set('disable_border', 1)

    def __call__(self):
        import pprint
        if self.request.form.has_key("submitted"):
            pprint.pprint(self.request.form)
        else:
            return self.template()

    def portal(self):
        portal_url = getToolByName(self, 'portal_url')
        return portal_url.absolute_url()

    def arprofiles(self):
        """ Return applicable client and Lab ARProfile records
        """
        profiles = []
        pc = getToolByName(self.context, 'portal_catalog')
        for proxy in pc(portal_type = 'ARProfile', getClientUID = self.context.UID(), sort_on = 'sortable_title'):
            profiles.append(proxy.getObject()) #XXX getObject()
        for proxy in pc(portal_type = 'LabARProfile', sort_on = 'sortable_title'):
            profile = proxy.getObject()
            profile.setTitle("Lab: %s" % profile.Title())
            profiles.append(proxy.getObject()) #XXX getObject()
        return profiles

    def Categories(self):
        """ Dictionary keys: field/lab
            Dictionary values: (Category Title,category UID)
        """
        pc = getToolByName(self.context, 'portal_catalog')
        cats = {}
        for service in pc(portal_type = "AnalysisService"):
            poc = service.getPointOfCapture
            if not cats.has_key(poc): cats[poc] = []
            cat = (service.getCategoryName, service.getCategoryUID)
            if cat not in cats[poc]: cats[poc].append(cat)
        return cats

class AnalysisRequestSelectCCView(BrowserView):
    """ The CC Selector popup window uses this view
    """
    template = ViewPageTemplateFile("templates/analysisrequest_select_cc.pt")
    def __call__(self):
        return self.template()

class AnalysisRequestSelectSampleView(BrowserView):
    """ The Sample Selector popup window uses this view
    """
    template = ViewPageTemplateFile("templates/analysisrequest_select_sample.pt")
    def Samples(self, client):
        pc = getToolByName(self.context, 'portal_catalog')
        return pc(portal_type = "Sample", getClient = client)

    def __call__(self):
        return self.template()

class AnalysisRequest_AnalysisServices(BrowserView):
    """ AJAX requests pull this data for insertion when category header rows are clicked.
        The view returns a standard pagetemplate, the entire html of which is inserted.
    """
    template = ViewPageTemplateFile("templates/analysisrequest_analysisservices.pt")
    def __call__(self):
        return self.template()

    def Services(self, CategoryUID, poc):
        pc = getToolByName(self, 'portal_catalog')
        return pc(portal_type = "AnalysisService",
                  getCategoryUID = CategoryUID, getPointOfCapture = poc)

class AnalysisRequest_ProfileServices(BrowserView):
    """ AJAX requests pull this to retrieve a list of services in an AR Profile.
        return JSON data
            {categoryUID: [serviceUID,serviceUID], ...}
    """
    def __call__(self):
        rc = getToolByName(self, 'reference_catalog')
        pc = getToolByName(self, 'portal_catalog')
        profile = rc.lookupObject(self.request['profileUID'])
        if not profile: return

        services = {}
        for service in profile.getService():
            service = pc(portal_type = "AnalysisService", UID = service.UID())[0]
            categoryUID = service.getCategoryUID
            poc = service.getPointOfCapture
            try: services["%s_%s" % (categoryUID, poc)].append(service.UID)
            except: services["%s_%s" % (categoryUID, poc)] = [service.UID, ]
        return json.dumps(services)

class AnalysisRequest_SampleTypes(BrowserView):
    """ autocomplete data source for sample types field
        return JSON data
            [string,string]
    """
    def __call__(self):
        pc = getToolByName(self, 'portal_catalog')
        term = self.request.get('term', '')
        items = [s.Title for s in pc(portal_type = "SampleType") if s.Title.find(term) > -1]
        return json.dumps(items)

class AnalysisRequest_SamplePoints(BrowserView):
    """ autocomplete data source for sample points field
        return JSON data
            [string,string]
    """
    def __call__(self):
        pc = getToolByName(self, 'portal_catalog')
        term = self.request.get('term', '')
        items = [s.Title for s in pc(portal_type = "SamplePoint") if s.Title.find(term) > -1]
        return json.dumps(items)
