from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims import interfaces
from bika.lims import logger
from bika.lims.permissions import EditResults, EditWorksheet
import plone.protect

class barcode_entry(BrowserView):
    """ return redirect url if the item exists
        passes the request to catalog
    """
    def __call__(self):
        try:
            plone.protect.CheckAuthenticator(self.request)
            plone.protect.PostOnly(self.request)
        except:
            return ""

        mtool = getToolByName(self.context, 'portal_membership')
        uc = getToolByName(self.context, 'uid_catalog')
        entry = self.request.get("entry", '').replace("*", "")

        items = uc(UID=entry)
        if not items:
            return ""
        item = items[0].getObject()

        if item.portal_type == "AnalysisRequest":
            if mtool.checkPermission(EditResults, item):
                destination_url = item.absolute_url() + "/manage_results"
            else:
                destination_url = item.absolute_url()
            return self.request.response.redirect(destination_url)

        elif item.portal_type == "Sample":
            ars = item.getAnalysisRequests()
            if len(ars) == 1:
                # If there's only one AR, go there
                if mtool.checkPermission(EditResults, ars[0]):
                    destination_url = ars[0].absolute_url() + "/manage_results"
                else:
                    destination_url = ars[0].absolute_url()
                return self.request.response.redirect(destination_url)
            else:
                # multiple or no ARs: direct to sample.
                destination_url = item.absolute_url()
                return self.request.response.redirect(destination_url)

        elif item.portal_type == "Worksheet":
            if mtool.checkPermission(EditWorksheet, item):
                destination_url = item.absolute_url()
                return self.request.response.redirect(destination_url)

        elif item.portal_type == "ReferenceSample":
            destination_url = item.absolute_url()
            return self.request.response.redirect(destination_url)


"""
Sample round/COC the user lands on the sampling round's view, if he/she is\
authorised to see it
"""
