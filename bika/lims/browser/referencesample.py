from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName
import json, plone

class QCView(BrowserView):
    pass
#    template = ViewPageTemplateFile("templates/reference_qc.pt")
#    def __call__(self):
#        return self.template()

class AJAXGetReferenceDefinitionResults():
    """ Returns a JSON encoded copy of the ReferenceResults field for a ReferenceDefinition,
        and a list of category UIDS that contain services with results.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        uid = self.request.get('uid', None)
        if not uid:
            return json.dumps({'errors':["No UID specified in request.",]})
        rc = getToolByName(self.context, 'reference_catalog')

        # first grab the reference results themselves
        ref_def = rc.lookupObject(uid)
        if not ref_def:
            return json.dumps({'errors':["Reference Definition %s does not exist."%uid,]})
        results = ref_def.getReferenceResults()
        if not results:
            return json.dumps({'errors':["The reference definition does not define any values.",]})

        # we return a list of category uids so the javascript knows which ones to expand
        categories = []
        for result in results:
            service = rc.lookupObject(result['uid'])
            cat_uid = service.getCategory().UID()
            if cat_uid not in categories: categories.append(cat_uid)

        return json.dumps({'results':results,
                           'categories':categories})
