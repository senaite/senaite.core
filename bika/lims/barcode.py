from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from bika.lims.browser import BrowserView
from bika.lims.permissions import EditResults

import json
import plone.protect


class barcode_entry(BrowserView):
    """Decide the best redirect URL for any barcode scanned into the browser.
    """
    def __call__(self):
        try:
            plone.protect.CheckAuthenticator(self.request)
        except:
            return self.return_json({
                'success': False,
                'failure': True,
                'error': 'Cannot verify authenticator token'})

        entry = self.get_entry()
        if not entry:
            return self.return_json({
                'success': False,
                'failure': True,
                'error': 'No barcode entry submitted'})

        instance = self.resolve_item(entry)
        if not instance:
            return self.return_json({
                'success': False,
                'failure': True,
                'error': 'Cannot resolve ID or Title: %s' % entry})

        url = getattr(self, 'handle_' + instance.portal_type)(instance) \
            if hasattr(self, 'handle_' + instance.portal_type) \
            else instance.absolute_url()

        return self.return_json({
            'success': True,
            'failure': False,
            'url': url})

    def get_entry(self):
        entry = self.request.get('entry', '')
        entry = entry.replace('*', '')
        entry = entry.strip()
        return entry

    def resolve_item(self, entry):
        for catalog in [self.bika_catalog, self.bika_setup_catalog]:
            brains = catalog(title=entry)
            if brains:
                return brains[0].getObject()
            brains = catalog(id=entry)
            if brains:
                return brains[0].getObject()

    def return_json(self, value):
        output = json.dumps(value)
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')
        self.request.RESPONSE.write(json.dumps(output))
        return output

    def handle_AnalysisRequest(self, instance):
        """Possible redirects for an AR.
        - If AR is sample_due: receive it before proceeding.
        - If AR belongs to Batch, redirect to the BatchBook view.
        - If AR does not belong to Batch:
            - if permission/workflow permit: go to AR manage_results.
        - For other ARs, just redirect to the view screen.
        """
        # - If AR is sample_due: receive it before proceeding.
        wf = getToolByName(self.context, 'portal_workflow')
        if wf.getInfoFor(instance, 'review_state') == 'sample_due':
            try:
                wf.doActionFor(instance, 'receive')
            except WorkflowException:
                pass
        # - If AR belongs to Batch, redirect to the BatchBook view.
        batch = instance.getBatch()
        if batch:
            return batch.absolute_url() + "/batchbook"
        #  - if permission/workflow permit: go to AR manage_results.
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(EditResults, instance):
            return instance.absolute_url() + '/manage_results'
        # - For other ARs, just redirect to the view screen.
        return instance.absolute_url()

    def handle_Sample(self, instance):
        """If this sample has a single AR, go there.
        If the sample has 0 or >1 ARs, go to the sample's view URL.
        """
        ars = instance.getAnalysisRequests()
        if len(ars) == 1:
            return self.handle_AnalysisRequest(instance)
        else:
            return instance.absolute_url()
