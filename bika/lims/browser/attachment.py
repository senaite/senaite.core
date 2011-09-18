from Products.Five.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from Products.CMFCore.utils import getToolByName
import json, plone
import plone.protect

class AJAXDeleteAnalysisAttachment():
    """ Removes an analysis attachment. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        attachment_id = form.get('attachment_id', None)
        if not attachment_id:
            return "error"
        rc = getToolByName(self.context, 'reference_catalog')
        client = self.context.aq_parent
        if attachment_id not in client.objectIds():
            return "error"
        attachment = client[attachment_id]
        for analysis in attachment.getBackReferences("AnalysisAttachment"):
            analysis.setAttachment([r for r in analysis.getAttachment() \
                                    if r.id != attachment.id])
        client.manage_delObjects(ids=[attachment_id,])
        return "success"
