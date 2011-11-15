from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Sticker(BrowserView):
    """ Invoked via URL on an object, we render a sticker for that object.
        Used manually with a list of objects, renders stickers for all
        provided objects, and invokes a print dialog.
    """
    ar_small = ViewPageTemplateFile("templates/analysisrequest_sticker_small.pt")
    ar_large = ViewPageTemplateFile("templates/analysisrequest_sticker.pt")
    sample_small = ViewPageTemplateFile("templates/sample_sticker_small.pt")
    sample_large = ViewPageTemplateFile("templates/sample_sticker.pt")
    referencesample_sticker = ViewPageTemplateFile("templates/referencesample_sticker.pt")

    def __call__(self):
        pc = getToolByName(self.context, 'portal_catalog')
        items = self.request.get('items', '')
        if items:
            self.items = [o.getObject() for o in pc(id=items.split(","))]
        else:
            # otherwise the label icon was clicked on a single object
            self.items = [self.context,]

        if self.items[0].portal_type == 'AnalysisRequest':
            if self.request.get('size', '') == 'small':
                return self.ar_small()
            else:
                return self.ar_large()
        elif self.items[0].portal_type == 'Sample':
            if self.request.get('size', '') == 'small':
                return self.sample_small()
            else:
                return self.sample_large()
        elif self.items[0].portal_type == 'ReferenceSample':
            return self.referencesample_sticker()
